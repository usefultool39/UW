# Changelog

## [Unreleased] 2026-08-06 — 第二月 Day 47–53 路线结果

### Added

- 公开共同地图路线新增 `village_shared_map_hearing`：玩家可选择收集村民亲历证词，或先审核证据簿再公开可确认部分。
- 三人暗线路线新增 `north_gate_team_source_probe`：玩家可选择沿回撤标记继续推进，或先完成一份可交给村务的密封副本。
- Day 53 新增 `ch1_d53_second_month_result`，根据当前路线只展示对应两个结果，并写入四种第三月入口 flag。
- Day 47–52 路线活动与 Day 53 结果均有 NPC 主动入口、关系/记忆/承诺后果和玩家可见收益预览。
- Day 49 与 Day 53 新增剧情日期闸门，防止跳过第二月后半段活动或月末结果。
- Playwright 新增 Day 47 公开地图活动 → Day 53 正式边界听证 → 第三月入口的完整 UI 路径。

### Changed

- 场景活动 requirements 支持 `day_min` / `day_max`；后端越界调用原子返回 `wrong_day_range`，前端显示明确开放日期。
- `month_02_plan.json` 的 Week 07/08 更新为实际可玩的路线专属活动、第二月结果和第三月入口，不再保留空里程碑。
- `NEXT_PHASE.md` 转向 Day 54–61 尾声循环、第二月路线摘要和四种结果的 NPC 反馈。

### Verification

- 后端：`261 passed`；内容校验 `ok=True`、0 errors、0 warnings；保留 1 个 Starlette/httpx 第三方弃用警告。
- 前端单测：`16 passed`；production build 通过；Phaser chunk 约 1.48 MB 的既有体积警告保持不变。
- Playwright E2E：`16 passed`。
- `git diff --check`：通过。

## [Unreleased] 2026-08-06 — 第二月路线选择与剧情日期闸门

### Added

- Day 32 三条第二月路线各增加两种明确做法：稳守线决定公开完整轮值或受训核心；远征线决定加固回撤标记或扩大首段测距；静默线决定补全见证人链或优先隔离信号模式。
- Day 39 NPC 会读取 Day 32 的选择，以不同语境引导巡逻板、远征补给或静默频率复核。
- Day 46 异常汇流增加“公开共同异常地图 / 暂留三人记录”选择，写入不同关系、记忆、承诺和后半月 route flags。
- Day 31、32、39、46 增加剧情日期闸门，玩家不能通过连续休息跳过第二月路线入口、中段活动或异常汇流。
- 内容校验器开始检查 `required_any_flags` 的 authored 生产来源。

### Changed

- 所有含 authored choices 的场景活动必须提交明确 `activity_choice`；缺失选择会事务性返回 `activity_choice_required`，不再把一次性活动标记为完成。
- `month_02_plan.json` 更新为当前已实现的 Day 32 → Day 39 → Day 46 短循环，不再显示“后续版本加入”的过时说明。

### Verification

- 后端：`253 passed`；保留 1 个 Starlette/httpx 第三方弃用警告。
- 前端单测：`16 passed`；production build 通过。
- Playwright E2E：`15 passed`，新增 Day 32 明确选择并解除日期闸门、Day 46 异常公开度选择路径。
- `git diff --check`：通过。

## [Unreleased] 2026-08-06 — 数据驱动路线活动可直接游玩

### Added

- 新增通用场景活动选择面板：非小游戏的 authored choices 现在会在游戏内展示做法、提示、关系变化和记忆对象，玩家选择后再由 Session 结算。
- Day 5–6 北门退路预演、Day 8–11 巡查板复核、Day 13–17 静默线复核新增 NPC 主动入口，填补第一月关键事件之间“有数据但玩家找不到”的内容断层。
- 场景活动公开 API 增加安全 choice preview，只公开关系数值和记忆对象，不暴露 flags、永久记忆正文或控制效果。
- Playwright 新增“巡查板选择可从游戏界面直接完成”的真实 UI 路径。

