import os
import json
from datetime import datetime


def generate_synthetic_dataset():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    genuine_dir = os.path.join(data_dir, "genuine")
    forged_dir = os.path.join(data_dir, "forged")

    os.makedirs(genuine_dir, exist_ok=True)
    os.makedirs(forged_dir, exist_ok=True)

    samples = [
        # Genuine Degree
        {
            "id": "gen_deg_01",
            "type": "degree",
            "category": "genuine",
            "holder_name": "Rajesh Kumar Sharma",
            "institution": "Indian Institute of Technology Bombay",
            "certificate_number": "IITB-2025-CS-99",
            "degree_name": "Bachelor of Technology",
            "branch": "Computer Science and Engineering",
            "issue_date": "2025-05-20",
            "is_tampered": False
        },
        # Forged Marksheet - Arithmetic Mismatch
        {
            "id": "forg_mark_01",
            "type": "marksheet",
            "category": "forged",
            "tamper_type": "arithmetic_mismatch",
            "holder_name": "Vikram Malhotra",
            "institution": "University of Delhi",
            "certificate_number": "DU-2025-MS-402",
            "total_printed": 490,  # Forged total printed
            "subject_marks_sum": 420,  # Actual sum of subjects
            "is_tampered": True,
            "expected_verdict": "NEEDS_REVIEW",
            "expected_risk": 85.0
        },
        # Forged Training - Mill Watchlist
        {
            "id": "forg_train_01",
            "type": "training",
            "category": "forged",
            "tamper_type": "diploma_mill_provider",
            "holder_name": "Amit Kumar",
            "provider_name": "Instant Degree Mill Online",
            "certificate_number": "MILL-9912",
            "is_tampered": True,
            "expected_verdict": "NEEDS_REVIEW",
            "expected_risk": 100.0
        }
    ]

    for sample in samples:
        target_folder = genuine_dir if sample["category"] == "genuine" else forged_dir
        file_path = os.path.join(target_folder, f"{sample['id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2)

    print(f"Synthetic dataset generated: {len(samples)} sample files created in {data_dir}.")


if __name__ == "__main__":
    generate_synthetic_dataset()
