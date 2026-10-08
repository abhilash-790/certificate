import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class CertificateType(Base):
    __tablename__ = "certificate_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    schema_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    weights_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    validators_config: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
