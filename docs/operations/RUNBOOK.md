# 本地运行手册

- **状态**：Current
- **基线**：macOS；Python 3.11–3.13；Node.js 20+

## 一键启动

```bash
cd /path/to/UW
./启动游戏.command
./启动游戏.command --setup-only
./启动游戏.command --no-open
./试玩盲测.command        # scripted production build，供真人盲测
```

入口：开发游戏 http://127.0.0.1:3000；盲测入口默认同端口；健康 http://127.0.0.1:8765/api/health；内容校验 http://127.0.0.1:8765/api/dev/content_validation。真人盲测请优先运行 `./scripts/playtest-preflight.sh` 后使用 `./试玩盲测.command`。

## 手动启动

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

一键脚本窗口按 Ctrl+C。端口残留时：

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
