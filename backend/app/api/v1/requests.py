from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from datetime import datetime
from app.database import get_db
from app.models.student_request import StudentRequest, RequestStatusHistory
from app.models.kardista import Kardista
from app.models.career import Career
from app.models.notification import Notification
from app.schemas.student_request import RequestCreate, RequestStatusUpdate, RequestOut
from app.core.permissions import get_current_user, require_kardista
from app.models.user import User

router = APIRouter()

VALID_STATUSES = ("pendiente", "en_proceso", "completado", "rechazado", "cancelado")


@router.post("", response_model=RequestOut, status_code=201)
async def create_request(data: RequestCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Auto-assign kardista based on career
    kardista_id = None
    if data.career_id:
        career_result = await db.execute(select(Career).where(Career.id == data.career_id))
        career = career_result.scalar_one_or_none()
        if career:
            kardista_result = await db.execute(select(Kardista).where(Kardista.kardex_type == career.kardex_type))
            kardista = kardista_result.scalar_one_or_none()
            if kardista:
                kardista_id = kardista.id

    req = StudentRequest(
        student_id=current_user.id,
        tramite_id=data.tramite_id,
        career_id=data.career_id,
        student_data=data.student_data,
        notes=data.notes,
        assigned_kardista_id=kardista_id,
    )
    db.add(req)
    await db.flush()

    # Status history entry
    history = RequestStatusHistory(request_id=req.id, previous_status=None, new_status="pendiente", changed_by_id=current_user.id)
    db.add(history)
    await db.commit()
    await db.refresh(req)
    return req


@router.get("/my", response_model=List[RequestOut])
async def my_requests(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(StudentRequest).where(StudentRequest.student_id == current_user.id).order_by(StudentRequest.submitted_at.desc()))
    return result.scalars().all()


@router.get("", response_model=List[RequestOut])
async def list_requests(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_kardista),
):
    query = select(StudentRequest).order_by(StudentRequest.submitted_at.desc())
    if current_user.role == "kardista":
        kardista_result = await db.execute(select(Kardista).where(Kardista.user_id == current_user.id))
        kardista = kardista_result.scalar_one_or_none()
        if kardista:
            query = query.where(StudentRequest.assigned_kardista_id == kardista.id)
    if status:
        query = query.where(StudentRequest.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{request_id}", response_model=RequestOut)
async def get_request(request_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(StudentRequest).where(StudentRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if current_user.role == "student" and req.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sin permisos")
    return req


@router.put("/{request_id}/status", response_model=RequestOut)
async def update_status(request_id: uuid.UUID, data: RequestStatusUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_kardista)):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {VALID_STATUSES}")
    result = await db.execute(select(StudentRequest).where(StudentRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    old_status = req.status
    req.status = data.status
    if data.admin_notes:
        req.admin_notes = data.admin_notes
    if data.status == "completado":
        req.completed_at = datetime.utcnow()

    history = RequestStatusHistory(request_id=req.id, previous_status=old_status, new_status=data.status, changed_by_id=current_user.id, notes=data.admin_notes)
    db.add(history)

    # Notify student
    if req.student_id:
        notif = Notification(user_id=req.student_id, request_id=req.id, type="status_change", title="Actualización de solicitud", message=f"Tu solicitud cambió a: {data.status}")
        db.add(notif)

    await db.commit()
    await db.refresh(req)
    return req
