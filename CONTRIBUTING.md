# Contributing to 边境回声

开始修改前请读：`docs/README.md`、`docs/planning/CURRENT_STATUS.md`、`docs/planning/NEXT_PHASE.md`、`docs/architecture/SYSTEM_OVERVIEW.md`、`docs/delivery/DEVELOPMENT_PROCESS.md`、`docs/delivery/DEFINITION_OF_DONE.md`。

## 原则

- 不大幅改变当前游戏内容，除非需求和验收先确认。
- 不覆盖或 reset 未提交的他人改动；先读 `git status` 和 `git diff`。
- 恢复功能前先查 Git 历史，避免旧版本覆盖新架构。
- 保持后端权威状态和 scripted 离线基线。
- 优先小改、兼容提取和可回滚提交，不做大爆炸重写。

## 步骤

1. 从 `main` 创建短分支。
2. 在 Issue/计划中写问题、范围、验收和风险。
3. 重大架构先写 ADR。
4. 先补/确认测试，再实现最小变更。
5. 运行质量门。
6. 更新 Changelog 和权威文档。
7. 使用 PR 模板自审。

## 验证

```bash
cd backend && .venv/bin/python -m pytest -q
cd ../frontend && npm run build
PYTHON_BIN=../backend/.venv/bin/python npm run test:e2e
cd .. && git diff --check
```

## Commit 示例

```text
feat: add visible relationship callback
fix: keep rejected patrol action atomic
refactor: extract activity resource planning
test: cover run-scoped npc memory
docs: consolidate delivery process
```

不要提交 `.env`、API key、`runs/`、`data/memory/`、构建/测试产物。
