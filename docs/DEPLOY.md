# AI万能视频下载器 - Render 全栈免费部署指南

> 🎉 **0 成本！一个平台！前后端全部部署到 Render！**
>
> 只需 **1 个链接**，任何人打开就能使用你的视频下载器！
>
> **v2.0 更新**：新增抖音专用模块部署说明

---

## ✨ 为什么选择全栈 Render？

| 特性 | 说明 |
|------|------|
| 💰 **完全免费** | ¥0/月，永远不花钱 |
| ♾️ **永久可用** | 只要你不删除，服务一直运行 |
| 🔗 **一个网址** | 前后端同一个地址，简单方便 |
| 🔒 **自动 HTTPS** | 无需手动配置证书 |
| 📱 **全球访问** | 任何人、任何地方都能使用 |
| ⚡ **自动部署** | 推送代码自动更新 |
| 🎬 **抖音支持** | v2.0 新增：无Cookie、无水印、多格式 |

---

## 📋 架构说明（v2.0）

```
                    ┌─────────────────────────────────┐
                    │       Render (唯一服务)           │
                    │                                 │
用户浏览器  ───────►│  https://xxx.onrender.com        │
                    │                                 │
                    │  ├── /          → 前端页面        │
                    │  ├── /api/*     → 后端API         │
                    │  ├── /ws/*      → WebSocket       │
                    │  ├── /assets/*  → 静态资源         │
                    │  └── /proxy-image → 图片代理(抖音) │
                    │                                 │
                    │  FastAPI + Vue3                  │
                    │  ├─ yt-dlp (通用引擎)             │
                    │  └─ douyin_scraper (抖音专用) ⭐   │
                    └─────────────────────────────────┘
```

**只需要 1 个 Render 服务，搞定一切！**

---

## 🚀 开始部署（3 步完成）

### 第1步：推送到 GitHub（2分钟）

#### 1.1 创建 GitHub 仓库

1. 打开 https://github.com/new
2. **Repository name**: `ai-video-downloader`
3. **Description**: `AI Universal Video Downloader - 支持抖音/YouTube/B站等多平台`
4. 选择 **Private**（私有）或 Public（公开）
5. ❌ 不要勾选 README、.gitignore、License
6. 点击 **Create repository**

#### 1.2 推送代码

```bash
cd <你的项目克隆目录>

# 初始化Git仓库（如果还没有）
git init
git add .
git commit -m "Initial commit: v2.0 with Douyin support"

# 添加远程仓库（替换成你的 GitHub 用户名）
git remote add origin https://github.com/你的GitHub用户名/ai-video-downloader.git

# 推送到 GitHub
git push -u origin main
```

---

### 第2步：部署到 Render（3分钟）

#### 2.1 注册 Render 账号

1. 打开 https://dashboard.render.com/register
2. 点击 **Continue with GitHub**
3. 授权登录（新用户获得 $200 免费额度）

#### 2.2 创建 Web Service

1. 登录后点击 **New +** 按钮
2. 选择 **Web Service**

#### 2.3 连接 GitHub 仓库

1. 点击 **Connect an existing repository**
2. 搜索并选择 `ai-video-downloader`
3. 点击 **Connect**

#### 2.4 配置部署参数

Render 会自动检测到 `render.yaml` 配置文件！

确认以下设置：

| 字段 | 值 |
|------|-----|
| **Name** | `ai-video-downloader` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build` |
| **Start Command** | `cd backend && python main.py --build-frontend` |
| **Instance Type** | **Free** (免费版) |

#### 2.5 确认环境变量 ⭐ 抖音相关配置

点击 **Advanced** 展开：

**基础配置**：
```
PORT = 9000
PYTHON_VERSION = 3.11.0
NODE_VERSION = 20
DOWNLOAD_PATH = /opt/render/project/downloads
```

**抖音模块特殊配置**（可选）：
```
# SSL证书验证（生产环境建议开启）
DOUYIN_VERIFY_SSL = true

