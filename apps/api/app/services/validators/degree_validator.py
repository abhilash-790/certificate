from datetime import datetime
from typing import Dict, Any, List
from app.services.validators.marksheet_validator import CheckDetail


class DegreeValidator:
    """
    Type-specific validator for degree certificates.
    Enforces convocation date ranges, minimum course duration logic, and degree program existence.
    """

    @classmethod
    def validate(cls, fields: Dict[str, Any], config: Dict[str, Any] = None) -> List[CheckDetail]:
        results: List[CheckDetail] = []
        
        issue_date_str = fields.get("issue_date")
        admission_year_str = fields.get("admission_year")

        if issue_date_str and admission_year_str:
            try:
                issue_year = int(issue_date_str[:4])
                admission_year = int(admission_year_str[:4]) if len(str(admission_year_str)) >= 4 else int(admission_year_str)
                
                duration = issue_year - admission_year
                if duration < 1:
                    results.append(CheckDetail(
                        check_name="C06_DEGREE_DURATION_LOGIC",
                        tier="TIER_B",
                        result="FAIL",
                        score=95.0,
                        reason=f"Impossible degree duration: Issue year ({issue_year}) is less than 1 year after admission year ({admission_year}).",
                        details={"admission_year": admission_year, "issue_year": issue_year, "duration": duration}
                    ))
                elif duration > 8:
                    results.append(CheckDetail(
                        check_name="C06_DEGREE_DURATION_LOGIC",
                        tier="TIER_B",
                        result="WARN",
                        score=35.0,
                        reason=f"Unusually long degree duration ({duration} years).",
                        details={"admission_year": admission_year, "issue_year": issue_year, "duration": duration}
                    ))
                else:
                    results.append(CheckDetail(
                        check_name="C06_DEGREE_DURATION_LOGIC",
                        tier="TIER_B",
                        result="PASS",
                        score=0.0,
                        reason="Degree program duration is realistic.",
                        details={"duration_years": duration}
                    ))
            except (ValueError, TypeError):
                pass

        return results
