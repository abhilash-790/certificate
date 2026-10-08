import enum
import uuid
from typing import Dict, Any, Optional
from sqlalchemy import String, Text, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class FieldSource(str, enum.Enum):
    OCR = "OCR"
    LLM = "LLM"
    USER = "USER"


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False)
    
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ocr_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    bbox_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    source: Mapped[FieldSource] = mapped_column(SQLEnum(FieldSource), default=FieldSource.LLM, nullable=False)

    verification = relationship("VerificationRequest", back_populates="extracted_fields")
