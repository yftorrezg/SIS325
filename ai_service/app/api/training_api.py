"""
Training API - triggers BERT fine-tuning jobs.
"""
import asyncio
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.training.trainer import fine_tune_classifier
from app.config import settings

router = APIRouter()

# In-memory job tracking (use Redis in production)
_jobs: Dict[str, dict] = {}


class TrainRequest(BaseModel):
    version_tag: str
    base_model: str = "dccuchile/bert-base-spanish-wwm-cased"
    epochs: int = 3
    batch_size: int = 16
    learning_rate: float = 2e-5
    dropout: float = 0.1
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    max_length: int = 128
    notes: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: str  # started | running | completed | failed
    progress: float = 0.0
    message: str = ""
    metrics: Optional[Dict[str, Any]] = None


async def run_training_job(job_id: str, config: TrainRequest):
    _jobs[job_id] = {"status": "running", "progress": 0.1, "message": "Iniciando entrenamiento..."}
    try:
        metrics = await fine_tune_classifier(
            version_tag=config.version_tag,
            base_model=config.base_model,
            epochs=config.epochs,
            batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            dropout=config.dropout,
            warmup_ratio=config.warmup_ratio,
            weight_decay=config.weight_decay,
            max_length=config.max_length,
            progress_callback=lambda p, msg: _jobs.update({job_id: {"status": "running", "progress": p, "message": msg}}),
        )
        _jobs[job_id] = {"status": "completed", "progress": 1.0, "message": "Entrenamiento completado", "metrics": metrics}
    except Exception as e:
        _jobs[job_id] = {"status": "failed", "progress": 0.0, "message": str(e)}


@router.post("", response_model=JobStatus, status_code=202)
async def start_training(config: TrainRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "started", "progress": 0.0, "message": "En cola..."}
    background_tasks.add_task(run_training_job, job_id, config)
    return JobStatus(job_id=job_id, status="started", message="Trabajo de entrenamiento iniciado")


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    job = _jobs[job_id]
    return JobStatus(job_id=job_id, **job)
