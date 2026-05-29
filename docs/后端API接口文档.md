# AI万能视频下载器 — 后端API接口文档

> 前端开发人员专用 | v2.0版本（新增抖音专用模块）| 基础地址: `http://127.0.0.1:9000`

---

## 一、基础信息

| 项目 | 说明 |
|------|------|
| 协议 | HTTP + WebSocket |
| 数据格式 | JSON (Content-Type: application/json) |
| 编码 | UTF-8 |
| 跨域 | 全部允许 (CORS: *) |

**WebSocket地址**: `ws://127.0.0.1:9000/ws/downloads`

**v2.0 新增特性**:
- ✅ 抖音视频自动识别与专用解析
- ✅ 无Cookie下载（用户无需任何操作）
- ✅ 无水印视频获取
- ✅ 多格式支持（无水印/有水印/音频）
- ✅ 视频封面提取
- ✅ 图片代理接口（解决跨域）

---

## 二、接口列表总览

| # | 方法 | 路径 | 说明 | 抖音支持 |
|---|------|------|------|----------|
| 1 | POST | `/api/parse` | 解析视频URL | ✅ 自动路由 |
| 2 | GET | `/api/proxy-image` | 图片代理 | ✅ 抖音封面 |
| 3 | POST | `/api/download` | 创建下载任务 | ✅ 多格式 |
| 4 | GET | `/api/downloads` | 获取所有任务 | — |
| 5 | POST | `/api/download/{id}/pause` | 暂停任务 | — |
| 6 | POST | `/api/download/{id}/resume` | 恢复任务 | — |
| 7 | DELETE | `/api/download/{id}` | 取消/删除任务 | — |
| 8 | POST | `/api/batch` | 批量下载 | ✅ 支持混合 |
| 9 | POST | `/api/convert` | 格式转换 | — |
| 10 | GET | `/api/settings` | 获取设置 | — |
| 11 | PUT | `/api/settings` | 更新设置 | — |
| WS | — | `/ws/downloads` | 实时进度推送 | — |

---

## 三、接口详情

### 3.1 解析视频URL ⭐

```
POST /api/parse
```

**请求**
```json
{
  "url": "https://www.douyin.com/video/7640844002783271851"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 视频URL（支持所有平台，自动识别）|

**支持的URL格式**:
```
✅ YouTube: https://www.youtube.com/watch?v=xxx
✅ Bilibili: https://www.bilibili.com/video/BVxxx
✅ 抖音标准: https://www.douyin.com/video/7640844002783271851
✅ 抖音精选: https://www.douyin.com/jingxuan?modal_id=xxx
✅ 抖音笔记: https://www.douyin.com/note/xxx
✅ 抖音短链: https://v.douyin.com/i2KQBE8c/
✅ TikTok: https://www.tiktok.com/@user/video/xxx
✅ Instagram: https://www.instagram.com/p/xxx
✅ Twitter/X: https://twitter.com/user/status/xxx
```

#### 成功响应 - YouTube/B站等通用平台 (200)

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

#### 成功响应 - 抖音专用模块 (200) ⭐

```json
{
  "title": "超燃混剪！2024最火BGM合集 #音乐推荐 #热门",
  "thumbnail": "https://p3-pc-sign.douyincdn.com/obj/tos-cn-p-00xxx/xxx.jpg",
  "duration": 45,
  "platform": "douyin",
  "uploader": "音乐达人小王",
  "formats": [
    {
      "format_id": "best",
      "ext": "mp4",
      "resolution": "1080p",
      "filesize": 0,
      "vcodec": "h264",
      "acodec": "aac",
      "tbr": 0,
      "url": "https://v26-web.douyinvod.com/play/xxx.mp4",
      "watermarked": false
    },
    {
      "format_id": "wm_1080p",
      "ext": "mp4",
      "resolution": "1080p (Watermark)",
      "filesize": 0,
      "vcodec": "h264",
      "acodec": "aac",
      "tbr": 0,
      "url": "https://v26-web.douyinvod.com/playwm/xxx.mp4",
      "watermarked": true
    },
    {
      "format_id": "audio",
      "ext": "mp3",
      "resolution": "Audio Only",
      "filesize": 0,
      "vcodec": "none",
      "acodec": "aac",
      "tbr": 128,
      "url": "https://v26-web.douyinvod.com/music/xxx.mp3",
      "watermarked": false
    }
  ],
  "is_playlist": false,
  "playlist_count": null,
  "entry_count": 0,
  "entries": [],
  "best_format": {
    "format_id": "best",
    "ext": "mp4",
    "resolution": "1080p",
    "note": "无水印高清"
  },
  "_direct_url": "https://v26-web.douyinvod.com/play/xxx.mp4",
  "_audio_url": "https://v26-web.douyinvod.com/music/xxx.mp3"
}
```

**抖音响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| formats[].watermarked | boolean | 是否带水印（false=无水印）|
| formats[].url | string | 直接下载地址（可直接用于下载）|
| _direct_url | string | 最佳无水印视频地址（内部字段）|
| _audio_url | string | 音频地址（内部字段）|
| thumbnail | string | 封面图地址（需通过proxy-image代理访问）|
| platform | string | 固定为 "douyin" |

**错误响应 (400)**
```json
{ "detail": "不支持该平台 / URL无效 / 网络超时 / 所有解析方法均失败" }
```

**注意**:
1. 此接口可能耗时较长（需请求目标网站），前端应显示loading状态
2. 抖音链接会自动走专用解析模块，无需用户提供Cookie
3. 建议前端根据 `platform` 字段显示不同UI样式

---

### 3.2 图片代理接口 ⭐

```
GET /api/proxy-image?url=<encoded_url>
```

**用途**: 解决跨域问题，代理请求图片资源（主要用于抖音封面图）

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 需要代理的图片URL（需URL编码）|

**示例请求**
```
GET /api/proxy-image?url=https%3A%2F%2Fp3-pc-sign.douyincdn.com%2Fobj%2Ftos-cn-p-00xxx%2Fxxx.jpg
```

**成功响应 (200)**
- Content-Type: image/jpeg 或 image/png
- Body: 图片二进制数据

**错误情况**
- 404: 图片不存在或无法访问
- 500: 服务器错误

**前端使用方式**
```vue
<template>
  <img :src="`/api/proxy-image?url=${encodeURIComponent(thumbnailUrl)}`" />
