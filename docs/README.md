# UW 文档地图

仓库只维护一套当前文档。版本、目标、状态和计划不得复制到新的日期文件中。

## 必读

| 文档 | 唯一职责 |
|---|---|
| [MASTER_GUIDE.md](MASTER_GUIDE.md) | **统一项目指南（唯一入口，包含一切）。永远先读这一份。** |
| [GAMEPLAY_DESIGN.md](GAMEPLAY_DESIGN.md) | 玩法与内容设计详细总纲（融合所有旧 v001/v002 写作文档） |
| [PROJECT.md](PROJECT.md) | 项目总纲（精简版） |
| [PLAN.md](PLAN.md) | 当前事实、优先级、执行顺序、验收、风险和冻结项 |
| [art/ASSET_REVIEW.md](art/ASSET_REVIEW.md) | 素材可用性、返工意见、缺口和制作规格 |
| [art/GENERATION_AGENT_PROMPT.md](art/GENERATION_AGENT_PROMPT.md) | 生图智能体的统一输入、生成、验收、交付和停止规则 |
| [art/ASSET_TASKS.md](art/ASSET_TASKS.md) | 当前版本按优先级排列的素材任务与输出要求 |
| [DELIVERY.md](DELIVERY.md) | Git、开发、测试、盲测、发布和版本规则 |

## 按需参考

- [architecture/SYSTEM_OVERVIEW.md](architecture/SYSTEM_OVERVIEW.md)：架构总览。
- `docs/architecture/adr/`：不可逆架构决策。
- `docs/architecture/` 其他文件：AI、客户端、场景和数据合同。
- [operations/RUNBOOK.md](operations/RUNBOOK.md)：启动与运行。
- [operations/TROUBLESHOOTING.md](operations/TROUBLESHOOTING.md)：故障排查。
- [../materials/README.md](../materials/README.md)：素材工作区与台账规则。

## 更新规则

- **任何重大变化 -> 同步更新 `MASTER_GUIDE.md`（唯一入口）**
- 玩法与内容设计变化：更新 `GAMEPLAY_DESIGN.md`（不创建新版本）。
- 范围与设计变化：更新 `PROJECT.md`。
- 完成度、优先级和验收变化：更新 `PLAN.md`。
- 素材状态变化：更新 `ASSET_REVIEW.md` 与素材台账。
- 工程流程变化：更新 `DELIVERY.md`。
- 架构所有权变化：新增或替换 ADR。
- 历史过程：交给 Git 提交和 PR，不新增仓库内历史副本。
