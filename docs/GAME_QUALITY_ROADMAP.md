# 游戏品质与 AI 世界重做任务板

> 2026-05-15 客户端路线调整：Cocos Creator 因账号/登录/首次启动流程带来额外摩擦，暂时冻结为未来备用正式客户端，不作为当前主开发路径。接下来默认继续以 `frontend/` 的 Vue + Phaser 可玩客户端为主线，优先打磨地图可读性、交互反馈、性能、UI 和美术接入。Cocos 已完成的工程、契约和场景资产保留，不删除；除非后续明确恢复 Cocos 路线，否则不再把 Creator 预览/登录/按钮验收列为当前阻塞项。详见 `docs/CLIENT_STRATEGY_DECISION.md`。

更新日期：2026-05-15  
状态：进行中  
用途：后续开发者或智能体接手时，以本文为主任务板。每完成一个任务，就把对应复选框从 `[ ]` 改成 `[x]`，并在“执行记录”里追加日期、改动摘要和验证结果。

下一窗口优先执行：见 [EXECUTION_BOARD.md](EXECUTION_BOARD.md)。`NEXT_HANDOFF_PLAN.md` 中的 Day 1 自然玩法循环多数已完成，后续默认以执行看板和 [FUTURE_DETAILED_PLAN.md](FUTURE_DETAILED_PLAN.md) 为新的计划入口。

## 目标

把当前“能运行的 AI RPG 原型”升级成一个真正有吸引力的单人 AI RPG 垂直切片：

- 玩家打开游戏 10 秒内知道自己是谁、在哪里、要做什么。
- 第一眼观感像游戏，不像开发调试界面。
- 移动、点击、交互、镜头和音效有即时反馈。
- 第一章前 20 分钟有明确目标、情绪钩子和可玩循环。
- NPC 不只是会聊天，而是能记住、计划、改变关系并主动影响玩家。
- 世界规则仍由后端权威维护，AI 只提出意图、表达、反思和记忆候选。

## 当前客观状态

已验证：

- 后端测试通过：`154 passed`。
- 前端构建通过：`npm.cmd run build`。
- E2E smoke 通过：Phaser canvas 可见，且覆盖读书、午餐、训练、日志和 Day 2 预告。
- 前端可访问：`http://127.0.0.1:3000`。
- 后端健康检查可访问：`http://127.0.0.1:8765/api/health`。

当前规模：

- NPC：5 个，见 `characters/meta.json`，包括爱丽丝、悠吉欧、赛尔卡、加雷特、罗温。
- 第一章剧情事件：Day 1-3 已可玩，第一月路线见 `data/story/month_01_plan.json`。
- 场景活动：读书、训练、午餐、晚餐、休息、边界相关活动已进入配置，见 `data/world/scene_activities.json`。
- 主地图：1 张正式地图，加 1 个 stub 地图目录。
- 前端：Vue 3 + Phaser。
- 后端：FastAPI + Pydantic + JSON 配置、本地 JSONL 记忆、NPC 主动意图、第一月计划和内容校验骨架。

核心问题：

- 画面像原型，不像商业游戏。
- 移动需要等待后端响应再播放路径，反馈不够即时。
- 首屏目标像测试说明，不像冒险动机。
- NPC 状态和行为模型太薄，还不是多智能体社会。
- 记忆系统只是事件摘要，不够支撑“意识感”。
- 剧情主要靠脚本事件，不是由 NPC 行为与世界状态自然涌现。

## 文档更新规则

- 每次开工前先读本文、`PROJECT.md`、`PLAYTEST.md`。
- 每完成一个小任务，立刻把 `[ ]` 改成 `[x]`。
- 如果任务拆分，保留原任务并新增子任务，不要删除历史目标。
- 如果发现计划不合理，在对应阶段加“调整说明”，不要默默改方向。
- 每次提交或交接前，在“执行记录”追加一条记录。
- 验证失败也要记录，写清楚失败命令和原因。

## 总体原则

- 先做 20 分钟高质量垂直切片，不扩成大世界。
- 先让 5-10 个 NPC 可信，不做 100 个空壳 NPC。
- 先解决首屏、操作、引导、反馈，再扩 AI 深度。
- 不直接发布官方 IP 同人复刻，角色名、地名、规则名必须原创化。
- 后端保存权威事实，前端只负责输入、表现、动画和反馈。
- LLM 不直接改世界，只能提出意图、对话、反思、记忆候选。

## 里程碑 0：基线和产品定位

目标：明确“最好版本”到底是什么，避免边做边散。

- [x] 写一页产品定位：玩家幻想、核心体验、首个 20 分钟体验目标。
- [x] 决定正式原创名称，替换“30小镇 / UW小镇 / Underworld”内部表达。
- [x] 决定第一章主角身份、村庄名、边界规则名、核心异常名。
- [x] 把 Alice / Eugeo / Kirito 等占位全部列入原创化清单。
- [x] 明确第一章最终 Demo 时长：建议 20-30 分钟。
- [x] 明确第一章验收标准：玩家能说出至少 1 个 NPC 为什么让他在意。

验收：

- [x] `docs/PROJECT.md` 与本文方向一致。
- [x] 根 README 不再把官方 IP 名称作为公开表达。

## 里程碑 1：首屏和 UI 重做

目标：打开游戏第一眼像幻想 RPG，而不是工具页面。

### 1.1 信息架构

- [x] 默认只进入游戏主界面，不显示“状态总览 / 地图探索”开发 Tab。
- [x] 把“状态总览”移动到开发者菜单或调试模式。
- [ ] 隐藏或移除首屏上的 `mq00_tutorial`、开发调试按钮、区域 JSON。
- [x] 右侧 QuestTracker 从说明面板改为任务追踪器：当前目标、目标 NPC、奖励/风险、下一步按钮。
- [x] 热栏改为动作栏：对话、调查、训练、休息、记忆/背包。
- [ ] 所有按钮补图标，减少纯文字矩形按钮。

