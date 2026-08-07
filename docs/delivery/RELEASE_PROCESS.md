# 发布流程

- **状态**：Current
- **当前阶段**：0.x Preview；每轮实现必须通过质量门、更新记录并提交推送；发布 tag 仍需单独确认。

## 候选版检查

1. `main` 工作区干净，改动已审查。
2. 更新 `VERSION` 和包版本。
3. `CHANGELOG.md` 的 Unreleased 归入版本日期。
4. 完整质量门和内容校验通过。
5. 全新 run 完成 Day 1–3 冒烟。
6. 无 API 的 scripted 模式通过。
7. 验证旧存档导入和新存档导出。
8. 干净 macOS 环境运行 `启动游戏.command --setup-only` 后启动。
9. 记录已知问题、证据和回滚 commit。
10. 创建 annotated tag，例如 `v0.5.0`。

## 回滚

回滚到上一个绿色 tag/commit；不直接删除用户存档。schema 不兼容时先备份并提供迁移/降级说明。P0 事故记录影响、根因、修复和防复发测试。

## 热修复

从稳定 tag 建 `fix/...`，只包含最小修复和回归测试；合并后增加 patch 或预发布序号，并同步 main。