</template>
```

---

### 3.3 创建下载任务

```
POST /api/download
```

**请求**
```json
{
  "url": "https://www.douyin.com/video/7640844002783271851",
  "format_id": "best",
  "output_format": "mp4"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| url | string | 是 | — | 视频URL |
| format_id | string | 否 | "" | 格式ID（抖音：best/wm_1080p/audio）|
| output_format | string | 否 | "mp4" | 输出容器格式: mp4/webm/mkv/mp3/aac/flac/wav |

**抖音格式ID说明**:
- `best`: 无水印高清（推荐）
- `wm_1080p`: 有水印高清（备用）
- `audio`: 仅音频MP3

**响应 (200)**
```json
{
  "task_id": "a1b2c3d4",
  "status": "queued"
}
```

---

### 3.4 获取所有任务

```
GET /api/downloads?status=downloading
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 过滤状态: queued/downloading/paused/completed/failed |

**成功响应 (200)**
```json
[
  {
    "id": "a1b2c3d4",
    "url": "https://www.douyin.com/video/7640844002783271851",
    "title": "超燃混剪！2024最火BGM合集",
    "platform": "douyin",
    "thumbnail": "https://p3-pc-sign.douyincdn.com/...",
    "duration": 45,
    "format_id": "best",
    "output_format": "mp4",
    "filepath": "downloads/超燃混剪！2024最火BGM合集.mp4",
    "filesize": 15728640,
    "status": "completed",
    "progress": 100.0,
    "speed": "",
    "eta": "",
    "error_message": "",
    "created_at": 1716585600.123
  }
]
```

**Task对象完整字段定义**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 任务唯一标识符（8位短UUID）|
| url | string | 原始视频URL |
| title | string | 视频标题（解析后更新）|
| platform | string | 平台标识: youtube/bilibili/douyin/tiktok/instagram/twitter/kuaishou |
| thumbnail | string | 封面图URL（需通过proxy-image代理）|
| duration | int | 视频时长（秒）|
| format_id | string | 选中的格式ID |
| output_format | string | 输出容器格式 |
| filepath | string | 本地文件路径（完成后填充）|
| filesize | int | 文件大小（字节，完成后填充）|
| status | string | 任务状态: queued/downloading/paused/merging/completed/failed |
| progress | float | 进度百分比 (0-100) |
| speed | string | 下载速度字符串（如 "2.50MiB/s"）|
| eta | string | 预计剩余时间（如 "00:05"）|
| error_message | string | 错误信息（失败时填充）|
| created_at | float | 创建时间戳 |

---

### 3.5 暂停任务

```
POST /api/download/{task_id}/pause
```

**响应 (200)**
```json
{ "ok": true }
```

**错误响应**
```json
{ "error": "任务不可暂停" }
```

**注意**: 抖音下载同样支持暂停/恢复功能

---

### 3.6 恢复任务

```
POST /api/download/{task_id}/resume
```

**响应 (200)**
```json
{ "ok": true }
```

**错误响应**
```json
{ "error": "任务不可恢复" }
```

---

### 3.7 取消/删除任务

```
DELETE /api/download/{task_id}
```

**响应 (200)**
```json
{ "ok": true }
```

**注意**: 正在下载的任务会被立即终止

---

### 3.8 批量下载

```
POST /api/batch
```

**请求**
```json
{
  "urls": [
    "https://www.youtube.com/watch?v=xxx",
    "https://www.douyin.com/video/7640844002783271851",
    "https://www.bilibili.com/video/BVxxx"
  ],
  "format_id": "",
  "output_format": "mp4"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| urls | string[] | 是 | URL列表（支持多平台混合）|
| entries | string[] | 否 | 从播放列表解析出的条目URL列表 |
| format_id | string | 否 | 统一格式ID |
| output_format | string | 否 | 统一输出格式 |

**响应 (200)**
```json
{
  "batch_id": "e5f6g7h8",
  "total": 3,
  "task_ids": ["a1b2c3d4", "b2c3d4e5", "c3d4e5f6"]
}
```

**特殊说明**: 批量下载支持混合平台（YouTube+B站+抖音），每个链接会自动路由到对应的解析引擎。

---

### 3.9 格式转换

```
POST /api/convert
```

**请求**
```json
{
  "input_path": "downloads/Rick Astley - Never Gonna Give You Up.mp4",
  "output_format": "mp3",
  "quality": "medium"
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| input_path | string | 是 | — | 输入文件路径 |
| output_format | string | 是 | — | 目标格式: mp4/webm/mkv/mp3/aac/flac/wav |
| quality | string | 否 | "medium" | 质量: high/medium/low |

**成功响应 (200)**
```json
{
  "success": true,
  "output_path": "downloads/Rick Astley - Never Gonna Give You Up.mp3",
  "file_size": 2097152
}
```

**错误响应 (500)**
```json
{
  "success": false,
  "error": "ffmpeg conversion failed..."
}
```

---

### 3.10 获取设置

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

---

### 3.11 更新设置

```
PUT /api/settings
```

**请求**
```json
{
  "max_concurrent": 5,
  "speed_limit": 10485760
}
```

**响应 (200)**: 返回完整的设置对象

**可更新的字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| download_path | string | 下载目录路径 |
| output_format | string | 默认输出格式 |
| default_quality | string | 默认画质: best/worst/audio |
| max_concurrent | int | 最大并发下载数（1-10）|
| speed_limit | int | 限速（bytes/s），0=不限速 |

---

## 四、WebSocket实时推送

### 4.1 连接建立

```
WS ws://127.0.0.1:9000/ws/downloads
```

**连接后立即收到初始化消息**:
```json
{
  "type": "init",
  "data": [
    // 当前所有任务的完整列表（同 GET /api/downloads 返回格式）
  ]
}
```

### 4.2 任务状态变更消息

当任何任务的状态发生变化时，服务端会主动推送：

```json
{
  "type": "task_update",
  "data": {
    "id": "a1b2c3d4",
    "url": "https://www.douyin.com/video/7640844002783271851",
    "title": "超燃混剪！2024最火BGM合集",
    "platform": "douyin",
    "status": "downloading",
    "progress": 45.6,
    "speed": "2.50MiB/s",
    "eta": "00:12",
    // ... 其他字段同 Task 对象
  }
}
```

**消息类型**:
- `init`: 初始化同步（连接时发送一次）
- `task_update`: 任务状态变更（任意字段变化时发送）

### 4.3 心跳保活

客户端可以发送：
```json
"ping"
```

服务端回复：
```json
{"type": "pong"}
```

### 4.4 自动重连策略

| 场景 | 处理方式 |
|------|----------|
| 网络断开 | 自动重连（最多10次，指数退避）|
| 服务端重启 | 重连后重新接收 init 消息同步状态 |
| 长时间无操作 | 心跳保活（建议30秒间隔）|

---

## 五、错误处理规范

### 5.1 HTTP状态码

| 状态码 | 含义 | 示例场景 |
|--------|------|----------|
| 200 | 成功 | 请求正常处理 |
| 400 | 请求参数错误 | URL无效、缺少必填字段 |
| 404 | 资源不存在 | 任务ID不存在 |
| 500 | 服务器内部错误 | 解析失败、下载失败、转换失败 |

### 5.2 错误响应格式

```json
{
  "detail": "人类可读的错误信息"
}
```

**常见错误信息**:
- `"不支持该平台"` — URL无法识别为已知平台
- `"URL无效"` — URL格式不正确
- `"网络超时"` — 无法连接到目标网站
- `"所有解析方法均失败"` — 抖音专用模块所有方法都失败
- `"任务不可暂停"` — 任务当前不在下载中状态
- `"任务不可恢复"` — 任务当前不是暂停状态

### 5.3 抖音特有错误及解决方案

| 错误信息 | 可能原因 | 建议 |
|----------|----------|------|
| `iesdouxin_API: status_code=11110` | API签名验证失败 | 自动降级到分享页面方法 |
| `iesdouyin_SharePage: Share page returned status xxx` | 分享页面被限制 | 自动尝试其他备用方法 |
| `所有解析方法均失败` | 视频已被删除/设为私密 | 提示用户检查视频是否可用 |

---

## 六、前端集成指南

### 6.1 快速开始（Vue 3 + Pinia）

```javascript
// stores/download.js
import { defineStore } from 'pinia'

export const useDownloadStore = defineStore('download', () => {
  const tasks = ref([])
  const parseResult = ref(null)
  const isParsing = ref(false)

  async function parseUrl(url) {
    isParsing.value = true
    try {
      const res = await fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      if (!res.ok) throw new Error((await res.json()).detail)
      parseResult.value = await res.json()
    } finally {
      isParsing.value = false
    }
  }

  async function startDownload(options) {
    const res = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: options.url,
        format_id: options.formatId || '',
        output_format: options.outputFormat || 'mp4'
      })
    })
    return await res.json() // { task_id, status }
  }

  function connectWebSocket() {
    const ws = new WebSocket(`ws://${location.host}/ws/downloads`)
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'init') tasks.value = msg.data
      else if (msg.type === 'task_update') {
        const idx = tasks.value.findIndex(t => t.id === msg.data.id)
        if (idx !== -1) tasks.value[idx] = msg.data
        else tasks.value.push(msg.data)
      }
    }
  }

  return { tasks, parseResult, isParsing, parseUrl, startDownload, connectWebSocket }
})
```

### 6.2 抖音视频处理最佳实践

```vue
<template>
  <!-- URL输入框 -->
  <input v-model="url" placeholder="支持 YouTube、B站、抖音、TikTok 等" />

  <!-- 解析按钮 -->
  <button @click="handleParse" :disabled="store.isParsing">
    {{ store.isParsing ? '解析中...' : '解析视频' }}
  </button>

  <!-- 视频预览（包含抖音特殊处理）-->
  <VideoPreview v-if="store.parseResult" :result="store.parseResult" />
