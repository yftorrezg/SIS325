"""
BERT-based text classifier for tramite intent detection.
Uses dccuchile/bert-base-spanish-wwm-cased fine-tuned on tramite utterances.
Falls back to keyword-based classification if model not loaded.
20 labels: 16 tramites + 4 conversational intents.
"""
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional
import torch
from app.config import settings

logger = logging.getLogger(__name__)

TRAMITE_LABELS = [
    # Matrícula
    "TRAMITE_MATRICULA_ALUMNO_NUEVO",
    "TRAMITE_MATRICULA_ALUMNO_REGULAR",
    # Titulación
    "TRAMITE_DIPLOMA_ACADEMICO",
    "TRAMITE_TITULO_PROVISION_NACIONAL",
    "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION",
    # Certificados y trámites académicos
    "SOLICITUD_CERTIFICADO_KARDEX",
    "SOLICITUD_CAMBIO_CARRERA",
    "SOLICITUD_CARRERA_SIMULTANEA",
    "SOLICITUD_REPROGRAMACIONES",
    "SOLICITUD_HOMOLOGACION_MATERIAS",
    # Bienestar e identificación
    "TRAMITE_BECAS",
    "CARNET_UNIVERSITARIO",
    "SEGURO_SOCIAL_UNIVERSITARIO",
    # Procesos en sistema web
    "PROCESO_MATRICULACION_WEB",
    "PROCESO_PROGRAMACION_ACADEMICA",
    # Conversacionales
    "SALUDO_BIENVENIDA",
    "DESPEDIDA",
    "AGRADECIMIENTO",
    "FALLBACK",
]

# Keyword fallback — used when no fine-tuned model is available
KEYWORD_MAP: dict[str, list[str]] = {
    "TRAMITE_MATRICULA_ALUMNO_NUEVO": [
        "nuevo", "bachiller", "primera vez", "admitido", "admisión", "admision",
        "preuniversitario", "primer ingreso", "ingreso nuevo", "inscribirme por primera",
        "recién bachiller", "acabo de salir del colegio", "entrar a la usfx",
    ],
    "TRAMITE_MATRICULA_ALUMNO_REGULAR": [
        "renovar matrícula", "matrícula regular", "matricularme", "pagar semestre",
        "banco unión matrícula", "depósito matrícula", "renovar inscripción",
        "ya soy alumno", "matrícula semestre", "volver a matricularme",
    ],
    "TRAMITE_DIPLOMA_ACADEMICO": [
        "diploma académico", "diploma academico", "sacar diploma", "trámite diploma",
        "requisitos diploma", "solvencia universitaria", "certificado conclusión",
        "terminé la carrera diploma", "obtener diploma",
        "titulación", "titulacion", "graduarme", "proceso de graduación", "modalidad de titulación",
        "tesis", "proyecto de grado", "examen de grado", "trabajo dirigido",
        "terminé todas las materias graduación", "obtener título graduación",
    ],
    "TRAMITE_TITULO_PROVISION_NACIONAL": [
        "título provisión", "titulo provision", "provisión nacional", "título profesional",
        "trámite título", "titulo en provision", "título en provisión",
    ],
    "TRAMITE_SIMULTANEO_DIPLOMA_PROVISION": [
        "simultáneo", "simultaneo", "diploma y título", "los dos", "ambos trámites",
        "diploma y provisión", "al mismo tiempo", "trámite simultáneo",
    ],
    "SOLICITUD_CERTIFICADO_KARDEX": [
        "kardex", "certificado de notas", "historial académico", "certificado académico",
        "notas oficiales", "solicitar kardex", "pedir certificado", "record académico",
        "constancia de notas", "certificado de estudios",
    ],
    "SOLICITUD_CAMBIO_CARRERA": [
        "cambio de carrera", "cambiar de carrera", "cambiarme de carrera",
        "pasar a otra carrera", "transferirme de carrera", "quiero cambiarme",
        "solicitud cambio carrera",
    ],
    "SOLICITUD_CARRERA_SIMULTANEA": [
        "carrera simultánea", "simultanea", "doble carrera", "dos carreras",
        "estudiar dos carreras", "segunda carrera", "carrera al mismo tiempo",
    ],
    "SOLICITUD_REPROGRAMACIONES": [
        "reprogramación", "reprogramar examen", "faltei al examen", "falté al examen",
        "justificar falta", "reprogramar parcial", "no pude dar el examen",
        "ausencia examen", "reprogramar final",
    ],
    "SOLICITUD_HOMOLOGACION_MATERIAS": [
        "homologación", "homologar", "equivalencia", "materias equivalentes",
        "reconocer materias", "validar materias", "homologación de materias",
        "materias de otra universidad", "equivalencias académicas",
    ],
    "TRAMITE_BECAS": [
        "beca", "becas", "beca universitaria", "beca por mérito", "beca académica",
        "beca económica", "solicitar beca", "convocatoria becas", "apoyo económico",
    ],
    "CARNET_UNIVERSITARIO": [
        "carnet universitario", "carnet estudiantil", "reponer carnet", "perdí mi carnet",
        "renovar carnet", "carne universitario", "identificación estudiantil",
        "carnet usfx", "credencial universitaria",
    ],
    "SEGURO_SOCIAL_UNIVERSITARIO": [
        "seguro social", "ssu", "seguro médico", "seguro universitario",
        "ficha médica", "ficha medica", "atención médica", "ssu-sucre",
        "cita médica", "atenderme en el seguro",
    ],
    "PROCESO_MATRICULACION_WEB": [
        "universitarios.usfx", "si2.usfx", "suniver", "número de depósito",
        "numero de deposito", "qr matrícula", "sistema web matrícula",
        "pago qr", "papeleta depósito", "no carga el sistema",
    ],
    "PROCESO_PROGRAMACION_ACADEMICA": [
        "programarme", "programación académica", "programacion", "inscribir materias",
        "seleccionar materias", "mis programaciones", "programación de materias",
        "programación manual", "programación automática",
    ],
    "SALUDO_BIENVENIDA": [
        "hola", "buenos días", "buenas tardes", "buenas noches", "buenas",
        "hey", "necesito ayuda", "alguien me puede ayudar", "buen día",
    ],
    "DESPEDIDA": [
        "adiós", "adios", "hasta luego", "chau", "bye", "hasta pronto",
        "nos vemos", "ya fue", "ya me voy",
    ],
    "AGRADECIMIENTO": [
        "gracias", "muchas gracias", "grax", "agradecido", "se agradece",
        "mil gracias", "muy amable", "excelente gracias",
    ],
}


