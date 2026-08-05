# WP-1C 冻结方案：Day 1 书库单一主入口

- 日期：2026-08-04
- 状态：Frozen / implementation slice
- 对应阶段：`NEXT_PHASE.md` 的 WP-1「首次玩家路径」
- 优先级：P0（首轮上手阻力）

## 体验审计

Day 1 书库阅览台同时暴露两个都像“读书”的入口：

- `read`：直接写入 `prologue_reading_done`，跳过玩法；
- `church_read_sacred_arts`：进入拼接刻印术和旧记录的短玩法，并且活动自身已经写入 `prologue_reading_done`。

这会让首次玩家不知道哪个才是主线，也让“线索 → 选择”的第一步出现可跳过的旁路。现有 Playtest 已把问题记录为 P2 交互入口重复。

## 冻结改造

- 删除阅览台 `read` 快捷 action。
- 保留 `church_read_sacred_arts` 作为唯一读书入口；活动后端效果继续负责写入 `prologue_reading_done`。
- 不改活动结算、资源消耗、剧情事件、NPC runtime 或存档结构。
- 不为兼容旧客户端新增 API；旧客户端请求任意 action 仍不影响后端权威状态，因为该 action 只是地图配置展示项。

## 兼容与回退

- scripted / hybrid / agent NPC 仍通过既有 `scene_activity` action 进入同一活动。
- 后端活动数据是唯一结算来源，固定 NPC 主动邀约不会重新创建另一套读书规则。
- 其他地点和 `prologue_reading_done` 的存档/剧情门控保持不变。

## 验收

1. 书库附近互动只显示一个读书主入口。
2. 该入口仍可进入拼接玩法并写入 `prologue_reading_done`。
3. Day 1 读书→边界记录→Day 2 的关键 E2E 不回归。
4. 后端全量测试、前端单测、production build、完整 E2E、`git diff --check` 全绿。