# 解析超时时间（秒）
DOUYIN_TIMEOUT = 30
```

> **注意**：抖音模块不需要任何API Key或Cookie，开箱即用！

#### 2.6 确认磁盘存储（可选）

勾选 **Disk**：
- Name: `downloads`
- Mount Path: `/opt/render/project/downloads`
- Size: 1 GB

> 用于保存下载的视频文件（重启后保留）

#### 2.7 点击 Deploy

点击底部的 **Create Web Service** 按钮

等待 3-5 分钟构建...

✅ **成功后你会得到：**
```
https://ai-video-downloader-xxxx.onrender.com
```

**这就是你的专属网址！分享给任何人都能用！🎉**

---

### 第3步：测试验证（1分钟）⭐ 含抖音测试

1. 打开你获得的 Render 地址
2. 应该看到完整的视频下载器界面
3. 测试 YouTube/B站 链接（通用功能）
4. **测试抖音链接**（v2.0新功能）：
   ```
   # 示例抖音链接
   https://www.douyin.com/video/7640844002783271851
   https://v.douyin.com/i2KQBE8c/
   ```
5. 点击解析 → 应看到：
   - 平台标识：douyin（青色标签）
   - 封面图片正常显示
   - 格式选项：无水印高清 / 有水印高清 / 仅音频
6. 选择"无水印高清" → 点击下载 → 完美运行！

---

## 🔧 高级配置（可选）

### 绑定自定义域名

1. 打开 Render 项目 → **Settings** → **Custom Domains**
2. 输入域名：`videoforge.yourdomain.com`
3. 按提示添加 DNS 记录：
   ```
   A 记录 → 指向 Render 提供的 IP 地址
   ```
4. 等待 DNS 生效（几分钟）

### 保持在线（防止休眠）

Render 免费版会在 **15 分钟无请求后休眠**。

**免费保活方案：**

1. 注册 [UptimeRobot](https://uptimerobot.com)（完全免费）
2. 添加监控：
   - **Type**: HTTP(s)
   - **URL**: `https://你的地址.onrender.com/api/health`
   - **Interval**: 5 minutes
3. 每 5 分钟自动 ping 一次，防止休眠

### 更新代码

```bash
# 本地修改后
git add .
git commit -m "更新内容"
git push
# Render 会自动重新部署！
```

---

## 🎬 抖音模块部署注意事项 ⭐

### 为什么抖音需要特殊处理？

抖音视频解析与YouTube/B站等平台有本质区别：

| 特性 | YouTube/B站 (yt-dlp) | 抖音 (专用模块) |
|------|----------------------|-----------------|
| Cookie需求 | 可选（部分功能） | ❌ 完全不需要 |
| API接口 | 公开标准API | iesdouyin.com公开页面 |
| 去水印方式 | 直接获取 | URL替换 playwm→play |
| 多格式支持 | yt-dlp原生 | 自定义实现 |
| 部署依赖 | yt-dlp包 | httpx库（已包含）|

### 部署前检查清单

确保以下文件已提交到GitHub：

```bash
✅ backend/services/douyin_scraper.py    # 抖音核心模块
✅ backend/services/downloader.py          # 主解析引擎（含路由逻辑）
✅ backend/main.py                         # FastAPI入口（含proxy-image路由）
✅ frontend/src/components/download/       # Vue组件（已适配抖音）
```

### 生产环境优化建议

#### 1. SSL证书验证

开发环境默认关闭SSL验证以方便调试，但生产环境建议开启：

```python
# douyin_scraper.py 中修改
async with httpx.AsyncClient(
    timeout=20,
    follow_redirects=True,
    headers=mobile_headers,
    verify=True  # 生产环境改为 True
) as client:
```

或者通过环境变量控制：
```python
import os
VERIFY_SSL = os.getenv('DOUYIN_VERIFY_SSL', 'false').lower() == 'true'
```

#### 2. 超时设置

抖音解析可能耗时较长，建议设置合理的超时时间：

```bash
# Render 环境变量
DOUYIN_TIMEOUT=30  # 30秒超时
```

#### 3. 错误监控

建议在Render中查看日志，关注以下关键词：

```
[DouyinScraper]  # 抖音模块日志
所有解析方法均失败  # 解析失败提示
status_code=11110 # API错误码
```

#### 4. 图片代理性能

抖音封面图通过 `/api/proxy-image` 代理访问，确保：

- 前端组件使用代理URL而非原始CDN链接
- Render实例有足够的带宽处理图片请求
- 考虑添加缓存机制（未来版本优化）

---

## 📊 免费额度详情

| 项目 | 限制 |
|------|------|
| **价格** | $0/月 ✅ |
| **实例数** | 1 个 |
| **内存** | 512 MB RAM |
| **CPU** | 共享 |
| **带宽** | 100 GB/月（出站）|
| **构建时间** | 45 分钟/次 |
| **磁盘** | 1 GB 免费 |
| **休眠时间** | 15 分钟无请求 |
| **运行时长** | 750 小时/月 ≈ 31 天连续 |

> 💡 个人项目**完全够用**！100GB 带宽可以下载约 500-1000 个视频。

---

## 🐛 问题排查

### Q1: 页面显示空白？

**检查方法：**
1. 访问 `https://xxx.onrender.com/api/health`
2. 如果返回 `{"status":"ok"}` → 后端正常，前端构建可能失败
3. 查看 Render Logs：项目页面 → **Logs** 标签

**常见原因：**
- Node.js 版本不兼容 → 确保 `NODE_VERSION=20`
- npm install 失败 → 检查 package.json 是否正确

### Q2: YouTube/B站解析正常，但抖音解析失败？ ⭐

**检查步骤：**

1. **查看日志**：
   ```
   Render Dashboard → Logs → 搜索 "DouyinScraper"
   ```

