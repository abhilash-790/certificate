import enum
import uuid
from datetime import datetime, date, timezone
from typing import Dict, Any, Optional
from sqlalchemy import String, Date, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class CertificateStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class IssuerCertificate(Base):
    __tablename__ = "issuer_certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    certificate_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("certificate_types.id"), nullable=False)
    
    certificate_number: Mapped[str] = mapped_column(String(100), nullable=False)
    holder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    holder_identifier_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    course: Mapped[str] = mapped_column(String(255), nullable=False)
    data_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[CertificateStatus] = mapped_column(SQLEnum(CertificateStatus), default=CertificateStatus.ACTIVE, nullable=False)
    
    canonical_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    signature: Mapped[str] = mapped_column(String, nullable=False)
    verification_token: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('institution_id', 'certificate_number', name='uq_institution_cert_number'),
    )

    institution = relationship("Institution", back_populates="certificates")
    revocation = relationship("Revocation", back_populates="certificate", uselist=False)
