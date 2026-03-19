from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


class KardistaUpdate(BaseModel):
    office_location: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email_contact: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None


class KardistaOut(BaseModel):
    id: uuid.UUID
    kardex_type: str
    office_location: Optional[str]
    phone: Optional[str]
    whatsapp: Optional[str]
    email_contact: Optional[str]
    schedule: Optional[Dict[str, Any]]
    model_config = {"from_attributes": True}


class KardistaWithUser(KardistaOut):
    user_full_name: str = ""
    user_email: str = ""
