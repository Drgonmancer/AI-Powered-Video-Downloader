"""AI video analysis: summary, mindmap (Markdown/Markmap), transcript."""

from typing import Any, Dict, Optional, Tuple

import httpx

MINDMAP_SYSTEM = """你是视频知识结构分析助手。只输出 Markdown 大纲思维导图，用于 Markmap 渲染。

格式要求：
1. 第一行必须是 # 视频主题（用视频标题）
2. 用 ## / ### / - 表示 2~4 层结构，至少 4 个节点
3. 重要分支标题请带时间戳，格式 [mm:ss] 或 [hh:mm:ss]，例如：### [02:30] 核心观点
4. 不要输出 Mermaid、JSON、代码块或解释文字
5. 只输出 Markdown 大纲本身"""

FULL_SYSTEM = """你是视频内容分析助手。根据提供的元数据生成分析结果。
必须严格按以下三段格式输出（保留分隔标记），每段内容均使用 Markdown 排版以提升可读性。

---SUMMARY---
用 Markdown 写「内容摘要」，结构必须包含：
## 一句话概述
（1-2 句概括视频主题与价值）
## 核心要点
- **要点标题**：具体说明（3-5 条）
## 适合人群
- 列出 2-3 类观众
> **收获**：用一句话总结观看后可获得什么

---MINDMAP---
（Markdown 大纲思维导图：# 标题，##/###/- 层级，重要节点带 [mm:ss] 时间戳，供 Markmap 渲染）

---TRANSCRIPT---
用 Markdown 写「字幕/内容要点」，结构必须包含：
## 内容脉络
### [00:00] 段落主题
- 要点 1
- 要点 2
（按逻辑分 3-6 个小节；若无精确时间可估算 [mm:ss]；若无字幕则基于简介归纳并注明）"""


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
        return True, "", "https://api.deepseek.com/v1", "deepseek-chat"


def _resolve_llm_credentials(
    user_id: Optional[int],
    provider_id: Optional[int],
) -> Tuple[str, str, str, str]:
    if user_id:
        from services.llm_provider_service import get_provider

        provider = get_provider(user_id, provider_id)
        if provider:
            return (
                provider["api_key"],
                provider.get("base_url") or "https://api.deepseek.com/v1",
                provider.get("model") or "deepseek-chat",
                provider.get("display_name") or "",
            )

    enabled, api_key, base_url, model = _load_ai_config()
    if not enabled:
        return "", base_url, model, ""
    return (api_key or "").strip(), base_url, model, "ai_config"


def _parse_sections(text: str) -> Dict[str, str]:
    markers = [
        ("summary", "---SUMMARY---"),
        ("mindmap", "---MINDMAP---"),
        ("transcript", "---TRANSCRIPT---"),
    ]
    result = {"summary": "", "mindmap": "", "transcript": ""}
    if not text:
        return result

    positions = []
    for key, marker in markers:
        idx = text.find(marker)
        if idx >= 0:
            positions.append((idx, key, marker))

    if not positions:
        result["summary"] = text.strip()
        return result

    positions.sort(key=lambda x: x[0])
    for i, (start, key, marker) in enumerate(positions):
        content_start = start + len(marker)
        content_end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        result[key] = text[content_start:content_end].strip()
    return result


def _normalize_mindmap_md(content: str, title: str) -> str:
    text = (content or "").strip()
    if not text:
        return f"# {title or '视频内容'}\n## 暂无结构\n- 请重新生成"
    if text.lstrip().startswith("mindmap"):
        lines = []
        for line in text.split("\n"):
            t = line.strip()
            if not t or t == "mindmap":
                continue
            t = t.replace("((", "").replace("))", "").strip()
            if t:
                lines.append(f"- {t}")
        body = "\n".join(lines) if lines else "- 要点待补充"
        return f"# {title or '视频内容'}\n{body}"
    if not text.startswith("#"):
        return f"# {title or '视频内容'}\n{text}"
    return text


def _looks_like_markdown(text: str) -> bool:
    if not text:
        return False
    markers = ("##", "**", "- ", "> ", "###", "`")
    return any(m in text for m in markers) or text.lstrip().startswith("#")


