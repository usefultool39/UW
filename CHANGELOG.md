# Changelog

本项目的玩家可见变化记录在此。版本遵循 Semantic Versioning；当前仍处于 0.x Preview。

## [Unreleased]

### Added

- 北境短程巡查三回合玩法、敌方意图与克制判断。
- scripted / hybrid / agent NPC 运行骨架和数据驱动固定对话。
- macOS 一键启动入口。
- 产品、需求、MVP、路线图、ADR、计划、测试、发布和运维文档体系。
- GitHub Actions 质量门与 Issue/PR 模板。

### Changed

- 开场与主线聚焦为 Underworld 分支篇的见习记录员视角。
- 统一行动收益预览、今日节奏、公开角色术语和休息恢复。
- 历史计划归档，`CURRENT_STATUS` / `NEXT_PHASE` 成为单一事实来源。
- 活动 UI 分发与后端资源规划逐步从巨型文件提取为独立模块。

### Fixed

- NPC 记忆按 run 隔离，避免新游戏继承旧周目内容。
- 危险活动先校验资源，避免失败时部分写入状态。

## 历史

仓库在建立正式版本治理前已有 54 个提交，未创建 tag。详细演进请使用 `git log` 和 `docs/archive/2026-legacy-plans/`；不伪造历史版本号。
