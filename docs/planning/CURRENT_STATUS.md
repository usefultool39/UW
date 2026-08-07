# 当前状态

> **项目级交接入口**：[PROJECT_HANDOFF_20260807.md](../delivery/PROJECT_HANDOFF_20260807.md)。它汇总版本、Git、架构、素材/盲测机制、质量门和下一智能体启动提示词；本页继续作为真实完成度和测试数字的权威事实页。

> **最新素材收件快照**：[ASSET_HANDOFF_SNAPSHOT_20260807.md](../delivery/ASSET_HANDOFF_SNAPSHOT_20260807.md)。2026-08-07 后续收件的地图 v004、环境 v004、角色 v005 仍未通过 active v004 contract；不要仅因文件存在或视觉质量提升而上调状态。

## 2026-08-07 Pre-Capture runtime checkpoint

- Authored story remains integrated and verified: four acts, N01-N10, fixed `alice_captured` endpoint, and 46 detected cross-node echoes. `story=ready`; legacy events are isolated behind backend-authoritative route flags.
- N10 now submits its authored choices through the verdict panel. A fresh-port `CI=1` verification on 2026-08-07 passes the Day 54 to Day 61 targeted case (`1/1`), the complete field smoke (`20/20`), and the full Playwright suite (`22/22`), including the continuous N01-N10 desktop route and touch-sized first interaction.
- Overall Pre-Capture readiness is now reported accurately as `materials=pending, story=ready`. The seven narrative input requests pass, but 16 first-phase runtime requests are part of the materials gate.
- The incoming v003 packages for `VIS-MAP-001`, `VIS-CHR-001` to `003`, `VIS-ENV-001`, `AUD-BGM-002`, `AUD-BGM-003`, and `AUD-AMB-002` are `changes_requested`. They have delivery fragments but do not satisfy the project schema/visual review; none entered formal MANIFEST or runtime. The active correction contract is v004.
- The v003 delivery snapshot is now in inbox but remains rejected: `check_materials.py` reports 7 unregistered intermediate-file errors, and the v003 runtime review reports 76 schema/path/visual-delivery issues. These are delivery blockers, not accepted or runtime-complete assets.
- The active runtime asset contract has moved non-destructively to v004. It intentionally reports missing v004 files until corrected deliveries arrive; v002/v003 findings remain audit evidence. The gate is read-only and runs from `scripts/quality.sh`.
- The runtime asset gate now decodes non-interlaced 8-bit PNG scanlines and requires both visible pixels and actual transparent pixels; an opaque RGBA sheet with a baked checkerboard is rejected. It also validates OGG page framing so arbitrary files cannot pass by existence alone. The focused runtime-spec suite is `8 passed`, including a regression lock that keeps the active replacement contract on v004.
- `check_materials.py` now also rejects orphan files under `frontend/public/assets/runtime`, runtime paths from non-approved manifest statuses, and runtime paths without reviewer/timestamp evidence. The current runtime directory exactly matches registered manifest paths; its focused registry suite is `5 passed`.
- Successful engineering baseline in the project Python environment: backend `330 passed` with one existing Starlette/httpx deprecation warning; frontend unit `16 passed`; production build passed; `git diff --check` passed. The latest targeted Pre-Capture E2E passed `2/2`; the previous fresh-port full-suite `22/22` remains historical successful evidence. A new full-suite attempt timed out in the legacy field smoke, so it is a monitored orchestration/runtime risk rather than a current full-gate pass. Active v004 runtime specs report `52 issues`; materials registry reports `7 errors`; readiness remains intentionally pending until corrected deliveries arrive.
- First phase is not complete: playable production map, real Sprite animation, VFX, capture presentation, complete audio/SFX, runtime acceptance, and 3-player blind testing remain open. `QA-PLAY-001` is still `pending-human-run` (`0/3`).
- Material handoff is now consolidated in `docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md`: five failed v002/v003 packages have a single v004 delivery contract, role boundary, three-layer status model, eight-step acceptance chain, and one copyable prompt. The 2026-08-05 handoff and live review board are explicitly historical.
- Project handoff is consolidated in `docs/delivery/PROJECT_HANDOFF_20260807.md`. `QA-PLAY-001` now requires each of three unfamiliar players to complete N01-N10, reach `alice_captured`, and verify post-capture progression is blocked; the older Day 1 kit remains onboarding evidence only.
- Handoff closeout rerun: backend `330 passed`, frontend unit `16 passed`, production build passed, and `git diff --check` passed. Targeted Pre-Capture Playwright on isolated ports `8034/4194` passed `2/2` (desktop N01-N10 plus 390x844 first interaction). A new full-suite attempt on `8033/4193` timed out in the legacy Day 54-61 `field-smoke` after the page reported a map-load/unknown-location state and the retry lost the frontend connection; therefore the earlier fresh-port `22/22` remains the last successful full-suite evidence, not a result from this closeout rerun.

