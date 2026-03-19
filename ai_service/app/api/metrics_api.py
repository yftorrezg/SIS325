from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
from app.models.classifier import classifier_model
from app.models.claude_client import set_runtime_key, clear_runtime_key, get_key_status
from app.config import settings

router = APIRouter()


class ModelInfo(BaseModel):
    is_loaded: bool
    version: str
    method: str
    device: str


@router.get("/model-info", response_model=ModelInfo)
async def model_info():
    return ModelInfo(
        is_loaded=classifier_model.is_loaded,
        version=classifier_model.current_version,
        method="bert" if classifier_model.is_loaded else "keyword-fallback",
        device=classifier_model._device,
    )


@router.get("/labels")
async def get_labels():
    from app.models.classifier import TRAMITE_LABELS
    return {"labels": TRAMITE_LABELS, "count": len(TRAMITE_LABELS)}


@router.get("/versions")
async def list_versions():
    """List all model versions saved on disk."""
    classifier_dir = settings.classifier_path
    if not classifier_dir.exists():
        return {"versions": []}
    versions = []
    for p in sorted(classifier_dir.iterdir()):
        if p.is_dir() and p.name != "active":
            version_file = p / "version.txt"
            tag = version_file.read_text().strip() if version_file.exists() else p.name
            is_active = classifier_model.current_version == tag
            versions.append({"version_tag": tag, "path": str(p), "is_active": is_active})
    return {"versions": versions}


class ActivateRequest(BaseModel):
    version_tag: str


@router.delete("/versions/{version_tag}")
async def delete_version(version_tag: str):
    """Delete a model version from disk."""
    model_path = settings.classifier_path / version_tag
    if not model_path.exists():
        raise HTTPException(status_code=404, detail=f"Versión '{version_tag}' no encontrada")
    import shutil
    shutil.rmtree(str(model_path))
    freed_mb = 0  # already deleted, can't measure after
    return {"ok": True, "deleted": version_tag}


@router.get("/claude-status")
async def claude_status():
    """Check if Claude layer is active."""
    return get_key_status()


class ClaudeKeyRequest(BaseModel):
    api_key: str


@router.post("/claude-key")
async def set_claude_key(req: ClaudeKeyRequest):
    """Activate Claude layer with an API key (stored in memory only)."""
    if not req.api_key or not req.api_key.strip().startswith("sk-ant-"):
        raise HTTPException(status_code=400, detail="API key inválida. Debe comenzar con 'sk-ant-'")
    set_runtime_key(req.api_key.strip())
    return {"ok": True, "message": "Claude activado correctamente"}


@router.delete("/claude-key")
async def delete_claude_key():
    """Deactivate Claude layer."""
    clear_runtime_key()
    return {"ok": True, "message": "Claude desactivado. El chatbot usará respuestas estáticas."}


@router.post("/activate")
async def activate_version(req: ActivateRequest):
    """Load a specific model version as the active model."""
    model_path = settings.classifier_path / req.version_tag
    if not model_path.exists() or not (model_path / "config.json").exists():
        raise HTTPException(status_code=404, detail=f"Versión '{req.version_tag}' no encontrada en disco")

    import asyncio, shutil

    def _load_and_swap():
        classifier_model._load_from_disk(str(model_path))
        active_path = settings.classifier_active_path
        if active_path.exists():
            shutil.rmtree(str(active_path))
        shutil.copytree(str(model_path), str(active_path))

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _load_and_swap)
    return {"ok": True, "active_version": classifier_model.current_version}
