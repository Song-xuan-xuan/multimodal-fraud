from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)
    confirm_password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: str

class ForgotPasswordRequest(BaseModel):
    username: str = Field(..., min_length=2)


class ForgotPasswordResponse(BaseModel):
    message: str


class VerifyCodeRequest(BaseModel):
    username: str
    code: str
    new_password: str = Field(..., min_length=6)
