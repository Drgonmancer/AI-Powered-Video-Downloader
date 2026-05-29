import os
import re
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import yt_dlp


def normalize_douyin_url(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if 'douyin' not in domain and 'iesdouyin' not in domain:
        return url

    video_id_match = re.search(r'(?:video|modal_id)[/_:]([\d]+)', url)
    if video_id_match:
        video_id = video_id_match.group(1)
        return f'https://www.douyin.com/video/{video_id}'

    short_id_match = re.search(r'/v/([a-zA-Z0-9]+)', url)
    if short_id_match:
        return url

    note_id_match = re.search(r'note/(\d+)', url)
    if note_id_match:
        return f'https://www.douyin.com/note/{note_id_match.group(1)}'

    return url


def build_headers(url: str) -> dict:
    domain = urlparse(url).netloc.lower()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    if 'bilibili' in domain or 'b23.tv' in domain:
        headers['Referer'] = 'https://www.bilibili.com/'
        headers['Origin'] = 'https://www.bilibili.com'
        headers['Sec-Fetch-Dest'] = 'empty'
        headers['Sec-Fetch-Mode'] = 'cors'
        headers['Sec-Fetch-Site'] = 'same-site'
    elif 'douyin' in domain or 'iesdouyin' in domain:
        headers.update({
            'Referer': 'https://www.douyin.com/',
            'Origin': 'https://www.douyin.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Accept-Encoding': 'gzip, deflate, br',
        })
    elif 'kuaishou' in domain:
        headers['Referer'] = 'https://www.kuaishou.com/'
    elif 'twitter' in domain or 'x.com' in domain:
        headers['Referer'] = 'https://x.com/'
    elif 'tiktok' in domain:
        headers['Referer'] = 'https://www.tiktok.com/'
    return headers


def build_extractor_args(url: str) -> dict:
    domain = urlparse(url).netloc.lower()
    if 'bilibili' in domain or 'b23.tv' in domain:
        return {'bilibili': {'player': 'web'}}
    elif 'douyin' in domain or 'iesdouyin' in domain:
        return {
            'douyin': {
                'webpage_download': True,
            },
            'tiktok': {
                'api_hostname': 'api16-normal-c-useast1a.tiktokv.com',
            },
        }
    return {}


def parse_video(url: str, cookies: str = '', cookies_from_browser: str = '') -> dict:
    from services.browser_cookies import get_cookies_for_browser

    url = normalize_douyin_url(url)
    print(f"[Parser] Processing URL: {url}")

    domain = urlparse(url).netloc.lower()
    if 'douyin' in domain or 'iesdouyin' in domain:
        try:
            from services.douyin_scraper import parse_douyin
            result = parse_douyin(url)
            if result and (result.get('_direct_url') or result.get('formats')):
                print('[Parser] Douyin scraper succeeded')
                return result
        except Exception as e:
            print(f'[Parser] Douyin scraper failed ({e}), falling back to yt-dlp')

    effective_cookies = cookies
    if cookies_from_browser and not effective_cookies:
        domain = urlparse(url).netloc.lower()
        print(f"[Parser] Auto-loading cookies from {cookies_from_browser} for {domain}")
        effective_cookies = get_cookies_for_browser(cookies_from_browser, domain)
        if effective_cookies:
            print(f"[Parser] Successfully loaded browser cookies ({len(effective_cookies)} bytes)")
        else:
            print(f"[Parser] Warning: Could not load cookies from {cookies_from_browser}, will try without")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'http_headers': build_headers(url),
        'extractor_args': build_extractor_args(url),
        'no_check_certificates': True,
        'extractor_retries': 3,
    }
    if effective_cookies:
        ydl_opts['cookie'] = effective_cookies
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return normalize_info(info)
    except Exception as e:
        err_msg = str(e)
        if 'Unsupported URL' in err_msg:
            raise Exception(f'不支持该链接格式: {url}\n\n建议:\n1. 确认链接是否完整\n2. 尝试使用视频分享页面的原始链接\n3. 某些特殊页面（如合集/直播）可能不支持')
        elif 'HTTP Error 412' in err_msg:
            raise Exception('B站反爬虫拦截，请稍后重试或使用Cookie')
        elif 'HTTP Error 403' in err_msg:
            raise Exception('访问被拒绝(403)，请检查链接或使用代理')
        elif 'HTTP Error 404' in err_msg:
            raise Exception('视频不存在或已被删除(404)')
        elif 'Sign' in err_msg or 'sign' in err_msg.lower():
            raise Exception('签名验证失败，该视频需要登录才能下载')
        elif 'JSON' in err_msg or 'json' in err_msg.lower():
            raise Exception(f'页面解析失败，可能需要更新 yt-dlp 或使用浏览器Cookie\n错误详情: {err_msg[:200]}')
        else:
            raise


