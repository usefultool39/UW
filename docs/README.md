# 边境回声文档中心

> **单一事实来源**：过时计划只保留在 `archive/` 中用于追溯，不再作为当前任务依据。

## 先回答三个问题

| 问题 | 权威文档 |
|---|---|
| 1. 已经做了什么？ | [planning/CURRENT_STATUS.md](planning/CURRENT_STATUS.md) |
| 2. 目标做什么？ | [product/PRODUCT_BRIEF.md](product/PRODUCT_BRIEF.md) / [product/ROADMAP.md](product/ROADMAP.md) |
| 3. 下一阶段做什么？ | [planning/NEXT_PHASE.md](planning/NEXT_PHASE.md)；候选工作在 [BACKLOG.md](planning/BACKLOG.md) |

## 新成员 / 新智能体 15 分钟阅读顺序

1. 本页。
2. [产品简述](product/PRODUCT_BRIEF.md)。
3. [当前状态](planning/CURRENT_STATUS.md)。
4. [下一阶段](planning/NEXT_PHASE.md)。
5. [系统架构](architecture/SYSTEM_OVERVIEW.md)。
6. [开发流程](delivery/DEVELOPMENT_PROCESS.md) 与 [完成定义](delivery/DEFINITION_OF_DONE.md)。
7. 再阅读改动对应的专题文档、ADR 和测试策略。

## 文档地图

### 产品
- [PRODUCT_BRIEF](product/PRODUCT_BRIEF.md)：愿景、体验支柱、非目标。
- [REQUIREMENTS](product/REQUIREMENTS.md)：带编号的功能和非功能需求。
- [MVP_SCOPE](product/MVP_SCOPE.md)：MVP 边界与退出标准。
- [ROADMAP](product/ROADMAP.md)：Now / Next / Later。
- [DAY1_VERTICAL_SLICE](product/DAY1_VERTICAL_SLICE.md)：Day 1 体验脚本。

### 架构
- [SYSTEM_OVERVIEW](architecture/SYSTEM_OVERVIEW.md)：模块边界与数据流。
- [DATA_AND_CONTENT](architecture/DATA_AND_CONTENT.md)：配置、存档和运行产物。
- [AI_NPC_BOUNDARY](architecture/AI_NPC_BOUNDARY.md)：scripted / hybrid / agent 边界。
- [CLIENT_CONTRACT](architecture/CLIENT_CONTRACT.md)：客户端 API 契约。
- [SCENE_SYSTEM](architecture/SCENE_SYSTEM.md)：场景扩展。
- [ADR 索引](architecture/adr/README.md)：重要架构决策。

### 计划与交付
- [CURRENT_STATUS](planning/CURRENT_STATUS.md)：当前真实状态。
- [NEXT_PHASE](planning/NEXT_PHASE.md)：当前唯一阶段计划。
- [BACKLOG](planning/BACKLOG.md)：候选工作。
- [DEVELOPMENT_PROCESS](delivery/DEVELOPMENT_PROCESS.md)：从需求到发布。
- [DEFINITION_OF_DONE](delivery/DEFINITION_OF_DONE.md)：完成定义。
- [TEST_STRATEGY](delivery/TEST_STRATEGY.md)：测试和质量门。
- [RELEASE_PROCESS](delivery/RELEASE_PROCESS.md)：发布与回滚。
- [VERSIONING](delivery/VERSIONING.md)：版本和兼容。
- [PLAYTEST](delivery/PLAYTEST.md)：试玩记录。

### 运行
- [RUNBOOK](operations/RUNBOOK.md)：安装、启动、停止、验证。
- [TROUBLESHOOTING](operations/TROUBLESHOOTING.md)：常见故障。
- [COCOS_SETUP](operations/COCOS_SETUP.md)：冻结的备用客户端。

## 文档更新规则

| 变化 | 必须更新 |
|---|---|
| 产品目标/用户体验 | `PRODUCT_BRIEF.md`，必要时 `REQUIREMENTS.md` |
| MVP 范围 | `MVP_SCOPE.md`、`ROADMAP.md` |
| 当前能力/测试/风险 | `CURRENT_STATUS.md` |
| 下一阶段 | **只更新** `NEXT_PHASE.md`，不要再建第二份 TODO |
| 新候选需求 | `BACKLOG.md`，写优先级和验收 |
| 重要架构 | 新增 ADR；不覆盖历史 ADR |
| API/数据格式 | `CLIENT_CONTRACT.md` / `DATA_AND_CONTENT.md` 与测试 |
| 玩家可见变化 | 根目录 `CHANGELOG.md` |
| 发布 | `VERSION`、`CHANGELOG.md`、发布证据 |

历史计划见 [archive/2026-legacy-plans/README.md](archive/2026-legacy-plans/README.md)。