</template>

<script setup>
import { useDownloadStore } from '@/stores/download'
const store = useDownloadStore()

async function handleParse() {
  await store.parseUrl(url.value)
  // 抖音视频会自动返回：
  // - platform: 'douyin'
  // - formats: [无水印, 有水印, 音频]
  // - thumbnail: 封面URL（需代理访问）
}
</script>
```

### 6.3 图片代理使用示例

```vue
<template>
  <div class="video-preview">
    <!-- 使用图片代理显示封面（解决跨域问题）-->
    <img
      :src="`/api/proxy-image?url=${encodeURIComponent(result.thumbnail)}`"
      alt="视频封面"
      class="w-full h-auto rounded-lg"
    />

    <!-- 平台标签（抖音显示青色）-->
    <span :class="getPlatformClass(result.platform)">
      {{ result.platform.toUpperCase() }}
    </span>

    <!-- 格式选择器（展示抖音多格式）-->
    <div class="format-list">
      <button
        v-for="fmt in result.formats"
        :key="fmt.format_id"
        @click="selectedFormat = fmt"
        :class="{ active: selectedFormat?.format_id === fmt.format_id }"
      >
        {{ fmt.resolution }} ({{ fmt.ext }})
        <!-- 抖音特有：水印标识 -->
        <span v-if="fmt.watermarked === false" class="text-green-500">✓ 无水印</span>
        <span v-else-if="fmt.watermarked" class="text-orange-500">⚠ 有水印</span>
      </button>
    </div>

    <!-- 下载按钮 -->
    <button @click="handleDownload">开始下载</button>
  </div>
