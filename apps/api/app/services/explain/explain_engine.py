from typing import List, Dict, Any
from app.services.scoring.risk_engine import RiskAssessment


class ExplanationEngine:
    """
    Generates plain-language explanations from structured check evidence.
    Includes template fallback when LLM service is offline or unavailable.
    """

    @classmethod
    def generate_explanation(cls, assessment: RiskAssessment, cert_type: str = "certificate") -> str:
        verdict = assessment.verdict
        risk_score = assessment.risk_score
        coverage = assessment.coverage_pct
        reasons = assessment.reasons

        # Template-based deterministic explanation phrasing
        if verdict == "VERIFIED":
            summary = (
                f"This {cert_type} has been successfully **VERIFIED**. "
                f"Authoritative registry records confirm the document details with a low overall risk score of {risk_score}/100 "
                f"({coverage}% evidence coverage)."
            )
        elif verdict == "REVOKED":
            summary = (
                f"CRITICAL WARNING: This {cert_type} is **REVOKED**. "
                f"The issuing institution has formally invalidated this certificate record."
            )
        elif verdict == "NOT_VERIFIED":
            summary = (
                f"This {cert_type} is marked **NOT VERIFIED**. "
                f"Extracted fields contradict official issuer registry records or digital signatures failed verification."
            )
        elif verdict == "UNVERIFIABLE_ISSUER":
            summary = (
                f"This {cert_type} is marked **UNVERIFIABLE ISSUER**. "
                f"The issuing institution is not registered in our database. Verification was conducted using format consistency and image forensics ({coverage}% coverage)."
            )
        else:  # NEEDS_REVIEW
            summary = (
                f"This {cert_type} requires **HUMAN REVIEW** (Risk Score: {risk_score}/100, Level: {assessment.risk_level}). "
                f"One or more deterministic validation checks or image forensic indicators flagged potential discrepancies."
            )

        bullet_points = "\n".join([f"- {r}" for r in reasons])
        return f"{summary}\n\n### Key Evidence Points:\n{bullet_points}"
