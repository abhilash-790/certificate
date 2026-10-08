import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole, UserStatus



class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VERIFIER
    institution_id: Optional[uuid.UUID] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    status: UserStatus
    institution_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)




class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