The sections below are retained as historical iteration records. When their older test counts or readiness labels conflict with this checkpoint, this checkpoint is authoritative.

- **状态**：Current / 权威事实页
- **快照日期**：2026-08-07
- **Git 基线**：`main` / `5ca1cb6`，工作区包含尚未提交的 Pre-Capture 收束改动
- **版本标识**：运行时仍为 `0.4.0-preview.1`；当前目标为尚未发布的 `0.5.0-pre-capture`

## 0.5 当前快照（先读本节）

- 当前产品目标已改为忠实覆盖 Alicization 前期从卢利特村日常到爱丽丝被整合骑士带走；旧“原创见习记录员分支”不再是当前定位。
- Vue 3 + Phaser 3 + FastAPI 技术栈、地图/活动、关系/记忆、日期闸、存档、离线 scripted、内容校验和自动测试基础已存在，继续复用。
- 正式 Pre-Capture 剧情已完成自动 authored contract 校验：四幕、N01-N10、唯一抓捕终点和跨节点回响均已存在；它仍未达到第一阶段完成，因为正式素材验收与真人盲测未完成。
- 当前 readiness 为 `materials=pending, story=ready`；7 项叙事输入通过，16 项 runtime 输入中有 8 项 `changes_requested`、4 项 `deferred`，因此不能把材料登记误写成正式素材完成。
- 已有候选/内测素材：开场关键图、部分肖像/UI、第一批 BGM/环境声。新收到的地图、核心 Sprite、六场景和第二批音频均留在 inbox 返工；仍缺互动动作、完整图标/VFX、SFX、抓捕关键图和整合骑士素材。
- 当前框架不迁移，完整战斗延后到独立原型。视觉/音频智能体只交付素材；剧情、代码、接入、审核和 QA 由本项目流程完成。
- `VIS-KA-002`、`VIS-CHR-005`、`VIS-ANIM-001`、`VIS-TILE-001` 已补登记为 `P1/deferred`，尚未生成或验收；0.5 的首批生产队列仍以素材审计列出的地图、核心 Sprite、场景、VFX 和音频为准。
- 本轮 0.5 Pre-Capture 验证以本页顶部 Runtime checkpoint 为准；下方历史迭代数字只保留审计。稳定快照：v003 materials `7 errors`、v003 runtime review `76 issues`、active v004 contract pending；工程门 backend `330 passed`、frontend unit `16 passed`、build passed、Playwright `22 passed`。
- 当前唯一执行入口是 [NEXT_PHASE.md](NEXT_PHASE.md)，素材细目见 [MATERIALS_AUDIT_20260807.md](../delivery/MATERIALS_AUDIT_20260807.md)。

> 下方 Day 1–117、原创见习记录员、月度循环和旧测试数字是系统演进/兼容记录。保留它们用于审计，但不得据此判断当前正典主线已完成，也不得从中继续扩写 Day 118+。

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


## 最新长期目标切片（2026-08-05，待提交）

