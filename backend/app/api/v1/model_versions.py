from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Any
import uuid, os
import httpx
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.model_version import ModelVersion
from app.core.permissions import require_admin, get_current_user_optional
from app.models.user import User

router = APIRouter()


class ModelVersionOut(BaseModel):
    id: uuid.UUID
    version_tag: str
    model_path: str
    training_samples_count: Optional[int] = None
    val_samples_count: Optional[int] = None
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    base_model: Optional[str] = None
    hyperparams: Optional[dict] = None
    trained_at: datetime
    is_active: bool
    notes: Optional[str] = None
    model_config = {"from_attributes": True}


class ModelVersionCreate(BaseModel):
    version_tag: str
    model_path: str
    training_samples_count: Optional[int] = None
    val_samples_count: Optional[int] = None
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    classification_report: Optional[Any] = None
    confusion_matrix: Optional[Any] = None
    base_model: Optional[str] = None
    hyperparams: Optional[dict] = None
    notes: Optional[str] = None


def _check_access(x_internal_key: Optional[str], current_user: Optional[User]):
    internal_key = os.getenv("INTERNAL_API_KEY", "")
    if x_internal_key and internal_key and x_internal_key == internal_key:
        return
    if current_user and current_user.role == "admin":
        return
    raise HTTPException(status_code=403, detail="Acceso denegado")


@router.get("", response_model=List[ModelVersionOut])
async def list_versions(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(
        select(ModelVersion).order_by(ModelVersion.trained_at.desc())
    )
    return result.scalars().all()


@router.post("/{version_id}/activate", response_model=ModelVersionOut)
async def activate_version(
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(ModelVersion).where(ModelVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Versión no encontrada")

    # Tell AI service to load this version
    ai_url = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            r = await client.post(f"{ai_url}/metrics/activate", json={"version_tag": version.version_tag})
            if r.status_code != 200:
                raise HTTPException(status_code=502, detail=f"AI service error: {r.text}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado cargando el modelo. Intenta de nuevo.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"No se pudo conectar al AI service: {e}")

    # Update is_active in DB
    prev = await db.execute(select(ModelVersion).where(ModelVersion.is_active == True))
    for v in prev.scalars().all():
        v.is_active = False
    version.is_active = True
    await db.commit()
    await db.refresh(version)
    return version


@router.delete("/{version_id}", status_code=204)
async def delete_version(
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(ModelVersion).where(ModelVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Versión no encontrada")
    if version.is_active:
        raise HTTPException(status_code=400, detail="No se puede eliminar el modelo activo. Activa otro primero.")

    # Borrar archivos del disco via AI service
    ai_url = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            await client.delete(f"{ai_url}/metrics/versions/{version.version_tag}")
    except Exception:
        pass  # Si falla el borrado en disco, igual eliminar de BD

    await db.delete(version)
    await db.commit()


@router.post("", response_model=ModelVersionOut, status_code=201)
async def create_version(
    data: ModelVersionCreate,
    db: AsyncSession = Depends(get_db),
    x_internal_key: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    _check_access(x_internal_key, current_user)
    # Desactivar versiones anteriores
    prev = await db.execute(select(ModelVersion).where(ModelVersion.is_active == True))
    for v in prev.scalars().all():
        v.is_active = False
    version = ModelVersion(**data.model_dump(exclude_none=True), is_active=True)
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version
