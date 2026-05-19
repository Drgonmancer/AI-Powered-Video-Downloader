# AI万能视频下载器 — 后端API接口文档

> 前端开发人员专用 | MVP版本 | 基础地址: `http://localhost:8976`

---

## 一、基础信息

| 项目 | 说明 |
|------|------|
| 协议 | HTTP + WebSocket |
| 数据格式 | JSON (Content-Type: application/json) |
| 编码 | UTF-8 |
| 跨域 | 全部允许 (CORS: *) |

**WebSocket地址**: `ws://localhost:8976/ws/downloads`

---

## 二、接口列表总览

| # | 方法 | 路径 | 说明 |
|---|------|------|------|
| 1 | POST | `/api/parse` | 解析视频URL |
| 2 | POST | `/api/download` | 创建下载任务 |
| 3 | GET | `/api/downloads` | 获取所有任务 |
| 4 | POST | `/api/download/{id}/pause` | 暂停任务 |
| 5 | POST | `/api/download/{id}/resume` | 恢复任务 |
| 6 | DELETE | `/api/download/{id}` | 取消/删除任务 |
| 7 | POST | `/api/batch` | 批量下载 |
| 8 | POST | `/api/convert` | 格式转换 |
| 9 | GET | `/api/settings` | 获取设置 |
| 10 | PUT | `/api/settings` | 更新设置 |
| WS | — | `/ws/downloads` | 实时进度推送 |

---

## 三、接口详情

### 3.1 解析视频URL

```
POST /api/parse
```

**请求**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 视频或播放列表的完整URL |

**成功响应 (200)**
```json
{
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "Official music video...",
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "duration": 212,
  "platform": "youtube",
  "uploader": "Rick Astley",
  "formats": [
    {
      "format_id": "137",
      "ext": "mp4",
      "resolution": "1080p",
      "filesize": 52428800,
      "vcodec": "h264",
      "acodec": "none",
      "tbr": 5000
    },
    {
      "format_id": "251",
      "ext": "webm",
      "resolution": "audio only",
      "filesize": 2097152,
      "vcodec": "none",
      "acodec": "opus",
      "tbr": 160
    }
  ],
  "is_playlist": false,
  "playlist_count": null,
  "entry_count": 0,
  "entries": [],
  "best_format": {
    "format_id": "137+251",
    "resolution": "1080p",
    "ext": "mp4",
    "note": "视频+音频合并（需合并）"
  }
}
```

**错误响应 (400)**
```json
{ "detail": "不支持该平台 / URL无效 / 网络超时" }
```

**注意**: 此接口可能耗时较长（需请求目标网站），前端应显示loading状态。

---

### 3.2 创建下载任务

```
POST /api/download
```

**请求**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format_id": "137+251",
  "output_format": "mp4"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| url | string | 是 | — | 视频URL |
| format_id | string | 否 | "" | 格式ID，空则用yt-dlp默认最佳 |
| output_format | string | 否 | "mp4" | 输出容器格式: mp4/webm/mkv |

**响应 (200)**
```json
{
  "task_id": "a1b2c3d4",
  "status": "queued"
}
```

创建后任务自动进入队列，通过WebSocket接收进度更新。

---

### 3.3 获取所有下载任务

```
GET /api/downloads?status=downloading
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 过滤状态: queued/downloading/paused/merging/completed/failed。不传返回全部 |

**响应 (200)**
```json
[
  {
    "id": "a1b2c3d4",
    "url": "https://...",
    "title": "视频标题",
    "platform": "youtube",
    "thumbnail": "https://...",
    "duration": 212,
    "format_id": "137+251",
    "output_format": "mp4",
    "filepath": "./downloads/标题.mp4",
    "filesize": 52428800,
    "status": "downloading",
    "progress": 65.3,
    "speed": "5.2MB/s",
    "eta": "00:02:30",
    "error_message": "",
    "created_at": 1700000000.0
  }
]
```

按 `created_at` 倒序排列（最新的在前）。

---

### 3.4 暂停任务

```
POST /api/download/{task_id}/pause
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

**响应 (200)**
```json
{ "ok": true }
```

**注意**: 仅 `status=downloading` 的任务可暂停。暂停后保留.part文件用于续传。

---

### 3.5 恢复任务

```
POST /api/download/{task_id}/resume
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

**响应 (200)**
```json
{ "ok": true }
```

**注意**: 仅 `status=paused` 的任务可恢复。恢复后重新进入排队等待。

---

### 3.6 取消/删除任务

```
DELETE /api/download/{task_id}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| task_id | string | 任务ID |

**响应 (200)**
```json
{ "ok": true }
```

从内存中移除任务，正在下载的任务会停止。

---

### 3.7 批量下载

```
POST /api/batch
```

**请求（两种模式二选一）**

**模式A：播放列表URL**
```json
{
  "playlist_url": "https://www.youtube.com/playlist?list=xxx",
  "format_id": "",
  "output_format": "mp4"
}
```

