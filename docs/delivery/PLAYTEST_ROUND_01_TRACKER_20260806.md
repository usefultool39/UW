# 首轮真人盲测批次跟踪表

- **批次**：`QA-PLAY-001 / Round 01`
- **版本基线**：`1b313c6`（Day 8–16 回响反馈切片）
- **当前状态**：`pending-human-run`
- **目标**：收集 3 名未参与开发玩家的 Day 1 首次体验证据；不把自动化 E2E、开发者自测或 AI 代打当作真人数据。
- **范围**：第一次有效互动、当天目标、行动代价/收益、剧情闸提示、继续意愿。

## 执行前固定检查

```bash
cd /Users/lzm/Desktop/UW
./scripts/quality.sh
UW_RATE_LIMIT_ENABLED=0 E2E_BACKEND_PORT=8011 E2E_FRONTEND_PORT=4174 \
  npm --prefix frontend run test:e2e
./start-macos.command
```

主持人必须使用全新浏览器上下文，从“新游戏”开始，不解释地图、日期或行动规则。具体话术和观察表使用：

- `/Users/lzm/Desktop/UW/docs/delivery/DAY1_BLIND_TEST_RUNBOOK_20260805.md`
- `/Users/lzm/Desktop/UW/materials/inbox/research/playtest/QA-PLAY-001_playtest_kit_v001.md`

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
- `continue_interest`: `yes / uncertain / no`
- `hint_count`
- `highest_frequency_blocker`

## 批次判定

首轮不追求“所有人都顺利”，只寻找最高频阻塞点：

- 上手：至少 2/3 在 60 秒内完成第一次有效互动；
- 目标：至少 2/3 能说出当天要追的目标；
- 代价：至少 2/3 能说出一种行动代价；
- 收益：至少 2/3 能说出一种线索、关系或记忆收益；
- 闸门：3/3 都不能在未完成必需事件时跨日；
- 继续意愿：至少 2/3 愿意查看 Day 2。

若只有一项不达标，只修该项对应的最高频阻塞；若多项不达标，优先修复“首次互动/当天目标”，再重复质量门和盲测。不得趁盲测一次性扩展新系统。

## 回填后动作

1. 将三份匿名玩家记录放入 `materials/inbox/research/playtest/`；
2. 检查录屏不含私人信息；私人录屏不提交 Git；
3. 汇总最高频阻塞点和原话，不写推测性结论；
4. 更新 `CURRENT_STATUS.md`、`NEXT_PHASE.md`、`CHANGELOG.md`；
5. 运行后端、前端、build、E2E 和 `git diff --check`；
6. 提交并推送；
7. 只有三份记录与访谈完整后，才把 QA-PLAY-001 标记为 `received`。
