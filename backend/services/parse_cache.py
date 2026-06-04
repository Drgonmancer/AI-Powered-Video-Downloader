"""短时解析结果缓存，避免重复解析同一链接。"""

import hashlib
import time
from typing import Any, Dict, Optional, Tuple

_CACHE: Dict[str, Tuple[float, dict]] = {}
_TTL_SEC = 300
_MAX_ENTRIES = 64


def _key(url: str, cookies: str, browser: str) -> str:
    raw = f"{url}|{bool(cookies)}|{browser or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def get_cached(url: str, cookies: str = "", browser: str = "") -> Optional[dict]:
    k = _key(url, cookies, browser)
    entry = _CACHE.get(k)
    if not entry:
        return None
    ts, data = entry
    if time.time() - ts > _TTL_SEC:
        _CACHE.pop(k, None)
        return None
    return data


def set_cached(url: str, data: dict, cookies: str = "", browser: str = "") -> None:
    if len(_CACHE) >= _MAX_ENTRIES:
        oldest = min(_CACHE.items(), key=lambda x: x[1][0])[0]
        _CACHE.pop(oldest, None)
    k = _key(url, cookies, browser)
    _CACHE[k] = (time.time(), data)