### Changed

- 北门月末守夜等既有通用选择活动不再跳过 choice 直接应用基础效果，而是要求玩家明确选择路线。
- 剧情事件与场景活动面板只在打开时渲染，避免隐藏面板造成重复可访问节点和自动化 strict-mode 冲突。

### Verification

- 后端：`249 passed`；保留 1 个 Starlette/httpx 第三方弃用警告。
- 前端单测：`16 passed`；production build 通过；Phaser chunk 约 1.48 MB 的既有体积警告保持不变。
- Playwright E2E：`14 passed`，新增覆盖通用场景活动从 UI 选择并写入路线 flag。
- `git diff --check`：通过。

## [Unreleased] 2026-08-06 — 第一月路线连续性与盲测证据

### Added

- Day 24 远征包事件会读取 Day 12 的公开巡查或低调补给路线，显示不同描述和选择提示，让第一月路线持续产生回响。
- 北门静默线复核活动增加玩家可见收益说明，明确这次判定会进入后续静默线演练。
- 新增首轮真人盲测批次跟踪表，集中记录三名玩家的执行状态、录屏、访谈与判定门槛，并明确 E2E 不能替代真人证据。

### Verification

- 后端：`247 passed`；保留 1 个 Starlette/httpx 第三方弃用警告。
- 前端单测：`15 passed`；production build 通过；Phaser chunk 约 1.48 MB 的既有体积警告保持不变。
- Playwright E2E：`13 passed`（`UW_RATE_LIMIT_ENABLED=0` 仅用于本地串行 smoke）。
- `git diff --check`：通过。

## [Unreleased] 2026-08-05 — Day 8–16 回响反馈

### Added

- 为村道传闻、巡查板复核增加玩家可见收益预览，让行动前能理解“这次投入会带来什么”。
- 为 Day 18 静默线演练增加公开安全流程、邀请村民记录、村道传闻三条 authored 叙事变体；保持硬闸门不变，避免支线软锁。
- 增加活动收益预览、Day 18 路线反馈的后端与前端回归测试。

### Verification

- 完整后端质量门：246 passed；保留 1 个 Starlette/httpx 第三方弃用警告。
- 前端单测：15 passed；production build 通过；Phaser chunk 约 1.48 MB 的既有体积警告保持不变。
- Playwright E2E：13 passed（`UW_RATE_LIMIT_ENABLED=0`，仅用于本地串行 smoke；生产默认限流仍开启）。
- `git diff --check`：通过。

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
- 建立可回退的 AI Provider 适配器：支持 StepFun、SenseTime 和 OpenAI-compatible 配置，NPC 对话/意图可灰度调用，离线 scripted/hybrid 回退保持可玩。

### Verification

- 2026-08-05 质量门：后端 `207 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `12 passed`；`git diff --check` 通过。已知非阻塞警告：Starlette/httpx 弃用提示、Phaser chunk 约 1.48 MB。
- 2026-08-05 AI Provider 适配器质量门：后端 `214 passed`；fake HTTP、StepFun/SenseTime 配置别名、对话/行动接入和 hybrid 回退均通过；未调用真实外部 API。

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

### 2026-08-05 长期目标迭代：AI 安全边界与运行预算

#### Added

- 新增 `memory_policy.py`：对模型记忆候选执行来源、类型、长度、权重、注入标记和置信度校验；低置信度候选只进入审计，不写入重要记忆。
- 新增 `intent_policy.py` 与 `npc_intent_agent.py`：模型只能从当前 authored NPC intent/response 白名单中提出预览推荐。
- 新增 `POST /api/npc/{npc_id}/intent/propose` 预览入口；推荐不会直接修改世界，确认执行仍必须进入 `Session.player_action`。
- 新增 `AgentBudget`：按单局 run 限制 action、dialogue、intent 的 AI 调用次数，耗尽后自动回退 scripted/heuristic。
- 新增 `docs/architecture/AI_INTENT_AGENT_LOOP.md`，记录候选、校验、审计和执行边界。

#### Changed

- 普通 scripted/fallback 对话的低权重记忆候选不再误写入永久重要记忆；高权重 authored 候选仍可提交。
- 对话返回值和 JSONL 审计新增 `memory_decision`、`memory_committed` 与 `ai_budget`。
- LLM 行动调用失败或预算耗尽时回退 heuristic，并标记 `decision_mode=heuristic_fallback`。
- `.env.example` 增加单局 AI 调用预算配置示例。

#### Verification

- 2026-08-05：后端 `235 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `12 passed`；`git diff --check` 通过。