调整说明：

- 2026-05-11 第一轮已把“状态总览 / 地图探索”切换收进 `?dev=1`，普通打开默认只显示游戏主界面。
- 任务追踪器已改成“今日目标 / 正在发生 / 附近 / 地点”的游戏内结构，但后续仍需要正式 UI 视觉稿和奖励/风险提示。
- 热栏已加入动作图标和“线索/调查”等更游戏化的标签，但全局按钮系统还没有完全图标化。

相关入口：

- `frontend/src/App.vue`
- `frontend/src/components/FieldSlice.vue`
- `frontend/src/components/FieldHeader.vue`
- `frontend/src/components/QuestTracker.vue`
- `frontend/src/components/Hotbar.vue`
- `frontend/src/components/PlayerHUD.vue`

验收：

- [x] 玩家不读文档也能知道第一步去哪里。
- [x] 首屏没有明显开发调试文本。
- [x] 1440x900 和 390x844 两个视口没有文字重叠。

### 1.2 视觉风格

- [ ] 确定正式美术方向：2D 手绘俯视、2.5D 等距、高清像素三选一。
  - [x] 第一版美术计划写入 `docs/ART_DIRECTION_PLAN.md`：推荐细颗粒 2D 俯视 / 高清像素混合风格，正式资产暂缓。
- [ ] 建立色彩规范：主色、危险色、任务色、NPC 色、夜晚/雨天色。
- [ ] 重新设计 HUD：角色状态、时间、天气、场景名、任务目标。
- [ ] 重新设计对话框：头像、名字、情绪、历史、关键记忆提示。
- [ ] 重新设计事件选择面板：选择风险、谁会记住、可能关系影响。
  - [x] 第一版选择预览已显示谁会记住、关系变化、承诺/紧张暗线。
- [ ] 统一圆角、边框、阴影、字体大小，不再混合开发卡片和游戏 HUD。

验收：

- [ ] 截图能明确看出“幻想村庄 RPG”。
- [ ] UI 不遮挡角色、事件标记、NPC。
- [ ] 任务标记、NPC、交互点一眼可分辨。

## 里程碑 2：地图美术和场景表现

目标：地图像一个世界，不像一张背景图上叠调试格子。

- [x] 取消或默认隐藏大面积格子遮罩，只在调试模式显示。
- [x] 把当前程序化地块绘制降级为 fallback，不作为正式画面主体。
- [ ] 用正式地图资产替代临时背景：地表、建筑、水渠、树、道路、边界。
- [ ] 拆分地图层：背景、地表、建筑、遮挡、动态氛围、碰撞、交互点。
  - [x] 第一版：主地图改为由 `world_map.json` 瓦片层直接驱动视觉，临时大背景不再覆盖可走/不可走逻辑。
  - [x] 第一版：道路、水域、森林、障碍按同一份地形码渲染，避免 NPC 看起来站在水面或背景错位。
  - [x] 第二版：NPC、POI、章节事件的显示位置会吸附到最近可走格，逻辑坐标和视觉落点不再硬绑。
  - [x] 第二版：锁区入口支持 `approach_tile_x/y`，北境边门这类“门在禁区内、玩家站在门前调查”的点可以被正确表现和校验。
  - [x] 第三版：地图渲染粒度下调到 `28px` tile，默认镜头拉远，角色 token 缩小到更贴近地图比例。
  - [x] 第四版：地图手感参数迁移到 `world_map.json.visual`，镜头、移动、烘焙和动态层刷新频率可直接配置。
- [ ] 增加动态氛围：雨、水面、树叶、炊烟、晨昏光、夜晚窗光。
  - [x] 增加第一版屏幕空间细雨和轻雾，让当前雨天地图先动起来。
  - [x] 增加第一版水面动态波纹和更自然的水岸/森林边缘。
- [ ] 角色和 NPC 使用统一动画规格，不再使用静态 token。
- [ ] NPC 需要小地图头像/头顶名牌/状态提示，但默认克制显示。
- [x] 任务点从黄色感叹号升级为与世界融合的光效或标记。

调整说明：

- 2026-05-11 第二轮已把正式背景图上的程序化地块层从主要画面降为很轻的规则影子，锁区纹理也降透明度。后续仍需要正式地图资产和更自然的任务标记。
- 2026-05-11 第三轮已把章节事件和任务点从黄色感叹号替换为世界内光柱、光环和核心点信标；后续仍需要正式 2D/2.5D 美术资产承接这套交互语言。

相关入口：

- `frontend/src/field/createWorldFieldScene.js`
- `frontend/src/field/worldMapDrawing.js`
- `frontend/src/field/sceneRegistry.js`
- `frontend/public/assets/game/`
- `data/world/world_map.json`

验收：

- [ ] 关掉 UI 后，单看地图也有完整场景观感。
- [ ] 不同场景区域不靠文字也能分辨：家、书库、广场、巨树、北门。
- [ ] 雨天、夜晚、清晨有明显但不刺眼的差异。

## 里程碑 3：移动手感和交互反馈

目标：操作像游戏，点击后立即反馈，不卡、不钝、不像网页表单。

### 3.1 移动系统

- [x] 前端本地先计算路径和播放移动，后端异步验证最终状态。
- [x] 保留后端权威校验，校验失败时平滑回滚或阻止进入。
- [x] 支持 WASD / 方向键移动。
- [ ] 支持点击移动、双击跑动或长按连续移动。
  - [x] 左键短按点击移动，左键拖拽平移镜头；右键/中键拖拽仍可用。
- [x] 移动开始立即显示目的地光圈和路线预览。
- [ ] 行走加入 idle / walk 动画、脚步音、落点反馈。
- [ ] 不可达区域显示世界内反馈，而不是只 toast 报错。
  - [x] 第一版：水域、树林、岩石障碍会在前端直接阻止移动，鼠标变为不可达状态，并给出镜头/提示反馈。

调整说明：

