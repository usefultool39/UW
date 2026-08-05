# 当前状态

- **状态**：Current / 权威事实页
- **快照日期**：2026-08-05
- **Git 基线**：`main` / `ac67991`（AI 安全边界、第一月关键剧情闸门、活动反馈与内容可达性校验已提交并推送）
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
