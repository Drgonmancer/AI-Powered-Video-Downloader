# AI 万能视频下载器

支持 YouTube、Bilibili、抖音、TikTok 等平台的视频解析与下载，集成 AI 摘要与 Stripe 会员订阅。

## 功能

- 多平台视频解析与下载（含抖音无水印专用解析）
- WebSocket 实时下载进度
- 用户注册 / 登录（JWT）
- 会员套餐与 Stripe 支付
- AI 视频摘要（DeepSeek，可选）

## 项目结构

```
backend/          # FastAPI 后端
frontend/         # Vue 3 + Vite 前端
docs/             # 技术文档与部署说明
```

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
copy config\stripe_config.example.py config\stripe_config.py   # Windows
# 配置 STRIPE_* 环境变量或编辑 stripe_config.py（勿提交密钥）
copy ai_config.example.py ai_config.py                         # 可选：AI 摘要
python main.py
```

服务默认：`http://127.0.0.1:9000`

### 2. 前端（开发模式）

```bash
cd frontend
npm install
npm run dev
```

生产环境可由后端挂载 `frontend/dist`（先执行 `npm run build`）。

## 文档

| 文档 | 说明 |
|------|------|
| [docs/快速启动说明.md](docs/快速启动说明.md) | 本地启动与文档索引 |
| [docs/MEMBERSHIP_DEPLOYMENT_GUIDE.md](docs/MEMBERSHIP_DEPLOYMENT_GUIDE.md) | 会员与 Stripe 配置 |
| [docs/后端API接口文档.md](docs/后端API接口文档.md) | API 说明 |
| [docs/DEPLOY.md](docs/DEPLOY.md) | 云端部署 |

## 安全说明

- `backend/config/stripe_config.py`、`backend/ai_config.py` 已加入 `.gitignore`
- 请勿将 Stripe / DeepSeek 真实密钥提交到仓库

## License

MIT
