# WP-2B 冻结方案：Day 1 书库选择延伸到 Day 3

- 日期：2026-08-04
- 状态：Frozen / implementation slice
- 对应阶段：`NEXT_PHASE.md` 的 WP-2「关系后果闭环」
- 优先级：P0（Day 1–3 因果闭环）

## 体验审计

WP-2A 已让 Day 1 书库选择在 Day 2 产生可操作的关系回响，但 Day 3 结局判定面板此前只显示固定的边界说明，玩家看不到“昨天的公开记录 / 坦白”如何继续影响最终判断。这样会让早期选择在关键收束前再次断开。

## 冻结改造

只增加两个 Day 3 事件 variant，并在结局判定面板显示后端返回的事件上下文：

1. `followed_alice_mark_day2=1`
   - Day 3 描述艾琳昨天圈出的记录如何成为共同判断依据。
   - 调整秩序 / 越界提示，强调这次选择是在共同记录上继续推进。
2. `confessed_hidden_note_day2=1`
   - Day 3 描述坦白后的符号已补进记录，玩家不能假装事实没有发生。
   - 调整回村 / 隐瞒提示，强调重新隐瞒会重新制造裂痕。

不增加新的结局 choice，不改变既有 `from_day2_together` / `from_day2_risk` 优先级的正常路线；两个新 variant 只匹配 WP-2A 独有 flag。

## 兼容边界

- 后端仍决定 variant、choice 可见性和最终关系/结局结算。
- 前端只展示 `event.description`，不自行推断关系结果。
- scripted、hybrid、agent 都消费同一事件上下文；AI 不能改写权威 flag 或 ending。

## 验收

1. 两条 WP-2A 路线在 Day 3 显示各自事件上下文。
2. 既有 Day 3 通用路线和结局流程不回归。
3. 后端测试验证 variant 优先级与路线分离。
4. 至少一条 Day 1→Day 3 浏览器试玩能看到关系因果。
5. 后端全量、前端单测、build、完整 E2E、`git diff --check` 全绿。
