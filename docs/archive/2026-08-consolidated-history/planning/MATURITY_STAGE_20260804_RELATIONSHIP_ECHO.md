# WP-2 冻结方案：Day 1 书库选择的 Day 2 关系回响

- 日期：2026-08-04
- 状态：Frozen / implementation slice
- 对应阶段：`NEXT_PHASE.md` 的 WP-2「关系后果闭环」
- 优先级：P0

## 体验审计

Day 1 的书库事件已经提供两条清晰选择：

1. 把边界记录告诉艾琳（`ask_alice`）；
2. 暂时隐瞒书页符号（`keep_note`）。

两条选择都会写入 flag、关系和永久记忆，但 Day 2「森林忽然安静」此前主要回响 Day 1 晚餐态度。玩家很难确认书库里的关键决定是否真的改变后续，削弱了“选择—关系—异常升级”的三日短循环。

## 冻结改造

只为 `ch1_d2_forest_anomaly` 增加两个由后端条件过滤的互斥选择，不新增 variant，不改变既有通用选择及 Day 2→Day 3 variant 优先级。

### 路线 A：公开记录

- choice：`use_alice_marked_record`
- 前置：`alice_warned_boundary=1` 且没有 `kept_boundary_note`
- 玩家表达：按艾琳昨天圈出的记录对照静默线
- 结算：写入 `followed_alice_mark_day2`，提升艾琳信任并保留适量异常紧张，写入艾琳永久记忆

### 路线 B：补交隐瞒信息

- choice：`confess_hidden_note`
- 前置：`kept_boundary_note=1` 且没有 `alice_warned_boundary`
- 玩家表达：把昨天隐瞒的书页符号告诉艾琳
- 结算：写入 `confessed_hidden_note_day2`，以短期紧张换取信任修复，写入艾琳永久记忆与关系紧张原因

## 兼容边界

- FastAPI 后端继续过滤可见 choice 并执行最终结算。
- scripted、hybrid、agent NPC 只消费同一事件结果和永久记忆，不自行决定 flag、关系或奖励。
- 不改存档结构，不新增 API，不向客户端暴露 authored effects。
- 非法分支必须返回 `unknown_choice`，且状态和记忆都不发生部分写入。

## 验收

1. 两条正常 Day 1 路线在 Day 2 只出现各自的回响选择。
2. 选择后 flag、关系变化和永久记忆正确。
3. 跨路线强选被后端拒绝且不写状态。
4. 至少一条 Day 1→Day 2 浏览器试玩验证能看到并结算关系回响。
5. 后端全量测试、前端单测、production build、完整 E2E、`git diff --check` 全绿。
