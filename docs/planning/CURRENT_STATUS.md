# 当前状态

- **状态**：Current / 权威事实页
- **快照日期**：2026-08-05
- **Git 基线**：`main` / `b7a62e1`（首批真实素材 runtime 接入与盲测准备已提交）
- **版本标识**：`0.4.0-preview.1`（候选工作区；首批 runtime 素材已接入，待推送后核验；未创建 tag）

## 版本收束（2026-08-04）

- `VERSION`、frontend package 与 backend package 已同步为 `0.4.0-preview.1`。
- 候选说明：`docs/delivery/RELEASE_0.4.0-preview.1.md`。
- 当前是可试玩候选工作区，不冒充正式发布：日期闸门迭代已 commit 并 push 到 `origin/main`；尚未创建 tag，也未完成真实首次玩家盲测。
- 素材生产与收件入口：`materials/00_INDEX.md`。

## 交接收束（2026-08-05）

- 已建立素材与宏观优化动态工作台：`docs/planning/MATERIALS_AND_MACRO_REVIEW_LIVE.md`；后续素材审查和优化交流以此为唯一动态入口。
- 已建立智能体交接文档：`docs/delivery/HANDOFF_20260805.md`；包含当前事实、不可破坏边界、验证基线、P0/P1 接手顺序和完成定义。
- 新增素材已完成第一轮宏观审查与技术返工：UI 图标、BGM、ambience v002 可进入内测；关键图/肖像 v002 已重导为真实 PNG / RGBA 透明 PNG 并通过二次复核（尺寸、alpha、sha256 与 MANIFEST 一致）；首批 runtime 已接入并通过截图/构建验收；剩余工作是 3 人陌生玩家盲测。
- 交接前复验：素材检查 `29 requests passed`，关键图/肖像/音频实物规格与台账一致；随后完成日期闸门迭代质量门：后端 `207 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `12 passed`；存在既有 Starlette/httpx 弃用警告和 Phaser chunk 体积警告。
- 素材返工记录：`docs/planning/MATERIALS_REWORK_STATUS_20260805.md`；审查证据图已放入 `docs/delivery/`。

## 第一轮成熟化改造（2026-08-04）

- 已完成实际首屏审计并冻结 `docs/product/UX_MATURITY_PASS_20260804.md`。
- 开场关闭后保留一次三步行动提示；场景 HUD 增加短循环和 NPC 运行态提示。
- 结果面板、任务卡、日志和后端世界权威边界保持兼容。


### 2026-08-04 持续改造切片
- WP-1B 已完成：活动目录通过安全 `preview` DTO 暴露资源成本和收益类别，互动面板展示代价/收益与恢复建议。
- WP-2 第一闭环已完成：Day 1 书库的“公开记录 / 隐瞒符号”在 Day 2 分别解锁“沿共同记录调查 / 坦白补全事实”的专属关系回响。
- WP-2B 已完成：两条关系路线在 Day 3 产生专属事件上下文，边界判定面板直接显示后端 variant 描述，早期选择贯穿三日。
- WP-1C 已完成：移除书库阅览台直接写 flag 的重复“翻阅旧记录”入口，刻印术拼接短玩法成为唯一读书主入口并继续写入 `prologue_reading_done`。
- WP-3A 已完成：reading / meal / patrol 的 panel、结果字段和完成提示进入 `activityRegistry.js`，`FieldSlice.vue` 使用统一活动完成流程；后端纯 activity engine / Session 提交边界保持不变。
- WP-1D 已完成：同一 activity 同时存在 NPC 主动包装与 POI 基础入口时只保留 NPC 入口；无 NPC 主动时基础入口仍保留，固定 NPC / hybrid / agent 可共用 activity id。
- WP-1E 已完成：Day 1 开场只保留“定位第一条线索”单一主 CTA，旁边解释定位后仍需跟随金色指引移动；不改变地图移动和后端结算边界。
- WP-1F 已完成：移除与右侧任务卡重复的左侧大型路线引导，主目标点击入口只留一个；短循环卡继续承担不可点击的玩法解释。
- 边界调查打开初始化改为同步执行，消除快速选择时被延迟 reset 覆盖的偶发确认禁用竞态。
- 两条回响由后端条件互斥过滤，结算写入 flag、关系、永久记忆和紧张原因；跨路线强选原子拒绝。
- 完整 authored effects、记忆文本和最终结算仍只在后端；scripted/hybrid/agent 共用同一事件结果和记忆结构。
- 方案与证据：`docs/planning/MATURITY_STAGE_20260804_DECISION_PREVIEW.md`、`docs/planning/MATURITY_STAGE_20260804_RELATIONSHIP_ECHO.md`、`docs/planning/MATURITY_STAGE_20260804_DAY3_ECHO.md`、`docs/planning/MATURITY_STAGE_20260804_DAY1_SINGLE_ENTRY.md`、`docs/planning/MATURITY_STAGE_20260804_ACTIVITY_REGISTRY.md`、`docs/planning/MATURITY_STAGE_20260804_DAY1_NPC_DEDUP.md`、`docs/planning/MATURITY_STAGE_20260804_DAY1_OPENING_SINGLE_CTA.md`、`docs/planning/MATURITY_STAGE_20260804_DAY1_GUIDANCE_HIERARCHY.md`。
- 验证（2026-08-05 runtime 素材接入后）：后端 207 passed；前端单测 14 passed；production build 通过；Playwright E2E 12 passed。

## 已经完成

### 产品与玩法
- Underworld 分支定位、原创见习记录员身份和卢利特村开场。
- 地图移动、POI 交互、故事事件、昼夜、休息和 Day 1–3 主线。
- 阅读、训练、用餐、边境探查/裁决、三回合北境巡查。
- 敌方意图与克制、HP/MP/体力消耗、边境标记、休息恢复。
- 主目标、今日节奏、收益预览、锁定提示、结果、日志和档案。
- 存档导入导出与新游戏重置。

### NPC 与叙事
- 爱丽丝、尤吉欧、赛鲁卡等资料与数据驱动固定对话。
- 关系、重要记忆、承诺、紧张关系和后续回响。
- 记忆按 `run_id` 隔离。
- scripted 默认；hybrid/agent 配置和回退骨架。
- `ai_provider.py` 已建立统一 Provider 适配器，支持 StepFun / SenseTime / OpenAI-compatible 配置；失败自动回退，不改变 Session 世界事实。
- 后端保有世界事实、资源、剧情闸和奖励最终决定权。

### 工程
- FastAPI + Vue 3/Phaser 主客户端，Cocos 备用骨架。
- 数据驱动地图、活动、剧情、日程、角色配置。
- macOS 一键启动，Windows 与手动入口保留。
- 内容校验、健康检查、JSONL、pytest 和 Playwright。
- 本轮建立产品/需求/MVP/架构/ADR/计划/交付/运维体系和 CI。

## 本轮验证基线（2026-08-04）

- 后端：205 passed；1 个 Starlette/httpx 第三方弃用警告。
- 前端单元测试：12 passed。
- 前端 production build：通过。
- Playwright E2E：11 passed。
- `git diff --check`：通过。
- Playwright 后端/前端端口支持 `E2E_BACKEND_PORT` / `E2E_FRONTEND_PORT` 覆盖；默认端口被占用时可隔离复验。
- 已知非阻塞项：Phaser minified chunk 约 1.48 MB。

## 已知风险

| 等级 | 项目 | 方向 |
|---|---|---|
| High | `FieldSlice.vue`、Phaser scene 仍偏大 | 活动完成流已收束；继续只抽独立纯逻辑/composable，不大拆场景 |
| High | `Session.player_action()` 其余分支仍长 | 活动已使用纯 engine；后续按事务边界逐类提取，不改变提交所有权 |
| Medium | 长线内容多于首三日体验验证 | 先稳定 Day 1–3 |
| Medium | Phaser chunk 约 1.48 MB | 记录预算，后续基于性能数据做懒加载 |
| Medium | 缺少真实首次玩家数据 | 记录完成率、卡点、时长和后果发现率 |
| Medium | 尚无正式 tag/release | 首个候选版开始 SemVer + Changelog + tag |
| Low | Cocos/Web 双路线 | 冻结 Cocos，保持契约即可 |

`docs/archive/` 是历史，不是当前计划。当前任务只看 `NEXT_PHASE.md`。

## 方向调整（2026-08-05）

根据产品方向补充，下一阶段不再把“素材风格锁定与首次盲测”作为唯一前置。当前优先级调整为：

1. Underworld 露茵村早期生活的设定基线；
2. 剧情事件驱动的日期推进；
3. Day 1 真正可玩闭环；
4. 再用素材接入和真人盲测验证吸引力。

### 日期推进调整（已实现，2026-08-05）

- 已删除玩家主动推荐日期/时间推进入口；前端只显示“剧情推进”状态。
- 普通活动只消耗行动时间，不直接跨日。
- 完成必需剧情事件并触发晚间结算后，日期自动进入下一天。
- 旧 `rest_until_next_day` / `home_sleep_until_morning` 只保留兼容语义，实际必须经过 `day_end_gate` 校验。
- 自动 tick、NPC 日程和环境模拟继续运行，但不能绕过剧情闸；跨日会写入 JSONL 审计记录。
- Day 1 需要 `clue_boundary_record`，Day 2 需要 `forest_anomaly_seen`，对应 E2E 已覆盖“未完成不能跨日 / 完成后自动跨日”。


## 日期闸门迭代质量门（2026-08-05）

- 代码提交：`0e70fa5`（叙事基线与文档）→ `8154e7e`（剧情事件驱动日期推进）。
- 后端：`207 passed`；保留 1 个既有 Starlette/httpx 弃用警告。
- 前端：单测 `14 passed`；production build 通过；仅有 Phaser chunk 体积警告。
- E2E：`12 passed`，新增覆盖“无独立时间推进按钮、剧情闸未完成不能跨日、完成事件后休息自动进入下一天”。
- 桌面/移动质量截图：`runs/quality_gate_desktop.png`、`runs/quality_gate_mobile.png`。
- 远端状态：执行 `git fetch origin` 后，`origin/main=25a5f84`；本地 `main=8154e7e`，领先 2 个提交，待推送。
