from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import uuid
from app.database import get_db
from app.models.kardista import Kardista
from app.models.user import User
from app.schemas.kardista import KardistaUpdate, KardistaOut
from app.core.permissions import require_admin, get_current_user

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_kardistas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Kardista).options(selectinload(Kardista.user)))
    kardistas = result.scalars().all()
    return [
        {
            "id": str(k.id),
            "kardex_type": k.kardex_type,
            "office_location": k.office_location,
            "phone": k.phone,
            "whatsapp": k.whatsapp,
            "email_contact": k.email_contact,
            "schedule": k.schedule,
            "full_name": k.user.full_name if k.user else "",
            "email": k.user.email if k.user else "",
        }
        for k in kardistas
    ]


@router.put("/{kardista_id}", response_model=KardistaOut)
async def update_kardista(
    kardista_id: uuid.UUID,
    data: KardistaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Kardista).where(Kardista.id == kardista_id))
    kardista = result.scalar_one_or_none()
    if not kardista:
        raise HTTPException(status_code=404, detail="Kardista no encontrado")
    if current_user.role not in ("admin",) and kardista.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permisos")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(kardista, field, value)
    await db.commit()
    await db.refresh(kardista)
    return kardista
