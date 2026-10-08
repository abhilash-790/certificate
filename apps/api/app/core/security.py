import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from app.core.config import settings

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates JWT access token with payload data and expiration."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes and validates JWT access token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# Cryptographic Signature & Hash Utilities (Ed25519 + SHA-256)

def compute_sha256(data: bytes | str) -> str:
    """Returns hexadecimal SHA-256 hash."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def compute_canonical_hash(payload: Dict[str, Any]) -> str:
    """
    Computes deterministic SHA-256 canonical hash over sorted JSON payload string.
    Ensures UTF-8 encoding and sorted keys per SPEC E6.
    """
    canonical_json_str = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return compute_sha256(canonical_json_str)


def generate_ed25519_keypair() -> tuple[str, str]:
    """Generates Ed25519 private key and public key pair in PEM string format."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    
    return private_pem, public_pem


def sign_payload(private_pem: str, canonical_hash: str) -> str:
    """Signs canonical SHA-256 hash string using Ed25519 private key."""
    private_key = serialization.load_pem_private_key(private_pem.encode("utf-8"), password=None)
    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("Key must be Ed25519PrivateKey")
    
    signature = private_key.sign(canonical_hash.encode("utf-8"))
    return signature.hex()


def verify_signature(public_pem: str, signature_hex: str, canonical_hash: str) -> bool:
    """Verifies Ed25519 signature against public key and canonical hash."""
    try:
        public_key = serialization.load_pem_public_key(public_pem.encode("utf-8"))
        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            return False
        
        public_key.verify(bytes.fromhex(signature_hex), canonical_hash.encode("utf-8"))
        return True
    except Exception:
        return False
