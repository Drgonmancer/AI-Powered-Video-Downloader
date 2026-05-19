# VideoForge Pro - 云部署完整指南

> 🚀 将你的视频下载器部署到云端，让任何人都能通过网址访问使用！

---

## 📋 部署方案对比

| 方案 | 平台 | 免费额度 | 部署难度 | 推荐度 |
|------|------|---------|---------|--------|
| **方案A（推荐）** | Railway | $5/月 | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| **方案B** | Render + Vercel | 750小时/月 | ⭐⭐ 中等 | ⭐⭐⭐⭐ |
| **方案C** | 自建服务器 (VPS) | 按需付费 | ⭐⭐⭐ 复杂 | ⭐⭐⭐ |

---

## 方案A：Railway 一键部署（推荐）

### 优势
- ✅ 前后端一键部署
- ✅ 免费 $5/月额度（足够个人使用）
- ✅ 自动 HTTPS
- ✅ 支持 WebSocket
- ✅ 自动扩容

### 步骤1：推送到 GitHub

```bash
# 1. 在项目根目录执行
cd "d:\vibe coding项目\AI万能视频下载器"

# 2. 添加所有文件
git add .

# 3. 创建首次提交
git commit -m "Initial commit: VideoForge Pro - AI Universal Video Downloader"

# 4. 在 GitHub 创建新仓库后，关联远程仓库
git remote add origin https://github.com/你的用户名/video-forge-pro.git

# 5. 推送到 GitHub
git push -u origin main
```

### 步骤2：在 Railway 部署

1. **注册 Railway**
   - 访问 https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"

3. **选择仓库**
   - 选择 `video-forge-pro` 仓库
   - Railway 会自动检测 `railway.json` 配置

4. **配置环境变量**（如果需要）
   - 点击 Settings → Variables
   - 添加：
     ```
     DOWNLOAD_PATH = /app/downloads
     PORT = 8976
     ```

5. **添加持久化存储**（用于保存下载的文件）
   - 点击 "+ New" → Volume
   - Name: `downloads`
   - Mount Path: `/app/downloads`

6. **部署完成！**
   - Railway 会自动分配一个公网 URL
   - 格式类似：`https://xxx.up.railway.app`
   - 这个 URL 就是别人可以访问的地址！

### 步骤3：自定义域名（可选）

1. 在 Railway 项目设置中点击 "Networking"
2. 点击 "Generate Domain" 或添加自定义域名
3. 按提示配置 DNS 记录

---

## 方案B：Render + Vercel 分离部署

### 适用场景
- 想要更精细的控制
- 前端和后端独立扩展

### 后端部署到 Render

1. **注册 Render**
   - 访问 https://render.com
   - 使用 GitHub 账号登录

2. **创建 Web Service**
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - Render 会自动识别 `render.yaml`

3. **配置参数**
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - 实例类型：Free（免费）

4. **获取后端 URL**
   - 格式：`https://xxx.onrender.com`
   - 记住这个 URL，前端需要用到

### 前端部署到 Vercel

1. **修改前端 API 地址**

编辑 `frontend/vite.config.js`：

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://xxx.onrender.com',  // 改成你的 Render 后端地址
        changeOrigin: true,
      },
      '/ws': {
        target: 'wss://xxx.onrender.com',     // 改成你的 Render 后端地址
        ws: true,
      }
    }
  }
})
```

2. **注册 Vercel**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

3. **导入项目**
   - 点击 "New Project"
   - 选择 `video-forge-pro` 仓库
   - Root Directory 设置为：`frontend`
   - Framework Preset: Vite
   - 点击 Deploy

4. **获取前端 URL**
   - 格式：`https://xxx.vercel.app`
   - 这就是给别人的访问链接！

---

## 方案C：自建服务器部署（VPS/云服务器）

### 适用场景
- 需要完全控制服务器
- 有大量下载需求
- 需要更高性能

### 推荐云服务商
| 服务商 | 价格 | 特点 |
|--------|------|------|
| 阿里云 ECS | ¥50-100/月 | 国内访问快 |
| 腾讯云 CVM | ¥50-100/月 | 学生优惠 |
| Vultr | $5-6/月 | 海外节点 |
| DigitalOcean | $4-6/月 | 简单易用 |

### 部署步骤

1. **购买服务器**
   - 推荐：2核4G、50G SSD、5Mbps带宽
   - 系统：Ubuntu 22.04 LTS

2. **连接服务器**
   ```bash
   ssh root@你的服务器IP
   ```

