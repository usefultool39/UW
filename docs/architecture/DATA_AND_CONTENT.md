# 数据、内容与持久化边界

- **状态**：Current

## 权威配置源

| 路径 | 内容 |
|---|---|
| `data/world/world_map.json` | 地图、POI、scene zone |
| `data/world/scene_activities.json` | 活动、选择、代价、效果 |
| `data/world/schedules.json` | NPC 日程 |
| `data/story/*.json` | 事件、主节点、月计划 |
| `characters/meta.json` | NPC 注册和运行模式 |
| `characters/<id>/*` | persona、背景、固定对话 |

## 非配置运行产物

`runs/`、`data/memory/`、`frontend/dist/`、`frontend/test-results/`、`playwright-report/` 不得作为剧情事实来源，也不提交个人运行数据。

## ID 规则

- 稳定英文 snake_case；公开名称与内部 ID 解耦。
- 已进入存档的 ID 不直接重命名，使用迁移映射。
- flag 使用命名空间，例如 `activity_done.*`、`activity_day.*`、`story.*`。
- run ID 后端清洗并限制长度。

## 存档

- 当前 `schema_version = 1`。
- 包含世界状态、最近事件和本 run 的 NPC memory summary。
- 新字段提供默认值；破坏性变化必须有迁移函数和旧版 fixture 回归。
- 导入失败不得部分覆盖当前 run。

## 内容改动检查

- [ ] JSON 可解析、ID 唯一，引用存在。
- [ ] 活动在正确地点/时段可达。
- [ ] 被拒绝路径不写状态。
- [ ] 结果解释时间、资源或关系变化。
- [ ] 更新自动测试或试玩用例。
- [ ] 同步 Current Status / Changelog（如适用）。

## 剧情事件驱动日期（2026-08-05）

日期推进是内容配置的一部分，不由前端按钮决定。建议事件或章节节点支持以下字段：

```json
{
  "day_end_gate": true,
  "required_for_day": true,
  "advance_policy": "after_evening_settlement",
  "auto_advance": true,
  "next_day": 2,
  "next_story_node_id": "ch1_day2_anomaly"
}
```

### 规则

- `required_for_day`：当前日期必须完成的事件。
- `day_end_gate`：允许进入日结算的剧情闸。
- `advance_policy`：日期推进时机，例如 `after_evening_settlement`、`after_choice`、`after_scene_exit`。
- `auto_advance`：事件完成后是否由后端自动执行日结算；不能由客户端自行解释。
- `next_day`：可选的目标日期；必须经过后端校验，不能任意跳跃。
- `next_story_node_id`：跨日后进入的剧情节点。

普通 `scene_activity` 只改变时间段、资源、关系和记忆；除非显式配置为剧情闸，不得改变 `day`。

运行产物和存档应记录：触发事件 ID、推进原因、推进前后的日期、日结算摘要和下一目标，便于回放和排查“为什么进入了下一天”。
