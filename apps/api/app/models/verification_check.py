import enum
import uuid
from typing import Dict, Any
from sqlalchemy import String, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class CheckTier(str, enum.Enum):
    TIER_A = "TIER_A"
    TIER_B = "TIER_B"
    TIER_C = "TIER_C"
    TIER_D = "TIER_D"


class CheckResult(str, enum.Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ERROR = "ERROR"


class VerificationCheck(Base):
    __tablename__ = "verification_checks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False)
    
    check_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[CheckTier] = mapped_column(SQLEnum(CheckTier), nullable=False)
    result: Mapped[CheckResult] = mapped_column(SQLEnum(CheckResult), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0 to 100 risk score
    details_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    verification = relationship("VerificationRequest", back_populates="checks")
