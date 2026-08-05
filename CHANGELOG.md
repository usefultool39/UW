# Changelog

本项目的玩家可见变化记录在此。版本遵循 Semantic Versioning；当前仍处于 0.x Preview。

## [Unreleased]

### Added

- 建立《刀剑神域 Alicization / Underworld》第一章的叙事参考基线，明确露茵村早期生活分支、古誓树/天职、教会制度压力与北境异常的递进关系。
- 为剧情节点增加日期闸门元数据（`required_for_day`、`day_end_gate`、`advance_policy`），让后续章节可以继续使用数据驱动的剧情推进。

### Changed

- 删除玩家主动推荐日期/时间的独立操作入口；普通活动现在只消耗行动时间，不直接推进日期。
- 日期改为由关键剧情事件触发，并在满足当日剧情闸、完成晚间结算且玩家在家中休息后自动进入下一天。
- 保留 NPC、环境和模拟 tick 的自动运行，但自动 tick 不得绕过剧情闸门。
- Day 1 / Day 2 的最小主线分别以“记录边界线索”和“目击森林异常”为跨日条件，形成 Day 1 → Day 2 → Day 3 的可验证纵向闭环。
- 前端将时间状态改为非交互的“剧情推进”提示，并在未满足闸门时显示缺失事件与恢复建议。
- 首批已审核素材进入 runtime：UI 影响图标、肖像 v002 256 派生图、Day 1 村庄关键图、BGM A 与 ambience A v002；所有素材均保留缺失回退。

### Verification

- 2026-08-05 质量门：后端 `207 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `12 passed`；`git diff --check` 通过。已知非阻塞警告：Starlette/httpx 弃用提示、Phaser chunk 约 1.48 MB。

## [0.4.0-preview.1] - 2026-08-04

### Added

- 开场关闭后增加 Day 1 三步短引导，明确“线索 → 选择 → 关系回响”。
- 场景 HUD 增加短循环、资源结算和固定 NPC / hybrid / agent 运行态提示。
- 行动面板显示时间/资源代价、关系/记忆/线索收益与不可用行动的恢复建议。
- Day 1 书库“公开记录 / 隐瞒符号”会在 Day 2 森林异常中分别解锁专属关系回响；选择结果写入关系、永久记忆和后续 flag。
- Day 3 边界判定会显示前两天共同记录或坦白补全事实的专属上下文，让早期关系选择贯穿三日收束。
- Day 1 书库阅览台收束为一个明确读书主入口，避免“直接标记完成”和短玩法同时争夺注意力。
- 北境短程巡查三回合玩法、敌方意图与克制判断。
- scripted / hybrid / agent NPC 运行骨架和数据驱动固定对话。
- macOS 一键启动入口。
- 产品、需求、MVP、路线图、ADR、计划、测试、发布和运维文档体系。
- GitHub Actions 质量门与 Issue/PR 模板。
- 可长期维护的素材需求、收件、权利记录和验收工作区（`materials/`）。

### Changed

- 开场与主线聚焦为 Underworld 分支篇的见习记录员视角。
- 统一行动收益预览、今日节奏、公开角色术语和休息恢复。
- Day 2 边界调查小游戏优先展示与 Day 1 书库选择对应的行动态度，同时保留既有通用和晚餐回响路线。
- Day 3 结局判定面板新增后端事件上下文层，叙事 variant 不再只存在于数据中。
- 历史计划归档，`CURRENT_STATUS` / `NEXT_PHASE` 成为单一事实来源。
- 活动 UI 分发与后端资源规划逐步从巨型文件提取为独立模块。
- reading / meal / patrol 的 panel、结果字段和完成提示统一进入活动 registry，三套完成回调收束为同一流程。
- 同一场景活动同时由固定 NPC 主动邀请和 POI 暴露时，优先保留带人物语境的 NPC 入口；普通入口仍在没有主动邀请时可用。
- Day 1 开场收束为一个“定位第一条线索”主 CTA，并明确点击后要跟随金色指引移动，避免两个近义入口争抢首次注意力。
- 开场后的主目标操作统一到右侧任务卡；移除遮挡地图且与任务卡重复的左侧大型路线引导，只保留短循环解释。

### Fixed

- 非当前路线的 Day 2 关系选择由后端拒绝，且不部分写入状态、关系或记忆。
- 移除可绕过刻印术拼接玩法的重复读书快捷入口；主活动仍写入相同进度 flag。
- NPC 记忆按 run 隔离，避免新游戏继承旧周目内容。
- 危险活动先校验资源，避免失败时部分写入状态。
- 边界调查面板打开时同步重置局部选择，避免极快操作被延迟初始化覆盖而导致确认按钮偶发不可用。

### Verification

- Backend pytest 205 passed；frontend unit 12 passed；production build passed；Playwright E2E 11 passed；`git diff --check` passed。
- 候选说明：`docs/delivery/RELEASE_0.4.0-preview.1.md`。

## 历史

仓库在建立正式版本治理前已有 54 个提交，未创建 tag。详细演进请使用 `git log` 和 `docs/archive/2026-legacy-plans/`；不伪造历史版本号。
