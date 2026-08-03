# 边境回声 Playtest 记录

- **状态**：Current

## 目标（本轮）

把主线关键路径 Day1-3、Day 4-6（第4-6天复盘）、Day39、Day 46（第46天 Week07）的“可触发 / 可完成 / 可结算”打通；把问题落地为可执行任务，形成下一轮小目标清单。

## 基础环境

1. 后端健康检查：`http://127.0.0.1:8765/api/health` 返回 `ok`
2. 前端打开：`http://127.0.0.1:3000`
3. 保持默认进入场景为起始村落
4. 每次记录前清空临时会话，避免前一次状态干扰

## 快速验收模板（每项都记录）

- 可触发：按钮/交互是否出现
- 可完成：点击后是否有响应、状态更新、任务推进
- 可结算：对应任务是否设置/移除 flag 或更新事件状态
- 体验分数：可见性 / 可操作性 / 提示清晰度（每项 1-3 分）
- 阻断级别：`P0`（卡住流程）`P1`（明显影响）`P2`（小瑕疵）

## 手动体验清单

### Day1-3 纵切（主线最小闭环）

- [x] Day1：从起始村落完成“接任务 → 寻找目标 → 与 NPC 对话 → 触发场景活动”闭环
- [x] Day2：完成第一条任务分支并返回主 NPC，确认后续意图更新
- [x] Day3：完成一个完整选择分支并进入小结（如 `chapter_ending_id`）
- [x] Day1-3 总体验：首次入场 UI 层级、交互入口、提示语是否清晰

### Day 4-6 事后复盘（第一月早期）

- [x] Day4：完成 Day3 后进入书库复盘事件 `ch1_d4_after_boundary_debrief`
- [x] Day4-6：确认艾琳主动意图能把玩家带回书库，而不是只依赖事件列表
- [x] 关键选择后写入记录口径、同伴记忆和下一步巡查目标

### Day 46 共享异常会合（第46天 / Week07）

- [x] `month02_day31_entry_done` + `month02_route_order` + `month02_order_patrol_standby_done` 打标后，切到 Day 46
- [x] 到达会合场景（`reading_hall`）后出现意图 `alice_calls_anomaly_convergence`
- [x] 会合活动 `boundary_anomaly_convergence` 可见并可点击
- [x] 结算后确认 `month02_anomaly_convergence_done` 与 `month02_anomaly_source_documented` 更新

### Day39 路线（订单/远征/静默）

- [x] 静默线：执行 `reading_hall_quiet_frequency_crosscheck` 并到达结算
- [x] 静默线：关键场景切换、NPC 意图和按钮提示完整

## 体验问题记录（按轮追加）

