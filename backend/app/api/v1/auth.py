from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.security import hash_password
from app.db.base import get_db
from app.db.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    VerifyCodeRequest,
)
from app.services.auth_service import (
    authenticate,
    clear_password_reset_code,
    create_password_reset_code,
    register,
    validate_password_reset_code,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")
    try:
        result = await register(db, req.username, req.password)
        return UserResponse(id=result["id"], username=result["username"], created_at="")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login_user(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await authenticate(db, req.username, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout_user():
    return {"message": "已成功退出登录"}


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    return UserResponse(id=user.id, username=user.username, created_at=str(user.created_at))


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    create_password_reset_code(req.username)
    return ForgotPasswordResponse(message="验证码已生成")


@router.post("/verify-reset-code")
async def verify_reset_code(req: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    try:
        validate_password_reset_code(req.username, req.code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password_hash = hash_password(req.new_password)
    clear_password_reset_code(req.username)

    return {"message": "密码重置成功"}
