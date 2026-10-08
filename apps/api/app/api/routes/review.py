import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.auth import UserResponse
from app.api.routes.auth import require_roles
from app.api.routes.certificates import _mock_verifications
from app.models.user import UserRole

router = APIRouter(prefix="/review", tags=["Review Queue"])


class ReviewDecisionRequest(BaseModel):
    decision: str = Field(..., description="APPROVE | REJECT | NEEDS_INFO")
    notes: str = Field(..., min_length=5, description="Mandatory notes justifying decision")


@router.get("/queue")
async def get_review_queue(
    current_user: UserResponse = Depends(require_roles([UserRole.REVIEWER, UserRole.ADMIN]))
):
    queue_items = []
    for ver_id, rec in _mock_verifications.items():
        # Include items that require human review or flagged HIGH risk
        if rec["verdict"] in ["NEEDS_REVIEW", "NOT_VERIFIED", "UNVERIFIABLE_ISSUER"] or rec["risk_level"] == "HIGH":
            queue_items.append({
                "verification_id": ver_id,
                "certificate_type": rec["confirmed_type"],
                "holder_name": rec["extracted_fields"].get("holder_name", "Unknown"),
                "verdict": rec["verdict"],
                "risk_score": rec["risk_score"],
                "risk_level": rec["risk_level"],
                "submitted_by": rec["submitted_by"],
                "status": rec["status"]
            })

    # Sort queue prioritizing HIGH risk items first
    queue_items.sort(key=lambda x: x["risk_score"], reverse=True)
    return queue_items


@router.post("/{id}/decision")
async def submit_review_decision(
    id: uuid.UUID,
    req: ReviewDecisionRequest,
    current_user: UserResponse = Depends(require_roles([UserRole.REVIEWER, UserRole.ADMIN]))
):
    rec = _mock_verifications.get(str(id))
    if not rec:
        raise HTTPException(status_code=404, detail="Verification ticket not found")

    rec["review_decision"] = req.decision
    rec["review_notes"] = req.notes
    rec["reviewed_by"] = str(current_user.id)
    rec["reviewed_at"] = "2026-10-08T01:55:00Z"
    rec["status"] = "COMPLETED"

    # Update verdict based on decision
    if req.decision == "APPROVE":
        rec["verdict"] = "VERIFIED"
    elif req.decision == "REJECT":
        rec["verdict"] = "NOT_VERIFIED"

    return rec