2. **确认网络连通性**：
   ```bash
   # 在本地测试是否能访问抖音域名
   curl -I https://www.iesdouyin.com
   ```

3. **常见错误及解决方案**：

   | 错误信息 | 原因 | 解决方案 |
   |----------|------|----------|
   | `status_code=11110` | API签名限制 | 自动降级到分享页面方法 |
   | `Share page returned status 403` | IP被限制 | 使用代理或等待一段时间 |
   | `所有解析方法均失败` | 视频不可用 | 检查视频是否已被删除 |
   | `Short URL resolution failed` | 短链接失效 | 使用完整douyin.com链接 |

4. **测试命令**（在Render Shell中执行）：
   ```bash
   cd /opt/render/project/src
   python -c "
   from services.douyin_scraper import is_douyin_url, parse_douyin_video
   import asyncio
   result = asyncio.run(parse_douyin_video('https://www.douyin.com/video/7640844002783271851'))
   print(result)
   "
   ```

### Q3: WebSocket 连接不上？

**正常现象：** 全栈部署下 WebSocket 和 API 在同一端口。

检查前端代码中 WebSocket 地址是否正确（应使用相对路径 `/ws/downloads`）。

### Q4: 下载的视频找不到？

**原因：** 未启用持久化磁盘

**解决：** 在 Render 设置中启用 Disk（上面第2.6步已说明）

### Q5: 抖音封面图无法显示？ ⭐

**原因分析**：
1. 未使用图片代理接口
2. CDN跨域限制
3. 图片URL编码错误

**解决方案**：
```vue
<!-- 正确用法 -->
<img :src="`/api/proxy-image?url=${encodeURIComponent(thumbnailUrl)}`" />

<!-- 错误用法 -->
<img :src="thumbnailUrl" />  <!-- 会遇到跨域问题 -->
```

### Q6: 首次访问很慢？

**正常：** 这是"冷启动"现象

- 后端休眠后首次访问需 10-30 秒唤醒
- 之后访问很快（< 1秒）
- 用 UptimeRobot 保活可避免

### Q7: 如何查看实时日志？ ⭐ 抖音调试

1. 打开 https://dashboard.render.com
2. 点击你的服务名称
3. 点击 **Logs** 标签
4. 过滤关键词：
   - `[DouyinScraper]` — 抖音模块日志
   - `error` / `failed` — 错误信息
   - `Success via` — 成功的方法

**关键日志示例**：
```
[Parser] Using specialized Douyin scraper (no Cookie required)
[DouyinScraper] Trying method 1b: Share Page...
[DouyinScraper] ✓ Success via Share Page! Title: xxx, Formats: 3
```

如果看到以上日志，说明抖音模块工作正常！

---

## 🎯 部署前清单

### 必须项
- [x] GitHub 账号
- [ ] 代码已推送到 GitHub（含douyin_scraper.py）
- [ ] Render 账号（GitHub 登录即可）
- [ ] 测试用的多平台视频链接：
  - [ ] YouTube链接
  - [ ] B站链接
  - [ ] **抖音链接** ⭐（重点测试）

### 可选项
- [ ] UptimeRobot账号（保活用）
- [ ] 自定义域名（如需绑定）

**预计总时间：5-10 分钟**

---

## 🔄 本地开发 vs 云端部署

| 环境 | 启动方式 | API 地址 | 抖音支持 |
|------|---------|---------|----------|
| **本地开发** | 双击 `一键启动.bat` | http://127.0.0.1:9000 | ✅ 完整支持 |
| **云端部署** | 自动（推送代码） | https://xxx.onrender.com | ✅ 完整支持 |

本地开发和云端部署**完全兼容**，无需修改任何代码！

---

## 📞 需要帮助？

- **Render 文档**: https://render.com/docs
- **Render 状态页**: https://status.render.com
- **GitHub Issues**: 在你的仓库提 Issue
- **技术文档**: [技术实现文档.md](./技术实现文档.md)
- **API文档**: [后端API接口文档.md](./后端API接口文档.md)

---

## 🎉 完成！（v2.0）

恭喜！你现在拥有了一个：

- ✅ **完全免费**的全栈应用
- ✅ **永久可用**的公开网址
- ✅ **一键部署**（推送代码即更新）
- ✅ **1700+ 平台**视频下载支持（通用引擎）
- ✅ **抖音专用**无Cookie、无水印下载 ⭐
- ✅ **多种格式**选择（无水印/有水印/音频）⭐
- ✅ **视频封面**自动提取和显示 ⭐
- ✅ **中英文双语**界面
- ✅ **Edge 浏览器**最佳适配

---

## 📈 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0 | 2026-05 | 初始部署指南，基础功能 |
| v2.0 | 2026-05-23 | 新增抖音模块部署说明、问题排查、生产环境优化 |

---

**你的专属链接：**
```
https://ai-video-downloader-xxxx.onrender.com
```

**立即分享给朋友，让他们体验抖音无水印下载的魔力！🚀**
