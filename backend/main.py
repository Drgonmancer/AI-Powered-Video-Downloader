import asyncio
import os
import subprocess
import sys
import threading
import uuid
import warnings

warnings.filterwarnings("ignore", message=".*urllib3.*doesn't match a supported version.*")
warnings.filterwarnings("ignore", message=".*chardet.*charset_normalizer.*doesn't match.*")

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from middleware.auth_middleware import get_optional_user

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

from services.downloader import (
    DownloadEngine,
    Task,
    TaskStatus,
    parse_video,
)
from services.converter import convert_file
from services.summarizer import summarize_video

from database.connection import init_database
from routes.auth_routes import router as auth_router
from routes.membership_routes import router as membership_router
from routes.watermark_routes import router as watermark_router
from routes.llm_routes import router as llm_router

init_database()

app = FastAPI(title="AI万能视频下载器", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {
    "download_path": os.path.join(os.getcwd(), "downloads"),
    "output_format": "mp4",
    "default_quality": "best",
    "max_concurrent": 3,
    "speed_limit": 0,
    "cookies": "",
    "cookies_from_browser": "",
    "locale": "zh",
}

tasks: dict[str, Task] = {}
_lock = threading.Lock()


class ConnectionManager:
    def __init__(self):
        self.active: set[WebSocket] = set()
        self._lock = threading.Lock()

    async def connect(self, ws: WebSocket):
        with self._lock:
            self.active.add(ws)

    def disconnect(self, ws: WebSocket):
        with self._lock:
            self.active.discard(ws)

    async def broadcast(self, message: dict):
        dead = set()
        with self._lock:
            for ws in list(self.active):
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.add(ws)
            for ws in dead:
                self.active.discard(ws)


ws_manager = ConnectionManager()

semaphore = asyncio.Semaphore(config["max_concurrent"])


def _safe_broadcast(task_data: dict):
    tid = task_data.get('id', '')
    with _lock:
        if tid in tasks:
            t = tasks[tid]
            for k, v in task_data.items():
                if k in t.to_dict():
                    setattr(t, k, v)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(ws_manager.broadcast(task_data))
        else:
            loop.run_until_complete(ws_manager.broadcast(task_data))
    except RuntimeError:
        threading.Thread(
            target=_broadcast_thread,
            args=(task_data,),
            daemon=True,
        ).start()


def _broadcast_thread(task_data: dict):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ws_manager.broadcast(task_data))
        loop.close()
    except Exception:
        pass


async def start_download(task: Task):
    async with semaphore:
        engine = DownloadEngine(
            task=task,
            config=config,
            on_progress=_safe_broadcast,
            on_complete=_safe_broadcast,
            on_error=_safe_broadcast,
        )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, engine.run_in_thread)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/proxy-image")
async def proxy_image(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        from services.downloader import build_headers
        headers = build_headers(url)
        
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            verify=False
        ) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code)
            content_type = resp.headers.get('content-type', 'image/jpeg')
            
            from fastapi.responses import Response
            return Response(content=resp.content, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/parse")
async def api_parse(req: dict):
    url = req.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="URL不能为空")
    try:
        cookies = config.get("cookies", "")
        cookies_from_browser = config.get("cookies_from_browser", "")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: parse_video(url, cookies, cookies_from_browser),
        )
        return result
    except Exception as e:
        err_msg = str(e)
        if 'HTTP Error 412' in err_msg:
            err_msg = 'B站反爬虫拦截，请稍后重试或使用Cookie'
        elif 'HTTP Error 403' in err_msg:
            err_msg = '访问被拒绝(403)，请检查链接'
        raise HTTPException(status_code=400, detail=err_msg)


