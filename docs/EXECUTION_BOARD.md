# 边境回声执行看板

整理日期：2026-05-25  
用途：把未来计划拆成可以直接交给下一轮开发的任务。每完成一项，就在本文和 `GAME_QUALITY_ROADMAP.md` 的执行记录里更新。

## 任务状态约定

- `[ ]` 未开始。
- `[~]` 进行中或已有骨架但未验收。
- `[x]` 已完成且验证通过。

## A. 质量门与基线

目标：确认当前项目能稳定启动、测试、截图和交接。

- [ ] 运行后端测试：`.conda\uw-runtime\python.exe -m pytest -q`。
- [ ] 运行前端构建：`npm.cmd run build`。
- [ ] 运行前端 E2E：`npm.cmd run test:e2e`。
- [ ] 打开 `http://127.0.0.1:3000`，截图桌面 `1440x900`。
- [ ] 截图手机 `390x844`。
- [ ] 检查普通模式没有明显开发文本、JSON、内部 id、测试按钮。
- [ ] 在 `GAME_QUALITY_ROADMAP.md` 追加本次验证记录。

完成定义：

- 三条命令通过，或失败项有明确原因和下一步。
- 截图在 `runs/` 可找到。
- 新玩家试玩清单可执行。

## B. 文档整理

目标：让项目、计划、执行、交接都有固定入口。

- [x] 新增 `docs/FUTURE_DETAILED_PLAN.md`。
- [x] 新增 `docs/EXECUTION_BOARD.md`。
- [x] 同步外部计划目录的 `未来优化计划.md`。
- [x] 新增外部计划目录的 `下一步执行清单.md`。
- [x] 新增外部计划目录的 `文档索引.md`。
- [ ] 每次阶段完成后更新根 README 和 `docs/README.md`。

完成定义：

- 从根 README 能找到项目说明、未来计划、执行看板、试玩验收。
- 从外部计划目录能找到项目本体路径和下一步任务。

## C. Day 1-3 稳定试玩

目标：三日 Demo 成为可靠纵切片。

- [~] Day 1 读书、训练、午餐/晚餐、休息结算已接入，需要完整回归。
- [~] Day 2 森林异常和目标预告已接入，需要验证不同 Day 1 选择影响。
- [~] Day 3 边界选择已有事件，需要验证三条结局路线和第一月路由。
- [ ] 新增或更新新玩家试玩清单：不看文档完成 Day 1。
- [ ] 检查日志是否能回看线索、NPC 记忆和关系暗线。
- [ ] 检查存档导出/导入后 Day、flags、关系、记忆仍一致。

重点文件：

- `data/story/events_chapter_01.json`
- `data/story/month_01_plan.json`
- `data/world/scene_activities.json`
- `frontend/src/components/FieldSlice.vue`
- `frontend/src/components/StoryResultPanel.vue`
- `frontend/src/components/ClueJournalPanel.vue`

完成定义：

- 玩家完整走完 Day 1-3 不出现阻断。
- 三条 Day 3 路线能影响第一月提示。
- 试玩流程写入 `docs/PLAYTEST.md`。

## D. 第一月 Day 4-10

目标：把 Day 3 后果自然接到第一月，而不是突然停在 Demo 末尾。

- [~] `month_01_plan.json` 已有 Day 4-6 事后复盘和 Day 7-10 巡查演练结构。
- [ ] 完成 Day 4-6 事件配置：记录口径、先稳住谁、同伴记忆写入。
- [ ] 完成 Day 7-10 北门巡查演练：安全距离、信号、撤退路线。
- [ ] 给 Day 4-10 各加至少一个场景活动。
- [ ] 给 Day 4-10 各加至少一个 NPC 主动意图。
- [ ] 回归三条 Day 3 结局对 Day 4-10 文案和可选项的影响。

重点文件：

- `data/story/month_01_plan.json`
- `data/story/events_chapter_01.json`
- `backend/app/month_plan.py`
- `backend/app/npc_intents.py`
- `frontend/src/field/gameContentConfig.js`

完成定义：

- Day 3 结束后有清晰 Day 4 目标。
- Day 7-10 巡查线能形成一套可重复日常流程。

## E. 重要 NPC 接入

目标：赛尔卡、加雷特、罗温不只是注册在角色表里，而是能参与玩法循环。

