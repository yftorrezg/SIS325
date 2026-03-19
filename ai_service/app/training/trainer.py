"""
BERT fine-tuning pipeline for tramite classification.
Fetches labeled samples from backend API, trains, evaluates, and saves model.
"""
import json
import logging
import asyncio
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import httpx
import torch
from app.config import settings
from app.models.classifier import TRAMITE_LABELS, classifier_model

logger = logging.getLogger(__name__)


async def fetch_training_data(min_samples: int = 10) -> tuple[list, list]:
    """Fetch verified training samples from backend."""
    texts, labels = [], []
    fetched_from_api = False
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{settings.backend_url}/api/v1/training/samples",
                params={"verified": True, "limit": 10000},
                headers={"X-Internal-Key": settings.internal_api_key},
            )
            if resp.status_code == 200:
                samples = resp.json()
                for s in samples:
                    if s["label"] in TRAMITE_LABELS:
                        texts.append(s["text"])
                        labels.append(s["label"])
                fetched_from_api = True
            else:
                logger.warning(f"Backend returned {resp.status_code}, falling back to local dataset")
    except Exception as e:
        logger.warning(f"Could not fetch from backend, using local dataset: {e}")

    if not fetched_from_api:
        # Fall back to local JSONL (dev path relative to this file, or Docker path)
        local_path = Path(__file__).parent.parent / "data" / "training" / "tramites_dataset.jsonl"
        if not local_path.exists():
            local_path = Path("/app/data/training/tramites_dataset.jsonl")
        if local_path.exists():
            for line in local_path.read_text(encoding="utf-8").strip().split("\n"):
                if line:
                    sample = json.loads(line)
                    if sample.get("label") in TRAMITE_LABELS:
                        texts.append(sample["text"])
                        labels.append(sample["label"])
        else:
            logger.error(f"Local dataset not found at {local_path}")
    return texts, labels