@app.post("/api/summarize")
async def api_summarize(req: dict, current_user: dict = Depends(get_optional_user)):
    """Async AI summary – called after /api/parse returns so UI is not blocked."""
    url = req.get("url", "")
    video_info = req.get("video_info") or {}
    if not url and not video_info:
        raise HTTPException(status_code=400, detail="url or video_info required")
    cookies = config.get("cookies", "")
    cookies_from_browser = config.get("cookies_from_browser", "")
    user_id = current_user.get("id") if current_user else None
    provider_id = req.get("provider_id")
    mode = req.get("mode", "full")
    loop = asyncio.get_event_loop()
    summary = await loop.run_in_executor(
        None,
        lambda: summarize_video(
            video_info,
            url=url,
            cookies=cookies,
            cookies_from_browser=cookies_from_browser,
            locale=config.get("locale", "zh"),
            user_id=user_id,
            provider_id=provider_id,
            mode=mode,
        ),
    )
    return summary


@app.post("/api/download")
async def api_download(req: dict, current_user: dict = Depends(get_optional_user)):
    url = req.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="URL不能为空")

    user_id = current_user.get("id") if current_user else None

    usage_payload = None
    if user_id:
        from services.membership_service import (
            check_daily_download_limit,
            increment_daily_download_count,
            get_usage_snapshot,
        )
        allowed, used, remaining = check_daily_download_limit(user_id)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"今日下载次数已用完({used}次)。请升级会员或明天再来！"
            )
        increment_daily_download_count(user_id)
        usage_payload = get_usage_snapshot(user_id)

    task = Task(
        url=url,
        format_id=req.get("format_id", ""),
        output_format=req.get("output_format", config["output_format"]),
        title=req.get("title", ""),
        thumbnail=req.get("thumbnail", ""),
        platform=req.get("platform", ""),
        duration=req.get("duration", 0),
        _direct_url=req.get("_direct_url", ""),
        user_id=user_id,
    )
    with _lock:
        tasks[task.id] = task
    _safe_broadcast(task.to_dict())
    asyncio.create_task(start_download(task))
    resp = {"task_id": task.id, "status": "queued"}
    if usage_payload:
        resp["usage"] = usage_payload
        asyncio.create_task(ws_manager.broadcast({"type": "usage", "data": usage_payload}))
    return resp


@app.get("/api/downloads")
async def api_list_tasks(status: str = ""):
    with _lock:
        result = [t.to_dict() for t in tasks.values()]
    if status:
        result = [t for t in result if t["status"] == status]
    return sorted(result, key=lambda x: x["created_at"], reverse=True)


@app.post("/api/download/{task_id}/pause")
async def api_pause(task_id: str):
    with _lock:
        task = tasks.get(task_id)
    if not task or task.status != TaskStatus.DOWNLOADING:
        raise HTTPException(status_code=400, detail="任务不可暂停")
    task.status = TaskStatus.PAUSED
    await ws_manager.broadcast(task.to_dict())
    return {"ok": True}


@app.post("/api/download/{task_id}/resume")
async def api_resume(task_id: str):
    with _lock:
        task = tasks.get(task_id)
    if not task or task.status != TaskStatus.PAUSED:
        raise HTTPException(status_code=400, detail="任务不可恢复")
    task.error_message = ""
    asyncio.create_task(start_download(task))
    await ws_manager.broadcast(task.to_dict())
    return {"ok": True}


@app.delete("/api/download/{task_id}")
async def api_cancel(task_id: str):
    with _lock:
        task = tasks.pop(task_id, None)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"ok": True}


@app.get("/api/download/{task_id}/open")
async def api_open_file(task_id: str):
    import subprocess
    import platform
    with _lock:
        task = tasks.get(task_id)
    if not task or not task.filepath:
        raise HTTPException(status_code=404, detail="文件路径不存在")
    if not os.path.exists(task.filepath):
        dl_dir = config['download_path']
        if os.path.exists(dl_dir):
            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', '/select,', dl_dir])
                return {"ok": True, "action": "folder", "path": dl_dir}
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', dl_dir])
                return {"ok": True, "action": "folder", "path": dl_dir}
            else:
                subprocess.Popen(['xdg-open', dl_dir])
                return {"ok": True, "action": "folder", "path": dl_dir}
        raise HTTPException(status_code=404, detail="文件和文件夹都不存在")
    if platform.system() == 'Windows':
        subprocess.Popen(['explorer', '/select,', task.filepath], shell=True)
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', '-R', task.filepath])
    else:
        subprocess.Popen(['xdg-open', os.path.dirname(task.filepath)])
    return {"ok": True, "action": "file", "path": task.filepath}


