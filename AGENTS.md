# AGENTS.md — UW 项目协作入口

本文件适用于所有进入仓库的人类开发者和智能体。

## 开始前必须阅读

1. `docs/README.md`
2. `docs/planning/CURRENT_STATUS.md`
3. `docs/product/PRODUCT_BRIEF.md`
4. `docs/planning/NEXT_PHASE.md`
5. `docs/architecture/SYSTEM_OVERVIEW.md`
6. `docs/delivery/DEVELOPMENT_PROCESS.md`
7. `docs/delivery/DEFINITION_OF_DONE.md`

## 当前唯一方向

稳定 Day 1–3 纵切片：容易上手、行动有判断、关系有回响、异常逐步升级。不要因为 `docs/archive/` 的旧 TODO 扩写无关内容。

## 不可破坏的边界

- FastAPI 后端是位置、时间、资源、flag、关系、剧情闸和永久记忆的权威。
- scripted NPC 是无 API 的完整产品基线；hybrid/agent 必须可回退。
- 被拒绝的行动不得部分写入任何状态。
- `runs/`、`data/memory/`、`frontend/dist/` 是运行产物，不是配置源。
- 不 reset、覆盖或删除未提交的既有改动；先检查 `git status`、`git diff`、`git log`。
- 优先小步兼容重构，不一次性重写 `FieldSlice.vue`、Phaser scene 或 `npc_intents.py`。

## 常用入口

```bash
./启动游戏.command              # macOS 启动游戏
./启动游戏.command --setup-only # 只准备环境
./scripts/quality.sh            # 后端 + 前端单测 + build + diff check
cd frontend && PYTHON_BIN=../backend/.venv/bin/python npm run test:e2e
```

## 修改完成后

- 测试通过。
- 用户可见变化更新 `CHANGELOG.md`。
- 状态变化更新 `CURRENT_STATUS.md`。
- 下一阶段变化只更新 `NEXT_PHASE.md`。
- 重要架构决策新增 ADR，不覆盖历史记录。
