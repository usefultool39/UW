# 下一窗口接手计划：Day 1 自然玩法循环

更新日期：2026-05-12  
接手目标：把当前“能点剧情事件的可玩原型”，推进成“玩家在地图上自然探索、调查、训练、对话、结算”的 Day 1 垂直切片。

## 当前状态

已经能玩，但仍是早期纵切：

- 地图主界面可运行，点击移动、WASD/方向键移动可用。
- 首屏有开场提示、线索信标、目标引导、细雨氛围。
- 剧情选择前会显示谁会记住、关系变化、承诺/紧张暗线。
- 剧情选择后会显示关系变化、NPC 记忆卡、下一条线索。
- 时间推进会显示 NPC 做了什么。
- 休息会显示 Day 1 结算和 Day 2 线索。

当前最大问题：

- 玩家仍然主要通过“点击章节事件按钮”推进，缺少自然地点调查和 NPC 引导。
- 训练、读书、晚餐仍偏文本活动，不够像游戏玩法。
- 没有线索手册/记忆日志，玩家难以回看自己发现了什么。
- NPC 会记住，但玩家还不能很方便地查看“谁为什么改变了态度”。

## 下一步首选任务

优先做 **里程碑 4 + 里程碑 5 的最小闭环**：

> Day 1 自然玩法循环：书库调查 → 告诉/隐瞒艾琳 → 巨树训练 → 和尤里建立差异化关系 → 回家休息 → Day 2 伏笔。

这比继续打磨弹窗更重要，因为它会直接提升可玩性。

## 任务 1：线索手册 / 记忆日志

目标：玩家能随时看到自己发现过什么、谁记住了什么。

状态：已完成第一版。

建议实现：

- 新增 `frontend/src/components/ClueJournalPanel.vue`。
- 在 `Hotbar.vue` 把第 5 个按钮从单纯“线索”扩展为“线索/日志”入口，或者新增可复用日志入口。
- 日志内容先从现有数据拼出来，不急着新增复杂后端：
  - `simState.completed_event_ids`
  - `simState.flags`
  - `simState.relationships`
  - 最近一次 `storyResult.memory_written`
  - 可选：调用已有 `/api/npc/{npc_id}/profile` 读取 NPC 重要记忆。
- 日志分三栏即可：
  - `发现的线索`
  - `NPC 记住的事`
  - `关系暗线`

建议文件：

- `frontend/src/components/FieldSlice.vue`
- `frontend/src/components/Hotbar.vue`
- `frontend/src/components/ClueJournalPanel.vue`
- `frontend/src/field/gameContentConfig.js`

验收：

- [x] 玩家完成一次剧情选择后，能在日志里看到对应线索。
- [x] 玩家能看到至少一个 NPC 记住了什么。
- [x] 日志不遮挡地图主操作；桌面和手机都可关闭。
- [x] 截图保存到 `runs/quality_after_clue_journal.png`，手机补图为 `runs/quality_after_clue_journal_mobile.png`。

## 任务 2：把“点击章节事件”改成自然地点触发

目标：玩家不是点右侧按钮读剧情，而是走到书库/巨树等地点，自然出现调查或事件入口。

状态：已完成第一版，右侧事件入口保留为兜底。

建议实现：

- 在 `QuestTracker.vue` 里保留“正在发生”，但弱化它的按钮感。
- 在 `FieldSlice.vue` 的 `nearbyInteract` / `visibleInteractActions` 中注入当前地点可触发的 story event。
- 当玩家靠近 event.location 对应 tile 或 scene_id 时：
  - 世界内出现“调查书页 / 询问艾琳 / 开始训练”等入口。
  - 点击入口打开 `StoryEventPanel`。
- 右侧任务栏只负责提示方向，不再作为主要触发入口。

建议文件：

- `frontend/src/components/FieldSlice.vue`
- `frontend/src/components/FieldInteractPanel.vue`
- `frontend/src/components/QuestTracker.vue`
- `frontend/src/field/createWorldFieldScene.js`
- `data/story/events_chapter_01.json`

验收：

- [x] 玩家走到书库附近，能看到“调查边界记录”入口。
- [x] 玩家走到巨树附近，能看到“开始训练”入口。
- [x] 不靠右侧事件按钮，也能打开 Day 1 两个核心事件。
- [x] 右侧事件按钮仍可作为兜底，不要直接删除。
- [x] 截图保存到 `runs/quality_after_natural_event_trigger.png`，巨树补图为 `runs/quality_after_natural_event_trigger_tree.png`。

## 任务 3：训练小游戏雏形

目标：巨树训练不只是点选文本，而有一个最小操作玩法。

状态：已完成第一版。

建议先做轻量版本，不要做复杂战斗系统：

- 新增 `TrainingMiniGamePanel.vue`。
- 玩家点击“巨树旁的训练”后，不直接完成，先进入 10-15 秒小游戏。
- 最小玩法：
  - 屏幕显示节奏条或三段时机点。
  - 玩家按空格/点击，命中越准，训练结果越好。
  - 结果映射到不同 choice 或 activity：
    - 稳定完成：`eugeo.affinity +5`
    - 追问边界：仍走原剧情 choice
    - 失误：只给轻量反馈，不惩罚太重。

