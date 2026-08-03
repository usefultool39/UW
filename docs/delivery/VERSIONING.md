# 版本与兼容策略

- **状态**：Current

采用 Semantic Versioning：`MAJOR.MINOR.PATCH[-PRERELEASE]`。

- `0.x`：快速验证，但仍保护存档/API 兼容。
- MINOR：新增玩家可见能力或里程碑。
- PATCH：兼容修复、文案/平衡、内部重构。
- 预发布：如 `0.4.0-preview.1`。

`VERSION` 是仓库级事实源；发布时同步 `frontend/package.json` 和 `backend/pyproject.toml`。开发期使用 `0.4.0-dev`。

兼容维度：存档 schema、HTTP API、内容 ID、NPC runtime envelope。玩家可见变化写入 `CHANGELOG.md` 的 Added / Changed / Fixed / Removed / Security。