- AI 记忆候选现在必须经过 `backend/app/memory_policy.py` 的确定性筛选：来源白名单、类型、长度、权重、注入标记与 AI 置信度均受控；普通低权重 fallback 对话不会误写永久重要记忆。
- 新增 `backend/app/npc_intent_agent.py` 与 `backend/app/intent_policy.py`：模型只能从当前 authored NPC intent/response 中提出预览建议；`POST /api/npc/{npc_id}/intent/propose` 不直接提交世界效果。
- 新增 `backend/app/agent_budget.py`：每局默认总计 24 次 AI 调用（action 12、dialogue 12、intent 6），耗尽后自动回退 scripted/heuristic，并写入 JSONL 审计。
- LLM 行动失败时回退 heuristic；对话返回和事件新增 `memory_decision`、`memory_committed`、`ai_budget`。
- 本轮验证：后端 `237 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `12 passed`；`git diff --check` 通过。
- 当前仍未调用真实外部 API，未读取或修改 `/Users/lzm/Desktop/ai-shop`，未宣称完成真人盲测或商业化授权。
- 最新 Git 状态：`main...origin/main` 已同步，远端与本地均为 `ac67991`。
- 本轮新增存档导入安全：清空旧 pending 写入、重置单局 AI 预算、过滤导入记忆危险文本；后端质量门更新为 `237 passed`。
- 本轮新增 Day 4 / Day 7 / Day 12 / Day 18 / Day 24 / Day 28 显式剧情闸门：第一月关键 authored 事件现在不能被连续休息直接跳过；后端质量门更新为 `242 passed`，Playwright E2E 更新为 `13 passed`。
- 修复边界调查小游戏父级重渲染导致选择状态偶发清空的问题，并让 E2E 等待每个选择真正进入 selected 状态。
- Day 8–16 第一轮短循环反馈已接入：巡查板复核 / 村道传闻会影响 Day 12 事件视图但不阻塞主线；内容校验新增日期闸门可达性检查；后端质量门更新为 `244 passed`。
- E2E 后端通过 `UW_RATE_LIMIT_ENABLED=0` 隔离本地 smoke 请求；生产默认仍开启 SlowAPI 限流。

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

## 2026-08-05 最新增量：Day 8–16 回响反馈

- 村道传闻与巡查板活动现在在行动卡上显示具体的玩家可见收益，不再只显示抽象的“关系 / 进度”。
- Day 18 静默线演练会根据 Day 8–16 的公开安全流程、邀请村民记录或村道传闻，显示不同的事件描述和选择提示；这些是可回放的 authored 叙事反馈，不绕过日期闸门。
- 新增后端 API、故事 Director 与前端行动预览回归测试；本轮质量门已通过：后端 `246 passed`、前端 `15 passed`、build 通过、Playwright `13 passed`、`git diff --check` 通过。

## 2026-08-06 第一月路线连续性与真人盲测状态

- Day 24 远征包事件会读取 Day 12 的 `month01_public_patrol` / `month01_supply_route` 路线，继续反馈公开村务或低调筹备的长期后果。
- 北门静默线复核活动会在行动前说明其后续用途，减少“做了活动却不知道有什么意义”的问题。
- 首轮真人盲测的执行跟踪表已建立：`docs/delivery/PLAYTEST_ROUND_01_TRACKER_20260806.md`。
- 当前状态仍为 `pending-human-run`；现有 Playwright 结果不能替代真实玩家证据，未伪造任何玩家记录。
- 本轮质量门：后端 `247 passed`、前端 `15 passed`、build 通过、Playwright `13 passed`、`git diff --check` 通过。

## 2026-08-06 数据驱动活动可直接游玩

- 修复“活动 JSON 有 choices，但玩家从 UI 无法选择”的可玩性断层；`route_drill`、`public_record`、`silent_line_check`、`expedition_pack`、`month_gate_vigil` 现在统一进入场景选择面板。
- 选择面板会显示做法、提示、同伴关系变化和谁会记住，不向前端暴露 flags 或记忆正文；最终效果仍由 FastAPI Session 权威结算。
- Day 5–6、Day 8–11、Day 13–17 新增 authored NPC 主动入口，让北门退路预演、巡查板复核和静默线复核能在第一月关键剧情之间被真实发现和完成。
- 月末守夜现在也必须明确选择“复核记录与承诺”或“复走撤退线”，不再静默跳过选择。
- 本轮质量门：后端 `249 passed`、前端 `16 passed`、build 通过、Playwright `14 passed`、`git diff --check` 通过。

## 2026-08-06 第二月可玩短循环

- 第二月不再只是单击活动骨架：Day 32 的稳守、远征、静默三条路线现在各有两种可选做法，并写入独立关系、记忆和路线 flags。
- Day 39 的 NPC 主动描述会读取 Day 32 选择：公开轮值/受训核心、回撤标记/扩大测距、见证人链/信号模式分别产生后续语境。
- Day 46 异常信号汇流要求玩家决定公开共同异常地图，或暂时保留在三人记录里；结果写入第二月后半段公开路线或暗线路线。
- Day 31、Day 32、Day 39、Day 46 已加入 authored 日期闸门，正常游玩不能再通过连续休息跳过第二月关键内容。
- 含 choices 的场景活动现在必须明确选择；缺失选择会在任何状态写入前返回 `activity_choice_required`。
- 内容校验覆盖 `required_any_flags` 的生产来源，避免三路线任一完成条件配置成无法到达。
- 本轮质量门：后端 `253 passed`、前端 `16 passed`、build 通过、Playwright `15 passed`、`git diff --check` 通过。


## 2026-08-06 第二月 Day 47 → 53 路线结果

- Day 46 的公开地图 / 三人暗线选择现在各自进入一项 Day 47–52 可玩活动：`village_shared_map_hearing` 或 `north_gate_team_source_probe`。
- 两项活动都要求玩家明确选择做法，并在行动前展示关系数值、记忆对象、承诺和 Day 53 后果；活动只在 Day 47–52 开放。
- Day 49 新增剧情闸门，公开路线必须完成共同地图听证准备，暗线路线必须完成三人源头试探，不能连续休息跳过。
- Day 53 新增 `ch1_d53_second_month_result`：公开路线只显示“正式边界听证 / 只公开警告”，暗线路线只显示“继续三人追查 / 交出密封副本”。
- 四个结果会写入不同的第三月入口 flag、关系、紧张、承诺和长期记忆；Day 53 完成事件后才能进入 Day 54。
- 场景活动引擎和前端可用性判断新增 authored `day_min` / `day_max` 日期窗口，越界调用会原子返回 `wrong_day_range`。
- scripted 模式继续完整离线可玩；FastAPI Session 仍是日期、flags、关系、记忆和存档的唯一权威。
- 首轮真人盲测仍为 `pending-human-run`；本轮 E2E 只证明自动化路径，不替代真实玩家证据。
- 本轮质量门：后端 `261 passed`；前端单测 `16 passed`；production build 通过；Playwright E2E `16 passed`；`git diff --check` 通过。既有 Starlette/httpx 弃用警告和 Phaser 约 1.48 MB chunk 警告保持非阻塞。


## 2026-08-06 第二月 Day 54 → 61 尾声闭环

- Day 53 四种结果现在各有一项 Day 54–60 路线专属尾声活动：听证规则落地、分层警告演练、源头追查校准、密封副本托管。
- 四项活动各有两个明确做法，都会写入共同的 `month02_tail_feedback_done`、路线专属 flag、关系、长期记忆，并在部分路线记录承诺或紧张变化。
- Day 58 新增尾声剧情闸门，玩家必须把第二月结果落成可执行规则，不能直接睡到月末。
- Day 61 新增 `ch1_d61_third_month_departure`；事件根据当前尾声路线只显示两个第三月准则，共八种可到达入口。
- Day 61 结果写入 `month03_departure_ready` 和对应第三月 route flag；完成事件后才能进入 Day 62。
- 月计划路线摘要现在优先显示 Day 53 的最终结果，不再只显示 Day 31 的稳守 / 远征 / 静默入口。
- 四种尾声都有 authored NPC 主动入口；Playwright 已覆盖正式听证 → 双人复核 → 第三月公开议事的完整 UI 路径。
- scripted 模式、Session 权威状态和 AI 回退边界保持不变；没有读取 `ai-shop`，没有调用真实 Provider。
- 首轮真人盲测仍为 `pending-human-run`，自动化测试不冒充玩家证据。
- 本轮质量门：后端 `268 passed`；前端单测 `16 passed`；production build 通过；Playwright E2E `17 passed`；内容校验 0 errors / 0 warnings；`git diff --check` 通过。


## 2026-08-06 第三月 Day 62 → 69 资源型短循环

- 新增 `/Users/lzm/Desktop/UW/data/story/month_03_plan.json`，第三月 Day 62–75 归并为三类可维护玩法族：公开协作、源头追查、责任情报。
- Day 62–68 新增三项路线专属资源活动：村务支持分配、边境负载选择、情报托管预算。
- 每项活动有两个真实资源方案，玩家会在行动前看到选择的体力 / 神圣力代价；后端会原子校验资源，不足时不会写入 flags、关系、记忆或一次性完成状态。
- 修复 authored `stamina_cost: 0` 被旧默认值误读为 8 的问题，允许“低体力、高神圣力”和“高体力、低神圣力”成为真实取舍。
- 场景选择公开预览增加资源代价 / 恢复信息，前端选择卡可以直接显示“体力 -3、神圣力 -10”等后果。
- Day 65 新增资源准备闸门；Day 69–74 新增 `ch1_d69_third_month_route_test`，根据具体资源方案只显示两个路线结果；Day 75 必须完成路线测试后才能进入 Day 76。
- 日志现在自动切换到第三月计划，并显示第三月标题与公开协作 / 源头追查 / 责任情报路线摘要；第一月旧标题保持兼容。
- 第三月活动和事件都补充 NPC 主动入口，scripted 模式保持完整离线可玩；没有读取 `ai-shop`，没有调用真实 Provider。
- 首轮真人盲测仍为 `pending-human-run`，自动化结果不替代真实玩家数据。
- 本轮质量门：后端 `277 passed`；前端单测 `16 passed`；production build 通过；Playwright E2E `18 passed`；内容校验 0 errors / 0 warnings；`git diff --check` 通过。


## 2026-08-06 第三月 Day 76 → 89 后果反馈与安全恢复

- Day 76–82 新增三类路线反馈活动：公开协作反馈、源头追查反馈、情报风险反馈；每项都读取 Day 69 的具体结果 flag，并把覆盖范围、缓存 / 中止线或情报风险写回下一阶段。
- Day 78–82 新增 `home_third_month_recovery_debrief`，玩家必须在体力恢复和神圣力恢复之间做一次安全选择；恢复不会跨日，也不会自动抹掉另一种资源的不足。
- Day 79 新增闸门，必须完成路线反馈和安全恢复；Day 83–88 新增 `ch1_d83_third_month_stage_result`，按三类玩法族只显示两个阶段决定；Day 89 必须完成阶段事件。
- 阶段决定会写入公开协作扩大 / 保守、源头路线延长 / 守住缓存、分层情报扩大 / 继续封存等后果 flags，并继续影响月计划摘要。
- 日志新增独立“当前承诺 / 紧张点”栏目，将 NPC profile 中的承诺与紧张从关系数值区分出来；不暴露永久记忆正文或控制 flags。
- 第三月 Week 11/12 已写入 `/Users/lzm/Desktop/UW/data/story/month_03_plan.json`；第三月第一次资源型循环现在完整覆盖 Day 62–89。
- scripted 模式、Session 权威状态和 AI 回退边界保持不变；没有读取 `ai-shop`，没有调用真实 Provider。
- 首轮真人盲测仍为 `pending-human-run`，自动化结果不替代真实玩家数据。
- 本轮质量门：后端 `284 passed`；前端单测 `16 passed`；production build 通过；Playwright E2E `19 passed`；内容校验 0 errors / 0 warnings；`git diff --check` 通过。


## 2026-08-06 第三月 Day 90 → 103 后果与承诺循环

- Day 90–94 新增三项路线专属每日一次活动：公开协作短轮值、源头固定短段取样、分层情报责任复核；活动复用村道广场、北门和书库，不扩张地图。
- 新增 `home_third_month_resource_status`，玩家必须明确选择优先恢复体力或神圣力；面板和结果会说明保留的另一类资源限制，恢复不会自动跨日。
- Day 94 新增日期闸门，要求至少完成一次路线练习和一次资源状态说明；Day 95 的 `ch1_d95_third_month_consequence_review` 只显示当前玩法族的两个后果选择。
- Day 96–102 新增三项可重复承诺回访活动；每天最多一次，至少完成一次后才能完成 Day 103 阶段结算。
- Day 103 新增 `ch1_d103_third_month_boundary_decision`，将公开轮值、源头取样或三重托管的后果写入下一阶段入口。
- NPC authored intent 已覆盖 Day 90–103 全部关键入口；scripted 离线基线、Session 权威状态和 AI 不越权边界保持不变。
- 第三月计划现已覆盖 Day 61–103，新增 Week 13/14 维护性内容与素材替换需求。
- 首轮真人盲测仍为 `pending-human-run`；自动化结果不替代真实玩家证据。
- 本轮质量门：后端 `288 passed`；前端单测 `16 passed`；production build 通过；Playwright E2E `20 passed`；内容校验 `0 errors / 0 warnings`；`git diff --check` 通过。


## 2026-08-06 素材完整性与真人盲测交付入口

- 强化 `materials/tools/check_materials.py`：现在同时检查 REQUESTS、inbox sidecar、MANIFEST 来源文件 SHA-256，以及所有已登记 runtime 文件的路径、存在性、hash 和 `integrated_at`。
- 修正 MANIFEST 中 `QA-PLAY-001_playtest_kit_v001.md` 与 `audio.meta.json` 的两条历史 hash 漂移；当前素材校验通过。
- 新增 `/Users/lzm/Desktop/UW/试玩盲测.command`：固定 `scripted`、production build、内容校验、一次性重置试玩 Session；如果安装了 Chrome，会打开隐身窗口。
- 新增 `/Users/lzm/Desktop/UW/scripts/playtest-preflight.sh`：默认执行依赖检查、素材校验、质量门和完整 E2E；`--quick` 跳过 E2E。
- 新增 `/Users/lzm/Desktop/UW/scripts/check_playtest_round.py` 与三个空白匿名记录模板；默认只报告 `pending-human-run`，只有真实回填满足字段后才允许 `--require-complete` 通过。
- 盲测启动记录写入被 Git 忽略的 `runs/playtest/`，只作为环境元数据，不伪造玩家证据。
- 本轮快速预检：后端 `293 passed`；前端单测 `16 passed`；build 通过；材料与 runtime hash 校验通过；Playwright E2E `20 passed`。真人盲测仍为 `pending-human-run`。

## 2026-08-06 Pre-Capture 方向审计

- 长期目标已锁定为从卢利特村可信日常连续玩到爱丽丝被整合骑士带走；后续章节另立阶段。
- Alicization 第一季官方 `Episode 1: Underworld` 与 `Episode 3: The End Mountains` 已作为当前事实锚点；“End of World”尚未确认是独立正传电影名。
- 当前运行时已有 21 个主事件和 28 个日期闸门，覆盖到 Day 117，但尚无尽头山脉越界和抓捕终点；长线循环不能替代目标剧情完成度。
- 运行数据仍存在旧角色名/旧术语，后续新文本必须统一正典显示名，旧 ID 仅保留兼容。
- 当前停止扩写 Day 118+；等待用户返还 `NAR-CANON-001` 等需求素材后，按四幕、8–12 个关键节点完成 Pre-Capture 主线。
- 执行入口：`materials/11_PRECAPTURE_EXECUTION_BRIEF.md`；素材与交流继续以 `materials/` 和 `MATERIALS_AND_MACRO_REVIEW_LIVE.md` 为单一入口。
## 2026-08-06 Pre-Capture readiness check

- Added `materials/tools/check_precapture_readiness.py` as a read-only report for the seven P0 material requests, source registration, four authored acts, 8-12 key nodes, fixed capture endpoint, and cross-node echoes.
- Current report is `materials=pending` and `story=pending`: the existing story file has 21 events but no Pre-Capture authored markers, fixed Alice capture endpoint, or readiness-contract echoes.
- Fixed `check_materials.py` text hashing for Windows `core.autocrlf=true`; `.md/.svg/.json/.csv` hashes are normalized to Git LF bytes while binary hashes remain byte-exact. Materials validation now passes for 36 requests.
- Added readiness and text-hash regression tests. Focused tests pass `5 passed`. Empty P0 delivery directories only keep requested inbox paths valid; they do not mean materials were received.
Added incremental validation for `precapture_act`, `precapture_key_node`, and `precapture_endpoint`; legacy events remain compatible, while marked capture events must write an allowed capture `ending_id` through a choice effect.
## 2026-08-06 Backend environment recovery

- Created the project-local `backend/.venv` from Python 3.11 and installed `backend/requirements.txt`; the existing start and quality scripts can now use their declared interpreter path.
- Full backend regression: `299 passed`, with one existing Starlette/httpx deprecation warning. This verifies the current story/session/API baseline plus the Pre-Capture contract tests.

## 2026-08-06 Windows E2E revalidation

- Full Playwright regression passed on isolated ports: `20 passed` (`E2E_BACKEND_PORT=8011`, `E2E_FRONTEND_PORT=4174`).
- A first run on the common `8765/3000` ports reused an unstable local service and produced cascading connection refusals; the isolated rerun confirms this was not a gameplay regression.
- Playwright now discovers the project-local Windows Python at `backend/.venv/python.exe` (and standard `Scripts/python.exe`) before the legacy `.conda/uw-runtime` fallback, so `npm run test:e2e` no longer requires a manual `PYTHON_BIN` override.

## 2026-08-06 Return packet and Windows quality gate

- `scripts/quality.sh` and `scripts/playtest-preflight.sh` now discover `backend/.venv/bin/python`, Conda-style `backend/.venv/python.exe`, standard Windows `Scripts/python.exe`, and the legacy runtime in that order; an explicit `PYTHON_BIN` still wins.
- Added return instructions to all seven Pre-Capture P0 inbox directories. These README files are ignored by readiness counting and do not change any request from `requested` to `received`.
- Windows Git Bash quality gate passed with no manual Python override: materials `36 requests`, backend `299 passed` with one existing deprecation warning, frontend `16 passed`, production build passed, and `git diff --check` passed.
- Quick playtest preflight passed and recorded automated readiness only; `QA-PLAY-001` remains `pending-human-run` with `0/3` human runs.
- Full Playwright E2E also passed without `PYTHON_BIN` override on isolated ports `8013/4176`: `20 passed`.
- Pre-Capture readiness now validates sidecar metadata (`request_id`, source, date, license, source URL, intended use) for seven narrative and 16 first-phase runtime requests, and rejects MANIFEST sources outside the request delivery directory.
- Marked Pre-Capture events now reject deprecated player-facing terminology and explicit post-capture spoilers. The capture endpoint must be a key node, appear exactly once as the final marked node, and use a matching choice `ending_id`; focused content/readiness tests pass `16 passed`, and the latest full quality gate passes with backend `306 passed`, frontend `16 passed`, and a successful production build.
- The capture endings `alice_captured` and `precapture_alice_captured` are now hard chapter terminals: story events, time/day progression, authored flags, NPC responses, dialogue, and story-node advancement are rejected after capture. Movement and scene/hub viewing remain available, while legacy route labels such as `cross` retain their existing non-terminal behavior.
- Terminal-state regression coverage passes in `backend/tests/test_story_director_events.py`; no Pre-Capture authored content has been accepted yet, so readiness remains `materials=pending`, `story=pending`, and human playtest remains `pending-human-run`.
## 2026-08-07 素材审计快照

- 当前详细审计见 `docs/delivery/MATERIALS_AUDIT_20260807.md`。
- 已生成并可继续审核：`VIS-KA-001`、`VIS-POR-001`、`VIS-UI-001`、`AUD-BGM-001`、`AUD-AMB-001`；它们是候选/内测素材，不代表完整美术和音频制作完成。
- 已收到但返工：`VIS-MAP-001`、`VIS-CHR-001` 至 `003`、`VIS-ENV-001`、`AUD-BGM-002`、`AUD-BGM-003`、`AUD-AMB-002`；它们均为 `changes_requested`，不得接入 runtime。
- 仍未收到：互动动作、完整图标、VFX、SFX、抓捕终点关键图、整合骑士到场素材和地图贴图/道具生产包。
- 新登记但继续延后：`VIS-KA-002`、`VIS-CHR-005`、`VIS-ANIM-001`、`VIS-TILE-001`。
- `check_materials.py`：最新稳定快照为 7 errors，来自 v003 工作目录中的未登记中间文件；v003 正式交付文件仍未进入 MANIFEST/runtime。
- Pre-Capture：`materials=pending`，`story=ready`；N01-N10、四幕、唯一抓捕终点和跨节点回响已完成自动校验，但美术/音频验收和 3 人盲测仍未完成。
