# 当前状态

- **状态**：Current / 权威事实页
- **快照日期**：2026-08-06
- **Git 基线**：`main` / `origin/main`（第二月 Day 53 结果切片；具体提交以 `git log -1` 为准）
- **版本标识**：`0.4.0-preview.1`（候选工作区；首批 runtime 素材与 AI 安全增强已接入；未创建 tag）

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
