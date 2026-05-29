"""Douyin video parser – iesdouyin share page + fallbacks."""

import asyncio
import json
import re
from html import unescape
from typing import Optional
from urllib.parse import urlparse

import httpx

MOBILE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.douyin.com/",
}


def is_douyin_url(url: str) -> bool:
    domain = urlparse(url).netloc.lower()
    return "douyin" in domain or "iesdouyin" in domain


def extract_aweme_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:video|modal_id|aweme_id)[/_:](\d+)",
        r"modal_id=(\d+)",
        r"note/(\d+)",
        r"share/video/(\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def normalize_douyin_url(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if "douyin" not in domain and "iesdouyin" not in domain:
        return url
    aweme_id = extract_aweme_id(url)
    if aweme_id:
        if "note" in url:
            return f"https://www.douyin.com/note/{aweme_id}"
        return f"https://www.douyin.com/video/{aweme_id}"
    return url


async def resolve_short_url(url: str) -> str:
    if "v.douyin.com" not in url and "/v/" not in url:
        return url
    async with httpx.AsyncClient(
        timeout=15, follow_redirects=True, headers=MOBILE_HEADERS, verify=False
    ) as client:
        resp = await client.get(url)
        return str(resp.url)


def _extract_router_json(html: str) -> dict:
    marker = "window._ROUTER_DATA = "
    idx = html.find(marker)
    if idx < 0:
        raise ValueError("Share page missing _ROUTER_DATA")
    start = idx + len(marker)
    depth = 0
    in_str = False
    escape = False
    end = start
    for i, ch in enumerate(html[start:], start):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    payload = html[start:end]
    return json.loads(payload)


def _clean_text(text: str) -> str:
    if not text:
        return ""
    return unescape(re.sub(r"<[^>]+>", "", text)).strip()


def build_format_list(no_wm_url: str, wm_url: str, audio_url: str) -> list:
    formats = []
    if no_wm_url:
        formats.append({
            "format_id": "best",
            "ext": "mp4",
            "resolution": "1080p",
            "filesize": 0,
            "vcodec": "h264",
            "acodec": "aac",
            "tbr": 0,
            "url": no_wm_url,
            "watermarked": False,
        })
    if wm_url and wm_url != no_wm_url:
        formats.append({
            "format_id": "wm_1080p",
            "ext": "mp4",
            "resolution": "1080p (Watermark)",
            "filesize": 0,
            "vcodec": "h264",
            "acodec": "aac",
            "tbr": 0,
            "url": wm_url,
            "watermarked": True,
        })
    if audio_url:
        formats.append({
            "format_id": "audio",
            "ext": "mp3",
            "resolution": "Audio Only",
            "filesize": 0,
            "vcodec": "none",
            "acodec": "aac",
            "tbr": 128,
            "url": audio_url,
            "watermarked": False,
        })
    return formats


async def parse_via_iesdouyin_share_page(aweme_id: str) -> dict:
    share_url = f"https://www.iesdouyin.com/share/video/{aweme_id}/"
    async with httpx.AsyncClient(
        timeout=20, follow_redirects=True, headers=MOBILE_HEADERS, verify=False
    ) as client:
        resp = await client.get(share_url)
        if resp.status_code != 200:
            raise ValueError(f"Share page returned status {resp.status_code}")
        router_data = _extract_router_json(resp.text)

    loader_data = router_data.get("loaderData", {})
    for node_value in loader_data.values():
        if not isinstance(node_value, dict):
            continue
        video_info_res = node_value.get("videoInfoRes", {})
        item_list = video_info_res.get("item_list", [])
        if not item_list:
            continue
        item_info = item_list[0]
        video_data = item_info.get("video", {})
        play_addr = video_data.get("play_addr", {})
        play_urls = play_addr.get("url_list", [])
        wm_url = play_urls[0] if play_urls else ""
        no_wm_url = wm_url.replace("playwm", "play") if wm_url else ""

        cover = ""
        for key in ("cover", "origin_cover", "dynamic_cover"):
            cover_list = video_data.get(key, {}).get("url_list", [])
            if cover_list:
                cover = cover_list[0]
                break

        music_data = item_info.get("music", {})
        audio_urls = music_data.get("play_url", {}).get("url_list", [])
        audio_url = audio_urls[0] if audio_urls else ""

        formats = build_format_list(no_wm_url, wm_url, audio_url)
        duration_ms = item_info.get("duration", 0) or video_data.get("duration", 0)
        duration = int(duration_ms / 1000) if duration_ms and duration_ms > 1000 else int(duration_ms or 0)

        return {
            "title": _clean_text(item_info.get("desc", "") or f"Douyin {aweme_id}"),
            "description": _clean_text(item_info.get("desc", ""))[:500],
            "thumbnail": cover,
            "duration": duration,
            "platform": "douyin",
            "uploader": item_info.get("author", {}).get("nickname", ""),
            "formats": formats,
            "is_playlist": False,
            "playlist_count": None,
            "entry_count": 0,
            "entries": [],
            "best_format": formats[0] if formats else None,
            "_direct_url": no_wm_url or wm_url,
            "_audio_url": audio_url,
        }

    raise ValueError("No video data in share page")


async def parse_douyin_video(url: str) -> dict:
    resolved = await resolve_short_url(url)
    normalized = normalize_douyin_url(resolved)
    aweme_id = extract_aweme_id(normalized)
    if not aweme_id:
        raise ValueError(f"无法从链接提取视频ID: {url}")

    errors = []
    print(f"[DouyinScraper] aweme_id={aweme_id}")

    try:
        result = await parse_via_iesdouyin_share_page(aweme_id)
        if result.get("_direct_url") or result.get("formats"):
            return result
    except Exception as e:
        errors.append(f"iesdouyin_SharePage: {e}")

    raise Exception("抖音解析失败:\n" + "\n".join(errors))


def parse_douyin(url: str) -> dict:
    """Sync entry used by downloader.parse_video."""
    return asyncio.run(parse_douyin_video(url))