def _train_sync(
    texts: list,
    labels: list,
    version_tag: str,
    base_model: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    dropout: float,
    warmup_ratio: float,
    weight_decay: float,
    max_length: int,
    progress_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    """Synchronous training function (runs in executor)."""
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
    from transformers import DataCollatorWithPadding, TrainerCallback
    from datasets import Dataset
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
    import numpy as np

    label2id = {l: i for i, l in enumerate(TRAMITE_LABELS)}
    id2label = {i: l for i, l in enumerate(TRAMITE_LABELS)}

    label_ids = [label2id[l] for l in labels]

    if progress_callback:
        progress_callback(0.05, "Dividiendo dataset en train/val...")

    texts_train, texts_val, labels_train, labels_val = train_test_split(
        texts, label_ids, test_size=0.15, random_state=42, stratify=label_ids
    )

    if progress_callback:
        progress_callback(0.1, f"Cargando tokenizador {base_model}...")

    tokenizer = AutoTokenizer.from_pretrained(base_model)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=max_length, padding=False)

    train_ds = Dataset.from_dict({"text": texts_train, "label": labels_train}).map(tokenize, batched=True)
    val_ds = Dataset.from_dict({"text": texts_val, "label": labels_val}).map(tokenize, batched=True)

    if progress_callback:
        progress_callback(0.2, f"Cargando modelo {base_model}...")

    from transformers import AutoConfig
    config = AutoConfig.from_pretrained(
        base_model,
        num_labels=len(TRAMITE_LABELS),
        id2label=id2label,
        label2id=label2id,
    )
    # Aplicar dropout según la arquitectura del modelo
    arch = config.model_type  # bert | roberta | distilbert | xlm-roberta
    if arch == "distilbert":
        config.seq_classif_dropout = dropout
    elif arch in ("bert", "roberta", "xlm-roberta"):
        config.hidden_dropout_prob = dropout
        config.attention_probs_dropout_prob = dropout
    else:
        # Intentar ambos, ignorar si no aplica
        for attr in ("hidden_dropout_prob", "attention_probs_dropout_prob", "seq_classif_dropout"):
            if hasattr(config, attr):
                setattr(config, attr, dropout)

    model = AutoModelForSequenceClassification.from_pretrained(
        base_model,
        config=config,
        ignore_mismatched_sizes=True,
    )

    output_dir = str(settings.classifier_path / version_tag)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        warmup_ratio=warmup_ratio,
        weight_decay=weight_decay,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        fp16=torch.cuda.is_available(),
        logging_steps=10,
        report_to="none",
        gradient_accumulation_steps=2,
    )

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    class ProgressCallback(TrainerCallback):
        def on_epoch_end(self, args, state, control, **kwargs):
            if progress_callback:
                p = 0.2 + (state.epoch / epochs) * 0.6
                progress_callback(p, f"Época {int(state.epoch)}/{epochs} completada")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=data_collator,
        callbacks=[ProgressCallback()],
    )

    if progress_callback:
        progress_callback(0.25, "Iniciando entrenamiento BERT...")

    trainer.train()

    if progress_callback:
        progress_callback(0.85, "Evaluando modelo...")

    # Evaluate
    preds_output = trainer.predict(val_ds)
    preds = np.argmax(preds_output.predictions, axis=1)
    true_labels = preds_output.label_ids

    accuracy = accuracy_score(true_labels, preds)
    f1 = f1_score(true_labels, preds, average="weighted")
    cm = confusion_matrix(true_labels, preds).tolist()
    report = classification_report(true_labels, preds, target_names=TRAMITE_LABELS, output_dict=True)

    if progress_callback:
        progress_callback(0.9, "Guardando modelo...")

    # Save model
    model_save_path = Path(output_dir)
    trainer.save_model(str(model_save_path))
    tokenizer.save_pretrained(str(model_save_path))
    (model_save_path / "version.txt").write_text(version_tag)

    # Activate new model (symlink / copy path)
    active_path = settings.classifier_active_path
    active_path.mkdir(parents=True, exist_ok=True)
    import shutil
    if active_path.exists():
        shutil.rmtree(str(active_path))
    shutil.copytree(str(model_save_path), str(active_path))

    if progress_callback:
        progress_callback(0.95, "Activando nuevo modelo...")

    # Hot-swap
    classifier_model.swap_model(str(active_path), version_tag)

    metrics = {
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "training_samples": len(texts_train),
        "val_samples": len(texts_val),
        "confusion_matrix": cm,
        "classification_report": report,
        "labels": TRAMITE_LABELS,
        "base_model": base_model,
        "hyperparams": {
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "dropout": dropout,
            "warmup_ratio": warmup_ratio,
            "weight_decay": weight_decay,
            "max_length": max_length,
        },
    }
    return metrics


async def fine_tune_classifier(
    version_tag: str,
    base_model: str = "dccuchile/bert-base-spanish-wwm-cased",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    dropout: float = 0.1,
    warmup_ratio: float = 0.1,
    weight_decay: float = 0.01,
    max_length: int = 128,
    progress_callback: Optional[Callable] = None,
) -> Dict[str, Any]:
    texts, labels = await fetch_training_data()
    if len(texts) < 20:
        raise ValueError(f"Insufficient training data: {len(texts)} samples (minimum 20)")

    if progress_callback:
        progress_callback(0.02, f"Dataset cargado: {len(texts)} muestras")

    loop = asyncio.get_event_loop()
    metrics = await loop.run_in_executor(
        None,
        _train_sync,
        texts, labels, version_tag, base_model, epochs, batch_size,
        learning_rate, dropout, warmup_ratio, weight_decay, max_length, progress_callback,
    )

    # Guardar version en el backend
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            await client.post(
                f"{settings.backend_url}/api/v1/model-versions",
                json={
                    "version_tag": version_tag,
                    "model_path": str(settings.classifier_path / version_tag),
                    "training_samples_count": metrics["training_samples"],
                    "val_samples_count": metrics["val_samples"],
                    "accuracy": metrics["accuracy"],
                    "f1_score": metrics["f1_score"],
                    "classification_report": metrics["classification_report"],
                    "confusion_matrix": metrics["confusion_matrix"],
                    "base_model": metrics["base_model"],
                    "hyperparams": metrics["hyperparams"],
                },
                headers={"X-Internal-Key": settings.internal_api_key},
            )
    except Exception as e:
        logger.warning(f"No se pudo guardar la version en el backend: {e}")

    return metrics