| 时间 | 场景 | 流程 | 问题类型 | 严重级别 | 重现步骤 | 期望 | 结论 |
|---|---|---|---|---|---|---|---|
| 2026-05-30 | | | | | | | |
| 2026-06-01 | Day1 起始村道广场 | 首屏入场 | 首屏层级 | P2 | 打开 `http://127.0.0.1:3000`，跳过开场后观察右侧任务、底部按钮、引导气泡 | 玩家不用读文档也能知道先去村西书库 | 可读性基本成立；首屏信息量偏大，但不阻断 |
| 2026-06-01 | Day1 起始村道广场 | 首屏视觉层级 | 浏览器基线 | 通过 / P2 | Playwright 分别截图桌面 1440x900 与移动 390x844，检查开场封面、HUD、任务追踪、热键、地图与 NPC 意图 | 首屏中文正常、核心 UI 不重叠，玩家能看到当前目标、可执行动作和地图方向 | 通过；开场封面桌面/移动观感稳定，HUD 核心区域无几何重叠。移动端底部时间推进按钮靠近热键，记录为后续 polish，不阻断 |
| 2026-06-01 | Day1 村西书道 / 书库阅览台 | 读书与边界记录 | 交互入口重复 | P2 | 到书库打开附近互动，`church_read_sacred_arts` 同时以 NPC 主动和轻量玩法出现 | 同一关键动作最好只有一个主入口，或明确主次 | 功能可完成；后续做 Day1 引导整理时合并/降噪 |
| 2026-06-01 | Day1-3 | 主线闭环 | 可玩性 | 通过 | 完成读书小游戏、`ch1_d1_reading_clue`、`ch1_d2_forest_anomaly`、`ch1_d3_boundary_choice` | Day1-3 可触发、可完成、可结算 | 通过；Day2 写入 `forest_anomaly_seen=1`，Day3 写入 `chapter_ending_id=cross` |
| 2026-06-01 | Day 1 首屏任务追踪 | 推荐线索按钮 | 远距离剧情触发 | P1 | 在村道广场跳过开场后点击“查看推荐线索” | 远距离只引导玩家前往书库附近，不直接打开书库剧情面板 | 已修复；远距离点击只提示“先去村西书库附近”，不再打开事件面板 |
| 2026-06-01 | Day 4 家中炉火 / 村西书库 | Day 4-6 事后复盘 | 路线提示称呼不一致 | P2 | 完成 Day3 后休息到 Day4，观察右侧目标与书库事件 | 艾琳主动意图和当前线索都应明确指向同一个玩家目的地 | 已修复并复验；目标、NPC 关注和当前线索都指向“村西书库” |
| 2026-06-01 | Day 4 村西书库 | Day 4-6 事后复盘 | 可玩性 | 通过 | 进入 `church_library`，打开 `ch1_d4_after_boundary_debrief`，选择 `write_truth` | 复盘事件可触发、可完成、可结算 | 通过；写入 `month01_debrief_done=1`、`month01_record_truth=1`，艾琳/尤里记忆更新，复盘意图消失 |
| 2026-06-01 | Day 4 村西书库 | 艾琳复盘人物厚度 | 人物感增强 | 通过 | 选择 `ch1_d4_after_boundary_debrief.write_truth` | 艾琳坚持写完整记录时，应能看出这是为了让风险变成家人也能理解的日常安全流程 | 已补强；结果文本加入“莉娜也能看懂的安全边距”，记忆摘要同步写入保护日常生活 |
| 2026-06-01 | Day 46 书库阅览台 | Week07 异常汇合 | 玩家可见旧名 | P1 | 设置 Month02 order 路线完成 flag 后触发 `boundary_anomaly_convergence` | 结算文本与当前角色名统一为艾琳 / 尤里 | 已修复并复验；旧名不再出现在 Day 46 汇合结果 |
| 2026-06-01 | Day 46 书库阅览台 | 艾琳人物厚度 | 人物感增强 | 通过 | 触发 `boundary_anomaly_convergence` 后阅读结果面板和记忆摘要 | 艾琳不只是记录员，应体现刻印术、长期牵挂和“先确认能否回来”的判断方式 | 通过；结果文本加入三枚刻印标记、妹妹来信页角、能否让大家回来，艾琳记忆摘要同步 |
| 2026-06-01 | Day39-45 村道广场 / 书库阅览台 | Month02 路线承接 | 玩家可见旧名 | P1 | 搜索 Day39 order / quiet 分支的 NPC 意图和场景活动文案 | Month02 玩家可见文案统一使用“艾琳”，保留内部 `alice` id 不变 | 已修复并测过；源内容 `data/backend/frontend` 中不再残留旧名 |
| 2026-06-01 | Day1 村西书库 | 把旧记录告诉艾琳 | 人物感增强 | 通过 | 选择 `ch1_d1_reading_clue.ask_alice` | 玩家第一次把旧记录告诉艾琳时，应理解她为什么在意记录，而不只是收到任务提示 | 已补强；结果文本加入莉娜练习页、刻印标记和“鸟声消失”圈注，记忆摘要同步写入日常安全牵挂 |
| 2026-06-01 | Day2 巨树清场边缘 | 森林异常共同调查 | 人物感增强 | 通过 | 选择 `ch1_d2_forest_anomaly.investigate_together` | 艾琳在异常出现后应体现判断方式，而不只是担心或阻止 | 已补强；艾琳用刻印标记压住安全距离，先判断异常有没有越过日常边界 |
| 2026-06-01 | Day39 书库阅览台 | 静默线频率复核 | E2E 质量门 | 通过 | 设置 Month02 quiet 前置 flag，Day39 进入 `reading_hall`，通过 UI 点击 `reading_hall_quiet_frequency_crosscheck` | Day39 至少一条路线有完整 E2E：意图出现、入口可点、结果可见、完成 flag 写入 | 已补 E2E；`month02_quiet_frequency_crosscheck_done=1` 与 `month02_quiet_frequency_crosschecked=1` |
| 2026-06-01 | Day46 / 存档导入 | Month02 required_any_flags | 存档兼容 | 通过 | 导出包含 `month02_quiet_frequency_crosscheck_done=1` 的 Day46 存档，重置后导入并执行 `boundary_anomaly_convergence` | 导入后保留 Month02 flags，Day46 收束活动仍能通过 `required_any_flags` 解锁并结算 | 已补后端测试；导入后写入 `month02_anomaly_convergence_done=1` 与 `month02_anomaly_source_documented=1` |
| 2026-06-01 | Day46 汇合结算后 | Week07 后续目标 | 目标回退 | P1 | 完成 `boundary_anomaly_convergence` 后关闭结果面板，观察右侧当前目标 | Day46 汇合后应给出第二月后段的下一步，而不是回退到 Day1 入门提示 | 已修复并复验；目标改为回北门复核撤退口令与安全边距，为第二月末选择做准备 |

