import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    compute_canonical_hash,
    generate_ed25519_keypair,
    sign_payload,
    verify_signature,
)


def test_password_hashing():
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_tokens():
    payload = {"sub": "12345", "email": "test@certiguard.io", "role": "VERIFIER"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "12345"
    assert decoded["email"] == "test@certiguard.io"
    assert decoded["role"] == "VERIFIER"


def test_canonical_hash_and_ed25519_signatures():
    payload_a = {
        "institution_id": "inst_100",
        "certificate_number": "CERT-2026-99",
        "holder_name": "Rajesh Sharma",
        "course": "B.Tech Computer Science",
        "issue_date": "2026-05-15"
    }
    
    payload_b = {
        "course": "B.Tech Computer Science",
        "holder_name": "Rajesh Sharma",
        "issue_date": "2026-05-15",
        "institution_id": "inst_100",
        "certificate_number": "CERT-2026-99"
    }
    
    hash_a = compute_canonical_hash(payload_a)
    hash_b = compute_canonical_hash(payload_b)
    
    # Key sorting must guarantee identical canonical hash
    assert hash_a == hash_b
    
    # Sign and verify
    priv_pem, pub_pem = generate_ed25519_keypair()
    sig = sign_payload(priv_pem, hash_a)
    
    assert verify_signature(pub_pem, sig, hash_a) is True
    
    # Tampered payload hash verification must fail
    tampered_hash = compute_canonical_hash({**payload_a, "holder_name": "Tampered Name"})
    assert verify_signature(pub_pem, sig, tampered_hash) is False
