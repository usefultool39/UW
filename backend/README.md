# 后端说明

FastAPI 后端负责权威世界状态、玩家行动校验、NPC 日程、剧情事件、关系/记忆、对话和存档。

完整架构见 [../docs/PROJECT.md](../docs/PROJECT.md)。

## 运行

```bat
cd /d F:\usefultool39\02-UW小镇\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

健康检查：

```text
http://127.0.0.1:8765/api/health
```

## 测试

```bat
cd /d F:\usefultool39\02-UW小镇\backend
python -m pytest -q backend/tests
```

当前测试使用 `backend/tests/conftest.py` 中的项目内临时目录 fixture，避免部分 Windows 环境中用户 Temp ACL 被锁导致 `tmp_path` 报权限错误。

## 主要模块

| 文件 | 作用 |
|------|------|
| `app/main.py` | API 路由 |
| `app/models.py` | 世界、玩家、NPC、关系模型 |
| `app/session.py` | 会话、行动、剧情选择、对话、存档 |
| `app/world.py` | 世界规则和 NPC 日程 |
| `app/story_director.py` | 章节事件触发和效果 |
| `app/dialogue_agent.py` | LLM/fallback 对话 |
| `app/memory_store.py` | NPC 记忆 summary 与 JSONL |
| `app/relationship.py` | 关系数值和档案 |

## 常用 API

| 方法 | 路径 |
|------|------|
| `GET` | `/api/state` |
| `POST` | `/api/player/action` |
| `GET` | `/api/story/available_events` |
| `POST` | `/api/story/choose` |
| `POST` | `/api/dialogue` |
| `GET` | `/api/npc/{npc_id}/profile` |
| `GET` | `/api/save/export` |
| `POST` | `/api/save/import` |

不要把 `runs/`、`data/memory/`、`_test_tmp/` 当作剧情配置源。
