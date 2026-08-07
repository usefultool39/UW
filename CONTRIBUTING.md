# 参与 UW 开发

开始前只需阅读：

1. `docs/PROJECT.md`
2. `docs/PLAN.md`
3. `docs/DELIVERY.md`
4. 与本次工作相关的架构或素材文档

## 原则

- 当前只服务版本 `0.5.0` 的卢利特村序章。
- 不恢复旧见习记录员、Day/月度路线或日期型计划文档。
- 不覆盖或 reset 他人未提交修改；先检查 `git status` 和 `git diff`。
- 保持后端权威状态和 scripted 离线基线。
- 优先小改、可验证、可回滚，不做无边界重写。
- 未审核素材不得进入 runtime。

## 标准流程

1. 从稳定分支创建目标明确的短分支。
2. 写清问题、范围、验收、风险和回滚。
3. 架构所有权变化先写 ADR。
4. 实现最小变更并补齐适用测试。
5. 运行 `./scripts/quality.sh`。
6. 更新唯一权威文档和 `CHANGELOG.md`。
7. 使用 PR 模板自审。
8. 只有准备发布时运行 `./scripts/release.sh`。

完整规则见 `docs/DELIVERY.md`。