@app.post("/api/batch")
async def api_batch(req: dict):
    playlist_url = req.get("playlist_url", "")
    urls = req.get("urls", [])
    format_id = req.get("format_id", "")
    output_format = req.get(
        "output_format", config["output_format"]
    )

    if playlist_url:
        try:
            info = parse_video(playlist_url)
            urls = info.get("entries", [])
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"播放列表解析失败: {e}"
            )

    if not urls:
        raise HTTPException(
            status_code=400, detail="未提供有效的下载链接"
        )

    created = []
    for url in urls:
        task = Task(
            url=url,
            format_id=format_id,
            output_format=output_format,
        )
        with _lock:
            tasks[task.id] = task
        _safe_broadcast(task.to_dict())
        asyncio.create_task(start_download(task))
        created.append(task.id)

    batch_id = uuid.uuid4().hex[:8]
    return {
        "batch_id": batch_id,
        "total": len(created),
        "task_ids": created,
    }


@app.post("/api/convert")
async def api_convert(req: dict):
    input_path = req.get("input_path", "")
    output_format = req.get("output_format", "")
    quality = req.get("quality", "medium")

    if not input_path or not os.path.exists(input_path):
        raise HTTPException(
            status_code=400, detail="输入文件不存在"
        )
    if not output_format:
        raise HTTPException(
            status_code=400, detail="请指定输出格式"
        )

    try:
        result = convert_file(input_path, output_format, quality)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"转换失败: {e}"
        )


@app.get("/api/settings")
async def api_get_settings():
    return config


@app.put("/api/settings")
async def api_update_settings(req: dict):
    global semaphore
    for key, value in req.items():
        if key in config:
            config[key] = value
    if "max_concurrent" in req:
        semaphore = asyncio.Semaphore(int(config["max_concurrent"]))
    # Ensure download_path directory exists
    dl_path = config.get("download_path", "")
    if dl_path:
        try:
            os.makedirs(dl_path, exist_ok=True)
        except Exception:
            pass
    return config


@app.get("/api/browse-folder")
async def api_browse_folder():
    """Open a native OS folder-picker dialog and return the selected path."""
    import threading
    import subprocess
    result_holder: list[str] = []

    def _pick_tk():
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes("-topmost", True)
            folder = filedialog.askdirectory(title="选择下载文件夹")
            root.destroy()
            result_holder.append(folder or "")
        except Exception:
            result_holder.append("")

    def _pick_ps():
        try:
            script = '''
            Add-Type -AssemblyName System.Windows.Forms
            $folder = New-Object System.Windows.Forms.FolderBrowserDialog
            $folder.Description = "选择下载文件夹"
            $folder.ShowNewFolderButton = $true
            if ($folder.ShowDialog() -eq "OK") { $folder.SelectedPath } else { "" }
            '''
            proc = subprocess.run(
                ['powershell', '-NoProfile', '-Command', script],
                capture_output=True, text=True, timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            path = proc.stdout.strip()
            if path:
                result_holder.append(path)
        except Exception:
            result_holder.append("")

    # Try PowerShell first (more reliable on Windows), fallback to tkinter
    _pick_ps()
    if not result_holder or not result_holder[0]:
        t = threading.Thread(target=_pick_tk, daemon=True)
        t.start()
        t.join(timeout=30)
    
    path = result_holder[0] if result_holder else ""
    return {"path": path}


@app.get("/api/open-path")
async def api_open_path(path: str = ""):
    """Open the specified path in file explorer."""
    import platform
    if not path:
        path = config.get("download_path", os.path.join(os.getcwd(), "downloads"))
    
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"路径不存在: {path}")
    
    if platform.system() == 'Windows':
        subprocess.Popen(['explorer', path], shell=True)
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])
    
    return {"ok": True, "path": path}


