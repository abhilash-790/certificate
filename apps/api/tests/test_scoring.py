import pytest
from app.services.validators.marksheet_validator import CheckDetail
from app.services.scoring.risk_engine import RiskEngine
from app.services.explain.explain_engine import ExplanationEngine


def test_verified_risk_assessment():
    checks = [
        CheckDetail(check_name="C05_REGISTRY_MATCH", tier="TIER_A", result="PASS", score=0.0, reason="Registry matched."),
        CheckDetail(check_name="C06_MARKSHEET_ARITHMETIC_SUM", tier="TIER_B", result="PASS", score=0.0, reason="Arithmetic pass.")
    ]
    assessment = RiskEngine.evaluate(
        checks=checks,
        issuer_registered=True,
        registry_matched=True
    )
    assert assessment.verdict == "VERIFIED"
    assert assessment.risk_level == "LOW"
    assert assessment.risk_score == 0.0
    
    explanation = ExplanationEngine.generate_explanation(assessment, "marksheet")
    assert "VERIFIED" in explanation


def test_revoked_decision_rule_r1():
    checks = []
    assessment = RiskEngine.evaluate(
        checks=checks,
        issuer_registered=True,
        is_revoked=True
    )
    assert assessment.verdict == "REVOKED"
    assert assessment.risk_score == 100.0
    assert "R1_REVOKED" in assessment.hard_rules_triggered


def test_unverifiable_issuer_decision_rule_r5():
    checks = [
        CheckDetail(check_name="C09_TAMPER_ELA", tier="TIER_C", result="PASS", score=10.0, reason="ELA pass."),
        CheckDetail(check_name="C08_METADATA_ANOMALY", tier="TIER_C", result="PASS", score=0.0, reason="Metadata pass.")
    ]
    assessment = RiskEngine.evaluate(
        checks=checks,
        issuer_registered=False,
        registry_matched=False
    )
    assert assessment.verdict == "UNVERIFIABLE_ISSUER"
    assert assessment.risk_level in ["LOW", "MEDIUM"]
