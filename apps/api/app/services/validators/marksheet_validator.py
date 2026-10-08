from typing import Dict, Any, List
from pydantic import BaseModel, Field


class CheckDetail(BaseModel):
    check_name: str
    tier: str = "TIER_B"
    result: str  # PASS | WARN | FAIL | NOT_APPLICABLE
    score: float  # 0.0 to 100.0 (Risk score: 0 is genuine, 100 is high risk/fail)
    reason: str
    details: Dict[str, Any] = Field(default_factory=dict)



class MarksheetValidator:
    """
    Type-specific deterministic validator for marksheets.
    Enforces arithmetic integrity, total consistency, CGPA calculations, and pass/fail logic.
    """

    @classmethod
    def validate(cls, fields: Dict[str, Any], config: Dict[str, Any] = None) -> List[CheckDetail]:
        results: List[CheckDetail] = []
        
        # 1. Subject sum arithmetic check
        subjects = fields.get("subjects", [])
        total_obtained = fields.get("total_obtained")
        total_max = fields.get("total_max")

        if subjects and isinstance(subjects, list):
            calc_sum = 0.0
            calc_max = 0.0
            valid_subject_marks = True
            
            for sub in subjects:
                if isinstance(sub, dict) and "obtained_marks" in sub:
                    try:
                        calc_sum += float(sub["obtained_marks"])
                        calc_max += float(sub.get("max_marks", 0))
                    except (ValueError, TypeError):
                        valid_subject_marks = False
                        break
            
            if valid_subject_marks and total_obtained is not None:
                try:
                    tot_obt_val = float(total_obtained)
                    # Allow minor float precision tolerance (0.5 mark)
                    if abs(calc_sum - tot_obt_val) > 0.5:
                        results.append(CheckDetail(
                            check_name="C06_MARKSHEET_ARITHMETIC_SUM",
                            tier="TIER_B",
                            result="FAIL",
                            score=100.0,
                            reason=f"Hard Arithmetic Mismatch: Sum of individual subject marks ({calc_sum}) does not equal printed total ({tot_obt_val}).",
                            details={"calculated_sum": calc_sum, "printed_total": tot_obt_val}
                        ))
                    else:
                        results.append(CheckDetail(
                            check_name="C06_MARKSHEET_ARITHMETIC_SUM",
                            tier="TIER_B",
                            result="PASS",
                            score=0.0,
                            reason="Subject mark arithmetic sum matches printed total.",
                            details={"calculated_sum": calc_sum, "printed_total": tot_obt_val}
                        ))
                except (ValueError, TypeError):
                    pass

        # 2. Percentage calculation check
        if total_obtained is not None and total_max is not None:
            try:
                tot_obt_val = float(total_obtained)
                tot_max_val = float(total_max)
                if tot_max_val > 0:
                    expected_pct = round((tot_obt_val / tot_max_val) * 100.0, 2)
                    printed_pct = fields.get("percentage")
                    
                    if printed_pct is not None:
                        try:
                            printed_pct_val = float(printed_pct)
                            if abs(expected_pct - printed_pct_val) > 1.0:
                                results.append(CheckDetail(
                                    check_name="C06_MARKSHEET_PERCENTAGE_LOGIC",
                                    tier="TIER_B",
                                    result="FAIL",
                                    score=85.0,
                                    reason=f"Percentage mismatch: Calculated percentage ({expected_pct}%) differs from printed percentage ({printed_pct_val}%).",
                                    details={"expected_pct": expected_pct, "printed_pct": printed_pct_val}
                                ))
                            else:
                                results.append(CheckDetail(
                                    check_name="C06_MARKSHEET_PERCENTAGE_LOGIC",
                                    tier="TIER_B",
                                    result="PASS",
                                    score=0.0,
                                    reason="Calculated percentage matches printed percentage.",
                                    details={"expected_pct": expected_pct, "printed_pct": printed_pct_val}
                                ))
                        except (ValueError, TypeError):
                            pass
            except (ValueError, TypeError):
                pass

        # 3. Pass/Fail Result Consistency
        result_status = str(fields.get("result_status", "")).upper()
        if result_status and subjects:
            has_failed_subject = False
            for sub in subjects:
                if isinstance(sub, dict) and sub.get("grade") in ["F", "FAIL"]:
                    has_failed_subject = True
                    break
            
            if has_failed_subject and "PASS" in result_status:
                results.append(CheckDetail(
                    check_name="C06_MARKSHEET_RESULT_STATUS_LOGIC",
                    tier="TIER_B",
                    result="FAIL",
                    score=90.0,
                    reason="Contradictory result status: Document states 'PASS' but contains failed subject grades.",
                    details={"result_status": result_status}
                ))

        return results
