import uuid
from typing import Dict, Any, List
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.models.base import Base


class RiskResult(Base):
    __tablename__ = "risk_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("verification_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    component_scores_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    hard_rules_triggered: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list, nullable=False)
    reasons_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=list, nullable=False)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False)

    verification = relationship("VerificationRequest", back_populates="risk_result")