</template>

<script setup>
function getPlatformClass(platform) {
  const classes = {
    youtube: 'bg-red-100 text-red-600',
    bilibili: 'bg-pink-100 text-pink-600',
    douyin: 'bg-cyan-100 text-cyan-600',  // 抖音专属颜色
    tiktok: 'bg-black text-white',
    instagram: 'bg-purple-100 text-purple-600',
  }
  return classes[platform] || 'bg-gray-100 text-gray-600'
}
</script>
```

### 6.4 批量下载示例

```javascript
async function batchDownload(urls) {
  const res = await fetch('/api/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      urls,  // 可以是混合平台的URL列表
      output_format: 'mp4'
    })
  })

  const { task_ids } = await res.json()
  console.log(`已创建 ${task_ids.length} 个下载任务`)
}
```

---

## 七、性能优化建议

### 7.1 前端优化

1. **防抖处理**: URL输入框添加300ms防抖
2. **懒加载**: 任务列表虚拟滚动（超过100个任务时）
3. **缓存策略**: 已完成的任务可以本地缓存
4. **图片优化**: 封面图使用 lazy loading 和缩略图

### 7.2 后端优化

1. **并发控制**: 默认最大3个并发下载（可通过设置调整）
2. **超时设置**: 解析接口60秒超时，避免长时间阻塞
3. **降级机制**: 抖音解析失败自动降级到yt-dlp（需要Cookie）

### 7.3 抖音专项优化

1. **多方法降级**: 5种解析方法依次尝试，提高成功率
2. **短链接解析**: 自动解析 v.douyin.com 短链接
3. **移动端UA**: 使用iPhone UA模拟手机浏览器，提高成功率
4. **SSL忽略**: 开发环境忽略SSL证书验证（生产环境需配置）

---

## 八、测试用例

### 8.1 抖音解析测试

```bash
# 测试1: 标准格式
curl -X POST http://127.0.0.1:9000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.douyin.com/video/7640844002783271851"}'

