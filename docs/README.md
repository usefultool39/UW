# 边境回声文档中心

> 项目交接先读 [PROJECT_HANDOFF_20260807.md](delivery/PROJECT_HANDOFF_20260807.md)。日常事实仍只认下列四个入口；`archive/` 和状态页下方的旧日志仅供追溯，不是任务来源。

## 先回答四个问题

| 问题 | 权威文档 |
|---|---|
| 最终要做成什么？ | [PRODUCT_DIRECTION.md](product/PRODUCT_DIRECTION.md) |
| 当前版本具体承诺什么？ | [PRODUCT_BRIEF.md](product/PRODUCT_BRIEF.md) / [MVP_SCOPE.md](product/MVP_SCOPE.md) |
| 现在真实完成到哪里？ | [CURRENT_STATUS.md](planning/CURRENT_STATUS.md) |
| 下一步只做什么？ | [NEXT_PHASE.md](planning/NEXT_PHASE.md) |

## 新成员阅读顺序

1. [项目交接总览](delivery/PROJECT_HANDOFF_20260807.md)
2. [最新素材交接快照](delivery/ASSET_HANDOFF_SNAPSHOT_20260807.md)
3. [产品方向与长期开发基线](product/PRODUCT_DIRECTION.md)
4. [产品简述](product/PRODUCT_BRIEF.md)
5. [当前状态](planning/CURRENT_STATUS.md)
6. [下一阶段](planning/NEXT_PHASE.md)
7. [当前素材返工交接](delivery/MATERIALS_REWORK_HANDOFF_20260807.md)
8. [Pre-Capture 执行简报](../materials/11_PRECAPTURE_EXECUTION_BRIEF.md)
9. 再阅读改动涉及的架构、素材和测试文档。

## 当前文档地图

### 产品

- [PRODUCT_DIRECTION](product/PRODUCT_DIRECTION.md)：唯一长期方向，包含正典、玩法、美术、动作、战斗和技术基线。
- [PRODUCT_BRIEF](product/PRODUCT_BRIEF.md)：0.5 的简明定位。
- [MVP_SCOPE](product/MVP_SCOPE.md)：Pre-Capture 边界和退出标准。
- [REQUIREMENTS](product/REQUIREMENTS.md)：带编号的产品、正典、表现和工程要求。
- [ROADMAP](product/ROADMAP.md)：Now / Next / Later / Future。

### 计划与素材

- [CURRENT_STATUS](planning/CURRENT_STATUS.md)：当前事实和历史验证记录。
- [NEXT_PHASE](planning/NEXT_PHASE.md)：唯一开工队列。
- [BACKLOG](planning/BACKLOG.md)：尚未开工的候选项。
- [素材工作区](../materials/00_INDEX.md)：需求、收件、sidecar、manifest、权利和验收入口。
- [当前素材审计](delivery/MATERIALS_AUDIT_20260807.md)：已生成、未生成和延后项。
- [最新素材交接快照](delivery/ASSET_HANDOFF_SNAPSHOT_20260807.md)：按最新收件文件核定的 request 状态、版本、缺口、门禁和生成提示词入口。
- [当前素材返工交接](delivery/MATERIALS_REWORK_HANDOFF_20260807.md)：五个 v003 返工包、状态机制、验收链和唯一整包提示词。
- [素材与宏观审查工作台](planning/MATERIALS_AND_MACRO_REVIEW_LIVE.md)：0.4 阶段历史审核日志，不作为当前开工入口。

### 架构与交付

- [PROJECT_HANDOFF](delivery/PROJECT_HANDOFF_20260807.md)：当前版本、Git、架构、素材/盲测机制、质量门和下一智能体启动提示词。
- [SYSTEM_OVERVIEW](architecture/SYSTEM_OVERVIEW.md)：模块边界与数据流。
- [DATA_AND_CONTENT](architecture/DATA_AND_CONTENT.md)：配置、存档和运行时产物。
- [AI_NPC_BOUNDARY](architecture/AI_NPC_BOUNDARY.md)：scripted / hybrid / agent 权限。
- [ADR 索引](architecture/adr/README.md)：重要架构决策。
- [DEVELOPMENT_PROCESS](delivery/DEVELOPMENT_PROCESS.md)：从需求到发布。
- [DEFINITION_OF_DONE](delivery/DEFINITION_OF_DONE.md)：完成定义。
- [TEST_STRATEGY](delivery/TEST_STRATEGY.md)：质量门与测试层级。
- [RUNBOOK](operations/RUNBOOK.md)：安装、启动、停止和排错。

## 历史文档

[archive/2026-legacy-plans](archive/2026-legacy-plans/README.md) 保存旧的 Day 1–117、原创见习记录员、月度扩展、Cocos 和成熟化计划。历史文件可能相互冲突，禁止直接从中开工。

## 更新规则

| 变化 | 必须更新 |
|---|---|
| 长期目标/玩法/美术/技术边界 | `PRODUCT_DIRECTION.md`，必要时 ADR |
| 当前版本范围 | `PRODUCT_BRIEF.md`、`MVP_SCOPE.md`、`REQUIREMENTS.md` |
| 真实完成度/测试/风险 | `CURRENT_STATUS.md` |
| 当前开工顺序 | 只更新 `NEXT_PHASE.md` |
| 新候选任务 | `BACKLOG.md` |
| 素材需求/来源/批准 | `materials/REQUESTS.csv`、sidecar、manifest 和审计 |
| 玩家可见变化/发布 | `CHANGELOG.md`、版本和发布证据 |
