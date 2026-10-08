import re
from typing import Dict, Any
from pydantic import BaseModel


class ClassificationResult(BaseModel):
    detected_type: str  # degree | marksheet | training | unknown
    confidence: float   # 0.0 to 1.0
    reasoning: str
    needs_type_confirmation: bool


class DocumentClassifier:
    """
    Vision & Pattern-based Document Type Classification Service.
    Uses keyword heuristics and LLM vision adapters to determine certificate type.
    """

    DEGREE_KEYWORDS = [
        "bachelor", "master", "doctor of philosophy", "degree", "convocation",
        "conferred upon", "b.tech", "m.tech", "b.sc", "m.sc", "b.a", "m.a",
        "university", "chancellor", "vice-chancellor"
    ]

    MARKSHEET_KEYWORDS = [
        "marksheet", "statement of marks", "grade card", "semester",
        "credit", "cgpa", "sgpa", "obtained", "maximum marks", "subject code",
        "total marks", "pass/fail"
    ]

    TRAINING_KEYWORDS = [
        "certificate of completion", "certificate of participation", "training",
        "successfully completed", "course", "workshop", "bootcamp", "nptel",
        "coursera", "udemy", "duration", "hours"
    ]

    @classmethod
    def classify_text(cls, text: str) -> ClassificationResult:
        text_lower = text.lower()
        
        degree_score = sum(1 for kw in cls.DEGREE_KEYWORDS if kw in text_lower)
        marksheet_score = sum(1 for kw in cls.MARKSHEET_KEYWORDS if kw in text_lower)
        training_score = sum(1 for kw in cls.TRAINING_KEYWORDS if kw in text_lower)

        scores = {
            "degree": degree_score,
            "marksheet": marksheet_score,
            "training": training_score
        }

        max_type, max_score = max(scores.items(), key=lambda x: x[1])

        if max_score == 0:
            return ClassificationResult(
                detected_type="unknown",
                confidence=0.0,
                reasoning="No strong certificate keywords detected in document text.",
                needs_type_confirmation=True
            )

        total_hits = sum(scores.values())
        confidence = min(0.95, round(max_score / max(1, total_hits * 0.7), 2))

        # Check threshold per SPEC C1 (F2): if confidence < 0.70, flag needs_type_confirmation
        needs_confirmation = confidence < 0.70

        return ClassificationResult(
            detected_type=max_type,
            confidence=confidence,
            reasoning=f"Matched {max_score} pattern indicators for '{max_type}' certificate.",
            needs_type_confirmation=needs_confirmation
        )
