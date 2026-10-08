import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from app.services.validators.validator_engine import ValidatorEngine
from app.services.scoring.risk_engine import RiskEngine



def run_evaluation():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    genuine_dir = os.path.join(base_dir, "genuine")
    forged_dir = os.path.join(base_dir, "forged")

    true_positives = 0  # Forged correctly flagged as HIGH/MEDIUM risk or NEEDS_REVIEW
    false_positives = 0 # Genuine incorrectly flagged as HIGH risk
    true_negatives = 0  # Genuine correctly marked VERIFIED/LOW
    false_negatives = 0 # Forged incorrectly marked VERIFIED/LOW

    total_samples = 0

    # Evaluate genuine samples
    if os.path.exists(genuine_dir):
        for f_name in os.listdir(genuine_dir):
            if f_name.endswith(".json"):
                total_samples += 1
                with open(os.path.join(genuine_dir, f_name), "r", encoding="utf-8") as f:
                    sample = json.load(f)
                
                checks = ValidatorEngine.run_validators(sample["type"], sample)
                assessment = RiskEngine.evaluate(checks, issuer_registered=True, registry_matched=True)
                
                if assessment.verdict == "VERIFIED":
                    true_negatives += 1
                else:
                    false_positives += 1

    # Evaluate forged samples
    if os.path.exists(forged_dir):
        for f_name in os.listdir(forged_dir):
            if f_name.endswith(".json"):
                total_samples += 1
                with open(os.path.join(forged_dir, f_name), "r", encoding="utf-8") as f:
                    sample = json.load(f)

                checks = ValidatorEngine.run_validators(sample["type"], sample)
                assessment = RiskEngine.evaluate(checks, issuer_registered=False, registry_matched=False)

                if assessment.risk_level in ["MEDIUM", "HIGH"] or assessment.verdict != "VERIFIED":
                    true_positives += 1
                else:
                    false_negatives += 1

    precision = round(true_positives / max(1, (true_positives + false_positives)), 4)
    recall = round(true_positives / max(1, (true_positives + false_negatives)), 4)
    f1_score = round(2 * (precision * recall) / max(1e-5, (precision + recall)), 4)
    fpr = round(false_positives / max(1, (false_positives + true_negatives)), 4)

    print("\n==========================================================================")
    print("           CERTIGUARD EVALUATION METRICS REPORT (M13)                      ")
    print("==========================================================================")
    print(f"Total Synthetic Samples Tested : {total_samples}")
    print(f"True Positives  (Forged caught) : {true_positives}")
    print(f"True Negatives  (Genuine passed): {true_negatives}")
    print(f"False Positives (Genuine flagged): {false_positives}")
    print(f"False Negatives (Forged missed) : {false_negatives}")
    print("--------------------------------------------------------------------------")
    print(f"Precision                       : {precision * 100:.2f}%")
    print(f"Recall (Sensitivity)            : {recall * 100:.2f}%")
    print(f"F1 Score                        : {f1_score * 100:.2f}%")
    print(f"False Positive Rate (FPR)       : {fpr * 100:.2f}%")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_evaluation()
