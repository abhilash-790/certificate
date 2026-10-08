from typing import Dict, Any, List
from app.services.validators.marksheet_validator import MarksheetValidator, CheckDetail
from app.services.validators.degree_validator import DegreeValidator
from app.services.validators.training_validator import TrainingValidator


class ValidatorEngine:
    """
    Unified Validator Engine running per-type deterministic checks.
    """

    @classmethod
    def run_validators(cls, cert_type: str, fields: Dict[str, Any], config: Dict[str, Any] = None) -> List[CheckDetail]:
        cert_type_clean = cert_type.lower().strip()
        
        if cert_type_clean == "marksheet":
            return MarksheetValidator.validate(fields, config)
        elif cert_type_clean == "degree":
            return DegreeValidator.validate(fields, config)
        elif cert_type_clean == "training":
            return TrainingValidator.validate(fields, config)
        
        return []