3. **安装环境**
   ```bash
   # 更新系统
   apt update && apt upgrade -y
   
   # 安装 Python
   apt install python3 python3-pip python3-venv -y
   
   # 安装 Node.js
   curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
   apt install nodejs -y
   
   # 安装 ffmpeg
   apt install ffmpeg -y
   
   # 安装 Nginx
   apt install nginx -y
   ```

4. **克隆项目**
   ```bash
   cd /opt
   git clone https://github.com/你的用户名/video-forge-pro.git
   cd video-forge-pro
   ```

5. **安装依赖并启动**
   ```bash
   # 安装 Python 依赖
   pip install -r backend/requirements.txt
   
   # 安装前端依赖
   cd frontend && npm install && npm run build && cd ..
   
   # 启动后端（后台运行）
   nohup python backend/main.py > app.log 2>&1 &
   
   # 配置 Nginx 反向代理
   nano /etc/nginx/sites-available/video-forge
   ```

6. **Nginx 配置**
   ```nginx
   server {
       listen 80;
       server_name 你的域名或IP;
       
       location /api {
           proxy_pass http://127.0.0.1:8976;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /ws {
           proxy_pass http://127.0.0.1:8976;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
       
       location / {
           root /opt/video-forge-pro/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
   }
   ```

7. **启动 Nginx**
   ```bash
   ln -s /etc/nginx/sites-available/video-forge /etc/nginx/sites-enabled/
   nginx -t && systemctl restart nginx
   ```

8. **配置域名 DNS（可选）**
   - A 记录指向服务器 IP
   - 配置 SSL 证书：`certbot --nginx`

9. **设置开机自启（systemd）**
   ```ini
   # /etc/systemd/system/video-forge.service
   [Unit]
   Description=VideoForge Pro Backend
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/opt/video-forge-pro/backend
   ExecStart=/usr/bin/python3 main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   systemctl enable video-forge
   systemctl start video-forge
   ```

---

## 🔐 安全注意事项

### 1. 不要提交敏感文件
以下文件已在 `.gitignore` 中排除：
- `.env` — 环境变量
- `cookies.txt` — Cookie 文件
- `downloads/` — 下载的文件

### 2. 生产环境建议
- [ ] 启用 HTTPS（Railway/Vercel 自动提供）
- [ ] 设置速率限制（防止滥用）
- [ ] 添加认证功能（如需要）
- [ ] 定期更新依赖包
- [ ] 监控日志和错误

### 3. 法律合规
- ⚠️ 视频下载可能涉及版权问题
- ⚠️ 请确保遵守各平台的服务条款
- ⚠️ 建议添加免责声明和使用协议

---

## 🐛 常见问题

### Q: 部署后无法下载视频？
**A:** 检查以下几点：
1. 服务器是否安装了 ffmpeg
2. 下载目录是否有写入权限
3. 是否有足够的磁盘空间
4. 查看 Railway/Render 的日志

### Q: WebSocket 连接失败？
**A:** 
- 确保 `/ws` 路径正确配置了代理
- 检查防火墙是否放行端口
- Railway/Render 默认支持 WebSocket

### Q: 如何绑定自己的域名？
**A:**
1. 在域名服务商添加 CNAME/A 记录
2. 在部署平台添加自定义域名
3. 等待 DNS 生效（通常几分钟到几小时）

### Q: 免费额度够用吗？
**A:**
- Railway: $5/月 ≈ 512小时运行时间，个人使用足够
- Render: 750小时免费，但会休眠（15分钟无请求）
- Vercel: 前端托管无限免费

### Q: 下载速度慢？
**A:**
- 免费版带宽有限，这是正常的
- 升级到付费套餐可以提升速度
- 或者考虑使用国内云服务器

---

## 📊 成本估算

| 方案 | 月费用 | 说明 |
|------|-------|------|
| Railway 免费版 | $0 | 有限制，适合测试 |
| Railway 基础版 | $5/月起 | 推荐生产使用 |
| Render + Vercel | $0 | 免费但有休眠 |
| 阿里云轻量 | ¥50-100/月 | 国内速度快 |
| Vultr VPS | $5-6/月 | 海外节点 |

---

## 🎯 快速开始推荐

如果你是第一次部署，我强烈推荐 **方案A（Railway）**：

1. ✅ 注册 GitHub 并推送代码
2. ✅ 注册 Railway 并连接 GitHub
3. ✅ 一键部署，获得公开 URL
4. ✅ 分享给朋友使用！

整个过程 **10 分钟内** 即可完成！

---

## 📞 需要帮助？

如果遇到问题，可以查看：
- [Railway 官方文档](https://docs.railway.app)
- [Render 官方文档](https://render.com/docs)
- [Vercel 官方文档](https://vercel.com/docs)

祝部署顺利！🎉