### 2026-08-05 长期目标续航：存档导入与回放安全

- 存档导入现在会清理尚未刷出的旧时间线写入，并为导入周目重置 AI 调用预算。
- `MemoryStore.replace_summary` 对导入的永久记忆、承诺和紧张文本执行长度、权重和危险标记过滤，保留旧存档兼容但不接受控制文本。
- 新增存档安全回放测试，确保导入恶意记忆不会进入当前 NPC 记忆上下文。
- 本轮后端质量门：`237 passed`；已知非阻塞 Starlette/httpx 弃用警告保持不变。

### 2026-08-05 长期目标续航：Day 4–7 主线闸门

- 将 Day 3 边界选择、Day 4 书库复盘和 Day 7 北门巡查演练纳入显式剧情日期闸门；玩家不能跳过关键事件直接跨日。
- Day 3 必须完成边界选择后才能进入 Day 4；Day 4 必须完成记录复盘后才能继续；Day 7 必须完成第一次巡查演练后才能进入 Day 8。
- 新增后端剧情闸门回归测试和 Playwright E2E，证明 Day 4 / Day 7 事件可以组成持续主线。
- E2E 后端测试环境关闭请求限流（`UW_RATE_LIMIT_ENABLED=0`），避免 13 个串行 smoke 用例共享本地 IP 时误触生产级 120/min 限制；默认运行环境仍保持限流开启。
- 本轮质量门：后端 `240 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `13 passed`。

### 2026-08-05 长期目标续航：Day 12 村务信任与调查稳定性

- 将 Day 12 村道广场信任事件加入显式日期闸门；完成巡查演练后仍必须完成“公开巡查板 / 低调筹备补给”的村务选择，才能进入 Day 13。
- 修复边界调查小游戏的响应式重置问题：组件不再因父级无关重渲染而清空已选神圣术短句，降低快速操作时“确认异常”按钮偶发禁用的问题。
- E2E 增加稳定的逐项选择等待，覆盖 Day 12 闸门；生产限流行为不变。
- 本轮质量门：后端 `241 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `13 passed`。

### 2026-08-05 长期目标续航：第一月后半段日期闸门

- 将 Day 18 静默线演练、Day 24 远征包、Day 28 北门前夜加入显式日期闸门，第一月关键 authored 事件不能再被连续休息跳过。
- 这些闸门只校验已存在的剧情 flag，不改变原有事件选择、关系效果或旧存档读取方式。
- 本轮质量门：后端 `242 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `13 passed`。

### 2026-08-05 长期目标续航：Day 8–16 短循环反馈

- Day 12 村务事件新增基于可选日常活动的 authored 反馈：如果玩家先复核巡查板或听取村道传闻，事件描述与选择提示会记住这段准备，而不是把日常活动和主线割裂。
- 新增回归测试验证 `village_patrol_board_review` 会改变 Day 12 事件的公开视图；不完成该活动仍可正常推进主线，保持易上手。
- 本轮质量门：后端 `243 passed`；前端单测 `14 passed`；production build 通过；Playwright E2E `13 passed`。

### 2026-08-05 内容校验增强

- 内容校验器现在会检查每个 `day_gate.required_flags` 是否确实由 authored 故事选择或场景活动写入，避免新增日期闸门后出现永远无法满足的软锁。
- 同时校验 `day_gate.required_events` 是否引用当前存在的故事事件。
- 新增坏配置回归测试；本轮后端质量门：`244 passed`。
