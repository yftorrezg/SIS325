import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Kardista(Base):
    __tablename__ = "kardistas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    kardex_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tecnologico | 6x
    office_location: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    whatsapp: Mapped[str] = mapped_column(String(50), nullable=True)
    email_contact: Mapped[str] = mapped_column(String(255), nullable=True)
    schedule: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="kardista_profile")
    assigned_requests: Mapped[list["StudentRequest"]] = relationship("StudentRequest", back_populates="assigned_kardista", foreign_keys="StudentRequest.assigned_kardista_id")