## 本轮证据

- E2E：`npm.cmd run test:e2e -- --reporter=line`，8 passed
- 后端：`.venv\Scripts\python.exe -m pytest backend/tests/test_month_plan.py backend/tests/test_npc_intents.py -q`，32 passed
- 构建：`npm.cmd run build`，passed
- 本轮复验（2026-06-01）：`npm.cmd run test:e2e -- --reporter=line`，8 passed；`npm.cmd run build`，passed；`.venv\Scripts\python.exe -m pytest backend/tests/test_month_plan.py backend/tests/test_npc_intents.py -q`，32 passed
- 手动截图：`runs/automation/codex_manual_20260531_165232_01_opening.png` 到 `runs/automation/codex_manual_20260531_165232_08_day46_result.png`
- Day46 旧名复验截图：`runs/automation/codex_verify_20260531_165829_day46_name_cleanup.png`
- Day1 推荐线索远距离门控截图：`runs/automation/codex_verify_route_gate_20260601_0128_01_far_click.png`
- Day4-6 复盘截图：`runs/automation/codex_day4_debrief_20260601_0205_01_day4_home.png` 到 `runs/automation/codex_day4_debrief_20260601_0205_04_result.png`
- Day4-6 路线口径复验截图：`runs/automation/codex_day4_copy_unified_20260601_0232_01_day4_home.png`
- Day4-6 艾琳人物厚度：`.venv\Scripts\python.exe -m pytest backend/tests/test_content_validator.py backend/tests/test_month_plan.py::test_first_month_events_chain_to_week_two_drill backend/tests/test_month_plan.py::test_month_plan_reflects_day_four_debrief_after_boundary_ending -q`，5 passed；故事/NPC 定向测试，9 passed；运行时 API 触发 `ch1_d4_after_boundary_debrief.write_truth` 复验通过
- Day46 艾琳人物厚度复验截图：`runs/automation/codex_day46_ailin_depth_20260601_0300_01_result.png`
- Day39-45 旧名清理：`rg -n "艾丽丝" data backend frontend` 无命中；`.venv\Scripts\python.exe -m pytest backend/tests/test_content_validator.py backend/tests/test_npc_intents.py -q`，21 passed；Day39 quiet / Day46 衔接定向测试，3 passed；运行时 API 复验通过（order intent / quiet intent / quiet activity 均无旧名）
- Day1 艾琳人物厚度：`.venv\Scripts\python.exe -m pytest backend/tests/test_content_validator.py backend/tests/test_story_director_events.py backend/tests/test_npc_intents.py::test_state_exposes_day1_npc_intents backend/tests/test_npc_intents.py::test_reading_activity_changes_alice_intent_to_reaction -q`，13 passed；运行时 API 触发 `ch1_d1_reading_clue.ask_alice` 复验通过
- Day2 艾琳人物厚度：`.venv\Scripts\python.exe -m pytest backend/tests/test_content_validator.py backend/tests/test_story_director_events.py -q`，11 passed；`npm.cmd run test:e2e -- --grep "Day 2" --reporter=line`，4 passed；运行时 API 触发 `ch1_d2_forest_anomaly.investigate_together` 复验通过
- Day39 静默线 E2E：`npm.cmd run test:e2e -- --grep "Day 39 quiet" --reporter=line`，1 passed；相关后端 Day39 / Month02 测试，2 passed；完整 E2E `npm.cmd run test:e2e -- --reporter=line`，9 passed
- Save/load 兼容：`.venv\Scripts\python.exe -m pytest backend/tests/test_api_framework.py::test_save_import_preserves_month_two_required_any_flags_for_day_forty_six -q`，1 passed；Month02 / Day46 定向测试，2 passed；完整 API 框架测试，29 passed
- 首屏视觉层级复查：Playwright 截图 `runs/automation/codex_first_screen_desktop_20260531_190137_initial.png`、`runs/automation/codex_first_screen_mobile_20260531_190137_initial.png`、`runs/automation/codex_first_hud_desktop_20260531_190259.png`、`runs/automation/codex_first_hud_mobile_20260531_190259.png`；核心 HUD overlap 检查为 0
- 玩家可见文案扫描：Playwright 覆盖 Day1 开场/HUD、Day4 复盘、Day39 静默线、Day46 汇合；未发现旧名、内部 id 或乱码暴露；发现 Day46 汇合后目标回退 P1 并修复
- Day46 后续目标修复：`npm.cmd run test:e2e -- --grep "Day 46" --reporter=line`，1 passed；`npm.cmd run build`，passed；完整 E2E `npm.cmd run test:e2e -- --reporter=line`，9 passed