@app.post("/api/chat")
async def api_chat(req: dict):
    """AI 追问对话：针对已解析视频内容进行 Q&A."""
    from ai_config import AI_SUMMARY_ENABLED, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
    question = (req.get("question") or "").strip()
    video_context = (req.get("video_context") or "").strip()
    history = req.get("history") or []
    locale = req.get("locale", "zh")

    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    key = (DEEPSEEK_API_KEY or "").strip()
    if not key:
        return {"answer": "未配置 DeepSeek API Key，请在 backend/ai_config.py 中填写。" if locale.startswith("zh") else "DEEPSEEK_API_KEY not configured."}

    lang_hint = "请使用中文回答" if locale.startswith("zh") else "Please respond in English"
    system_prompt = (
        "你是视频内容助手，帮助用户深入理解视频内容。"
        f"以下是视频信息：\n\n{video_context}\n\n"
        f"{lang_hint}。回答要简洁、准确，结合视频内容作答。"
    )
    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-10:]:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": question})

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": DEEPSEEK_MODEL, "messages": messages, "temperature": 0.5, "max_tokens": 600},
            )
            resp.raise_for_status()
            data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        return {"answer": answer}
    except httpx.HTTPStatusError as e:
        detail = e.response.text[:200] if e.response else str(e)
        raise HTTPException(status_code=502, detail=f"AI error: {detail}")


def _snapshot_tasks() -> list:
    with _lock:
        return [t.to_dict() for t in tasks.values()]


@app.websocket("/ws/downloads")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await ws_manager.connect(websocket)
    try:
        current_state = await asyncio.to_thread(_snapshot_tasks)
        await websocket.send_json({"type": "init", "data": current_state})

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        print(f"[WS] connection error: {exc}")
        ws_manager.disconnect(websocket)


def build_frontend():
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    pkg_json = os.path.join(frontend_dir, "package.json")
    if not os.path.exists(pkg_json):
        print("[Build] No frontend package.json found, skipping build")
        return
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("[Build] Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            check=True,
            capture_output=True,
        )
    print("[Build] Building frontend...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=frontend_dir,
        capture_output=False,
        text=True,
        shell=os.name == "nt",
    )
    if result.returncode != 0:
        print(f"[Build] Build failed (exit {result.returncode})")
    else:
        print("[Build] Frontend built successfully")


_frontend_mounted = False