def _normalize_summary_md(content: str, title: str) -> str:
    text = (content or "").strip()
    if not text:
        return ""
    if _looks_like_markdown(text):
        return text

    sentences = [s.strip() for s in text.replace("\n", "。").split("。") if s.strip()]
    bullets = "\n".join(f"- {s}" for s in sentences[:5]) or f"- {text}"
    return (
        f"## 一句话概述\n\n{sentences[0] if sentences else text}\n\n"
        f"## 核心要点\n\n{bullets}"
    )


def _normalize_transcript_md(content: str, title: str) -> str:
    text = (content or "").strip()
    if not text:
        return ""
    if _looks_like_markdown(text):
        return text

    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) <= 1:
        return f"## 内容脉络\n\n### 主要内容\n\n- {text}"
    body = "\n".join(f"- {ln}" for ln in lines[:12])
    return f"## 内容脉络\n\n### {title or '章节要点'}\n\n{body}"


def _build_transcript_hint(video_info: dict) -> str:
    description = (video_info or {}).get("description") or ""
    subs = (video_info or {}).get("subtitles_available") or []
    auto = (video_info or {}).get("automatic_captions_available") or []
    duration = (video_info or {}).get("duration") or 0
    lines = []
    if duration:
        mins = int(duration // 60)
        secs = int(duration % 60)
        lines.append(f"视频时长: {mins}分{secs}秒")
    if subs:
        lines.append("可用字幕: " + ", ".join(subs[:8]))
    if auto:
        lines.append("自动字幕: " + ", ".join(auto[:8]))
    if description:
        lines.append("简介:\n" + description[:2000])
    return "\n".join(lines) if lines else "(无字幕与简介数据)"


def _call_llm(
    api_key: str,
    base_url: str,
    model: str,
    system: str,
    user_content: str,
) -> str:
    with httpx.Client(timeout=90) as client:
        resp = client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.4,
                "max_tokens": 2200,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def _empty_response(message: str) -> Dict[str, Any]:
    return {
        "enabled": False,
        "summary": "",
        "mindmap": "",
        "mindmap_md": "",
        "transcript": "",
        "message": message,
    }


def summarize_video(
    video_info: dict,
    url: str = "",
    cookies: str = "",
    cookies_from_browser: str = "",
    locale: str = "zh",
    user_id: Optional[int] = None,
    provider_id: Optional[int] = None,
    mode: str = "full",
) -> Dict[str, Any]:
    key, base_url, model, provider_name = _resolve_llm_credentials(user_id, provider_id)
    title = (video_info or {}).get("title", "")
    platform = (video_info or {}).get("platform", "")
    uploader = (video_info or {}).get("uploader", "")
    transcript_hint = _build_transcript_hint(video_info)

    if not key:
        if user_id:
            msg = "请先在左侧栏「大模型配置」中添加 API Key 并设为默认。"
        else:
            msg = "未配置 API Key：请登录后在左侧栏添加大模型。"
        return _empty_response(msg)

    lang = "请用中文" if locale.startswith("zh") else "Please respond in English"
    user_content = (
        f"标题: {title}\n"
        f"平台: {platform}\n"
        f"作者: {uploader}\n"
        f"链接: {url}\n"
        f"字幕与简介数据:\n{transcript_hint}\n"
        f"{lang}。"
    )

    try:
        if mode == "mindmap":
            raw = _call_llm(key, base_url, model, MINDMAP_SYSTEM, user_content)
            mindmap_md = _normalize_mindmap_md(raw, title)
            return {
                "enabled": True,
                "mindmap": mindmap_md,
                "mindmap_md": mindmap_md,
                "message": "",
                "provider": provider_name or model,
            }

        system = FULL_SYSTEM + f"\n{lang}。不要编造未提供的信息。"
        raw = _call_llm(key, base_url, model, system, user_content)
        sections = _parse_sections(raw)
        mindmap_md = _normalize_mindmap_md(sections["mindmap"], title)
        summary_md = _normalize_summary_md(sections["summary"], title)
        transcript_md = _normalize_transcript_md(
            sections["transcript"] or transcript_hint,
            title,
        )

        return {
            "enabled": True,
            "summary": summary_md,
            "summary_md": summary_md,
            "mindmap": mindmap_md,
            "mindmap_md": mindmap_md,
            "transcript": transcript_md,
            "transcript_md": transcript_md,
            "message": "",
            "provider": provider_name or model,
        }
    except Exception as e:
        err = str(e)[:200]
        return {
            "enabled": True,
            "summary": "",
            "mindmap": "",
            "mindmap_md": "",
            "transcript": "",
            "message": f"AI分析失败: {err}",
        }
