import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    NEEDS_TYPE_CONFIRMATION = "NEEDS_TYPE_CONFIRMATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VerdictType(str, enum.Enum):
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"
    NOT_VERIFIED = "NOT_VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    UNVERIFIABLE_ISSUER = "UNVERIFIABLE_ISSUER"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("certificate_files.id"), nullable=False)
    submitted_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    detected_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    type_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confirmed_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    status: Mapped[RequestStatus] = mapped_column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, index=True, nullable=False)
    verdict: Mapped[Optional[VerdictType]] = mapped_column(SQLEnum(VerdictType), index=True, nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[Optional[RiskLevel]] = mapped_column(SQLEnum(RiskLevel), nullable=True)
    coverage_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    rule_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    extracted_fields = relationship("ExtractedField", back_populates="verification", cascade="all, delete-orphan")
    checks = relationship("VerificationCheck", back_populates="verification", cascade="all, delete-orphan")
    risk_result = relationship("RiskResult", back_populates="verification", uselist=False, cascade="all, delete-orphan")
