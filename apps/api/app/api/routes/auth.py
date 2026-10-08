import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.errors import CertiGuardException
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# In-memory mock DB fallback for standalone execution / unit testing prior to Postgres setup
_mock_users_db: dict[str, User] = {}


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Dependency to retrieve and validate authenticated user from JWT token."""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        if not user_id or not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")
        
        # Check mock DB or return synthetic user
        if email in _mock_users_db:
            user = _mock_users_db[email]
            return UserResponse.model_validate(user)
        
        return UserResponse(
            id=uuid.UUID(user_id),
            name=payload.get("name", "Authenticated User"),
            email=email,
            role=UserRole(payload.get("role", "VERIFIER")),
            status=UserStatus.ACTIVE,
            institution_id=uuid.UUID(payload["institution_id"]) if payload.get("institution_id") else None
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


def require_roles(allowed_roles: List[UserRole]):
    """RBAC dependency factory enforcing user roles."""
    def role_checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' is not authorized. Allowed roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest):
    if req.email in _mock_users_db:
        raise CertiGuardException(message="User with this email already exists", code="USER_ALREADY_EXISTS", status_code=400)
    
    hashed_pass = hash_password(req.password)
    user = User(
        id=uuid.uuid4(),
        name=req.name,
        email=req.email,
        password_hash=hashed_pass,
        role=req.role,
        status=UserStatus.ACTIVE,
        institution_id=req.institution_id
    )
    _mock_users_db[req.email] = user
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(req: UserLoginRequest):
    user = _mock_users_db.get(req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise CertiGuardException(message="Invalid email or password", code="INVALID_CREDENTIALS", status_code=401)
    
    access_token = create_access_token({
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "institution_id": str(user.institution_id) if user.institution_id else None
    })
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