def keyword_classify(text: str) -> tuple[str, float]:
    """Fallback keyword-based classification."""
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for label, keywords in KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[label] = score
    if not scores:
        return "FALLBACK", 0.5
    best = max(scores, key=scores.get)
    confidence = min(scores[best] / 2.0, 0.85)
    return best, confidence


class ClassifierModel:
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._label2id = {label: i for i, label in enumerate(TRAMITE_LABELS)}
        self._id2label = {i: label for i, label in enumerate(TRAMITE_LABELS)}
        self.is_loaded = False
        self.current_version = "none"
        self._device = "cuda" if (settings.use_gpu and torch.cuda.is_available()) else "cpu"

    async def load(self):
        """Load fine-tuned model if available, otherwise use keyword fallback."""
        active_path = settings.classifier_active_path
        if active_path.exists() and (active_path / "config.json").exists():
            await asyncio.get_event_loop().run_in_executor(None, self._load_from_disk, str(active_path))
        else:
            logger.info("No fine-tuned model found. Using keyword fallback until first training.")
            self.is_loaded = False
            self.current_version = "keyword-fallback"

    def _load_from_disk(self, model_path: str):
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        try:
            logger.info(f"Loading classifier from {model_path}")
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self._model.to(self._device)
            self._model.eval()
            version_file = Path(model_path) / "version.txt"
            self.current_version = version_file.read_text().strip() if version_file.exists() else "unknown"
            self.is_loaded = True
            logger.info(f"Classifier loaded on {self._device}, version: {self.current_version}")
        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")
            self.is_loaded = False

    def unload(self):
        self._model = None
        self._tokenizer = None
        self.is_loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def predict(self, text: str, top_k: int = 3) -> dict:
        """Classify text and return label + confidence scores."""
        if not self.is_loaded:
            label, confidence = keyword_classify(text)
            return {
                "label": label,
                "confidence": confidence,
                "top_k": [{"label": label, "score": confidence}],
                "method": "keyword",
            }

        with torch.no_grad():
            inputs = self._tokenizer(
                text, return_tensors="pt", truncation=True, max_length=128, padding=True
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).squeeze().cpu().tolist()

        scored = sorted(
            [(self._id2label[i], p) for i, p in enumerate(probs)],
            key=lambda x: -x[1],
        )
        return {
            "label": scored[0][0],
            "confidence": scored[0][1],
            "top_k": [{"label": l, "score": s} for l, s in scored[:top_k]],
            "method": "bert",
        }

    def swap_model(self, new_model_path: str, version_tag: str):
        """Hot-swap to a newly trained model."""
        old_model = self._model
        old_tokenizer = self._tokenizer
        try:
            self._load_from_disk(new_model_path)
            logger.info(f"Model swapped to version {version_tag}")
        except Exception as e:
            logger.error(f"Swap failed, reverting: {e}")
            self._model = old_model
            self._tokenizer = old_tokenizer


# Global singleton
classifier_model = ClassifierModel()
