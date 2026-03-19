from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import uuid
from app.database import get_db
from app.models.notification import Notification
from app.core.permissions import get_current_user
from app.models.user import User
from pydantic import BaseModel
from datetime import datetime


class NotificationOut(BaseModel):
    id: uuid.UUID
    type: str | None
    title: str | None
    message: str | None
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}


router = APIRouter()


@router.get("", response_model=List[NotificationOut])
async def get_notifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(50))
    return result.scalars().all()


@router.put("/{notif_id}/read", status_code=204)
async def mark_read(notif_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.execute(update(Notification).where(Notification.id == notif_id, Notification.user_id == current_user.id).values(is_read=True))
    await db.commit()


@router.put("/read-all", status_code=204)
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.execute(update(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False).values(is_read=True))
    await db.commit()
