import asyncio
import os
import uuid
import threading

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from services.downloader import (
    DownloadEngine,
    Task,
    TaskStatus,
    parse_video,
)
from services.converter import convert_file

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
}

tasks: dict[str, Task] = {}
_lock = threading.Lock()


class ConnectionManager:
    def __init__(self):
        self.active: set[WebSocket] = set()
        self._lock = threading.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
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
        from services.downloader import build_headers
        headers = build_headers(url)
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
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
        result = parse_video(url, cookies, cookies_from_browser)
        return result
    except Exception as e:
        err_msg = str(e)
        if 'HTTP Error 412' in err_msg:
            err_msg = 'B站反爬虫拦截，请稍后重试或使用Cookie'
        elif 'HTTP Error 403' in err_msg:
            err_msg = '访问被拒绝(403)，请检查链接'
        raise HTTPException(status_code=400, detail=err_msg)


@app.post("/api/download")
async def api_download(req: dict):
    url = req.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="URL不能为空")

    task = Task(
        url=url,
        format_id=req.get("format_id", ""),
        output_format=req.get("output_format", config["output_format"]),
        title=req.get("title", ""),
        thumbnail=req.get("thumbnail", ""),
        platform=req.get("platform", ""),
        duration=req.get("duration", 0),
    )
    with _lock:
        tasks[task.id] = task
    _safe_broadcast(task.to_dict())
    asyncio.create_task(start_download(task))
    return {"task_id": task.id, "status": "queued"}


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
    return config


@app.websocket("/ws/downloads")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        with _lock:
            current_state = [t.to_dict() for t in tasks.values()]
        await websocket.send_json({"type": "init", "data": current_state})

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    os.makedirs(config["download_path"], exist_ok=True)
    print(f"\n[OK] Server started: http://localhost:8976")
    uvicorn.run(app, host="127.0.0.1", port=8976)
