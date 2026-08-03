# 标准开发流程

- **状态**：Current
- **原则**：采用大团队的可追溯性，不照搬审批层级。

## 流程

```text
Idea → Requirement → MVP/Roadmap Scope → Issue
→ 设计说明或 ADR → 短生命周期分支 → 小批量实现 + 测试
→ PR + 自动质量门 → Review → Merge main
→ Version/Changelog/Release → 试玩观察 → 更新状态和下一阶段
```

流程参考 GitHub Flow、Google 小变更代码评审、ADR、DORA 指标、Epic/Feature/Backlog 分层和 Semantic Versioning。一个人开发也要写验收、测试和决策，但不引入无价值会议。

## 需求进入

新想法先进入 Backlog 或 Issue，写用户问题、预期结果、非目标、验收、风险。影响产品方向时先更新产品/需求文档。

## 计划拆分

- Epic：跨多个可独立交付结果的大目标。
- Feature：玩家可感知、可单独验收的能力。
- Task/Chore：为 Feature 服务的工程工作。
- Bug：实际行为偏离需求或基线。

每项变更尽量 0.5–2 天完成；大改拆成“兼容提取 → 切换调用 → 清理旧实现”。

## 设计门槛

状态所有权、框架、存档/API 破坏性变化、AI 边界、长期基础设施变化必须写 ADR。普通 UI、内容、局部实现不需要 ADR，但 PR 要说明方案和测试。

## 分支与提交

- `main` 始终可启动、可测试。
- 分支：`feat/<issue>-name`、`fix/...`、`refactor/...`、`docs/...`。
- 禁止在功能分支顺手做无关大格式化。
- 推荐 Conventional Commits：`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`。

## PR

PR 应小、聚焦，包含问题、方案、明确不做、风险、回滚、测试证据、文档/Changelog/兼容影响。多人协作时由非作者批准；高风险改动额外 review。

## 质量门

默认执行后端 pytest、前端 build、Playwright Chromium、差异卫生。CI 失败不得合并；豁免必须记录原因、风险和补救 Issue。

## 指标

只追踪有助于交付的指标：变更前置时间、发布频率、变更失败率、恢复时间、试玩完成率、首个有效行动时间、卡点和后果发现率。

## 参考

- GitHub Flow：https://docs.github.com/en/get-started/using-github/github-flow
- Google Small CLs：https://google.github.io/eng-practices/review/developer/small-cls.html
- ADR：https://cloud.google.com/architecture/architecture-decision-records
- DORA：https://dora.dev/guides/dora-metrics-four-keys/
- Azure Epics/Features：https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/define-features-epics
- SemVer：https://semver.org/
