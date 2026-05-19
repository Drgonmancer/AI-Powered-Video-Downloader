# VideoForge Pro - Render 全栈免费部署指南

> 🎉 **0 成本！一个平台！前后端全部部署到 Render！**
>
> 只需 **1 个链接**，任何人打开就能使用你的视频下载器！

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

---

## 📋 架构说明

```
                    ┌─────────────────────────────┐
                    │      Render (唯一服务)        │
                    │                             │
用户浏览器  ───────►│  https://xxx.onrender.com   │
                    │                             │
                    │  ├── /          → 前端页面    │
                    │  ├── /api/*     → 后端API    │
                    │  ├── /ws/*      → WebSocket  │
                    │  └── /assets/*  → 静态资源    │
                    │                             │
                    │  FastAPI + Vue3 + yt-dlp     │
                    └─────────────────────────────┘
```

**只需要 1 个 Render 服务，搞定一切！**

---

## 🚀 开始部署（3 步完成）

### 第1步：推送到 GitHub（2分钟）

#### 1.1 创建 GitHub 仓库

1. 打开 https://github.com/new
2. **Repository name**: `video-forge-pro`
3. **Description**: `AI Universal Video Downloader - 支持多平台视频下载`
4. 选择 **Private**（私有）或 Public（公开）
5. ❌ 不要勾选 README、.gitignore、License
6. 点击 **Create repository**

#### 1.2 推送代码

```bash
cd "d:\vibe coding项目\AI万能视频下载器"

# 添加远程仓库（替换成你的 GitHub 用户名）
git remote add origin https://github.com/你的GitHub用户名/video-forge-pro.git

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

![创建Web Service](https://render.com/images/docs/web-service-new.png)

#### 2.3 连接 GitHub 仓库

1. 点击 **Connect an existing repository**
2. 搜索并选择 `video-forge-pro`
3. 点击 **Connect**

#### 2.4 配置部署参数

Render 会自动检测到 `render.yaml` 配置文件！

确认以下设置：

| 字段 | 值 |
|------|-----|
| **Name** | `video-forge-pro` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build` |
| **Start Command** | `cd backend && python main.py --build-frontend` |
| **Instance Type** | **Free** (免费版) |

#### 2.5 确认环境变量

点击 **Advanced** 展开：

```
PORT = 8976
PYTHON_VERSION = 3.11.0
NODE_VERSION = 20
DOWNLOAD_PATH = /opt/render/project/downloads
```

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
https://video-forge-pro-xxxx.onrender.com
```

**这就是你的专属网址！分享给任何人都能用！🎉**

---

### 第3步：测试验证（1分钟）

1. 打开你获得的 Render 地址
2. 应该看到完整的视频下载器界面
3. 粘贴 YouTube/B站/抖音 链接测试
4. 点击解析 → 下载 → 完美运行！

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

### Q2: 解析视频报错？

**查看日志：**
1. Render Dashboard → 你的服务
2. 点击 **Logs** 查看实时错误输出
3. 常见问题：yt-dlp 版本、网络限制、反爬虫

### Q3: WebSocket 连接不上？

**正常现象：** 全栈部署下 WebSocket 和 API 在同一端口。

检查前端代码中 WebSocket 地址是否正确（应使用相对路径 `/ws/downloads`）。

### Q4: 下载的视频找不到？

**原因：** 未启用持久化磁盘

**解决：** 在 Render 设置中启用 Disk（上面第2.6步已说明）

### Q5: 首次访问很慢？

**正常：** 这是"冷启动"现象

- 后端休眠后首次访问需 10-30 秒唤醒
- 之后访问很快（< 1秒）
- 用 UptimeRobot 保活可避免

### Q6: 如何查看实时日志？

1. 打开 https://dashboard.render.com
2. 点击你的服务名称
3. 点击 **Logs** 标签
4. 可看到所有请求和错误信息

---

## 🎯 部署前清单

- [x] GitHub 账号
- [ ] 代码已推送到 GitHub
- [ ] Render 账号（GitHub 登录即可）
- [ ] 一个测试用的视频链接

**预计总时间：5-10 分钟**

---

## 🔄 本地开发 vs 云端部署

| 环境 | 启动方式 | API 地址 |
|------|---------|---------|
| **本地开发** | 双击 `启动.bat` | http://localhost:8976 |
| **云端部署** | 自动（推送代码） | https://xxx.onrender.com |

本地开发和云端部署**完全兼容**，无需修改任何代码！

---

## 📞 需要帮助？

- **Render 文档**: https://render.com/docs
- **Render 状态页**: https://status.render.com
- **GitHub Issues**: 在你的仓库提 Issue

---

## 🎉 完成！

恭喜！你现在拥有了一个：

- ✅ **完全免费**的全栈应用
- ✅ **永久可用**的公开网址
- ✅ **一键部署**（推送代码即更新）
- ✅ **1700+ 平台**视频下载支持
- ✅ **中英文双语**界面
- ✅ **Edge 浏览器**最佳适配

---

**你的专属链接：**
```
https://video-forge-pro-xxxx.onrender.com
```

**把这个链接发给朋友，他们直接打开就能用！** 🚀
