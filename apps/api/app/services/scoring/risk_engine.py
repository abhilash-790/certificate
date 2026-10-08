from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.validators.marksheet_validator import CheckDetail


class RiskAssessment(BaseModel):
    verdict: str         # VERIFIED | REVOKED | NOT_VERIFIED | NEEDS_REVIEW | UNVERIFIABLE_ISSUER
    risk_score: float    # 0.0 to 100.0 (Higher = riskier)
    risk_level: str      # LOW | MEDIUM | HIGH
    coverage_pct: float  # 0.0 to 100.0
    hard_rules_triggered: List[str]
    reasons: List[str]


class RiskEngine:
    """
    CertiGuard Risk Scoring & Decision Engine.
    Executes SPEC B5 Decision Rules (R1 - R6), computes weighted risk score over applicable checks,
    and calculates evidence coverage %.
    """

    DEFAULT_WEIGHTS = {
        "C03_QR_TOKEN_MATCH": 15.0,
        "C04_SIGNATURE_MATCH": 20.0,
        "C05_REGISTRY_MATCH": 25.0,
        "C06_MARKSHEET_ARITHMETIC_SUM": 15.0,
        "C06_MARKSHEET_PERCENTAGE_LOGIC": 10.0,
        "C06_DEGREE_DURATION_LOGIC": 10.0,
        "C06_TRAINING_PROVIDER_WATCHLIST": 15.0,
        "C06_TRAINING_PROVIDER_TRUSTED": 10.0,
        "C08_METADATA_ANOMALY": 5.0,
        "C09_TAMPER_ELA": 10.0
    }

    @classmethod
    def evaluate(
        cls,
        checks: List[CheckDetail],
        issuer_registered: bool = True,
        is_revoked: bool = False,
        registry_matched: bool = False,
        registry_mismatch: bool = False,
        weights_config: Optional[Dict[str, float]] = None
    ) -> RiskAssessment:
        weights = weights_config or cls.DEFAULT_WEIGHTS
        hard_rules_triggered: List[str] = []
        reasons: List[str] = []

        # ---------------------------------------------------------
        # Step 1: Evaluate Sequential Decision Rules (First Match Wins)
        # ---------------------------------------------------------

        # R1: Tier A Revocation Record
        if is_revoked:
            hard_rules_triggered.append("R1_REVOKED")
            reasons.append("Matching certificate record has been officially revoked by the issuing institution.")
            return RiskAssessment(
                verdict="REVOKED",
                risk_score=100.0,
                risk_level="HIGH",
                coverage_pct=100.0,
                hard_rules_triggered=hard_rules_triggered,
                reasons=reasons
            )

        # R3: Registry record found but key field contradicts
        if registry_mismatch:
            hard_rules_triggered.append("R3_REGISTRY_MISMATCH")
            reasons.append("Document fields contradict authoritative registry record.")
            return RiskAssessment(
                verdict="NOT_VERIFIED",
                risk_score=95.0,
                risk_level="HIGH",
                coverage_pct=90.0,
                hard_rules_triggered=hard_rules_triggered,
                reasons=reasons
            )

        # ---------------------------------------------------------
        # Step 2: Compute Weighted Risk Score & Coverage %
        # ---------------------------------------------------------
        applicable_checks = [c for c in checks if c.result != "NOT_APPLICABLE"]
        
        weighted_score_sum = 0.0
        applicable_weight_sum = 0.0
        total_possible_weight = sum(weights.values())

        for check in applicable_checks:
            w = weights.get(check.check_name, 10.0)
            weighted_score_sum += w * check.score
            applicable_weight_sum += w

            if check.result == "FAIL":
                hard_rules_triggered.append(f"HARD_FAIL_{check.check_name}")
                reasons.append(check.reason)
            elif check.result == "WARN":
                reasons.append(check.reason)

        if applicable_weight_sum > 0:
            risk_score = round(weighted_score_sum / applicable_weight_sum, 2)
        else:
            risk_score = 50.0  # Default neutral score if no checks ran

        coverage_pct = round((applicable_weight_sum / max(1.0, total_possible_weight)) * 100.0, 2)

        # ---------------------------------------------------------
        # Step 3: Determine Risk Level (0-30 LOW, 31-65 MEDIUM, 66-100 HIGH)
        # ---------------------------------------------------------
        if risk_score <= 30.0:
            risk_level = "LOW"
        elif risk_score <= 65.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Low coverage cap rule: if coverage < 40%, cap auto-LOW to MEDIUM
        if coverage_pct < 40.0 and risk_level == "LOW" and not registry_matched:
            risk_level = "MEDIUM"
            reasons.append("Limited evidence available (<40% coverage). Risk level set to MEDIUM for reviewer inspection.")

        # ---------------------------------------------------------
        # Step 4: Assign Final Verdict (R2, R4, R5)
        # ---------------------------------------------------------
        if issuer_registered and registry_matched:
            # R2: Tier A match & fields agree
            if risk_score < 66.0:
                verdict = "VERIFIED"
                reasons.append("Authoritative issuer registry record matches document key fields.")
            else:
                verdict = "NEEDS_REVIEW"
                reasons.append("Registry record matches, but image forensic indicators flagged high risk.")
        elif hard_rules_triggered:
            # R4: Hard Tier B failure without Tier A match
            verdict = "NEEDS_REVIEW"
            risk_score = max(risk_score, 66.0)
            risk_level = "HIGH"
        elif not issuer_registered:
            # R5: Issuer not in registry
            verdict = "UNVERIFIABLE_ISSUER"
            reasons.append("Issuer is not registered in authoritative database; document verified via consistency and forensics checks only.")
        else:
            verdict = "NEEDS_REVIEW"

        if not reasons:
            reasons.append("All applicable verification checks passed successfully.")

        return RiskAssessment(
            verdict=verdict,
            risk_score=risk_score,
            risk_level=risk_level,
            coverage_pct=coverage_pct,
            hard_rules_triggered=hard_rules_triggered,
            reasons=reasons
        )
