from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.student_request import StudentRequest
from app.models.tramite import Tramite
from app.models.training_sample import TrainingSample
from app.models.user import User
from app.core.permissions import require_admin

router = APIRouter()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    # Requests by status
    status_result = await db.execute(select(StudentRequest.status, func.count(StudentRequest.id)).group_by(StudentRequest.status))
    by_status = {row[0]: row[1] for row in status_result.all()}

    # Total tramites
    tramite_count = await db.execute(select(func.count(Tramite.id)).where(Tramite.is_active == True))

    # Total training samples
    sample_count = await db.execute(select(func.count(TrainingSample.id)))

    # Total users by role
    user_result = await db.execute(select(User.role, func.count(User.id)).group_by(User.role))
    by_role = {row[0]: row[1] for row in user_result.all()}

    return {
        "requests_by_status": by_status,
        "total_tramites": tramite_count.scalar(),
        "total_training_samples": sample_count.scalar(),
        "users_by_role": by_role,
    }
