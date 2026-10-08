from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.routes.issuer import _mock_issuer_certs_db

router = APIRouter(prefix="/public", tags=["Public Verification"])


class PublicVerificationResponse(BaseModel):
    status: str            # ACTIVE | REVOKED
    verdict: str           # VERIFIED | REVOKED
    certificate_number: str
    holder_name_masked: str
    course: str
    issue_date: str
    verified_at: str


@router.get("/verify/{token}", response_model=PublicVerificationResponse)
async def public_verify_token(token: str):
    cert = _mock_issuer_certs_db.get(token)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification token invalid or not found in registry."
        )

    # Name masking per SPEC F2 (e.g. "Rajesh Kumar Sharma" -> "R****** K**** S*****")
    raw_name = cert.get("holder_name", "")
    masked_parts = []
    for part in raw_name.split():
        if len(part) > 1:
            masked_parts.append(part[0] + "*" * (len(part) - 1))
        else:
            masked_parts.append(part)
    holder_masked = " ".join(masked_parts)

    is_revoked = cert.get("status") == "REVOKED"
    verdict = "REVOKED" if is_revoked else "VERIFIED"

    return PublicVerificationResponse(
        status=cert.get("status", "ACTIVE"),
        verdict=verdict,
        certificate_number=cert["certificate_number"],
        holder_name_masked=holder_masked,
        course=cert["course"],
        issue_date=cert["issue_date"],
        verified_at=datetime.now(timezone.utc).isoformat()
    )