- 2026-05-11 第一轮已实现本地 BFS 预走、目的地光圈、路径播放和后端回滚。还没有做 WASD、跑动、角色 walk 动画和完整不可达世界内反馈。

相关入口：

- `frontend/src/components/FieldSlice.vue`
- `frontend/src/components/FieldMap.vue`
- `frontend/src/field/createWorldFieldScene.js`
- `backend/app/world_map.py`
- `backend/app/session.py`

验收：

- [ ] 点击后 100ms 内有视觉反馈。
- [ ] 短距离移动体感低于 1 秒。
- [ ] 连续移动不会因为请求刷新产生卡顿。
- [ ] 低配机器上仍能稳定 50-60 FPS。

### 3.2 镜头和反馈

- [ ] 镜头跟随平滑但不漂。
- [ ] 到达关键地点时镜头轻微停顿或聚焦。
- [ ] 点击 NPC、任务点、互动点有不同音效和光效。
- [x] NPC 附近自动出现交互提示，不要求玩家猜按钮。
- [x] 任务目标支持方向箭头或地面引导线。

调整说明：

- 2026-05-11 第二轮已增加从玩家朝最近章节事件/任务 POI 的金色地面引导线和箭头。后续需要把它做得更像世界内特效，并支持开关或距离自适应。

验收：

- [ ] 玩家第一次移动、第一次对话、第一次调查都有明确反馈。
- [ ] 鼠标、键盘、触控三种输入至少有基础可用体验。

## 里程碑 4：新手引导和第一天重写

目标：第一天不是“点两个事件”，而是一段自然的日常悬疑。

建议流程：

1. 主角醒来，收到 NPC 留言。
2. 跟随任务箭头去书库。
3. 与核心 NPC 第一次对话。
4. 调查书页，获得“北境异常”线索。
5. 去巨树清场找另一个核心 NPC。
6. 做一次训练小游戏。
7. 晚餐时出现第一次分歧选择。
8. 日结算：关系变化、谁记住了什么、明天伏笔。

任务：

- [x] 写第一天完整体验脚本，不超过 20 个关键节点。
- [x] 把当前“点击章节事件”改成自然地点触发和 NPC 引导触发。
- [x] 增加可跳过的新手提示，不用常驻说明文字。
- [x] 增加第一天日结算界面。
- [x] 增加“谁记住了你今天做的事”的情绪化反馈。
- [x] 增加第二天目标预告。

相关入口：

- `data/story/events_chapter_01.json`
- `data/world/scene_activities.json`
- `frontend/src/components/StoryEventPanel.vue`
- `frontend/src/components/StoryResultPanel.vue`
- `frontend/src/field/gameContentConfig.js`

验收：

- [x] 新玩家不看文档能完成 Day 1。
- [x] Day 1 至少有 3 次主动选择，而不是只读文本。
- [x] 玩家能感到两个核心 NPC 的性格差异。

## 里程碑 5：核心玩法循环

目标：AI 世界必须好玩，不只是能聊天。

### 5.1 探索循环

- [ ] 每个场景至少有 2 个可调查点。
- [ ] 调查点有状态变化：未发现、已发现、已解释、影响后续。
- [x] 增加线索手册或记忆日志。
- [ ] 地图上标记“已知目标”和“可疑地点”，但保留少量探索空间。

### 5.2 日常活动循环

- [x] 砍树训练做成轻量小游戏，而不是只推进 tick。
- [x] 读书做成线索选择或关键词拼接。
- [x] 帮忙准备午餐/晚餐做成关系和时间选择。
- [ ] 休息不只是跳天，要进入梦境/回忆/日结算。

### 5.3 关系循环

- [ ] NPC 关系变化必须影响后续对话、邀请、隐瞒和冲突。
  - [x] 第一版：Day 1 晚餐选择会改变 Day 2 森林异常描述、可见选项和后续关系/记忆。
  - [x] 第一版：备用 NPC 对话会根据 trust / affinity / tension 改变普通回应语气。
  - [x] 第二版：NPC 主动意图新增回应选项，玩家回应会写入 flags、关系变化、NPC 重要记忆、承诺或紧张点。
- [ ] 关系不只对玩家，还要增加 NPC 与 NPC 的关系。
- [ ] 增加承诺、秘密、误会、紧张点四类关系状态。
- [x] 增加 NPC 主动找玩家的事件。
  - [x] 第一版：`state.npc_intents` 会在书库、巨树、晚餐和 Day 2 异常节点主动给出 NPC 推动项，前端地点互动面板可直接回应或进入事件。

验收：

- [ ] 第一章不靠调试按钮也能自然推进。
- [ ] 玩家至少有两条不同的 Day 2 体验路径。
- [ ] 关系变化在 UI 和对话里都能被玩家感知。

## 里程碑 6：AI NPC 智能体升级

目标：NPC 有记忆、目标、计划和社会行为，而不是只回答玩家。

### 6.1 NPC 状态模型

- [ ] 扩展 `AgentState`：traits、beliefs、needs、skills、inventory、secrets。
- [ ] 增加 `GoalState`：长期目标、今日目标、当前意图、优先级。
- [ ] 增加 NPC 对 NPC 的关系网。
- [ ] 增加主观认知：NPC 不一定知道真实世界事实。
  - [x] 第一版：NPC Profile 增加 `mind` 快照，展示当前目标、状态倾向、主动关注点、判断理由和由 flags/关系推断出的主观认知。

相关入口：

- `backend/app/models.py`
- `backend/app/agent_registry.py`
- `characters/meta.json`
- `data/world/schedules.json`

### 6.2 记忆系统

- [ ] 将记忆拆为事件记忆、语义记忆、关系记忆、承诺/紧张点。
- [ ] 增加重要性评分、时间衰减、冲突记忆、遗忘/压缩。
- [ ] 增加按当前情境检索记忆，而不是只取前几条。
- [ ] 增加 NPC 睡前反思：把当天事件压缩成可用记忆。
- [ ] 增加记忆调试页面：能看到为什么 NPC 记住这件事。