**模式B：多个独立URL**
```json
{
  "urls": ["https://url1", "https://url2", "https://url3"],
  "format_id": "",
  "output_format": "mp4"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| playlist_url | string | 模式A必填 | 播放列表URL |
| urls | string[] | 模式B必填 | URL数组 |
| format_id | string | 否 | 格式ID |
| output_format | string | 否 | 输出格式，默认mp4 |

**响应 (200)**
```json
{
  "batch_id": "e5f6g7h8",
  "total": 10,
  "task_ids": ["id1", "id2", ..., "id10"]
}
```

每个URL会创建一个独立的Task，通过WebSocket分别推送进度。

---

### 3.8 格式转换

```
POST /api/convert
```

**请求**
```json
{
  "input_path": "./downloads/video.webm",
  "output_format": "mp4",
  "quality": "medium"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| input_path | string | 是 | — | 已下载文件的绝对/相对路径 |
| output_format | string | 是 | — | 目标格式: mp4/webm/mkv/mp3/aac/flac/wav |
| quality | string | 否 | "medium" | high/medium/low |

**成功响应 (200)**
```json
{
  "success": true,
  "output_path": "./downloads/video.mp4",
  "file_size": 52428800
}
```

**失败响应 (200)**
```json
{
  "success": false,
  "error": "ffmpeg conversion failed..."
}
```

**注意**: 需要系统安装ffmpeg。此接口为同步阻塞操作。

---

### 3.9 获取设置

```
GET /api/settings
```

**响应 (200)**
```json
{
  "download_path": "./downloads",
  "output_format": "mp4",
  "default_quality": "best",
  "max_concurrent": 3,
  "speed_limit": 0
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| download_path | string | 下载保存目录 |
| output_format | string | 默认输出格式 |
| default_quality | string | 默认质量选择: best/1080/720/480/audio |
| max_concurrent | int | 最大同时下载数(1-5) |
| speed_limit | int | 速度限制(bytes/s), 0=不限速 |

---

### 3.10 更新设置

```
PUT /api/settings
```

**请求（部分更新，只传需要改的字段）**
```json
{
  "max_concurrent": 5,
  "speed_limit": 10485760
}
```

**响应 (200)** — 返回完整的最新配置。

---

### 3.11 WebSocket 实时进度推送

```
WS /ws/downloads
```

**连接建立后，服务端主动推送以下消息：**

#### 初始化消息（连接时立即发送一次）
```json
{
  "type": "init",
  "data": [ /* 所有当前任务的完整列表，格式同 GET /api/downloads */ ]
}
```

前端收到init消息后应用全量状态，替代轮询GET接口。

#### 任务更新消息（任意任务状态变化时推送）
```json
{
  "id": "a1b2c3d4",
  "url": "https://...",
  "title": "视频标题",
  "platform": "youtube",
  "thumbnail": "...",
  "duration": 212,
  "format_id": "137+251",
  "output_format": "mp4",
  "filepath": "./downloads/标题.mp4",
  "filesize": 52428800,
  "status": "downloading",
  "progress": 65.3,
  "speed": "5.2MB/s",
  "eta": "00:02:30",
  "error_message": "",
  "created_at": 1700000000.0
}
```

**前端处理逻辑**:
- 收到 `type:init` → 替换整个任务列表
- 收到普通更新 → 根据 `id` 匹配并更新对应任务

#### 心跳保活（可选）
```
客户端发送:   "ping"
服务端回复:   { "type": "pong" }
```

#### 断线重连
- 连接断开时触发 `onclose`
- 建议前端延迟3秒后自动重连
- 重连后会再次收到 `init` 消息，状态完全恢复

---

## 四、TaskStatus 枚举值说明

| status | 含义 | 前端展示建议 |
|--------|------|-------------|
| `queued` | 排队等待中 | 灰色, 显示"排队中..." |
| `downloading` | 正在下载 | 蓝色, 显示动态进度条+速度+ETA |
| `paused` | 已暂停 | 黄色, 按钮[▶恢复] |
| `merging` | 合并音视频中 | 紫色, 显示"处理中..." |
| `completed` | 下载完成 | 绿色, 显示✓ + [打开文件][打开目录] |
| `failed` | 失败 | 红色, 显示错误信息 + [重试][删除] |

---

## 五、业务规则速查

| 规则 | 说明 |
|------|------|
| 并发控制 | 默认最多3个同时下载，由后端Semaphore控制 |
| 断点续传 | yt-dlp原生支持(.part文件)，pause后resume自动续传 |
| 文件命名 | yt-dlp默认模板: `%(title)s.%(ext)s` |
| 播放列表 | 传入playlist_url，后端自动拆分为多个Task |
| 格式推荐 | 后端在parse接口返回 `best_format` 字段，前端可直接使用 |
| 内存存储 | 重启后端后所有任务清零（MVP设计，无持久化） |
