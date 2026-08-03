# 测试策略

- **状态**：Current
- **原则**：规则靠快速测试，跨层关键路径靠少量 E2E，体验品质靠结构化试玩。

## 分层

| 层级 | 目标 | 位置 |
|---|---|---|
| 单元 | 纯规则、校验、资源规划 | `backend/tests/` |
| 集成/API | Session、存档、记忆、API envelope | `backend/tests/` |
| 构建 | Vue/Vite 编译与资源引用 | `npm run build` |
| E2E | 开场、移动、活动、故事和回响 | `frontend/e2e/` |
| 内容校验 | 坏引用、重复 ID、不可达节点 | validator/API |
| 人工试玩 | 上手、节奏、情绪和理解 | `PLAYTEST.md` |

## 本地命令

```bash
./scripts/quality.sh
cd frontend && PYTHON_BIN=../backend/.venv/bin/python npm run test:e2e
```

`quality.sh` 执行 pytest、前端单测、production build 和 `git diff --check`；UI/发布改动再执行 E2E。

## 关键不变量

- 被拒绝活动不修改资源、flag、关系或记忆。
- HP 不因活动降到 0；MP/体力不为负。
- once/daily 活动阻止重复执行。
- 记忆按 run 隔离；reset 不继承旧周目。
- scripted 和模型失败回退可用。
- 存档旧字段默认、导入失败原子。
- 前端活动注册表正确选择 panel 和结果字段。

CI 在 `.github/workflows/quality-gate.yml` 中运行 backend、frontend build、E2E 三个 job。