相关入口：

- `backend/app/memory_store.py`
- `backend/app/dialogue_agent.py`
- `backend/app/session.py`

### 6.3 Agent Loop

每个重要 NPC 的循环应升级为：

1. 感知：我在哪里、谁在附近、发生了什么。
2. 检索：哪些记忆和关系与当前有关。
3. 目标：我今天想做什么，我担心什么。
4. 计划：下一步去哪里，找谁，说什么。
5. 行动：提出意图。
6. 校验：后端规则决定能否执行。
7. 反思：行动结果是否改变记忆、关系、计划。

任务：

- [ ] 新增 `agent_loop.py`，不要继续把所有逻辑塞进 `session.py`。
- [ ] 把 LLM 输出从“动作名”升级为“意图 + 理由 + 可执行动作候选”。
- [ ] 增加规则校验层：AI 意图不合法时返回可解释失败。
- [ ] 增加离屏 NPC 摘要模拟，不要每个 NPC 每 tick 调 LLM。
- [ ] 区分核心 NPC、重要 NPC、背景 NPC 三种运行成本。

验收：

- [ ] NPC 能主动改变地点和目标。
- [ ] NPC 会因为记忆改变说法或行动。
- [ ] NPC 之间至少能产生一个非玩家直接触发的小事件。

## 里程碑 7：内容扩展到 5-10 个可信 NPC

目标：做小社会，不做空壳大世界。

- [ ] 新增 3 个原创 NPC：村长/导师、治疗者/记录者、巡逻者/边界见证者。
- [ ] 每个 NPC 有 persona、backstory、日程、目标、关系网、秘密或压力点。
- [ ] 每个 NPC 至少有 3 个日常行为和 2 个剧情反应。
- [ ] NPC 之间有关系：亲近、责任、怀疑、利益、旧事。
- [ ] 增加村庄传言系统：玩家行为会被 NPC 传播或误解。

验收：

- [ ] 玩家能在不对话的情况下观察到 NPC 日程。
- [ ] 至少 2 个 NPC 会基于同一事件产生不同态度。
- [ ] 至少 1 个事件由 NPC 之间的关系触发。

## 里程碑 8：内容工具和调试器

目标：AI 社会必须可观察，否则不可维护。

- [ ] 增加世界观察器页面：当前时间、flags、active events、NPC 目标。
- [ ] 增加 NPC 调试面板：状态、记忆、关系、计划、最近决策理由。
- [ ] 增加事件时间线回放。
- [x] 增加剧情配置校验脚本：事件 id、flag、参与者、地点是否有效。
- [x] 增加地图配置校验脚本：POI 是否可达、zone 是否重叠、入口是否有效。
  - [x] NPC 日程 tile 必须在对应 scene zone 内且可走，避免角色刷到水域或错误场景。
  - [x] POI 支持 `approach_tile_x/y` 校验，锁区边门可以有可达调查点。
- [ ] 增加存档迁移版本机制。

相关入口：

- `backend/tests/`
- `backend/app/content_validator.py`
- `backend/app/main.py`
- `/api/dev/content_validation`
- `frontend/src/components/`
- `scripts/`

验收：

- [ ] 开发者能解释任意 NPC 为什么在当前地点。
- [x] 配置错误能在测试中暴露，而不是运行时才发现。
  - [x] `visual.camera`、`visual.movement`、`visual.performance` 的数字和范围错误会被内容校验捕获。

## 里程碑 9：第二场景样板

目标：验证地图切换、实例玩法和边界异常的升级路线。

- [ ] 做正式第二张地图：北境森林边缘或洞窟入口。
- [ ] 通过第一章选择解锁第二场景入口。
- [ ] 第二场景不只是新地图，要有独立玩法：调查、危险、NPC 分歧。
- [ ] 增加一个 instance 场景样板：梦境、训练、遭遇、剧情演出四选一。
- [ ] instance 结束后写回关系、记忆、flags、玩家位置。

验收：

- [ ] 从村庄到第二地图切换无明显卡顿。
- [ ] 第二场景有明确的视觉差异和玩法差异。
- [ ] instance 不污染 field 地图渲染器。

## 里程碑 10：音频、动画和情绪表现

目标：让世界有情绪，不只是 UI 有文字。

- [ ] 建立音频表：点击、移动、对话、调查、事件、夜晚、雨、确认、失败。
- [ ] 增加环境音：雨、水、风、村庄、夜晚炉火。
- [ ] 重要事件加入短镜头和音效，不只弹窗。
- [ ] NPC 对话加入表情差分和情绪状态。
- [ ] 章节结尾加入余韵画面或日记，不只显示 ending_id。

验收：

- [ ] 关闭文字提示，玩家仍能通过画面和声音理解状态变化。
- [ ] 事件选择结果有情绪冲击，而不是只像表格结算。

## 里程碑 11：性能和质量门槛

目标：做到可持续开发，不靠手感猜测。

- [ ] 建立前端性能基线：首屏加载、FPS、移动耗时、内存。
  - [x] 第一版性能修复：静态地图 Graphics 烘焙为纹理，天气/引导线降频，常驻 HUD 去掉重合成 blur/mix-blend。
  - [x] E2E 质量门耗时从约 1.8 分钟降到约 22 秒，作为当前交互流畅度的粗基线。
- [x] 增加 Playwright 视觉 smoke：桌面和移动截图。
- [x] 增加 canvas 非空和关键 UI 不重叠检查。
- [x] 前端 build 不能有新增错误。
- [x] 后端 pytest 必须通过。
- [ ] E2E 至少覆盖：打开、移动、对话、触发事件、导出导入。
  - [x] 当前已覆盖：打开、画布 smoke、自然触发、读书玩法、午餐选择、训练小游戏、日志、Day 2 预告。
  - [ ] 待补：导出/导入存档、NPC 对话完整提交。

推荐验证命令：

