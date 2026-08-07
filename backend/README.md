# 后端

FastAPI 后端负责权威世界状态、行动校验、NPC 日程、剧情事件、关系与记忆、对话和存档。

- 产品与边界：`../docs/PROJECT.md`
- 架构：`../docs/architecture/SYSTEM_OVERVIEW.md`
- 运行：`../docs/operations/RUNBOOK.md`

## 启动

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Windows 可使用 `.venv\Scripts\python.exe`。

健康检查：`http://127.0.0.1:8765/api/health`

## 测试

从仓库根目录运行：

```bash
backend/.venv/bin/python -m pytest -q backend/tests
```

## 主要模块

| 文件 | 作用 |
|---|---|
| `app/main.py` | API 路由 |
| `app/models.py` | 世界、玩家、NPC 和关系模型 |
| `app/session.py` | 行动、剧情、对话、存档和权威提交 |
| `app/activity_engine.py` | 活动规划与校验 |
| `app/world.py` | 世界规则、时间和 NPC 日程 |
| `app/story_director.py` | 剧情触发和效果 |
| `app/npc_runtime.py` | scripted/hybrid/agent 路由 |
| `app/memory_store.py` | 按 run 隔离的记忆和 JSONL |

## 常用 API

| 方法 | 路径 |
|---|---|
| `GET` | `/api/state` |
| `POST` | `/api/player/action` |
| `GET` | `/api/story/available_events` |
| `POST` | `/api/story/choose` |
| `POST` | `/api/dialogue` |
| `GET` | `/api/save/export` |
| `POST` | `/api/save/import` |

`runs/`、`data/memory/` 和 `_test_tmp/` 是运行或测试产物，不是剧情配置源。
