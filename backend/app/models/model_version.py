import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Float, Integer, DateTime
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_tag: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    model_path: Mapped[str] = mapped_column(String(500), nullable=False)
    training_samples_count: Mapped[int] = mapped_column(Integer, nullable=True)
    val_samples_count: Mapped[int] = mapped_column(Integer, nullable=True)
    accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    f1_score: Mapped[float] = mapped_column(Float, nullable=True)
    confusion_matrix: Mapped[Any] = mapped_column(JSONB, nullable=True)
    classification_report: Mapped[Any] = mapped_column(JSONB, nullable=True)
    base_model: Mapped[str] = mapped_column(String(255), nullable=True)
    hyperparams: Mapped[dict] = mapped_column(JSONB, nullable=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
