from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid, os
from app.database import get_db
from app.models.training_sample import TrainingSample
from app.core.permissions import require_admin, get_current_user_optional
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime


class SampleCreate(BaseModel):
    text: str
    label: str
    source: str = "manual"


class SampleUpdate(BaseModel):
    text: Optional[str] = None
    label: Optional[str] = None


class SampleOut(BaseModel):
    id: uuid.UUID
    text: str
    label: str
    source: str
    verified: bool
    created_at: datetime
    model_config = {"from_attributes": True}


router = APIRouter()


@router.get("/samples", response_model=List[SampleOut])
async def list_samples(
    label: Optional[str] = None,
    verified: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    x_internal_key: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    internal_key = os.getenv("INTERNAL_API_KEY", "")
    is_internal = x_internal_key and internal_key and x_internal_key == internal_key
    is_admin = current_user and current_user.role == "admin"
    if not is_internal and not is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado")

    query = select(TrainingSample).order_by(TrainingSample.created_at.desc()).limit(limit).offset(offset)
    if label:
        query = query.where(TrainingSample.label == label)
    if verified is not None:
        query = query.where(TrainingSample.verified == verified)
    if search:
        query = query.where(TrainingSample.text.ilike(f"%{search}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/samples", response_model=SampleOut, status_code=201)
async def create_sample(data: SampleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    sample = TrainingSample(**data.model_dump())
    db.add(sample)
    await db.commit()
    await db.refresh(sample)
    return sample


@router.put("/samples/{sample_id}", response_model=SampleOut)
async def update_sample(sample_id: uuid.UUID, data: SampleUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(TrainingSample).where(TrainingSample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Muestra no encontrada")
    if data.text is not None:
        sample.text = data.text
    if data.label is not None:
        sample.label = data.label
    await db.commit()
    await db.refresh(sample)
    return sample


@router.put("/samples/{sample_id}/verify", response_model=SampleOut)
async def verify_sample(sample_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)):
    result = await db.execute(select(TrainingSample).where(TrainingSample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Muestra no encontrada")
    sample.verified = True
    sample.verified_by_id = current_user.id
    await db.commit()
    await db.refresh(sample)
    return sample


@router.delete("/samples/{sample_id}", status_code=204)
async def delete_sample(sample_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(TrainingSample).where(TrainingSample.id == sample_id))
    sample = result.scalar_one_or_none()
    if not sample:
        raise HTTPException(status_code=404, detail="Muestra no encontrada")
    await db.delete(sample)
    await db.commit()


@router.get("/samples/count")
async def count_samples(
    label: Optional[str] = None,
    verified: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(func.count(TrainingSample.id))
    if label:
        query = query.where(TrainingSample.label == label)
    if verified is not None:
        query = query.where(TrainingSample.verified == verified)
    if search:
        query = query.where(TrainingSample.text.ilike(f"%{search}%"))
    result = await db.execute(query)
    return {"total": result.scalar()}


@router.get("/samples/stats")
async def sample_stats(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(TrainingSample.label, func.count(TrainingSample.id)).group_by(TrainingSample.label))
    return {"distribution": {row[0]: row[1] for row in result.all()}}
