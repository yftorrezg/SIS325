import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    kardex_type: Mapped[str] = mapped_column(String(50), nullable=False)  # tecnologico | 6x
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    requests: Mapped[list["StudentRequest"]] = relationship("StudentRequest", back_populates="career")
