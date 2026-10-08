import pytest
from app.services.validators.validator_engine import ValidatorEngine


def test_marksheet_arithmetic_pass():
    fields = {
        "total_obtained": 450,
        "total_max": 500,
        "percentage": 90.0,
        "subjects": [
            {"subject_name": "Math", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Physics", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Chemistry", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "English", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "CS", "obtained_marks": 90, "max_marks": 100}
        ]
    }
    results = ValidatorEngine.run_validators("marksheet", fields)
    assert len(results) >= 1
    sum_check = next(c for c in results if c.check_name == "C06_MARKSHEET_ARITHMETIC_SUM")
    assert sum_check.result == "PASS"
    assert sum_check.score == 0.0


def test_marksheet_arithmetic_fail():
    fields = {
        "total_obtained": 490,  # Printed total altered to 490, but sum is 450
        "total_max": 500,
        "percentage": 98.0,
        "subjects": [
            {"subject_name": "Math", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Physics", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "Chemistry", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "English", "obtained_marks": 90, "max_marks": 100},
            {"subject_name": "CS", "obtained_marks": 90, "max_marks": 100}
        ]
    }
    results = ValidatorEngine.run_validators("marksheet", fields)
    sum_check = next(c for c in results if c.check_name == "C06_MARKSHEET_ARITHMETIC_SUM")
    assert sum_check.result == "FAIL"
    assert sum_check.score == 100.0


def test_degree_duration_fail():
    fields = {
        "admission_year": "2024",
        "issue_date": "2024-05-10"  # 0 years duration for a degree
    }
    results = ValidatorEngine.run_validators("degree", fields)
    dur_check = next(c for c in results if c.check_name == "C06_DEGREE_DURATION_LOGIC")
    assert dur_check.result == "FAIL"
    assert dur_check.score == 95.0


def test_training_watchlist_fail():
    fields = {
        "provider_name": "Fast Diploma Pro Certificate Mill",
        "start_date": "2025-01-01",
        "completion_date": "2025-01-05"
    }
    results = ValidatorEngine.run_validators("training", fields)
    watch_check = next(c for c in results if c.check_name == "C06_TRAINING_PROVIDER_WATCHLIST")
    assert watch_check.result == "FAIL"
    assert watch_check.score == 100.0