- [~] 三个 NPC 已进入 `characters/meta.json` 和 `data/world/schedules.json`。
- [ ] 赛尔卡：书库/疗愈/情绪观察主动意图。
- [ ] 加雷特：北门巡守/风险提醒/巡查流程主动意图。
- [ ] 罗温：村务/律令解释/上报压力主动意图。
- [ ] 每人至少 1 条 persona、1 条 backstory、1 条关系反馈、1 条记忆写入验收。
- [ ] NPC Profile 能显示三人的最近态度来源。

重点文件：

- `characters/selka/`
- `characters/garret/`
- `characters/rulid_elder/`
- `backend/app/npc_intents.py`
- `backend/app/relationship.py`
- `frontend/src/components/NpcProfilePanel.vue`

完成定义：

- 玩家能说出每个 NPC 在第一月中的功能。
- 三人至少各有一次主动影响玩家路线。

## F. Agent Loop 最小版

目标：让 NPC 从固定脚本升级为受状态驱动的智能体，但先做低风险版本。

- [ ] 新增 `backend/app/agent_loop.py`。
- [ ] 定义 NPC 感知输入：时间、地点、玩家最近行动、关系、flags、active events。
- [ ] 定义记忆检索输入：重要记忆、承诺、紧张点、最近误会。
- [ ] 输出只允许生成 `npc_intent`、`memory_candidate`、`reflection`，不能直接改世界事实。
- [ ] 核心 NPC 高频，重要 NPC 中频，背景 NPC 低频或无 LLM。
- [ ] 增加测试覆盖：无 key fallback、成本控制、非法行动过滤。

完成定义：

- 关闭 LLM key 时游戏仍可玩。
- AI 输出必须经过后端校验。
- 单次状态刷新不会造成明显延迟。

## G. 世界观察器与内容校验

目标：后续内容越来越多时还能维护。

- [~] `backend/app/content_validator.py` 已有骨架，需要扩展规则和前端入口。
- [ ] 世界观察器显示：day、time、flags、active events、NPC 位置、NPC intent。
- [ ] NPC 调试面板显示：记忆、关系、计划、最近决策理由。
- [ ] 内容校验覆盖：事件 id、flags、participants、location、scene_id、POI 可达性。
- [ ] 配置错误能指出具体文件和字段。
- [ ] 所有调试入口只在 `?dev=1` 显示。

完成定义：

- 新增事件或 NPC 后，开发者能在 1 分钟内发现配置错误。
- 普通玩家界面完全看不到调试器。

## H. 美术与音频第一版

目标：让第一章画面和声音从原型进入“像游戏”的阶段。

- [ ] 地形素材：草地、路、水岸、森林、障碍。
- [ ] 地标素材：书库、小屋、古誓树、北境边门、村道广场。
- [ ] 角色动画：玩家、爱丽丝、悠吉欧 idle/walk 四方向。
- [ ] 世界反馈：不可达、调查点、NPC 可对话、目标方向。
- [ ] 音效：点击、脚步、雨、水、炉火、异常静默、结算提示。
- [ ] 视觉验收：桌面和手机截图无重叠、Canvas 非空、NPC 落点正确。

重点文件：

- `docs/ART_DIRECTION_PLAN.md`
- `frontend/public/assets/game/`
- `frontend/public/assets/game/tilesets/luin_village_v1.json`
- `frontend/src/field/worldMapDrawing.js`
- `frontend/src/field/createWorldFieldScene.js`

完成定义：

- 不看文字也能识别核心地点。
- 角色移动不再是静态 token 滑动。

## I. 发布包与维护

目标：做出可分发、可回归、可继续迭代的版本。

- [ ] 存档版本号和迁移机制。
- [ ] 发布包只包含运行必需项。
- [ ] 清理规则：`runs/`、`data/memory/`、`frontend/dist/`、缓存目录。
- [ ] 每个稳定版本记录截图、测试命令、已知问题和下一步。
- [ ] 写一页玩家试玩说明，不暴露内部实现。

完成定义：

- 新机器能按 README 启动。
- 旧存档不会因为新增字段直接坏掉。

## 下一轮推荐提示词

```text
请在 F:\usefultool39\02-UW小镇 继续《边境回声》。

先读：
1. docs\PROJECT.md
2. docs\FUTURE_DETAILED_PLAN.md
3. docs\EXECUTION_BOARD.md
4. docs\PLAYTEST.md

优先执行 EXECUTION_BOARD.md 的 A「质量门与基线」和 C「Day 1-3 稳定试玩」。
要求：不碰无关文件，不重写架构；完成后运行后端 pytest、前端 build、E2E，桌面和手机截图放到 runs；最后更新 GAME_QUALITY_ROADMAP.md 执行记录。
```
