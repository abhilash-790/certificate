import uuid
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.security import compute_sha256
from app.core.errors import CertiGuardException
from app.schemas.auth import UserResponse
from app.api.routes.auth import get_current_user
from app.services.classify.classifier import DocumentClassifier
from app.services.validators.validator_engine import ValidatorEngine
from app.services.forensics.forensics_engine import ForensicsEngine
from app.services.scoring.risk_engine import RiskEngine
from app.services.explain.explain_engine import ExplanationEngine

router = APIRouter(prefix="/certificates", tags=["Certificates"])

# Mock store for verification sessions
_mock_verifications: Dict[str, Dict[str, Any]] = {}


class FieldUpdateItem(BaseModel):
    field_name: str
    value: str


class CertificateUploadResponse(BaseModel):
    verification_id: uuid.UUID
    file_id: uuid.UUID
    detected_type: str
    type_confidence: float
    status: str
    needs_type_confirmation: bool


@router.post("", response_model=CertificateUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_certificate(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    # Validate MIME type and file size per SPEC F1
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise CertiGuardException(
            message=f"Unsupported file format '{file.content_type}'. Allowed: PDF, PNG, JPEG.",
            code="INVALID_FILE_TYPE",
            status_code=400
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    if file_size > 10 * 1024 * 1024:
        raise CertiGuardException(
            message=f"File size exceeds 10 MB limit ({round(file_size/(1024*1024), 2)} MB).",
            code="FILE_TOO_LARGE",
            status_code=400
        )

    sha256_hash = compute_sha256(file_bytes)
    verification_id = uuid.uuid4()
    file_id = uuid.uuid4()

    # Classification
    try:
        text_content = file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text_content = ""

    classification = DocumentClassifier.classify_text(text_content)

    # Mock initial extraction fields
    mock_fields = {
        "holder_name": "Rajesh Kumar Sharma",
        "institution": "Indian Institute of Technology Bombay",
        "certificate_number": "IITB-2025-CS-99",
        "total_obtained": "450",
        "total_max": "500",
        "percentage": "90.0",
        "issue_date": "2025-05-20",
        "subjects": [
            {"subject_name": "Data Structures", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Algorithms", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Operating Systems", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Computer Networks", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Database Systems", "obtained_marks": 90, "max_marks": 100}
        ]
    }

    # Run initial checks
    val_checks = ValidatorEngine.run_validators(classification.detected_type, mock_fields)
    forensic_checks = ForensicsEngine.run_forensics(image=None, metadata={"producer": "PyMuPDF Renderer"})
    all_checks = val_checks + forensic_checks

    assessment = RiskEngine.evaluate(
        checks=all_checks,
        issuer_registered=True,
        registry_matched=True
    )
    explanation = ExplanationEngine.generate_explanation(assessment, classification.detected_type)

    session_record = {
        "verification_id": str(verification_id),
        "file_id": str(file_id),
        "submitted_by": str(current_user.id),
        "detected_type": classification.detected_type,
        "type_confidence": classification.confidence,
        "confirmed_type": classification.detected_type,
        "status": "NEEDS_TYPE_CONFIRMATION" if classification.needs_type_confirmation else "COMPLETED",
        "verdict": assessment.verdict,
        "risk_score": assessment.risk_score,
        "risk_level": assessment.risk_level,
        "coverage_pct": assessment.coverage_pct,
        "extracted_fields": mock_fields,
        "checks": [c.model_dump() for c in all_checks],
        "explanation": explanation,
        "reasons": assessment.reasons,
        "sha256": sha256_hash
    }

    _mock_verifications[str(verification_id)] = session_record

    return CertificateUploadResponse(
        verification_id=verification_id,
        file_id=file_id,
        detected_type=classification.detected_type,
        type_confidence=classification.confidence,
        status=session_record["status"],
        needs_type_confirmation=classification.needs_type_confirmation
    )


@router.get("/{id}")
async def get_verification_detail(
    id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    rec = _mock_verifications.get(str(id))
    if not rec:
        raise HTTPException(status_code=404, detail="Verification session not found")
    
    # Ownership / RBAC check
    if rec["submitted_by"] != str(current_user.id) and current_user.role not in ["REVIEWER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this verification request")

    return rec


@router.patch("/{id}/fields")
async def update_extracted_fields(
    id: uuid.UUID,
    updates: List[FieldUpdateItem],
    current_user: UserResponse = Depends(get_current_user)
):
    rec = _mock_verifications.get(str(id))
    if not rec:
        raise HTTPException(status_code=404, detail="Verification session not found")

    # Update field values
    for item in updates:
        rec["extracted_fields"][item.field_name] = item.value

    # Re-run downstream checks per SPEC D2 stage 11
    val_checks = ValidatorEngine.run_validators(rec["confirmed_type"], rec["extracted_fields"])
    forensic_checks = ForensicsEngine.run_forensics(image=None, metadata={})
    all_checks = val_checks + forensic_checks

    assessment = RiskEngine.evaluate(
        checks=all_checks,
        issuer_registered=True,
        registry_matched=True
    )
    explanation = ExplanationEngine.generate_explanation(assessment, rec["confirmed_type"])

    rec["verdict"] = assessment.verdict
    rec["risk_score"] = assessment.risk_score
    rec["risk_level"] = assessment.risk_level
    rec["coverage_pct"] = assessment.coverage_pct
    rec["checks"] = [c.model_dump() for c in all_checks]
    rec["explanation"] = explanation
    rec["reasons"] = assessment.reasons

    return rec
