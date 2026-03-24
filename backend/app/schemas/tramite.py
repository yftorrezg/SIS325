from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime


class RequirementBase(BaseModel):
    step_number: int
    title: str
    description: Optional[str] = None
    document_name: Optional[str] = None
    is_mandatory: bool = True
    notes: Optional[str] = None


class RequirementCreate(RequirementBase):
    pass


class RequirementOut(RequirementBase):
    id: uuid.UUID
    tramite_id: uuid.UUID
    created_at: datetime
    model_config = {"from_attributes": True}


class TramiteBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    duration_days: Optional[int] = None
    cost: float = 0.00
    applies_to: str = "all"
    order_index: int = 0
    icon: Optional[str] = None
    office_location: Optional[str] = None
    contact_info: Optional[str] = None
    cost_details: Optional[str] = None
    duration_details: Optional[str] = None
    web_system_url: Optional[str] = None
    web_instructions: Optional[str] = None


class TramiteCreate(TramiteBase):
    pass


class TramiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration_days: Optional[int] = None
    cost: Optional[float] = None
    applies_to: Optional[str] = None
    order_index: Optional[int] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    office_location: Optional[str] = None
    contact_info: Optional[str] = None
    cost_details: Optional[str] = None
    duration_details: Optional[str] = None
    web_system_url: Optional[str] = None
    web_instructions: Optional[str] = None


class TramiteOut(TramiteBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    requirements: List[RequirementOut] = []
    model_config = {"from_attributes": True}


class TramiteSummary(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    category: Optional[str]
    duration_days: Optional[int]
    cost: float
    applies_to: str
    icon: Optional[str]
    model_config = {"from_attributes": True}
