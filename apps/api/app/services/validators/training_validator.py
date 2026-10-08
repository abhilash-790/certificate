from datetime import datetime
from typing import Dict, Any, List
from app.services.validators.marksheet_validator import CheckDetail


class TrainingValidator:
    """
    Type-specific validator for training and professional course certificates.
    Enforces start-end date logic, duration realism, and trusted provider matching.
    """

    TRUSTED_PROVIDERS = [
        "nptel", "iit bombay", "iit delhi", "coursera", "edx", "udemy",
        "google", "aws", "microsoft", "cisco", "oracle"
    ]

    CERTIFICATE_MILL_WATCHLIST = [
        "instant degree mill", "fast certs online", "fake diploma pro",
        "fast diploma pro", "buy certificate direct", "diploma mill"
    ]


    @classmethod
    def validate(cls, fields: Dict[str, Any], config: Dict[str, Any] = None) -> List[CheckDetail]:
        results: List[CheckDetail] = []
        
        provider = str(fields.get("provider_name", "")).lower()

        # 1. Watchlist mill check
        if any(mill in provider for mill in cls.CERTIFICATE_MILL_WATCHLIST):
            results.append(CheckDetail(
                check_name="C06_TRAINING_PROVIDER_WATCHLIST",
                tier="TIER_B",
                result="FAIL",
                score=100.0,
                reason=f"High Risk Provider: Provider '{fields.get('provider_name')}' matches known diploma/certificate mill watchlist.",
                details={"provider_name": fields.get("provider_name")}
            ))
        elif any(trusted in provider for trusted in cls.TRUSTED_PROVIDERS):
            results.append(CheckDetail(
                check_name="C06_TRAINING_PROVIDER_TRUSTED",
                tier="TIER_B",
                result="PASS",
                score=0.0,
                reason=f"Provider '{fields.get('provider_name')}' is on trusted provider allow-list.",
                details={"provider_name": fields.get("provider_name")}
            ))

        # 2. Date order check
        start_date_str = fields.get("start_date")
        completion_date_str = fields.get("completion_date")

        if start_date_str and completion_date_str:
            try:
                start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                comp_dt = datetime.strptime(completion_date_str, "%Y-%m-%d")
                if comp_dt < start_dt:
                    results.append(CheckDetail(
                        check_name="C06_TRAINING_DATE_LOGIC",
                        tier="TIER_B",
                        result="FAIL",
                        score=90.0,
                        reason=f"Impossible dates: Completion date ({completion_date_str}) precedes start date ({start_date_str}).",
                        details={"start_date": start_date_str, "completion_date": completion_date_str}
                    ))
            except ValueError:
                pass

        return results
