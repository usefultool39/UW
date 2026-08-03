# 常见故障排查

- **状态**：Current

## 端口占用

```bash
lsof -nP -iTCP:8765 -sTCP:LISTEN
lsof -nP -iTCP:3000 -sTCP:LISTEN
```
确认进程来源；若已有本项目服务，直接访问或先停止。

## 找不到 Node/npm

需要 Node.js 20+。Finder 双击失败但终端正常时，检查脚本 PATH 是否包含 Homebrew 或 `~/.local/nodejs/bin`。

## Python 不支持

需要 3.11–3.13。删除损坏的 `backend/.venv` 后重新运行启动脚本；不要提交 `.venv`。

## 前端显示后端离线

检查 `/api/health`、后端日志、端口和 API 配置。重启后端后刷新状态，不要编辑浏览器本地状态替代修复。

## Playwright 浏览器缺失

```bash
cd frontend
npx playwright install chromium
```

## E2E 误用旧服务

本地默认复用已有服务；需要隔离时先停止旧服务，或设置 `CI=1` 强制启动新服务。

## NPC API 不可用

没有 key 时应自动 scripted；若主线阻塞，这是 P0 回退缺陷。

## 新游戏继承旧对话

检查是否复用 run_id，并运行记忆隔离测试。不要把 `data/memory/` 加回 Git。

## Phaser chunk 警告

当前非阻塞。先测首屏性能，再通过动态 import/分包治理；不要为消警告破坏场景。
