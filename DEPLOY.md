# VideoForge Pro - 完全免费云部署指南

> 🎉 **0 成本！永久免费！域名永远可用！**
>
> 使用 **Render + Vercel** 组合部署，让任何人都能通过网址访问你的视频下载器！

---

## ✨ 为什么选择这个方案？

| 特性 | 说明 |
|------|------|
| 💰 **完全免费** | ¥0/月，永远不花钱 |
| ♾️ **永久可用** | 只要你不主动删除，服务一直运行 |
| 🔗 **固定域名** | 部署后获得永久访问链接 |
| 🔒 **自动 HTTPS** | 无需手动配置证书 |
| 📱 **全球访问** | 任何人、任何地方都能使用 |
| ⚡ **自动部署** | 推送代码自动更新 |

---

## 📋 部署架构

```
用户浏览器
    ↓ 访问
┌─────────────────────────┐
│   Vercel (前端)          │ ← 免费托管静态文件
│   your-app.vercel.app    │
│         ↓                │
│   /api/* → 代理转发       │
│   /ws/*  → WebSocket代理  │
└─────────────────────────┘
            ↓
┌─────────────────────────┐
│   Render (后端)           │ ← 免费托管 Python API
│   your-api.onrender.com  │
│                         │
│   FastAPI + yt-dlp       │
└─────────────────────────┘
```

---

## 🚀 开始部署（5 步完成）

### 第1步：推送到 GitHub（2分钟）

#### 1.1 在 GitHub 创建新仓库

1. 打开 https://github.com/new
2. **Repository name**: `video-forge-pro`（或你喜欢的名字）
3. **Description**: `AI Universal Video Downloader - 支持多平台视频下载`
4. **选择 Private**（私有，只有你能看到代码）或 Public（公开）
5. ❌ **不要勾选**：Add a README file
6. ❌ **不要勾选**：Add .gitignore
7. ❌ **不要勾选**：Choose a license
8. 点击 **Create repository**

#### 1.2 执行推送命令

在项目目录打开终端（或 PowerShell），执行：

```bash
cd "d:\vibe coding项目\AI万能视频下载器"

# 添加远程仓库（替换成你的 GitHub 用户名）
git remote add origin https://github.com/你的GitHub用户名/video-forge-pro.git

# 推送到 GitHub
git push -u origin main
```

✅ 完成后你的代码就在 GitHub 上了！

---

### 第2步：部署后端到 Render（3分钟）

#### 2.1 注册 Render 账号

1. 打开 https://dashboard.render.com/register
2. 点击 **Continue with GitHub**（推荐）
3. 授权 GitHub 账号登录
4. 新用户会获得 **$200 的免费额度**（足够用很久）

#### 2.2 创建 Web Service

1. 登录后点击 **New +** 按钮
2. 选择 **Web Service**