```powershell
cd /d F:\usefultool39\02-UW小镇\backend
& 'F:\usefultool39\02-UW小镇\.conda\uw-runtime\python.exe' -m pytest -q

cd /d F:\usefultool39\02-UW小镇\frontend
npm.cmd run build
npm.cmd run test:e2e
```

注意：上面的 Python 命令如果路径含空格或失败，使用完整路径：

```powershell
& 'F:\usefultool39\02-UW小镇\.conda\uw-runtime\python.exe' -m pytest -q
```

## 里程碑 12：客户端契约与 Cocos 并行客户端（冻结备用）

目标：保留当前 Vue/Phaser 可玩基线，同时把 Cocos Creator 已完成部分冻结为未来备用表现层；当前阶段不继续投入 Creator 登录、预览和手工场景验收。

调整说明：
- 2026-05-15 起，当前主客户端回到 `frontend/` 的 Vue + Phaser。
- `cocos-client/` 不删除，用来保留 API 契约、DTO、地图渲染和未来迁移样板。
- Cocos 相关未完成项不再阻塞当前 Demo 质量提升。

- [x] 新增 `docs/CLIENT_CONTRACT.md`，锁定 Vue/Phaser 与 Cocos 共用 API、DTO、玩家行动和地图表现配置。
- [x] 后端路由 body 模型抽到 `backend/app/api_models.py`，保持 HTTP wire shape 兼容。
- [x] 玩家行动 kind、别名、失败 envelope 和常用 helper 抽到 `backend/app/player_actions.py`。
- [x] visual config 校验抽到 `backend/app/content_validation_visual.py`，并校验 `tileset_manifest` 类型。
- [x] 新建 `cocos-client/` Cocos Creator v0 工程骨架：API、DTO、本地 BFS、地图渲染、Field 控制器、Overlay UI 和静态校验。
- [x] 新增 `frontend/public/assets/game/tilesets/luin_village_v1.json` 作为 Vue/Phaser 与 Cocos 共用 tileset manifest 第一版。
- [x] Vue 客户端新增 `frontend/src/contracts/clientContract.js`，API route 和行动 kind 不再散落硬写。
- [x] `FieldSlice.vue` 先抽出 `useFieldToast`，作为前端大组件降债的第一步。
- [x] 在 Cocos Creator 编辑器内创建正式 `Boot` / `Field` 场景文件，并把当前脚本挂到节点上验证运行。
- [x] Cocos v0 脚本层补齐 Day 1 核心交互：读书、训练、午餐/晚餐态度、剧情选择、NPC 档案/对话、休息跨天。
- [x] Cocos `FieldController` 支持运行时自举，未手动绑定节点时也会自动创建基础地图和 UI 节点。
- [x] Cocos `FieldController` 运行时自动生成 Day 1 操作按钮，并避免按钮点击同时触发地图移动。
- [x] 增加 Cocos offline / live / cross-client smoke，覆盖 manifest、核心活动、真实后端 Day 1 API 链和双客户端契约一致性。
- [ ] 暂缓：在 Cocos Creator 编辑器内把上述方法绑定到按钮，完成真实点击验收。
- [ ] 暂缓：Cocos Creator 编辑器内真实构建/预览，并确认自动自举场景与手动绑定场景都能运行。

验收：

- [x] Cocos 骨架静态校验 `node scripts/validate-client.mjs` 通过。
- [x] 后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过。
- [x] 前端 `npm.cmd run build` 和 `npm.cmd run test:e2e` 通过。
- [x] 内容校验 `ok=True`，0 errors。

## 不要优先做

- 不要现在做 MMO 联机。
- 不要现在做大地图开放世界。
- 不要现在加大量职业、装备、经济系统。
- 不要把所有 NPC 都接入每 tick LLM。
- 不要把战斗逻辑塞进 `createWorldFieldScene.js`。
- 不要继续依赖官方 IP 名称作为公开设定。

这些不是永远不能做，而是会在当前阶段稀释核心体验。

## 推荐执行顺序

当前最新短期顺序以 [NEXT_HANDOFF_PLAN.md](NEXT_HANDOFF_PLAN.md) 为准。长期顺序如下：

第一批必须先做：

- 里程碑 0：产品定位和原创化清单。
- 里程碑 1.1：首屏信息架构。
- 里程碑 3.1：移动即时反馈。
- 里程碑 4：第一天体验重写。

第二批再做：

- 里程碑 12：客户端契约与 Cocos 并行客户端骨架。
- 里程碑 1.2：正式 UI 风格。
- 里程碑 2：地图美术资产。
- 里程碑 5：探索、日常、关系循环。
- 里程碑 8：调试器和配置校验。

第三批做世界深度：

- 里程碑 6：AI NPC 智能体升级。
- 里程碑 7：扩展到 5-10 个可信 NPC。
- 里程碑 9：第二场景样板。
- 里程碑 10：音频、动画和情绪表现。
- 里程碑 11：质量门槛。

## 单次开工模板

后续每次让智能体工作时，可以这样发：

```text
请读取 docs/GAME_QUALITY_ROADMAP.md，执行其中的「里程碑 X / 任务 Y」。
完成后：
1. 更新文档里的复选框。
2. 在执行记录追加本次改动。
3. 跑必要验证。
4. 告诉我改了哪些文件、哪些任务已完成、还有什么风险。
```

## 执行记录

