from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr

from middleware.auth_middleware import get_current_user
from services.auth_service import (
    login_user,
    register_user,
    save_avatar,
    update_profile,
    update_username,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    username: str | None = None


class UsernameUpdateRequest(BaseModel):
    username: str


@router.post("/register")
async def register(body: RegisterRequest):
    try:
        data = register_user(body.email, body.password)
        return {"success": True, "message": "注册成功", "data": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(body: LoginRequest):
    try:
        data = login_user(body.email, body.password)
        return {"success": True, "data": data}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"success": True, "data": current_user}


@router.put("/profile")
async def update_user_profile(
    body: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    data = update_profile(current_user["id"], body.model_dump(exclude_unset=True))
    return {"success": True, "data": data}


@router.put("/username")
async def change_username(
    body: UsernameUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        data = update_username(current_user["id"], body.username)
        return {"success": True, "data": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过5MB")
    data = save_avatar(current_user["id"], file.filename or "avatar.jpg", content)
    return {"success": True, "data": data}
