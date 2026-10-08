from typing import Dict, Any, List
from PIL import Image
from app.services.forensics.ela import ErrorLevelAnalysis
from app.services.forensics.metadata import MetadataAnalyzer
from app.services.validators.marksheet_validator import CheckDetail


class ForensicsEngine:
    """
    Unified Forensic Analysis Engine returning Tier C heuristic checks.
    """

    @classmethod
    def run_forensics(cls, image: Image.Image = None, metadata: Dict[str, Any] = None) -> List[CheckDetail]:
        checks: List[CheckDetail] = []

        # 1. Error Level Analysis (ELA)
        if image is not None:
            ela_res = ErrorLevelAnalysis.analyze_pil_image(image)
            checks.append(CheckDetail(
                check_name="C09_TAMPER_ELA",
                tier="TIER_C",
                result="WARN" if ela_res["is_suspicious"] else "PASS",
                score=ela_res["tamper_score"],
                reason=ela_res["reason"],
                details=ela_res
            ))

        # 2. Metadata Anomaly Check
        if metadata:
            meta_res = MetadataAnalyzer.analyze_metadata(metadata)
            checks.append(CheckDetail(
                check_name="C08_METADATA_ANOMALY",
                tier="TIER_C",
                result=meta_res["result"],
                score=meta_res["score"],
                reason=meta_res["reason"],
                details=meta_res
            ))

        return checks
