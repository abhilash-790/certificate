import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_and_login_flow():
    # Register new verifier
    register_payload = {
        "name": "Jane Doe",
        "email": "jane@company.com",
        "password": "SecurePassword123!",
        "role": "VERIFIER"
    }
    reg_resp = client.post("/api/v1/auth/register", json=register_payload)
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == "jane@company.com"
    assert user_data["role"] == "VERIFIER"

    # Login
    login_payload = {
        "email": "jane@company.com",
        "password": "SecurePassword123!"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data

    # Fetch /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "jane@company.com"


def test_login_invalid_credentials():
    login_payload = {
        "email": "nonexistent@company.com",
        "password": "WrongPassword!"
    }
    login_resp = client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 401
