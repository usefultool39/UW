# 首轮真人盲测批次跟踪表

- **批次**：`QA-PLAY-001 / Round 01`
- **版本基线**：当前未发布 `0.5.0-pre-capture` 工作树；正式发布版本仍为 `0.4.0-preview.1`
- **当前状态**：`pending-human-run`
- **目标**：收集 3 名未参与开发玩家从新游戏连续完成 N01-N10、到达 `alice_captured` 的真人证据；不把自动化 E2E、开发者自测或 AI 代打当作真人数据。
- **范围**：第一次有效互动、目标与代价/收益、跨节点回响、完整主线完成、抓捕原因与终点理解、抓捕后不可推进、继续意愿。

> 旧 Day 1 套件与话术可继续用于记录 60 秒上手证据，但不能独立满足第一阶段的 3 人完整主线盲测。

## 执行前固定检查

```powershell
cd C:\Users\liang\Desktop\UW
backend\.venv\python.exe -m pytest -q
npm.cmd --prefix frontend run test:unit
npm.cmd --prefix frontend run build
$env:CI='1'
$env:E2E_BACKEND_PORT='8033'
$env:E2E_FRONTEND_PORT='4193'
npm.cmd --prefix frontend run test:e2e -- --reporter=line
```

主持人必须使用全新浏览器上下文，从“新游戏”开始，不解释地图、日期或行动规则。具体话术和观察表使用：

- `C:\Users\liang\Desktop\UW\docs\delivery\DAY1_BLIND_TEST_RUNBOOK_20260805.md`（仅上手阶段话术）
- `C:\Users\liang\Desktop\UW\materials\inbox\research\playtest\QA-PLAY-001_playtest_kit_v001.md`（仅上手阶段套件）

## 盲测交付入口

macOS 原有盲测启动脚本可用于固定 scripted 和重置存档：

```bash
cd /Users/lzm/Desktop/UW
./scripts/playtest-preflight.sh
```

交给主持人：

```bash
./试玩盲测.command
```

该入口会固定 `scripted`、使用 production build、验证内容校验、重置一次试玩存档，并在有 Chrome 时打开隐身窗口。Windows 尚无等价专用盲测批处理时，可在工程门通过后用 `启动全部项目.bat`，手动选择新游戏并确认 NPC 模式为 scripted。`runs/playtest/launch_*.json` 只是环境启动元数据，不是玩家证据。

三名玩家之间重新启动入口，或在游戏内选择新游戏；不要复用上一名玩家的存档。

## 玩家证据状态

| 玩家 | 记录文件 | 录屏 | 访谈五问 | 状态 |
|---|---|---|---|---|
| player01 | `materials/inbox/research/playtest/QA-PLAY-001_player01.md` | pending | pending | pending-human-run |
| player02 | `materials/inbox/research/playtest/QA-PLAY-001_player02.md` | pending | pending | pending-human-run |
| player03 | `materials/inbox/research/playtest/QA-PLAY-001_player03.md` | pending | pending | pending-human-run |

不得在没有真人执行的情况下把 `pending` 改成 `received`，也不得用预测或开发者意见填入玩家原话。

## 统一回填指标

每位玩家只记录观察到的事实：

- `first_effective_interaction_seconds`
- `understood_day_goal`: `yes / partial / no`
- `named_action_cost`: `yes / partial / no`
- `named_action_benefit`: `yes / partial / no`
- `bypassed_day_gate`: `yes / no`
- `completed_precapture_route`: 必须为 `yes`
- `reached_alice_captured`: 必须为 `yes`
- `post_capture_progress_blocked`: 必须为 `yes`
- `recognized_choice_echo`: `yes / partial / no`
- `understood_capture_reason`: `yes / partial / no`
- `total_session_minutes`
- `endpoint_explanation`: 玩家对抓捕原因和终点的原话摘要
- `continue_interest`: `yes / uncertain / no`
- `hint_count`
- `highest_frequency_blocker`

## 批次判定

第一阶段完成要求三人都完成全程；体验指标用于定位最高频阻塞点：

- 上手：至少 2/3 在 60 秒内完成第一次有效互动；
- 目标：至少 2/3 能说出当天要追的目标；
- 代价：至少 2/3 能说出一种行动代价；
- 收益：至少 2/3 能说出一种线索、关系或记忆收益；
- 闸门：3/3 都不能在未完成必需事件时跨日；
- 主线：3/3 完成 N01-N10 并到达 `alice_captured`；
- 终端：3/3 观察到抓捕后 authored 剧情/日期不可继续推进；
- 理解：至少 2/3 能说明爱丽丝被带走的直接原因并识别一次选择回响；
- 继续意愿：至少 2/3 愿意继续探索同一阶段的可选生活内容。

若只有一项不达标，只修该项对应的最高频阻塞；若多项不达标，优先修复“首次互动/当天目标”，再重复质量门和盲测。不得趁盲测一次性扩展新系统。

## 回填后动作

1. 将三份匿名玩家记录放入 `materials/inbox/research/playtest/`；
2. 检查录屏不含私人信息；私人录屏不提交 Git；
3. 汇总最高频阻塞点和原话，不写推测性结论；
4. 更新 `CURRENT_STATUS.md`、`NEXT_PHASE.md`、`CHANGELOG.md`；
5. 运行后端、前端、build、E2E 和 `git diff --check`；
6. 只有三份完整 N01-N10 记录与访谈通过 checker 后，才把 QA-PLAY-001 标记为 `received`；
7. 提交或推送前必须获得用户明确确认。
