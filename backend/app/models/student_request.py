import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class StudentRequest(Base):
    __tablename__ = "student_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tramite_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tramites.id"))
    career_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("careers.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pendiente")
    student_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[str] = mapped_column(Text, nullable=True)
    assigned_kardista_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("kardistas.id"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped["User"] = relationship("User", back_populates="requests", foreign_keys=[student_id])
    tramite: Mapped["Tramite"] = relationship("Tramite", back_populates="requests")
    career: Mapped["Career"] = relationship("Career", back_populates="requests")
    assigned_kardista: Mapped["Kardista"] = relationship("Kardista", back_populates="assigned_requests", foreign_keys=[assigned_kardista_id])
    status_history: Mapped[list["RequestStatusHistory"]] = relationship("RequestStatusHistory", back_populates="request", cascade="all, delete-orphan")


class RequestStatusHistory(Base):
    __tablename__ = "request_status_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student_requests.id", ondelete="CASCADE"))
    previous_status: Mapped[str] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    request: Mapped["StudentRequest"] = relationship("StudentRequest", back_populates="status_history")
