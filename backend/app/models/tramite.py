import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Tramite(Base):
    __tablename__ = "tramites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=True)
    cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    applies_to: Mapped[str] = mapped_column(String(50), default="all")  # all | tecnologico | 6x
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Aspect-specific fields (used by Claude to answer focused questions)
    office_location: Mapped[str] = mapped_column(String(255), nullable=True)    # UBICACION aspect
    contact_info: Mapped[str] = mapped_column(String(255), nullable=True)       # CONTACTO aspect
    cost_details: Mapped[str] = mapped_column(Text, nullable=True)              # COSTO aspect (payment instructions)
    duration_details: Mapped[str] = mapped_column(Text, nullable=True)          # PLAZO aspect (extra timing info)
    web_system_url: Mapped[str] = mapped_column(String(255), nullable=True)     # SISTEMA_WEB aspect
    web_instructions: Mapped[str] = mapped_column(Text, nullable=True)          # SISTEMA_WEB aspect (step-by-step)

    requirements: Mapped[list["Requirement"]] = relationship("Requirement", back_populates="tramite", order_by="Requirement.step_number", cascade="all, delete-orphan")
    requests: Mapped[list["StudentRequest"]] = relationship("StudentRequest", back_populates="tramite")


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tramite_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tramites.id", ondelete="CASCADE"))
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    document_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    tramite: Mapped["Tramite"] = relationship("Tramite", back_populates="requirements")
