import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt

from database.connection import get_db_connection

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AVATARS_DIR = os.path.join(PROJECT_ROOT, "data", "avatars")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


PLAN_FEATURES = {
    "free": {
        "max_downloads_per_day": 5,
        "max_ai_summaries_per_day": 3,
        "max_quality": "720p",
        "batch_download": False,
    },
    "basic": {
        "max_downloads_per_day": 50,
        "max_ai_summaries_per_day": 30,
        "max_quality": "1080p",
        "batch_download": True,
    },
    "pro": {
        "max_downloads_per_day": -1,
        "max_ai_summaries_per_day": -1,
        "max_quality": "8k",
        "batch_download": True,
    },
}


def _role_label(role: str, plan: str, is_active: bool) -> str:
    if role == "admin":
        return "管理员"
    if plan == "pro" and is_active:
        return "PRO会员"
    if plan == "basic" and is_active:
        return "VIP会员"
    return "普通用户"


def _plan_display_name(plan: str) -> str:
    return {"free": "免费版", "basic": "基础版", "pro": "专业版"}.get(plan, plan)


def get_user_profile(user_id: int) -> Optional[dict]:
    """聚合用户资料、会员权益与当日用量。"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None

    from services.membership_service import (
        get_membership_status,
        check_daily_download_limit,
        get_daily_reset_info,
        get_download_limits,
    )

    d = dict(row)
    membership = get_membership_status(user_id)
    plan = membership.get("plan", "free")
    is_active = membership.get("is_active", True)
    features = PLAN_FEATURES.get(plan, PLAN_FEATURES["free"])

    allowed, used, remaining = check_daily_download_limit(user_id)
    limits = get_download_limits()
    limit = limits.get(plan, 5)
    reset_info = get_daily_reset_info()

    return {
        "id": d["id"],
        "user_id": d["id"],
        "email": d["email"],
        "username": d.get("username") or "",
        "name": d.get("username") or "",
        "avatar": d.get("avatar") or "",
        "role": d.get("role") or "user",
        "role_label": _role_label(d.get("role") or "user", plan, is_active),
        "created_at": d.get("created_at"),
        "plan": plan,
        "plan_name": _plan_display_name(plan),
        "is_vip": plan in ("basic", "pro") and is_active,
        "membership": {
            "plan": plan,
            "plan_name": _plan_display_name(plan),
            "status": membership.get("status", "active"),
            "is_active": is_active,
            "current_period_start": membership.get("current_period_start"),
            "current_period_end": membership.get("current_period_end"),
            "cancel_at_period_end": bool(membership.get("cancel_at_period_end")),
            "features": features,
        },
        "usage": {
            "downloads": {
                "used": used if used >= 0 else 0,
                "limit": limit,
                "remaining": remaining,
                "is_unlimited": limit == -1,
            },
            "ai_summaries": {
                "limit": features.get("max_ai_summaries_per_day", 3),
                "note": "按套餐额度展示",
            },
            "usage_date": reset_info["usage_date"],
            "resets_at": reset_info["resets_at"],
            "reset_timezone": reset_info["timezone"],
        },
        "usage_count": used if used >= 0 else 0,
    }


def _row_to_user(row) -> dict:
    if not row:
        return {}
    return get_user_profile(row["id"]) or {}


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def register_user(email: str, password: str) -> Dict[str, Any]:
    email = email.lower().strip()
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        raise ValueError("邮箱格式无效")
    if len(password) < 6:
        raise ValueError("密码至少6位")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("该邮箱已注册")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = email.split("@")[0]
    cursor.execute(
        """INSERT INTO users (email, password_hash, username, avatar, role, created_at)
           VALUES (?, ?, ?, '', 'user', ?)""",
        (email, _hash_password(password), username, now),
    )
    user_id = cursor.lastrowid

    cursor.execute(
        """INSERT OR IGNORE INTO memberships (user_id, plan, status, updated_at)
           VALUES (?, 'free', 'active', ?)""",
        (user_id, now),
    )
    conn.commit()
    conn.close()

    token = create_token(user_id, email)
    user = get_user_by_id(user_id)
    return {**user, "token": token}


def login_user(email: str, password: str) -> Dict[str, Any]:
    email = email.lower().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row or not _verify_password(password, row["password_hash"]):
        raise ValueError("邮箱或密码错误")

    user = _row_to_user(row)
    token = create_token(row["id"], email)
    return {**user, "token": token}


def update_profile(user_id: int, data: dict) -> dict:
    allowed = {"username"}
    updates = {k: v for k, v in data.items() if k in allowed and v is not None}
    if not updates:
        return get_user_by_id(user_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    if "username" in updates:
        cursor.execute(
            "UPDATE users SET username = ? WHERE id = ?",
            (str(updates["username"]).strip(), user_id),
        )
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)


def update_username(user_id: int, username: str) -> dict:
    username = username.strip()
    if not username or len(username) > 50:
        raise ValueError("用户名无效")
    return update_profile(user_id, {"username": username})


def save_avatar(user_id: int, filename: str, content: bytes) -> dict:
    os.makedirs(AVATARS_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1].lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        ext = ".jpg"
    safe_name = f"{user_id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(AVATARS_DIR, safe_name)
    with open(filepath, "wb") as f:
        f.write(content)

    avatar_url = f"/api/avatars/{safe_name}"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar_url, user_id))
    conn.commit()
    conn.close()
    user = get_user_by_id(user_id)
    return {"avatar": avatar_url, **user}
