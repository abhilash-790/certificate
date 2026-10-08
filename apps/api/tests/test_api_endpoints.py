import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_end_to_end_verification_and_issuance_flow():
    # 1. Register institution user
    inst_reg_payload = {
        "name": "IIT Bombay Admin",
        "email": "admin@iitb.ac.in",
        "password": "SecurePassword123!",
        "role": "INSTITUTION"
    }
    reg_resp = client.post("/api/v1/auth/register", json=inst_reg_payload)
    assert reg_resp.status_code == 201

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "admin@iitb.ac.in",
        "password": "SecurePassword123!"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Issue signed certificate record
    issue_payload = {
        "certificate_type_code": "degree",
        "certificate_number": "IITB-2026-CS-101",
        "holder_name": "Rajesh Sharma",
        "course": "B.Tech Computer Science",
        "data_json": {"cgpa": "9.2"},
        "issue_date": "2026-05-30"
    }
    issue_resp = client.post("/api/v1/issuer/certificates", json=issue_payload, headers=headers)
    assert issue_resp.status_code == 201
    issued_data = issue_resp.json()
    assert "canonical_hash" in issued_data
    assert "signature" in issued_data
    verification_token = issued_data["verification_token"]

    # 3. Public QR Verification Lookup
    public_resp = client.get(f"/api/v1/public/verify/{verification_token}")
    assert public_resp.status_code == 200
    pub_data = public_resp.json()
    assert pub_data["verdict"] == "VERIFIED"
    assert pub_data["certificate_number"] == "IITB-2026-CS-101"

    # 4. Upload Certificate File
    file_content = b"Sample Certificate Document Text with Bachelor of Technology degree from university."
    files = {"file": ("cert.pdf", file_content, "application/pdf")}
    upload_resp = client.post("/api/v1/certificates", files=files, headers=headers)
    assert upload_resp.status_code == 202
    upload_data = upload_resp.json()
    ver_id = upload_data["verification_id"]

    # 5. Fetch Verification Detail
    detail_resp = client.get(f"/api/v1/certificates/{ver_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["verdict"] in ["VERIFIED", "UNVERIFIABLE_ISSUER", "NEEDS_REVIEW"]

    # 6. Edit Extracted Fields
    patch_resp = client.patch(
        f"/api/v1/certificates/{ver_id}/fields",
        json=[{"field_name": "holder_name", "value": "Rajesh Kumar Sharma"}],
        headers=headers
    )
    assert patch_resp.status_code == 200


    # 7. Revoke Certificate
    revoke_resp = client.post(
        f"/api/v1/issuer/certificates/{verification_token}/revoke",
        json={"reason": "Degree issued in error due to administrative correction."},
        headers=headers
    )
    assert revoke_resp.status_code == 200

    # 8. Re-query Public Verification (Must return REVOKED)
    public_revoked_resp = client.get(f"/api/v1/public/verify/{verification_token}")
    assert public_revoked_resp.status_code == 200
    assert public_revoked_resp.json()["verdict"] == "REVOKED"