## 今晚目标调节

今晚先把目标从“继续扩内容”调成“把一个核心人物做厚”。推荐先聚焦艾琳，因为她贯穿 Day1 书库引导、Day2 异常判断、Day 4-6 复盘和 Day 46 共同记录收束。

验收口径：

- 玩家第一次见艾琳时，能理解她为什么在意旧记录
- Day2 异常后，艾琳的担心不只是任务提示，而能体现她的判断方式
- Day 46 收束时，艾琳与尤里的分工清楚：艾琳负责记录与判断，尤里负责撤退与行动风险
- 不新增大系统；优先补台词、意图、结果文案、记忆摘要和少量 UI 提示

## 回归闭环

- 问题发现 → 在 `runs/automation` 记录（时间、重现、日志/截图）
- 选择一个最小可验证修复项（每轮只改一个目标）
- 修复后执行对应 Playtest 或 E2E 条目并记录
- 通过后更新 `NEXT_TODO.md` 与本页状态

## 当前状态

- 版本基线：`a487210`
- 当前验证：Day1-3、Day 4-6、Day39 静默线与 Day 46（第46天）基线已通过；Day 46 旧名 P1 已修复并复验；Day39-45 旧名 P1 已清理并通过后端校验；Day 1 远距离推荐线索门控已修复；Day 4-6 目的地口径已统一；Day1、Day2、Day4-6 与 Day46 艾琳人物厚度已有落点；Month02 save/load required_any_flags 兼容已覆盖；首屏开场与 HUD 视觉层级已做桌面/移动基线复查；Day46 汇合后目标回退 P1 已修复
- 下一步动作：继续做玩家可见文案清理，或补 Week08 / 第二月末选择的下一组小闭环