def _landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>AI万能视频下载器</title>
<style>body{font-family:system-ui;background:#0f0f1a;color:#e2e8f0;max-width:520px;margin:80px auto;padding:24px}
h1{font-size:1.25rem}p{color:#94a3b8;line-height:1.6}a{color:#6C63FF}</style></head>
<body><h1>前端页面尚未就绪</h1>
<p>请在项目根目录运行：<code>python start.py</code></p>
<p>或先构建前端：<code>cd frontend && npm install && npm run build</code>，再启动后端。</p>
<p>请用 Edge/Chrome 打开：<a href="http://127.0.0.1:9000">http://127.0.0.1:9000</a>（勿用 Cursor 内置预览）</p>
<p>开发模式（需另开 Vite）：<a href="http://localhost:3000">http://localhost:3000</a></p>
<p>API 文档：<a href="/docs">/docs</a></p></body></html>"""


def _no_cache(resp):
    """Set no-cache headers and strip ETag/Last-Modified to prevent 304 responses."""
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    if 'ETag' in resp.headers:
        del resp.headers['ETag']
    if 'Last-Modified' in resp.headers:
        del resp.headers['Last-Modified']


def mount_frontend():
    global _frontend_mounted
    if _frontend_mounted:
        return bool(os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")))

    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        assets_dir = os.path.join(FRONTEND_DIST, "assets")
        if os.path.isdir(assets_dir):
            app.mount(
                "/assets",
                StaticFiles(directory=assets_dir),
                name="static-assets",
            )

        avatars_dir = os.path.join(BASE_DIR, "data", "avatars")
        if os.path.isdir(avatars_dir) or True:
            os.makedirs(avatars_dir, exist_ok=True)
            app.mount(
                "/api/avatars",
                StaticFiles(directory=avatars_dir),
                name="avatar-files",
            )

        @app.get("/", include_in_schema=False)
        async def serve_index():
            resp = FileResponse(index_path)
            _no_cache(resp)
            return resp

        @app.middleware("http")
        async def _no_cache_assets(request, call_next):
            response = await call_next(request)
            if request.url.path.startswith("/assets/") or request.url.path == "/":
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                if 'ETag' in response.headers:
                    del response.headers['ETag']
                if 'Last-Modified' in response.headers:
                    del response.headers['Last-Modified']
            return response

        from fastapi import Request
        from fastapi.responses import JSONResponse

        @app.api_route(
            "/{full_path:path}",
            methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            include_in_schema=False,
        )
        async def serve_spa(request: Request, full_path: str):
            if full_path.startswith("api/") or full_path.startswith("ws/"):
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Route not found: /{full_path}"},
                )
            if request.method not in ("GET", "HEAD"):
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Route not found: /{full_path}"},
                )
            if full_path in ("docs", "redoc", "openapi.json"):
                raise HTTPException(status_code=404)

            file_path = os.path.join(FRONTEND_DIST, full_path)
            if os.path.isfile(file_path):
                resp = FileResponse(file_path)
                _no_cache(resp)
                return resp

            resp = FileResponse(index_path)
            _no_cache(resp)
            return resp

        _frontend_mounted = True
        print(f"[Frontend] Mounted at / (serving from {FRONTEND_DIST})")
        return True

    @app.get("/", include_in_schema=False)
    async def serve_landing():
        return HTMLResponse(_landing_html())

    _frontend_mounted = True
    print(f"[Frontend] No dist at {FRONTEND_DIST}, showing setup page at /")
    return False


def setup_frontend(*, allow_build: bool = False) -> bool:
    """allow_build=True 时始终重新构建 frontend/dist（本地一键启动用）。"""
    if allow_build:
        build_frontend()
    return mount_frontend()


def _register_api_routers():
    app.include_router(auth_router)
    app.include_router(membership_router)
    app.include_router(watermark_router)
    app.include_router(llm_router)


_register_api_routers()

print("[Membership] 会员系统已启用 - 认证API: /api/auth/*, 会员API: /api/membership/*")
print("[LLM] 大模型配置API: /api/llm/providers (GET/POST/DELETE)")


def _should_build_frontend() -> bool:
    if "--build-frontend" in sys.argv:
        return True
    return os.environ.get("BUILD_FRONTEND", "").lower() in ("1", "true", "yes")


# API 路由必须先于 SPA 回退注册；一键启动传 --build-frontend 会先构建再挂载前端
setup_frontend(allow_build=_should_build_frontend())


if __name__ == "__main__":
    import uvicorn

    os.makedirs(config["download_path"], exist_ok=True)

    is_render = os.environ.get("RENDER", "") or os.environ.get("RENDER_SERVICE_ID", "")
    if is_render and not os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
        setup_frontend(allow_build=True)

    port = int(os.environ.get("PORT", 9000))
    host = "0.0.0.0" if is_render else "127.0.0.1"
    ui_url = f"http://127.0.0.1:{port}/"
    print(f"\n[OK] Server started: {ui_url}")
    if not os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
        print("[HINT] Run 'python start.py' from project root to build and open the UI")
    uvicorn.run(app, host=host, port=port)
