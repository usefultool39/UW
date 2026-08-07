# 本地运行手册

- **状态**：Current
- **基线**：Windows / macOS；Python 3.11–3.13；Node.js 20+

## 一键启动

Windows 首选：

```powershell
cd C:\Users\liang\Desktop\UW
.\启动全部项目.bat
# 或等价入口
.\start.bat
```

Windows 入口会启动开发前端 `http://127.0.0.1:3000` 和后端健康检查 `http://127.0.0.1:8765/api/health`。

macOS：

```bash
cd /path/to/UW
./启动游戏.command
./启动游戏.command --setup-only
./启动游戏.command --no-open
./试玩盲测.command        # scripted production build，供真人盲测
```

通用入口：开发游戏 http://127.0.0.1:3000；盲测入口默认同端口；健康 http://127.0.0.1:8765/api/health；内容校验 http://127.0.0.1:8765/api/dev/content_validation。真人盲测请先通过工程和素材预检，再从全新浏览器上下文开始。

## 手动启动

Windows，从项目根目录分别打开两个 PowerShell：

```powershell
backend\.venv\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765
```

```powershell
npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 3000
```

macOS：

```bash
cd backend
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

另一个终端：

```bash
cd frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 3000
```

## 停止与端口

一键脚本窗口按 Ctrl+C。Windows 端口残留时先只读检查：

```powershell
netstat -ano | Select-String -Pattern ':8765|:3000'
```

确认 PID 属于本项目后再停止进程。macOS：

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

确认是本项目进程后再终止。

## 重置

优先用游戏内新游戏/重置。开发调试可用：

```bash
curl -X POST http://127.0.0.1:8765/api/reset
```

不要把 `data/memory/` 当内容配置。

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`。默认 scripted 不需要 API key；真实 key 不得进入 Git、文档、截图。

## 开发质量门

```bash
./scripts/quality.sh
make quality  # 等价入口
make e2e      # UI/发布前
```

Windows 项目环境优先使用 `backend/.venv/python.exe`；Playwright 和质量脚本会自动发现该路径，也支持通过 `PYTHON_BIN` 覆盖。