def normalize_info(raw_info: dict) -> dict:
    formats = []
    if raw_info.get('formats'):
        for f in raw_info['formats']:
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                formats.append({
                    'format_id': f['format_id'],
                    'ext': f.get('ext', ''),
                    'resolution': f.get('resolution', f.get('format_note', '')),
                    'filesize': f.get('filesize') or f.get('filesize_approx', 0),
                    'vcodec': f.get('vcodec', ''),
                    'acodec': f.get('acodec', ''),
                    'tbr': f.get('tbr', 0),
                })

    best = pick_best_format(formats)

    return {
        'title': raw_info.get('title', ''),
        'description': (raw_info.get('description') or '')[:500],
        'thumbnail': raw_info.get('thumbnail', ''),
        'duration': raw_info.get('duration', 0),
        'platform': get_platform(
            raw_info.get('webpage_url', raw_info.get('url', ''))
        ),
        'uploader': raw_info.get('uploader', ''),
        'formats': formats,
        'is_playlist':
            '_type' in raw_info and raw_info['_type'] == 'playlist',
        'playlist_count':
            raw_info.get('playlist_count')
            if raw_info.get('_type') == 'playlist'
            else None,
        'entry_count': raw_info.get('entry_count',
                                  len(raw_info.get('entries', []))),
        'entries': [
            e['url'] for e in raw_info.get('entries', [])
        ] if raw_info.get('entries') else [],
        'best_format': best,
    }


