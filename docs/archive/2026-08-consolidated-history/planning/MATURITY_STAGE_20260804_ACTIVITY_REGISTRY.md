# WP-3A 冻结方案：活动结果映射进入 Registry

- 日期：2026-08-04
- 状态：Frozen / implementation slice
- 对应阶段：`NEXT_PHASE.md` 的 WP-3「活动架构收束」
- 优先级：P0（稳定短玩法扩展边界）

## 审计结论

后端已经具备正确的事务边界：

- `backend/app/activity_engine.py` 负责纯规划、资源校验和 flag 计算，不做 IO；
- `Session.player_action()` 负责提交状态、关系、记忆、日志和 runtime 刷新。

前端仍有三处重复结构：

- `FieldSlice.vue` 用条件分支把 activity id 映射到 reading / meal / patrol panel；
- `runSceneActivity()` 手写 `reading_result`、`meal_result`、`patrol_result` 三个结果字段；
- 三个完成回调重复请求、关闭 panel、刷新剧情和同步 Phaser。

这会使新增固定 NPC 活动或未来 agent 活动时，容易只接上后端却漏掉 UI 结果反馈。

## 冻结改造

只收束前端适配层，不重写 `FieldSlice.vue`：

1. `activityRegistry.js` 为每个特殊活动声明：
   - `panel`
   - `openMessage`
   - `resultField`
   - `completionMessage`
2. Registry 提供纯函数，把小游戏结果映射为结果字段；未知 activity 返回空映射，不猜测字段。
3. `FieldSlice.vue` 使用统一 panel 开关和一个 `onActivityComplete` 流程；三种短玩法仍使用现有组件和后端 API。
4. 保留 interaction kind fallback，使未来数据驱动活动可以不依赖固定 id 接入已有 panel。

## 不做

- 不重写 `FieldSlice.vue`、Phaser scene 或 NPC intent runtime。
- 不改变后端 API、活动结算、存档结构、资源规则和 NPC 权威边界。
- 不把 agent 输出变成状态写入入口。

## 验收

1. 既有 reading / meal / patrol 结果字段与完成提示不回归。
2. Registry 纯函数单测覆盖已知、interaction kind fallback、未知活动。
3. 后端全量 pytest、前端单测、production build、完整 E2E 全绿。
4. Day 1 读书、晚餐和北境巡查试玩仍能看到对应结果反馈。
