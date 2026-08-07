# 运行手册

## 推荐入口

在仓库根目录运行：

macOS：

```bash
./启动游戏.command
```

Windows：

```powershell
.\启动全部项目.bat
```

首次安装或修复依赖可使用启动脚本提供的 setup 选项。

## 手动启动

后端：

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Windows 虚拟环境可将 Python 路径替换为 `.venv\Scripts\python.exe`。

前端：

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

地址：

- 游戏：`http://127.0.0.1:3000`
- 后端健康：`http://127.0.0.1:8765/api/health`
- 内容校验：`http://127.0.0.1:8765/api/dev/content_validation`

## 验证

日常开发：

```bash
./scripts/quality.sh
```

准备发布：

```bash
./scripts/release.sh
```

单独运行：

```bash
backend/.venv/bin/python -m pytest -q backend/tests
npm --prefix frontend run test:unit
npm --prefix frontend run build
cd frontend && npm run test:e2e
```

## 全新试玩

1. 确认后端和前端都在运行。
2. 使用新的浏览器上下文。
3. 调用游戏内新游戏，或执行 `POST /api/reset`。
4. 不复用旧 run 作为盲测起点。
5. 从 N01 连续推进到 N10，并保存终点证据。

## 外部 AI Provider

Provider 是可选增强。没有密钥、超时、非法响应或预算耗尽时，系统必须自动使用 scripted。密钥只放环境变量，不写入仓库、日志或文档。