def pick_best_format(formats: list) -> dict:
    import shutil, glob as _glob, os as _os
    has_ffmpeg = shutil.which('ffmpeg') is not None
    if not has_ffmpeg:
        winget_paths = _glob.glob(_os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\*\ffmpeg-*\bin\ffmpeg.exe'))
        has_ffmpeg = len(winget_paths) > 0

    video_formats = [
        f for f in formats if f.get('vcodec', '') not in ('none', '')
    ]
    audio_formats = [
        f for f in formats if f.get('acodec', '') not in ('none', '')
    ]

    if not video_formats and audio_formats:
        best_audio = max(audio_formats, key=lambda x: x.get('tbr', 0))
        return {
            'format_id': best_audio['format_id'],
            'resolution': 'audio only',
            'ext': best_audio['ext'],
            'note': '最佳音质',
        }

    merged_mp4 = [
        f for f in formats
        if f.get('vcodec', '') not in ('none', '')
        and f.get('acodec', '') not in ('none', '')
        and f.get('ext', '') == 'mp4'
    ]
    if merged_mp4:
        best = max(merged_mp4, key=lambda x: x.get('tbr', 0))
        return {
            'format_id': best['format_id'],
            'resolution': best['resolution'],
            'ext': best['ext'],
            'note': '最佳画质' + (' (已含音频)' if has_ffmpeg else ''),
        }

    if video_formats and audio_formats:
        best_v = max(video_formats, key=lambda x: x.get('tbr', 0))
        if has_ffmpeg:
            best_a = max(audio_formats, key=lambda x: x.get('tbr', 0))
            return {
                'format_id': f"{best_v['format_id']}+{best_a['format_id']}",
                'resolution': best_v['resolution'],
                'ext': 'mp4',
                'note': '视频+音频合并',
            }
        return {
            'format_id': best_v['format_id'],
            'resolution': best_v['resolution'],
            'ext': best_v.get('ext', 'mp4'),
            'note': '最佳画质 (无音频)',
        }

    if video_formats:
        best_v = max(video_formats, key=lambda x: x.get('tbr', 0))
        return {
            'format_id': best_v['format_id'],
            'resolution': best_v['resolution'],
            'ext': best_v.get('ext', 'mp4'),
            'note': '最佳画质',
        }

    return {'format_id': '', 'resolution': '', 'ext': '',
            'note': '无可选格式'}


def get_platform(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    platform_map = {
        'youtube.com': 'youtube', 'youtu.be': 'youtube',
        'bilibili.com': 'bilibili', 'b23.tv': 'bilibili',
        'douyin.com': 'douyin', 'iesdouyin.com': 'douyin',
        'kuaishou.com': 'kuaishou',
        'twitter.com': 'twitter', 'x.com': 'twitter',
        'instagram.com': 'instagram',
        'tiktok.com': 'tiktok',
    }
    for domain_key, name in platform_map.items():
        if domain_key in domain:
            return name
    return 'unknown'


class TaskStatus:
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


class DownloadEngine:
    def __init__(self, task, config,
                 on_progress=None, on_complete=None, on_error=None):
        self.task = task
        self.config = config
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        self._cancelled = False
        self._ydl = None

    def build_ydl_opts(self) -> dict:
        import shutil
        import glob as _glob
        ffmpeg_path = None
        has_ffmpeg = shutil.which('ffmpeg') is not None
        if not has_ffmpeg:
            import os as _os
            winget_paths = _glob.glob(_os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\*\ffmpeg-*\bin\ffmpeg.exe'))
            if winget_paths:
                ffmpeg_path = winget_paths[0]
                has_ffmpeg = True
                print(f"[Downloader] Found ffmpeg: {ffmpeg_path}")

        self.task.url = normalize_douyin_url(self.task.url)

        opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join(
                self.config['download_path'], '%(title)s.%(ext)s'
            ),
            'progress_hooks': [self._progress_hook],
            'http_headers': build_headers(self.task.url),
            'extractor_args': build_extractor_args(self.task.url),
            'no_check_certificates': True,
            'retries': 10,
            'fragment_retries': 10,
            'concurrent_fragment_downloads': 4,
            'buffersize': 1024 * 64,
        }
        if ffmpeg_path:
            opts['ffmpeg_location'] = ffmpeg_path
        from services.browser_cookies import get_cookies_for_browser
        effective_cookies = self.config.get('cookies', '')
        cookies_from_browser = self.config.get('cookies_from_browser', '')
        if cookies_from_browser and not effective_cookies:
            from urllib.parse import urlparse as _urlparse
            domain = _urlparse(self.task.url).netloc.lower()
            print(f"[Downloader] Auto-loading cookies from {cookies_from_browser} for {domain}")
            effective_cookies = get_cookies_for_browser(cookies_from_browser, domain)
            if effective_cookies:
                print(f"[Downloader] Successfully loaded browser cookies ({len(effective_cookies)} bytes)")
            else:
                print(f"[Downloader] Warning: Could not load cookies, will try without")
        if effective_cookies:
            opts['cookie'] = effective_cookies
        if cookies_from_browser:
            opts['cookiesfrombrowser'] = (self.config['cookies_from_browser'],)
        if has_ffmpeg:
            opts['merge_output_format'] = self.task.output_format
        if self.config.get('speed_limit', 0) > 0:
            opts['ratelimit'] = self.config['speed_limit']
        if self.task.format_id:
            fmt = self.task.format_id
            if '+' in fmt and not has_ffmpeg:
                fmt = fmt.split('+')[0]
                print(f"[Downloader] No ffmpeg, using single stream: {fmt}")
            opts['format'] = fmt
        return opts

    def _progress_hook(self, d: dict):
        try:
            if d['status'] == 'downloading':
                total = (
                    d.get('total_bytes')
                    or d.get('total_bytes_estimate', 1)
                )
                downloaded = d.get('downloaded_bytes', 0)
                self.task.progress = min((downloaded / total) * 100, 99.9)
                self.task.speed = d.get('_speed_str', '')
                self.task.eta = d.get('_eta_str', '')
                if self.on_progress:
                    self.on_progress(self.task.to_dict())
            elif d['status'] == 'finished':
                self.task.progress = 99.9
                self.task.status = TaskStatus.MERGING
                self.task.speed = ''
                self.task.eta = ''
                if self.on_progress:
                    self.on_progress(self.task.to_dict())
            elif d['status'] == 'error':
                self.task.error_message = d.get('info', {}).get('error') or d.get('error', 'Download error')
                self.task.status = TaskStatus.FAILED
                if self.on_error:
                    self.on_error(self.task.to_dict())
        except Exception as e:
            print(f"[ProgressHook] Error: {e}")

    def run_in_thread(self):
        try:
            os.makedirs(self.config['download_path'], exist_ok=True)
            self.task.status = TaskStatus.DOWNLOADING
            self.task.started_at = time.time()
            opts = self.build_ydl_opts()

            with yt_dlp.YoutubeDL(opts) as self._ydl:
                info = self._ydl.extract_info(
                    self.task.url, download=True
                )
                if info:
                    self.task.title = info.get(
                        'title', self.task.title
                    )
                    try:
                        expected_filename = (
                            self._ydl.prepare_filename(info)
                        )
                        if expected_filename and os.path.exists(expected_filename):
                            self.task.filepath = expected_filename
                    except Exception:
                        pass
                    if not self.task.filepath or not os.path.exists(self.task.filepath):
                        dl_dir = self.config.get('download_path', '')
                        title_clean = info.get('title', self.task.title or '')
                        import glob as _glob
                        exts = ['mp4', 'mkv', 'webm', 'flv', 'avi', 'mov']
                        for ext in exts:
                            pattern = os.path.join(dl_dir, f'*{title_clean[:20]}*.{ext}')
                            matches = _glob.glob(pattern)
                            if matches:
                                self.task.filepath = matches[0]
                                break
                        if not self.task.filepath:
                            pattern = os.path.join(dl_dir, '*.*')
                            all_files = _glob.glob(pattern)
                            valid_files = [f for f in all_files if os.path.isfile(f) and os.path.splitext(f)[1][1:].lower() in exts]
                            if valid_files:
                                valid_files.sort(key=os.path.getmtime, reverse=True)
                                self.task.filepath = valid_files[0]
                    if self.task.filepath and os.path.exists(self.task.filepath):
                        self.task.filesize = os.path.getsize(
                            self.task.filepath
                        )

            self.task.progress = 100
            self.task.speed = ''
            self.task.eta = ''
            self.task.status = TaskStatus.COMPLETED
            self.task.completed_at = time.time()
            if self.on_complete:
                self.on_complete(self.task.to_dict())

        except Exception as e:
            err_msg = str(e)
            if 'HTTP Error 412' in err_msg:
                err_msg = 'B站反爬虫拦截，请稍后重试或使用Cookie'
            elif 'HTTP Error 403' in err_msg:
                err_msg = '访问被拒绝(403)，请检查链接或使用代理'
            elif 'HTTP Error 404' in err_msg:
                err_msg = '视频不存在或已被删除(404)'
            elif 'Sign' in err_msg or 'sign' in err_msg.lower():
                err_msg = '签名验证失败，该视频需要登录才能下载'
            self.task.error_message = err_msg
            self.task.status = TaskStatus.FAILED
            if self.on_error:
                self.on_error(self.task.to_dict())

    def cancel(self):
        self._cancelled = True
        if self._ydl:
            try:
                self._ydl.params['abort'] = True
            except Exception:
                pass


class Task:
    def __init__(self, **kwargs):
        import uuid
        self.id = kwargs.get('id', uuid.uuid4().hex[:8])
        self.url = kwargs.get('url', '')
        self.title = kwargs.get('title', '')
        self.platform = kwargs.get('platform', '')
        self.thumbnail = kwargs.get('thumbnail', '')
        self.duration = kwargs.get('duration', 0)
        self.format_id = kwargs.get('format_id', '')
        self.output_format = kwargs.get('output_format', 'mp4')
        self.filepath = kwargs.get('filepath', '')
        self.filesize = kwargs.get('filesize', 0)
        self.status = kwargs.get('status', TaskStatus.QUEUED)
        self.progress = float(kwargs.get('progress', 0.0))
        self.speed = kwargs.get('speed', '')
        self.eta = kwargs.get('eta', '')
        self.error_message = kwargs.get('error_message', '')
        self.created_at = kwargs.get('created_at', time.time())
        self.started_at = kwargs.get('started_at')
        self.completed_at = kwargs.get('completed_at')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'platform': self.platform,
            'thumbnail': self.thumbnail,
            'duration': self.duration,
            'format_id': self.format_id,
            'output_format': self.output_format,
            'filepath': self.filepath,
            'filesize': self.filesize,
            'status': self.status,
            'progress': round(self.progress, 1),
            'speed': self.speed,
            'eta': self.eta,
            'error_message': self.error_message,
            'created_at': self.created_at,
        }
