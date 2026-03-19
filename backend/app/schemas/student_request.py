from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


class RequestCreate(BaseModel):
    tramite_id: uuid.UUID
    career_id: Optional[uuid.UUID] = None
    student_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class RequestStatusUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None


class RequestOut(BaseModel):
    id: uuid.UUID
    tramite_id: uuid.UUID
    career_id: Optional[uuid.UUID]
    status: str
    student_data: Optional[Dict[str, Any]]
    notes: Optional[str]
    admin_notes: Optional[str]
    submitted_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    model_config = {"from_attributes": True}
