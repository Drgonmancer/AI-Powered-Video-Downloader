import os
import sys
import tempfile
import shutil
import time
from typing import Optional, Tuple

_COOKIE_CACHE: dict = {}
_COOKIE_TTL_SEC = 300


def _cache_get(browser: str, domain: Optional[str]) -> Optional[str]:
    key = f"{browser}|{domain or '*'}"
    entry = _COOKIE_CACHE.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > _COOKIE_TTL_SEC:
        _COOKIE_CACHE.pop(key, None)
        return None
    return value


def _cache_set(browser: str, domain: Optional[str], value: str) -> None:
    key = f"{browser}|{domain or '*'}"
    _COOKIE_CACHE[key] = (time.time(), value)


def get_edge_cookies(domain: str = None) -> str:
    cookies_str = ""
    try:
        import browser_cookie3
        if domain:
            cj = browser_cookie3.edge(domain_name=domain)
        else:
            cj = browser_cookie3.edge()
        for cookie in cj:
            cookies_str += f"{cookie.domain}\tTRUE\t{cookie.path}\t{'FALSE' if cookie.secure else 'FALSE'}\t{str(int(cookie.expires)) if cookie.expires else 0}\t{cookie.name}\t{cookie.value}\n"
        print(f"[EdgeCookie] Successfully loaded {len(list(cj))} cookies from Edge via browser_cookie3")
        return cookies_str
    except Exception as e:
        err_msg = str(e).lower()
        if 'admin' in err_msg or 'require' in err_msg or 'permission' in err_msg:
            print(f"[EdgeCookie] Admin privilege required, trying alternative method...")
            return _get_edge_cookies_via_ytdlp_fallback()
        print(f"[EdgeCookie] browser_cookie3 failed: {e}")
        return _get_edge_cookies_via_ytdlp_fallback()

def _get_edge_cookies_via_ytdlp_fallback() -> str:
    try:
        import yt_dlp
        ydl = yt_dlp.YoutubeDL({
            'quiet': True,
            'cookiesfrombrowser': ('edge',),
        })
        cj = ydl.cookiejar
        cookie_list = list(cj)
        cookies_str = ""
        for c in cookie_list:
            domain = getattr(c, 'domain', '')
            path = getattr(c, 'path', '/')
            secure = getattr(c, 'secure', False)
            expires = getattr(c, 'expires', 0)
            name = getattr(c, 'name', '')
            value = getattr(c, 'value', '')
            cookies_str += f"{domain}\tTRUE\t{path}\t{'TRUE' if secure else 'FALSE'}\t{int(expires) if expires else 0}\t{name}\t{value}\n"
        print(f"[EdgeCookie] Loaded {len(cookie_list)} cookies from Edge via yt-dlp fallback")
        return cookies_str
    except Exception as e2:
        print(f"[EdgeCookie] All methods failed: {e2}")
        return ""

def get_cookies_for_browser(browser: str, domain: str = None) -> str:
    cached = _cache_get(browser, domain)
    if cached is not None:
        return cached

    browser_map = {
        'edge': ('edge', get_edge_cookies),
        'chrome': ('chrome', lambda d: _get_chromium_cookies('chrome', d)),
        'firefox': ('firefox', lambda d: _get_firefox_cookies(d)),
        'brave': ('brave', lambda d: _get_chromium_cookies('brave', d)),
    }
    if browser not in browser_map:
        return ""
    _, func = browser_map[browser]
    try:
        result = func(domain)
        _cache_set(browser, domain, result or "")
        return result
    except Exception as e:
        print(f"[BrowserCookie] Error reading {browser} cookies: {e}")
        return ""

def _get_chromium_cookies(browser_name: str, domain: str = None) -> str:
    try:
        import browser_cookie3
        loader = {
            'chrome': browser_cookie3.chrome,
            'edge': browser_cookie3.edge,
            'brave': browser_cookie3.brave,
        }.get(browser_name, browser_cookie3.chrome)
        if domain:
            cj = loader(domain_name=domain)
        else:
            cj = loader()
        cookies_str = ""
        for cookie in cj:
            cookies_str += f"{cookie.domain}\tTRUE\t{cookie.path}\t{'FALSE' if cookie.secure else 'FALSE'}\t{str(int(cookie.expires)) if cookie.expires else 0}\t{cookie.name}\t{cookie.value}\n"
        print(f"[BrowserCookie] Loaded {len(list(cj))} cookies from {browser_name}")
        return cookies_str
    except Exception as e:
        print(f"[BrowserCookie] browser_cookie3 failed for {browser_name}: {e}")
        try:
            import yt_dlp
            ydl = yt_dlp.YoutubeDL({
                'quiet': True,
                'cookiesfrombrowser': (browser_name,),
            })
            cj = ydl.cookiejar
            cookie_list = list(cj)
            cookies_str = ""
            for c in cookie_list:
                domain = getattr(c, 'domain', '')
                path = getattr(c, 'path', '/')
                secure = getattr(c, 'secure', False)
                expires = getattr(c, 'expires', 0)
                name = getattr(c, 'name', '')
                value = getattr(c, 'value', '')
                cookies_str += f"{domain}\tTRUE\t{path}\t{'TRUE' if secure else 'FALSE'}\t{int(expires) if expires else 0}\t{name}\t{value}\n"
            print(f"[BrowserCookie] Loaded {len(cookie_list)} cookies from {browser_name} via fallback")
            return cookies_str
        except Exception as e2:
            print(f"[BrowserCookie] Fallback also failed for {browser_name}: {e2}")
            return ""

def _get_firefox_cookies(domain: str = None) -> str:
    try:
        import browser_cookie3
        if domain:
            cj = browser_cookie3.firefox(domain_name=domain)
        else:
            cj = browser_cookie3.firefox()
        cookies_str = ""
        for cookie in cj:
            cookies_str += f"{cookie.domain}\tTRUE\t{cookie.path}\t{'FALSE' if cookie.secure else 'FALSE'}\t{str(int(cookie.expires)) if cookie.expires else 0}\t{cookie.name}\t{cookie.value}\n"
        print(f"[BrowserCookie] Loaded {len(list(cj))} cookies from Firefox")
        return cookies_str
    except Exception as e:
        print(f"[BrowserCookie] Failed to read Firefox cookies: {e}")
        return ""
