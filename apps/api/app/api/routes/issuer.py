import uuid
import secrets
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field

from app.core.security import compute_canonical_hash, generate_ed25519_keypair, sign_payload
from app.schemas.auth import UserResponse
from app.api.routes.auth import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter(prefix="/issuer", tags=["Issuer"])

# Mock stores for institutions and registry
_mock_institutions_db: Dict[str, Dict[str, Any]] = {}
_mock_issuer_certs_db: Dict[str, Dict[str, Any]] = {}

# Seed default keypair for demo institution
DEMO_PRIV_KEY, DEMO_PUB_KEY = generate_ed25519_keypair()


class IssueCertificateRequest(BaseModel):
    certificate_type_code: str  # degree | marksheet | training
    certificate_number: str
    holder_name: str
    course: str
    data_json: Dict[str, Any]
    issue_date: str


class IssueCertificateResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    certificate_number: str
    holder_name: str
    course: str
    canonical_hash: str
    signature: str
    verification_token: str
    qr_resolve_url: str


class RevokeRequest(BaseModel):
    reason: str


@router.post("/certificates", response_model=IssueCertificateResponse, status_code=status.HTTP_201_CREATED)
async def issue_certificate(
    req: IssueCertificateRequest,
    current_user: UserResponse = Depends(require_roles([UserRole.INSTITUTION, UserRole.ADMIN]))
):
    inst_id = current_user.institution_id or uuid.uuid4()
    cert_id = uuid.uuid4()
    verification_token = secrets.token_hex(16)  # Random 128-bit verification token

    # Construct Canonical Payload per SPEC E6
    canonical_payload = {
        "institution_id": str(inst_id),
        "certificate_type": req.certificate_type_code,
        "certificate_number": req.certificate_number,
        "holder_name": req.holder_name.strip().upper(),
        "course": req.course.strip(),
        "issue_date": req.issue_date,
        "data": req.data_json,
        "schema_version": "v1.0"
    }

    canonical_hash = compute_canonical_hash(canonical_payload)
    signature = sign_payload(DEMO_PRIV_KEY, canonical_hash)

    cert_record = {
        "id": str(cert_id),
        "institution_id": str(inst_id),
        "certificate_type_code": req.certificate_type_code,
        "certificate_number": req.certificate_number,
        "holder_name": req.holder_name,
        "course": req.course,
        "data_json": req.data_json,
        "issue_date": req.issue_date,
        "status": "ACTIVE",
        "canonical_hash": canonical_hash,
        "signature": signature,
        "verification_token": verification_token,
        "public_key": DEMO_PUB_KEY
    }

    _mock_issuer_certs_db[verification_token] = cert_record

    return IssueCertificateResponse(
        id=cert_id,
        institution_id=inst_id,
        certificate_number=req.certificate_number,
        holder_name=req.holder_name,
        course=req.course,
        canonical_hash=canonical_hash,
        signature=signature,
        verification_token=verification_token,
        qr_resolve_url=f"/api/v1/public/verify/{verification_token}"
    )


@router.post("/certificates/{token}/revoke")
async def revoke_certificate(
    token: str,
    req: RevokeRequest,
    current_user: UserResponse = Depends(require_roles([UserRole.INSTITUTION, UserRole.ADMIN]))
):
    cert = _mock_issuer_certs_db.get(token)
    if not cert:
        raise HTTPException(status_code=404, detail="Issued certificate token not found")

    cert["status"] = "REVOKED"
    cert["revocation_reason"] = req.reason
    return {"message": "Certificate revoked successfully", "token": token, "status": "REVOKED"}
