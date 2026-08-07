# WP-1D 冻结方案：Day 1 NPC 主动活动去重

- 日期：2026-08-04
- 状态：Frozen / implementation slice
- 对应阶段：`NEXT_PHASE.md` 的 WP-1「首次玩家路径」
- 优先级：P0（首次互动可理解性）

## 体验审计

书库阅览台的核心活动 `church_read_sacred_arts` 既会从 POI 基础配置出现，也会被艾琳的 `alice_invites_reading` NPC 主动事件再次包装。前一轮已经移除了可以绕过玩法的 `read` shortcut，但同一个活动仍可能显示两个入口：一个是“艾琳想让你先看旧记录”，另一个是普通“拼接刻印术和旧记录线索”。首次玩家容易误以为这是两个不同动作。

## 冻结改造

- 在前端合并互动 action 时，若某个 activity id 已有 `source: npc_intent` 的主动入口，则隐藏同 id 的 POI 基础入口。
- 保留 NPC 主动入口，使 stakes、回应选项和关系语境不丢失。
- 如果没有 NPC 主动入口，基础活动照常显示；未来 agent / hybrid 只要返回相同 activity id，也自动复用去重规则。
- 不删除活动配置，不改变后端 API、活动结算、NPC intent、存档或权威状态。

## 验收

1. Day 1 书库互动中 `church_read_sacred_arts` 只出现一个入口。
2. NPC 主动入口仍能进入同一读书玩法并完成 `prologue_reading_done`。
3. 没有 NPC 主动的场景活动仍不被误隐藏。
4. 前端纯函数单测、Day 1 定向 E2E、后端全量、build 和完整 E2E 全绿。
