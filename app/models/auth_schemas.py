from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, description="User email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name of investor")
    password: str = Field(..., min_length=8, max_length=128, description="Plaintext password to be hashed")


class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