- 2026-05-11：创建本任务板。当前只完成规划文档，尚未开始代码和美术改造。
- 2026-05-11：完成第一轮可视化改造。改动包括：普通模式隐藏顶部开发 Tab，`?dev=1` 才显示状态总览；重写第一章首屏任务文案；QuestTracker 改为“今日目标 / 正在发生 / 附近 / 地点”；Hotbar 改为动作栏并加入图标；移动点击改为前端本地 BFS 先播放，后端异步校验并可回滚；点击目标增加目的地光圈。验证：`npm.cmd run build` 通过；Playwright 截图输出到 `runs/quality_after_first_pass.png`，移动测试输出到 `runs/quality_after_move_test.png`，短距离移动记录 `lastWalkMs=479ms`。
- 2026-05-11：完成第二轮操作和地图观感改造。改动包括：降低程序化地块层、地形覆盖层和锁区纹理透明度，减少调试格子感；增加从玩家指向最近章节事件/任务 POI 的金色地面引导线；增加 WASD 和方向键移动，并在 Vue 全局热键层兜底，避免 Phaser 焦点丢失。验证：`npm.cmd run build` 通过，`npm.cmd run test:e2e` 通过；Playwright WASD 测试通过，记录 `lastWalkMs=371ms`；截图输出到 `runs/quality_after_guide_keyboard.png` 和 `runs/quality_after_wasd_move.png`。
- 2026-05-11：完成第三轮首屏目标和线索视觉改造。改动包括：世界内任务/章节事件从黄色感叹号替换为光柱、光环、核心点和标签组成的线索信标；任务面板事件标识改为发光圆点；热栏“线索”按钮改为星芒符号；新增可跳过的第一天开场叙事提示，并提供“前往线索”按钮把镜头移动到第一个剧情事件。验证：`npm.cmd run build` 通过，`npm.cmd run test:e2e` 通过；Playwright 桌面和手机截图输出到 `runs/quality_after_beacon_opening_desktop.png` 与 `runs/quality_after_beacon_opening_mobile.png`。截图检查发现桌面提示框与动作栏有 2px 重叠，已修正为 `bottom: 6.25rem`；手机提示框遮挡 HUD，已修正为 `top: 11.4rem`。受本次工具额度限制，最后一次 CSS 间距修正尚未重新截图和重新构建验证。
- 2026-05-12：十分钟快改轮。改动包括：Phaser 场景新增屏幕空间细雨和轻雾天气层，雨天地图有动态氛围；首屏按钮从“前往线索”改为“查看线索”，点击后镜头聚焦第一个剧情事件并自动打开事件选择面板；手机端开场提示改成左侧窄浮层，避开 HUD、小地图、世界内“进入村内交流”提示和底部热栏。验证：项目自带 Python 环境启动后端健康检查通过；Vite 前端启动成功；`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过；Playwright 截图输出到 `runs/quality_after_rain_brief_desktop.png`、`runs/quality_after_rain_brief_mobile.png`、`runs/quality_after_story_entry_panel.png`；自动框选检查确认 1440x900 与 390x844 下开场提示不遮挡 HUD、小地图、任务面板、顶部栏和热栏。
- 2026-05-12：完成选择反馈与日结算改造。改动包括：后端 `public_event_view` 为每个剧情选择输出 preview，用于前端提前显示谁会记住、关系变化、承诺和紧张暗线；`StoryEventPanel` 在选择按钮内显示影响标签；`StoryResultPanel` 改成更像结算页，展示情绪总结、关系变化、NPC 记忆卡、承诺/不安、时间推进事件和下一条线索；顶部“时间推进”和底部“休息”都会打开结算反馈，休息会显示 Day 1 结束与 Day 2 新线索。验证：`npm.cmd run build` 通过；后端 `pytest -q` 通过，137 passed；`npm.cmd run test:e2e` 通过；截图输出到 `runs/quality_after_choice_preview.png`、`runs/quality_after_choice_result_memory.png`、`runs/quality_after_daily_summary.png`、`runs/quality_after_day_settlement.png`。
- 2026-05-12：新增下一窗口接手计划文档 `docs/NEXT_HANDOFF_PLAN.md`，明确下一阶段优先做 Day 1 自然玩法循环：线索手册/记忆日志、自然地点触发、训练小游戏雏形、NPC 态度来源和 Day 2 目标预告；同时在 `docs/README.md` 和本文顶部加入入口，便于另一个窗口直接接手。
- 2026-05-12：完成 Day 1 自然玩法循环第一版。改动包括：新增 `ClueJournalPanel` 作为热栏第 5 格日志入口，汇总已发现线索、最近写入的 NPC 记忆和关系暗线；靠近书库/巨树时，地点互动面板会注入“调查边界记录 / 开始巨树训练”等章节事件入口，右侧“正在发生”仍保留为兜底；Day 1 休息后的日结算增加 Day 2 目标卡和“查看目标”镜头聚焦按钮。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过；Playwright 截图输出到 `runs/quality_after_clue_journal.png`、`runs/quality_after_clue_journal_mobile.png`、`runs/quality_after_natural_event_trigger.png`、`runs/quality_after_natural_event_trigger_tree.png`、`runs/quality_after_day2_preview.png`、`runs/quality_after_day2_preview_mobile.png`。
- 2026-05-12：完成 NPC 态度来源和训练小游戏第一版。改动包括：`NpcProfilePanel` 顶部新增“最近态度来源”，用关系数值、最近重要记忆、承诺和紧张点解释 NPC 为什么信任或担心玩家，并对重复记忆做 UI 去重；新增 `TrainingMiniGamePanel`，巨树训练事件会先进入 3 次点击/空格节奏判定，再调用原有剧情选择写入关系变化和 NPC 记忆，结算页显示训练表现。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过；Playwright 截图输出到 `runs/quality_after_npc_profile_reason.png`、`runs/quality_after_training_minigame.png`、`runs/quality_after_training_minigame_result.png`。
- 2026-05-12：完成下一阶段第一批执行包。改动包括：`README.md` 和 `docs/PROJECT.md` 改为“边境回声”公开定位，补齐玩家幻想、核心体验、20-30 分钟目标和原创化清单；新增 `docs/DAY1_VERTICAL_SLICE.md`，用 20 个关键节点定义 Day 1 完整体验；后端 `scene_activity` 支持 `activity_choice`，读书/午餐/晚餐选择可写入 flags、关系、NPC 记忆、承诺和紧张点；新增 `ReadingMiniGamePanel.vue` 和 `MealChoicePanel.vue`；更新场景活动、角色显示名、persona 和公开 UI 文本；QuestTracker 增加 NPC 附近对话提示；E2E 扩展到视觉 smoke、读书、午餐、训练、日志和 Day 2 预告。验证：后端 `pytest -q` 通过，138 passed（仅 pytest cache 权限警告）；`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过；截图输出到 `runs/quality_gate_desktop.png`、`runs/quality_gate_mobile.png`。
- 2026-05-13：完成第二批的关系影响与配置校验第一版。改动包括：Day 2 森林异常会根据 Day 1 晚餐选择切换描述、提示和可见选项；兑现艾琳谨慎或尤里承诺会写入 flags、关系、记忆、承诺和紧张点；备用 NPC 对话根据 trust / affinity / tension 改变普通回应语气；新增 `backend/app/content_validator.py` 和 `/api/dev/content_validation`，校验剧情事件、活动、地图、POI、scene、participants、relationship key 和 story node 引用；修正 Day 3 边界事件坐标到可走 tile。验证：后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，145 passed；前端 `npm.cmd run build` 通过；前端 `npm.cmd run test:e2e` 通过，2 passed。
- 2026-05-13：完成地图可读性修复第一版。改动包括：`world_map.json` 和 `north_boundary_stub.json` 增加 `visual.background=false`，前端不再用临时大背景作为主视觉；`worldMapDrawing.js` 强化道路、水、森林、障碍的分层渲染，道路直接跟可走数据对齐；新增可切换导航调试层；配置校验扩展到 NPC schedules，日程 tile 如果落到不可走区域会在测试里暴露。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过，2 passed；后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，145 passed。
- 2026-05-13：完成地图分层与落点修复第二版。改动包括：NPC、POI、章节事件在前端显示时会吸附到最近可走格；北境边门新增 `approach_tile_x/y`，玩家站在门前道路即可调查，配置校验也按 approach tile 判断可达性；修正艾琳/尤里傍晚日程坐标，新增 schedule scene-zone 校验，避免 NPC 刷到错误场景或水面；草地底色改为更连续的地表，水岸、森林边缘、障碍和水面波纹进一步细化；水域、树林、岩石障碍点击会在前端直接阻止并给出不可达反馈；导航调试层可通过 `Ctrl/Shift+V` 切换。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过，2 passed，截图输出到 `runs/quality_gate_desktop.png` 和 `runs/quality_gate_mobile.png`；后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，145 passed；内容校验 `ok=True`，0 errors，仅剩 3 个已知 zone overlap warnings。
- 2026-05-13：补充美术方向计划并调细当前地图框架。新增 `docs/ART_DIRECTION_PLAN.md`，明确推荐“细颗粒 2D 俯视 / 高清像素混合风格”、地图层级、资产清单、角色/地形比例和制作顺序；当前框架把主地图和北境 stub 的 `tile_size` 从 34 调到 28，默认镜头拉远，玩家和 NPC token 缩小，交互提示缩小，减少角色像大棋子的感觉。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过，2 passed，截图刷新到 `runs/quality_gate_desktop.png` 和 `runs/quality_gate_mobile.png`；后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，145 passed；内容校验 `ok=True`，0 errors，3 个已知 zone overlap warnings。
- 2026-05-13：完成第一轮操作流畅度修复。改动包括：把静态地图底层、地形覆盖层和导航调试层从大量 Phaser Graphics 烘焙为纹理，避免每帧重画几千个矢量图元；水纹、天气和任务引导线降频更新；移动速度从 430px/s 提到 720px/s，镜头跟随从 0.08 提到 0.18；新增左键拖拽平移镜头，短按仍然点击移动；降低常驻 HUD、小地图、热栏、任务面板的 blur / mix-blend 合成开销。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过，2 passed，总耗时约 21.9s；后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，145 passed；内容校验 `ok=True`，0 errors，3 个已知 zone overlap warnings。
- 2026-05-13：完成初始地图框架整理与下午接手计划。改动包括：`world_map.json.visual` 和 `north_boundary_stub.json.visual` 增加 `scale/camera/movement/performance` 配置，前端读取这些配置决定默认 zoom、滚轮步进、镜头跟随、移动速度、左键拖拽、动态层刷新频率和静态层烘焙；`backend/app/content_validator.py` 增加 visual 配置校验；`data/world/maps/README.md` 补充 visual schema 和调参建议；新增 `docs/AFTERNOON_MAP_POLISH_PLAN.md`，写清下午继续优化点击移动、镜头拖拽、地图可读性、性能基线和美术接入框架的路线。验证：`npm.cmd run build` 通过；`npm.cmd run test:e2e` 通过，2 passed，总耗时约 22.1s；后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，145 passed；内容校验 `ok=True`，0 errors，3 个已知 zone overlap warnings。
- 2026-05-13：完成 Cocos 并行客户端与可维护框架升级第一版。改动包括：新增 `docs/CLIENT_CONTRACT.md` 锁定双客户端共用 API/DTO/玩家行动/地图表现契约；后端新增 `api_models.py`、`player_actions.py` 和 `content_validation_visual.py`，把路由 body、玩家行动共享规则和 visual 校验从大文件中拆出；`world_map.json.visual` 与北境 stub 增加 `tileset_manifest`，新增 `luin_village_v1.json` manifest；Vue 客户端新增 `clientContract.js` 并让 `useGameApi` 统一使用 route 常量，`FieldSlice` 抽出 `useFieldToast`；`cocos-client/` 从占位 README 升级为 Cocos Creator v0 工程骨架，包含 API、DTO、本地 BFS、地图渲染、Field 控制器、Overlay UI 和静态校验脚本。验证：后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，149 passed；前端 `npm.cmd run build` 通过；前端 `npm.cmd run test:e2e` 通过，2 passed，总耗时约 20.0s；Cocos 骨架 `node scripts\validate-client.mjs` 通过；内容校验 `ok=True`，0 errors，3 个已知 zone overlap warnings。
- 2026-05-13：继续推进 Cocos v0 Day 1 脚本闭环。改动包括：`GameApi.ts` 扩展场景活动、剧情选择、NPC 对话、NPC Profile、存档导入导出和 reset；`FieldController.ts` 增加可直接绑定按钮的方法：读书、训练、午餐、晚餐、首个剧情选择、NPC 档案、NPC 问候、休息跨天和重置；`OverlayUI.ts` 增加目标/详情 Label 更新；新增 `cocos-client/assets/scenes/README.md` 写清 Boot/Field 场景节点接线和按钮绑定；Cocos 静态校验脚本现在会检查关键 API 和 Day 1 按钮方法是否存在。验证：后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，149 passed；前端 `npm.cmd run build` 通过；前端 `npm.cmd run test:e2e` 通过，2 passed，总耗时约 22.0s；Cocos 骨架 `node scripts\validate-client.mjs` 通过；内容校验 `ok=True`，0 errors，3 个已知 zone overlap warnings。
- 2026-05-13：继续完成 Cocos v0 自举和契约回归。改动包括：`FieldController` 新增 `ensureRuntimeWiring`，没有手动拖拽绑定时会自动创建 `AutoMapRoot`、`MapGraphics`、`Player`、`NpcRoot`、`PoiRoot` 和三条 Overlay Label；`runDinnerDemo` 会先推进到 evening/night 再执行晚餐，避免清晨直接点击失败；新增 `field.scene-manifest.json` 作为机器可读场景绑定清单；新增 `offline-contract-smoke.mjs`、`live-contract-smoke.mjs`、`cross-client-contract-smoke.mjs`，分别验证地图/活动/manifest、真实后端 Day 1 API 链、Vue 与 Cocos 的契约版本/路由/action 一致性。验证：后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，149 passed；前端 `npm.cmd run build` 通过；前端 `npm.cmd run test:e2e` 通过，2 passed，总耗时约 30.9s；Cocos `validate-client`、offline smoke、cross-client smoke、live smoke 全部通过；内容校验 `ok=True`，0 errors，3 个已知 zone overlap warnings。备注：本机未检测到可用 Cocos Creator CLI，因此仍未做编辑器内真实预览验收。
- 2026-05-14：继续完成 Cocos v0 真实场景资产。改动包括：新增 `assets/scenes/Boot.scene` 和 `assets/scenes/Field.scene`，`Boot` 挂载 `Boot.ts` 并自动加载 `Field`，`Field` 建立 `Canvas/Camera/FieldRoot` 并挂载 `FieldController`；`FieldController` 的自动地图根节点默认偏移到可视区域，`MapRenderer` 新增 `uiToTile` 让点击坐标正确换算到地图 tile；`field.scene-manifest.json` 记录真实场景资产；`validate-client.mjs` 现在会检查场景文件、meta importer、Boot/Field 脚本组件类型；`cocos-client/.gitignore` 补齐 lowercase `library/`、`temp/`；场景说明文档更新为“可直接打开 Boot/Field”而不是只给手工搭建说明。验证：`npm.cmd run validate`、`npm.cmd run typecheck`、`npm.cmd run doctor`、`npm.cmd run verify`、`npm.cmd run smoke:live` 全部通过；Cocos Creator 运行中已自动导入 `Boot.scene` 与 `Field.scene`，`library/.assets-info.json` 和 `.assets-data.json` 均出现对应 UUID。备注：尚未在编辑器预览窗口里完成按钮真实点击验收，下一步继续补 Overlay 按钮节点。
- 2026-05-14：补齐 Cocos v0 运行时 Day 1 操作按钮。改动包括：`FieldController.ensureRuntimeWiring` 自动生成 Refresh、Story、Read、Train、Lunch、Dinner、NPC Profile、Greet、Rest、Reset 按钮；按钮使用 Cocos `Button` 组件和 Label，直接调用现有 Day 1 方法；新增运行时按钮命中区域判断，避免点击按钮时同时触发地图移动；`validate-client.mjs` 增加 `makeRuntimeButton` 检查。验证：`npm.cmd run typecheck`、`npm.cmd run validate`、`npm.cmd run verify`、`npm.cmd run smoke:live` 全部通过。备注：真实编辑器预览窗口点击验收仍是下一步。
- 2026-05-15：完成公开命名与启动文档收尾。改动包括：浏览器标题改为“边境回声 · 露茵村第一章”；前后端 README、根 `package-lock.json`、`backend/pyproject.toml`、备用 `frontend/server.cjs` banner、Windows 启动窗口标题和 `docs/SCENE_SYSTEM.md` 启动路径清理旧项目名/历史路径；`backend/start.sh` 改为按当前目录、`app.main:app`、8765/3000 端口启动；pytest 缓存改到已忽略的 `_test_tmp/.pytest_cache`，避开旧 `.pytest_cache` ACL 警告。验证：后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，151 passed；前端 `npm.cmd run build` 通过；前端 `npm.cmd run test:e2e` 通过，2 passed；旧公开命名复扫仅剩原创化对照表和当前磁盘路径。
- 2026-05-15：完成交互和 AI NPC 深度第一版。改动包括：`NpcIntent` 增加 `stakes` 与 `response_options`；新增 `respond_npc_intent` 玩家行动，回应 NPC 主动意图后写入 flags、关系变化、NPC 重要记忆、承诺和紧张点，并返回 `intent_result`；艾琳/尤里的书库、训练、午餐、晚餐和 Day 2 异常意图补充可回应选项；前端互动面板会显示“NPC 回应”按钮，结果复用结算面板；NPC Profile 增加 `mind` 快照，展示当前目标、主动关注点、状态倾向和主观认知；Vue/Cocos 客户端契约升级到 `client-contract-2026-05-15-v2`。验证：后端 `.conda\uw-runtime\python.exe -m pytest -q` 通过，154 passed；前端 `npm.cmd run build` 通过；前端 `npm.cmd run test:e2e` 通过，2 passed；Cocos `npm.cmd run typecheck` 和 `npm.cmd run smoke:cross-client` 通过。
