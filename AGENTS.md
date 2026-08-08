# UW 协作规则

进入仓库后按顺序阅读：

1. `docs/MASTER_GUIDE.md` -- **统一项目指南（唯一入口，包含一切）**
2. `docs/GAMEPLAY_DESIGN.md` -- 玩法与内容设计详细总纲
3. `docs/PLAN.md` -- 当前状态和执行计划
4. `docs/art/ASSET_REVIEW.md` -- 素材审查与制作清单
5. `docs/art/ASSET_TASKS.md` -- 素材任务单
6. `docs/art/GENERATION_AGENT_PROMPT.md` -- 生图智能体主 Prompt
7. `docs/DELIVERY.md` -- 交付规则

## 当前唯一目标

完成版本 `0.6.0` 的卢利特村序章纵切片：玩家身份为桐人，主线从三人村庄日常推进到爱丽丝在村中被带走。同时实现玩法优化（关系可视化、日常活动丰富化、物品栏、小游戏深化），让玩家"想再多玩一天"。旧"见习记录员"、月度路线、长期 Day 编号和历史升级代号均已停止。

## 不可破坏的边界

- FastAPI 是位置、时间、资源、flag、关系、剧情闸和永久记忆的权威。
- scripted NPC 是无模型 API 时的完整产品基线；hybrid/agent 必须可回退。
- 被拒绝的行动不得部分写入状态。
- 未审核素材不得进入 runtime。
- `sample_candidate` 只表示已收到的候选样张，不表示内容、透明度、权利或游戏内验收通过；没有人工结论前不得改成 `approved-candidate`、填写 `runtime_file` 或接入 runtime。
- `runs/`、`data/memory/`、`frontend/dist/`、密钥和本地环境不得提交。
- 架构所有权变化先写 ADR；产品范围变化先修改 `docs/MASTER_GUIDE.md`。

## 文档纪律

- 不新增日期型 status、handoff、upgrade、phase 或版本副本。
- **不创建新的 v003/v004 写作文档副本；所有内容变更直接修改 `docs/MASTER_GUIDE.md` 或 `docs/GAMEPLAY_DESIGN.md`**。
- 当前完成度和下一步只写入 `docs/PLAN.md`。
- 玩家可见名称、文档标题和沟通使用自然语言，不暴露内部 ID。
- 素材请求 ID 只保留在 `REQUESTS.csv`、`MANIFEST.csv` 和素材 sidecar 中。
- 旧事实使用 Git 历史追溯，不在仓库内继续复制归档文档。

## 完成前

```bash
./scripts/quality.sh
./scripts/release.sh   # 仅在准备发布时运行
```

用户可见改动更新 `CHANGELOG.md`；测试和交付证据更新 `docs/PLAN.md`；素材结论更新 `docs/art/ASSET_REVIEW.md`；玩法和内容设计变更更新 `docs/GAMEPLAY_DESIGN.md`；**任何重大变化同步更新 `docs/MASTER_GUIDE.md`**。

当前素材统一从各分类的 `current/` 目录读取，不使用修订号作为入口。地图、三位角色、抓捕关键图、VFX 和 SFX 均为候选：地图有水印残留；角色锚点 alpha 检查失败；关键图仍是黑白构图；静默线语义偏离；SFX 仍待人耳 QA。