# 测试2: 短链接
curl -X POST http://127.0.0.1:9000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://v.douyin.com/i2KQBE8c/"}'

# 测试3: 精选页格式
curl -X POST http://127.0.0.1:9000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.douyin.com/jingxuan?modal_id=7640844002783271851"}'
```

### 8.2 下载测试

```bash
# 下载无水印版本
curl -X POST http://127.0.0.1:9000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url":"https://www.douyin.com/video/7640844002783271851",
    "format_id":"best",
    "output_format":"mp4"
  }'

# 下载仅音频
curl -X POST http://127.0.0.1:9000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url":"https://www.douyin.com/video/7640844002783271851",
    "format_id":"audio",
    "output_format":"mp3"
  }'
```

### 8.3 图片代理测试

```bash
# 测试图片代理
curl "http://127.0.0.1:9000/api/proxy-image?url=https%3A%2F%2Fp3-pc-sign.douyincdn.com%2Ftest.jpg" \
  --output test_image.jpg
```

---

## 九、版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0 | 2026-05 | 初始版本，基础API文档 |
| v2.0 | 2026-05-23 | 新增抖音专用模块文档、图片代理、多格式支持 |

---

**文档结束**

> 如需了解技术实现细节，请查看 [技术实现文档](./技术实现文档.md)
> 如需快速启动应用，请查看 [快速启动说明](./快速启动说明.md)
