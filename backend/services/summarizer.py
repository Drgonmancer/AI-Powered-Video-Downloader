"""AI video summary via DeepSeek (optional)."""

from typing import Any, Dict, Optional

import httpx


def _load_ai_config():
    try:
        from ai_config import (
            AI_SUMMARY_ENABLED,
            DEEPSEEK_API_KEY,
            DEEPSEEK_BASE_URL,
            DEEPSEEK_MODEL,
        )
        return AI_SUMMARY_ENABLED, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
    except ImportError:
        return False, "", "https://api.deepseek.com/v1", "deepseek-chat"


def summarize_video(
    video_info: dict,
    url: str = "",
    cookies: str = "",
    cookies_from_browser: str = "",
    locale: str = "zh",
) -> Dict[str, Any]:
    enabled, api_key, base_url, model = _load_ai_config()
    title = (video_info or {}).get("title", "")
    description = (video_info or {}).get("description", "")
    platform = (video_info or {}).get("platform", "")
    uploader = (video_info or {}).get("uploader", "")

    if not enabled:
        return {
            "enabled": False,
            "summary": "",
            "message": "AI摘要未启用" if locale.startswith("zh") else "AI summary disabled",
        }

    key = (api_key or "").strip()
    if not key:
        msg = (
            "未配置 DeepSeek API Key，请复制 backend/ai_config.example.py 为 ai_config.py 并填写。"
            if locale.startswith("zh")
            else "DEEPSEEK_API_KEY not configured."
        )
        return {"enabled": False, "summary": "", "message": msg}

    lang = "请用中文" if locale.startswith("zh") else "Please respond in English"
    system = (
        "你是视频内容分析助手。根据提供的元数据生成简洁的视频摘要（3-5句话），"
        "包含主题、要点，不要编造未提供的信息。"
        f"{lang}。"
    )
    user_content = (
        f"标题: {title}\n"
        f"平台: {platform}\n"
        f"作者: {uploader}\n"
        f"链接: {url}\n"
        f"简介: {description[:800] if description else '(无)'}"
    )

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.4,
                    "max_tokens": 500,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        summary = data["choices"][0]["message"]["content"].strip()
        return {"enabled": True, "summary": summary, "message": ""}
    except Exception as e:
        err = str(e)[:200]
        return {
            "enabled": True,
            "summary": "",
            "message": f"AI摘要失败: {err}",
        }