建议为了快，先只前端小游戏，最后仍调用现有 `chooseStoryEvent` 或 `playerAction`。

建议文件：

- `frontend/src/components/TrainingMiniGamePanel.vue`
- `frontend/src/components/FieldSlice.vue`
- `frontend/src/components/StoryEventPanel.vue`
- `data/story/events_chapter_01.json`

验收：

- [x] 玩家在巨树训练前至少有一个点击/按键动作。
- [x] 训练完成后仍写入关系变化和 NPC 记忆。
- [x] 失败/一般/优秀至少有 2 档可见反馈。
- [x] 截图保存到 `runs/quality_after_training_minigame.png`，结算补图为 `runs/quality_after_training_minigame_result.png`。

## 任务 4：NPC Profile 加“最近为什么这样看你”

目标：把 AI NPC 的记忆和关系变化变得更可信。

状态：已完成第一版。

建议实现：

- 在 `NpcProfilePanel.vue` 顶部增加“最近态度来源”区域。
- 展示：
  - 当前信任/好感/紧张。
  - 最近一条重要记忆。
  - 最近承诺/最近紧张点。
- 如果后端已有 profile 字段就直接用；不要先重构 memory store。

建议文件：

- `frontend/src/components/NpcProfilePanel.vue`
- `backend/app/relationship.py`，仅在 profile 缺字段时小改。
- `backend/app/memory_store.py`，只读现有 summary，不做大重构。

验收：

- [x] 点击 NPC 的关系档案时，能看到“TA 为什么信任/担心你”。
- [x] 完成一次剧情选择后，NPC 档案内容会变化。
- [x] 截图保存到 `runs/quality_after_npc_profile_reason.png`。

## 任务 5：Day 2 目标预告

目标：Day 1 结束后玩家知道下一天要做什么，不会中断。

状态：已完成第一版。

建议实现：

- 在 `StoryResultPanel` 的 `day_settlement` 模式里加强 Day 2 预告。
- 如果 `next_events` 有事件，显示：
  - 事件名
  - 地点名
  - 参与 NPC
  - “明天去哪里”的按钮
- 按钮可以调用现有 `centerCameraOnTile`，先不自动移动玩家。

建议文件：

- `frontend/src/components/StoryResultPanel.vue`
- `frontend/src/components/FieldSlice.vue`
- `frontend/src/field/gameContentConfig.js`

验收：

- [x] Day 1 休息后，玩家能看到 Day 2 的第一目标。
- [x] 点击目标按钮能把镜头带到 Day 2 线索附近。
- [x] 截图保存到 `runs/quality_after_day2_preview.png`，手机补图为 `runs/quality_after_day2_preview_mobile.png`。

## 推荐执行顺序

另一个窗口建议按这个顺序做：

1. 做任务 1：线索手册 / 记忆日志。
2. 做任务 2：自然地点触发。
3. 做任务 5：Day 2 目标预告。
4. 如果还有时间，再做任务 4：NPC Profile 态度来源。
5. 最后再做任务 3：训练小游戏雏形，因为它最容易扩散。

原因：

- 线索日志和自然触发能最快补上“我在探索世界”的感觉。
- Day 2 目标预告能让当前 Day 1 结算真正接上后续。
- 训练小游戏很重要，但要小心不要把范围扩大成战斗系统。

## 不要在下一窗口优先做

- 不要扩成大地图或 MMO。
- 不要重写 Phaser 场景架构。
- 不要一次性新增大量 NPC。
- 不要大改后端 AI loop。
- 不要把所有 UI 都推倒重做。
- 不要删除右侧事件入口，先保留兜底。

## 必跑验证

每完成一组改动后至少跑：

```powershell
cd /d F:\usefultool39\02-UW小镇\frontend
npm.cmd run build
npm.cmd run test:e2e
```

如果改了后端：

```powershell
cd /d F:\usefultool39\02-UW小镇\backend
& 'F:\usefultool39\02-UW小镇\.conda\uw-runtime\python.exe' -m pytest -q
```

视觉改动必须用 Playwright 截图，至少覆盖：

- `1440x900`
- `390x844`

截图放到 `runs/`，并在 `docs/GAME_QUALITY_ROADMAP.md` 的执行记录里写清楚。

## 给下一个窗口的提示词

可以直接复制下面这段给另一个窗口：

```text
请读取 F:\usefultool39\02-UW小镇\docs\NEXT_HANDOFF_PLAN.md 和 docs\GAME_QUALITY_ROADMAP.md。

优先执行 NEXT_HANDOFF_PLAN.md 里的「任务 1：线索手册 / 记忆日志」和「任务 2：把点击章节事件改成自然地点触发」。

要求：
1. 每完成一个子任务，就在 NEXT_HANDOFF_PLAN.md 和 GAME_QUALITY_ROADMAP.md 里打勾。
2. 不要重写整体架构，不要删除右侧剧情事件兜底入口。
3. 保持后端为权威世界状态，前端只做表现和输入。
4. 完成后运行 npm.cmd run build、npm.cmd run test:e2e；如果改后端，运行后端 pytest。
5. 用 Playwright 截 1440x900 和 390x844 图，保存到 runs/。
6. 最后告诉我改了哪些文件、哪些任务已完成、截图在哪里、还有什么风险。
```