![创建Web Service](https://render.com/images/docs/web-service-new.png)

#### 2.3 连接 GitHub 仓库

1. 点击 **Connect an existing repository**
2. 搜索并选择 `video-forge-pro`
3. 点击 **Connect**

#### 2.4 配置构建参数

填写以下信息：

| 字段 | 值 |
|------|-----|
| **Name** | `video-forge-backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Instance Type** | Free（免费版）|

#### 2.5 配置环境变量（重要！）

点击 **Advanced** 展开更多选项：

1. 找到 **Environment Variables**
2. 添加以下变量：

```
PORT = 8976
PYTHONUNBUFFERED = 1
DOWNLOAD_PATH = /opt/render/project/downloads
```

3. **磁盘持久化**（可选，用于保存下载文件）：
   - 勾选 **Disk**
   - Name: `downloads`
   - Mount Path: `/opt/render/project/downloads`
   - Size: 1 GB（免费额度内）

#### 2.6 设置工作目录

点击 **Advanced** → **Working Directory**:
```
backend
```

这告诉 Render 从 `backend` 目录启动应用。

#### 2.7 点击 Deploy

点击底部的 **Create Web Service** 按钮

等待 2-3 分钟构建完成...

✅ **成功后你会看到类似这样的地址：**
```
https://video-forge-backend-xxxx.onrender.com
```

**📝 复制这个地址，下一步要用！**

---

### 第3步：部署前端到 Vercel（2分钟）

#### 3.1 注册 Vercel 账号

1. 打开 https://vercel.com/signup
2. 使用 **GitHub** 或 Google 账号注册
3. 新用户获得无限免费额度

#### 3.2 导入项目

1. 登录后点击 **Add New...** → **Project**
2. 选择 **Import Git Repository**
3. 浏览并选择 `video-forge-pro` 仓库
4. 点击 **Import**

#### 3.3 配置前端项目

填写以下配置：

| 字段 | 值 |
|------|-----|
| **Framework Preset** | Other |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

#### 3.4 配置环境变量（关键！）

点击 **Environment Variables**，添加：

```
VITE_API_URL = https://video-forge-backend-xxxx.onrender.com
```

> ⚠️ 把 `video-forge-backend-xxxx.onrender.com` 替换成你第2步得到的 **Render 后端地址**

#### 3.5 配置重写规则（让 API 请求转发到后端）

Vercel 会自动读取项目根目录的 `vercel.json` 配置。

如果需要修改，在 Vercel 项目设置中：
1. 点击 **Settings** → **Functions**
2. 或者直接在项目中修改 `vercel.json` 文件：
```json
{
  "version": 2,
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-render-url.onrender.com/api/$1"
    },
    {
      "source": "/ws/(.*)",
      "destination": "wss://your-render-url.onrender.com/ws/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/$1"
    }
  ]
}
```

#### 3.6 点击 Deploy

点击 **Deploy** 按钮

等待 1-2 分钟...

✅ **成功后你会得到最终的前端地址：**
```
https://video-forge-pro.vercel.app
```

---

### 第4步：测试验证（1分钟）

1. **打开你获得的 Vercel 地址**
2. 应该能看到完整的视频下载器界面
3. 粘贴一个 YouTube/B站 视频链接测试
4. 点击解析按钮，应该能获取到视频信息

#### 如果遇到问题：

- **页面空白**：检查浏览器控制台是否有错误
- **API 报错**：确认 Render 后端正在运行（访问 `/api/health`）
- **WebSocket 失败**：检查 vercel.json 中的 ws 重写规则

---

### 第5步：分享给朋友！（30秒）

把你的 **Vercel 地址** 发送给任何人：

```
https://video-forge-pro.vercel.app
```

他们可以直接在浏览器中使用你的视频下载器！🎉

---

## 🔧 高级配置（可选）

### 绑定自定义域名

#### Vercel 自定义域名：

1. 打开 Vercel 项目 → **Settings** → **Domains**
2. 输入你的域名，如 `videoforge.yourdomain.com`
3. 按提示配置 DNS 记录（通常添加 CNAME）：
   ```
   Type: CNAME
   Name: videoforge (或 @)
   Value: cname.vercel-dns.com
   ```
4. 等待 DNS 生效（几分钟到几小时）

#### Render 自定义域名（可选）：

1. 打开 Render 服务设置 → **Custom Domains**
2. 添加域名如 `api.yourdomain.com`
3. 配置 A 记录指向 Render 提供的 IP

### 自动休眠说明

Render 免费版会在 **15-30 分钟无请求后自动休眠**。

| 行为 | 说明 |
|------|------|
| 休眠时访问 | 显示加载状态（约 10-30 秒唤醒） |
| 有活跃用户 | 保持在线，不会休眠 |
| 唤醒速度 | 通常 10-30 秒 |

**解决方案（如果需要保持在线）：**
1. 使用 [UptimeRobot](https://uptimerobot.com)（免费）每 5 分钟 ping 一次
2. 或升级到 Render 付费版 ($7/月)

### UptimeRobot 保活配置（免费）

1. 注册 https://uptimerobot.com
2. 添加新监控：
   - **Monitor Type**: HTTP(s)
   - **URL**: 你的 Render 后端地址 + `/api/health`
   - **Monitoring Interval**: 5 minutes
3. 这样每 5 分钟会自动访问一次，防止休眠

---

## 📊 免费额度详情

### Render 免费计划

| 项目 | 限制 |
|------|------|
| **价格** | $0/月 |
| **实例数** | 1 个 |
| **内存** | 512 MB RAM |
| **CPU** | 共享 |
| **带宽** | 100 GB/月（出站）|
| **休眠时间** | 15 分钟无请求 |
| **构建时长** | 45 分钟/次 |
| **实例数** | 750 小时/月（约 31 天连续运行）|

### Vercel 免费计划

| 项目 | 限制 |
|------|------|
| **价格** | $0/月 |
| **带宽** | 100 GB/月 |
| **构建次数** | 100 次/月 |
| **Serverless 函数** | 无限 |
| **团队人数** | 1 人 |
| **域名绑定** | 无限 |

> 💡 对于个人项目来说，这些限制**完全够用**！

---

## 🔄 更新部署

当代码有更新时：

1. 本地提交并推送：
   ```bash
   git add .
   git commit -m "更新内容描述"
   git push
   ```

2. **Render 和 Vercel 会自动检测到更新并重新部署！**

无需任何手动操作，3-5 分钟后自动生效。

---

## 🐛 常见问题排查

### Q1: 页面显示但无法解析视频？

**检查清单：**
- [ ] Render 后端是否正在运行？（访问 `xxx.onrender.com/api/health`）
- [ ] 前端环境变量 `VITE_API_URL` 是否正确？
- [ ] 查看 Render Logs 是否有错误

### Q2: WebSocket 连接失败？

**可能原因：**
1. vercel.json 中 ws 重写规则未正确配置
2. Render 后端未响应 WebSocket 升级请求

**解决方法：**
```json
// vercel.json
{
  "rewrites": [
    {
      "source": "/ws/(.*)",
      "destination": "wss://your-render-url.onrender.com/ws/$1"
    }
  ]
}
```

### Q3: 下载的视频找不到？

**原因：** Render 免费版每次重启会清空临时存储

**解决方案：**
- 启用 Render Disk 持久化存储
- 或将文件保存到外部存储（如 AWS S3）

### Q4: 首次访问很慢？

**正常现象：** 这是 Render 的"冷启动"

- 后端休眠后首次访问需要 10-30 秒唤醒
- 之后访问会很快（< 1秒）

**加速方法：**
- 使用 UptimeRobot 保活（上面已介绍）
- 或升级到付费版

### Q5: 如何查看日志？

**Render 日志：**
1. 打开 Render Dashboard
2. 点击你的服务
3. 点击 **Logs** 标签
4. 可以实时查看所有请求和错误

**Vercel 日志：**
1. 打开 Vercel Dashboard
2. 点击你的项目
3. 点击 **Deployments** → 选择最近一次部署
4. 点击 **View Function Logs**

### Q6: 想要更快的速度？

**选项：**
1. **升级 Render** ($7/月) — 不休眠，更快响应
2. **使用国内服务器** — 国内用户访问更快
3. **CDN 加速** — Cloudflare 免费套餐

---

## 🎯 快速开始清单

在开始之前，确保你有：

- [x] GitHub 账号
- [ ] 代码已推送到 GitHub（第1步）
- [ ] Render 账号（用 GitHub 登录即可）
- [ ] Vercel 账号（用 GitHub 登录即可）
- [ ] 一个视频链接用于测试

**预计总时间：10-15 分钟**

---

## 📞 需要帮助？

- **Render 文档**: https://render.com/docs
- **Vercel 文档**: https://vercel.com/docs
- **GitHub 支持**: https://support.github.com

---

## 🎉 完成！

恭喜！你现在拥有了一个：

- ✅ **完全免费**的视频下载器网站
- ✅ **永久可用**的访问链接
- ✅ **任何人都能使用**
- ✅ **支持 1700+ 平台**视频下载
- ✅ **自动更新**（推送代码即可）

**把你的链接分享给朋友们吧！** 🚀

```
你的专属链接: https://你的项目名.vercel.app
```
