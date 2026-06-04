"""Per-user LLM provider configs (name + API key + model)."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from database.connection import get_db_connection

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"


def _mask_api_key(key: str) -> str:
    key = (key or "").strip()
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


def _row_to_dict(row, *, include_key: bool = False) -> dict:
    d = dict(row)
    out = {
        "id": d["id"],
        "display_name": d["display_name"],
        "base_url": d.get("base_url") or DEFAULT_BASE_URL,
        "model": d.get("model") or DEFAULT_MODEL,
        "is_default": bool(d.get("is_default")),
        "created_at": d.get("created_at"),
        "api_key_masked": _mask_api_key(d["api_key"]),
    }
    if include_key:
        out["api_key"] = d["api_key"]
    return out


def list_providers(user_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, display_name, api_key, base_url, model, is_default, created_at
           FROM user_llm_providers WHERE user_id = ? ORDER BY is_default DESC, id ASC""",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_provider(user_id: int, provider_id: Optional[int] = None) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if provider_id:
        cursor.execute(
            """SELECT id, display_name, api_key, base_url, model, is_default, created_at
               FROM user_llm_providers WHERE user_id = ? AND id = ?""",
            (user_id, provider_id),
        )
    else:
        cursor.execute(
            """SELECT id, display_name, api_key, base_url, model, is_default, created_at
               FROM user_llm_providers WHERE user_id = ? ORDER BY is_default DESC, id ASC LIMIT 1""",
            (user_id,),
        )
    row = cursor.fetchone()
    conn.close()
    return _row_to_dict(row, include_key=True) if row else None


def create_provider(
    user_id: int,
    display_name: str,
    api_key: str,
    base_url: str = "",
    model: str = "",
) -> dict:
    display_name = (display_name or "").strip()
    api_key = (api_key or "").strip()
    if not display_name:
        raise ValueError("请填写大模型名称")
    if not api_key:
        raise ValueError("请填写 API Key")

    base_url = (base_url or "").strip() or DEFAULT_BASE_URL
    model = (model or "").strip() or DEFAULT_MODEL
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) AS c FROM user_llm_providers WHERE user_id = ?",
        (user_id,),
    )
    count = cursor.fetchone()["c"]
    is_default = 1 if count == 0 else 0

    cursor.execute(
        """INSERT INTO user_llm_providers
           (user_id, display_name, api_key, base_url, model, is_default, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, display_name, api_key, base_url, model, is_default, now),
    )
    provider_id = cursor.lastrowid
    conn.commit()
    conn.close()
    result = get_provider(user_id, provider_id)
    if result:
        result.pop("api_key", None)
    return result  # type: ignore


def delete_provider(user_id: int, provider_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_default FROM user_llm_providers WHERE user_id = ? AND id = ?",
        (user_id, provider_id),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    was_default = bool(row["is_default"])
    cursor.execute(
        "DELETE FROM user_llm_providers WHERE user_id = ? AND id = ?",
        (user_id, provider_id),
    )
    conn.commit()

    if was_default:
        cursor.execute(
            """SELECT id FROM user_llm_providers WHERE user_id = ? ORDER BY id ASC LIMIT 1""",
            (user_id,),
        )
        next_row = cursor.fetchone()
        if next_row:
            cursor.execute(
                "UPDATE user_llm_providers SET is_default = 1 WHERE id = ?",
                (next_row["id"],),
            )
            conn.commit()
    conn.close()
    return True


def set_default_provider(user_id: int, provider_id: int) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM user_llm_providers WHERE user_id = ? AND id = ?",
        (user_id, provider_id),
    )
    if not cursor.fetchone():
        conn.close()
        return None
    cursor.execute(
        "UPDATE user_llm_providers SET is_default = 0 WHERE user_id = ?",
        (user_id,),
    )
    cursor.execute(
        "UPDATE user_llm_providers SET is_default = 1 WHERE user_id = ? AND id = ?",
        (user_id, provider_id),
    )
    conn.commit()
    conn.close()
    return get_provider(user_id, provider_id)
