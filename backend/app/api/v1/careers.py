from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.career import Career
from app.core.permissions import require_admin
from app.models.user import User
import uuid
from pydantic import BaseModel
from typing import Optional


class CareerOut(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    kardex_type: str
    is_active: bool
    model_config = {"from_attributes": True}


class CareerCreate(BaseModel):
    name: str
    code: str
    kardex_type: str


router = APIRouter()


@router.get("", response_model=List[CareerOut])
async def list_careers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Career).where(Career.is_active == True).order_by(Career.name))
    return result.scalars().all()


@router.post("", response_model=CareerOut, status_code=201)
async def create_career(data: CareerCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    career = Career(**data.model_dump())
    db.add(career)
    await db.commit()
    await db.refresh(career)
    return career
