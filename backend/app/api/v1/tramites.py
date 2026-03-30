from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.tramite import Tramite, Requirement
from app.schemas.tramite import TramiteCreate, TramiteUpdate, TramiteOut, TramiteSummary, RequirementCreate, RequirementOut
from app.core.permissions import require_admin, get_current_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[TramiteSummary])
async def list_tramites(
    category: Optional[str] = None,
    applies_to: Optional[str] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    query = select(Tramite).order_by(Tramite.order_index)
    if not include_inactive:
        query = query.where(Tramite.is_active == True)
    if category:
        query = query.where(Tramite.category == category)
    if applies_to:
        query = query.where(or_(Tramite.applies_to == applies_to, Tramite.applies_to == "all"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/search", response_model=List[TramiteSummary])
async def search_tramites(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    query = select(Tramite).where(
        Tramite.is_active == True,
        or_(
            Tramite.name.ilike(f"%{q}%"),
            Tramite.description.ilike(f"%{q}%"),
        )
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{tramite_id}", response_model=TramiteOut)
async def get_tramite(tramite_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tramite).where(Tramite.id == tramite_id))
    tramite = result.scalar_one_or_none()
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    return tramite


@router.post("", response_model=TramiteOut, status_code=201)
async def create_tramite(data: TramiteCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    tramite = Tramite(**data.model_dump())
    db.add(tramite)
    await db.commit()
    await db.refresh(tramite)
    return tramite


@router.put("/{tramite_id}", response_model=TramiteOut)
async def update_tramite(tramite_id: uuid.UUID, data: TramiteUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Tramite).where(Tramite.id == tramite_id))
    tramite = result.scalar_one_or_none()
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(tramite, field, value)
    await db.commit()
    await db.refresh(tramite)
    return tramite


@router.delete("/{tramite_id}", status_code=204)
async def delete_tramite(tramite_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Tramite).where(Tramite.id == tramite_id))
    tramite = result.scalar_one_or_none()
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    tramite.is_active = False
    await db.commit()


@router.post("/{tramite_id}/requirements", response_model=RequirementOut, status_code=201)
async def add_requirement(tramite_id: uuid.UUID, data: RequirementCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    req = Requirement(tramite_id=tramite_id, **data.model_dump())
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req


@router.put("/{tramite_id}/requirements/{req_id}", response_model=RequirementOut)
async def update_requirement(tramite_id: uuid.UUID, req_id: uuid.UUID, data: RequirementCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Requirement).where(Requirement.id == req_id, Requirement.tramite_id == tramite_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")
    for field, value in data.model_dump().items():
        setattr(req, field, value)
    await db.commit()
    await db.refresh(req)
    return req


@router.delete("/{tramite_id}/requirements/{req_id}", status_code=204)
async def delete_requirement(tramite_id: uuid.UUID, req_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    result = await db.execute(select(Requirement).where(Requirement.id == req_id, Requirement.tramite_id == tramite_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Requisito no encontrado")
    await db.delete(req)
    await db.commit()
