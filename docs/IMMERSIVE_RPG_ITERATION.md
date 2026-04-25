# 沉浸式 RPG 迭代说明

更新日期：2026-04-25

本分支目标是把项目从“能走动的地图演示”推进到“可以逐步扩展的单人 RPG 纵切”。当前仍然是第一章原型，但已经把后续做梦幻西游式日常循环、巫师三式场景探索、以及 Underworld 风格 NPC 记忆互动需要的骨架铺开。

## 当前新增内容

- 本轮修复了 `POST /api/player/action` 的历史兼容问题：旧的 `move_world`、`move_scene`、`scene_activity` 仍可用，新的 `move_map`、`enter_scene`、`interact_with_hub`、`compound_sleep`、`daily_tick` 会返回统一的 `state/events/camera/scene_update` 结构。
- 模型配置集中到 `backend/app/llm_config.py`，默认动作模型和对话模型都为 `M2-H`；`.env` 只需要覆盖 `ACTION_MODEL`、`DIALOGUE_MODEL` 或密钥。
- 小地图改为 DOM 固定层，视口框会按缩放夹取到地图范围内，避免缩放后看不到或读不清。
- 地图分区现在显式携带 `regionType`、`entry_points`、`transfers`、`requirements`，前端小地图和世界高亮不再重复推断区域含义。
- 玩家只要进入工作区/休息区/互动区的高亮范围，就能打开对应入口；不必精确踩到某一个小点。
- 场景活动数据化：`data/world/scene_activities.json` 定义砍树、读书、晚餐、睡觉、广场听传闻、北境远望等活动。
- 地图 POI 可承载玩法：`data/world/world_map.json` 的互动点只引用 `activity_id`，具体耗时、可用时段、关系变化和记忆写入都放在活动数据里。
- 时间和天气进入世界状态：后端会随 tick/day 更新 `weather`、`weather_label`、`weather_note`，前端地图会叠加清晨、傍晚、夜色、薄雾和细雨氛围。
- NPC 记忆接入玩法：活动结果可以写入 Alice/Eugeo 的重要记忆，之后 NPC 资料和对话上下文会读到这些记忆。
- 活动结果可视化：完成活动后会显示时间推进、巨树损伤、关系变化和被 NPC 记住的内容。
- 活动重复规则：活动可以配置 `repeat: "daily"` 或 `repeat: "once"`，避免玩家在同一天反复刷关系、记忆和巨树进度。
- 更细的场景分区：同一张大地图内已经细分 `church_library`、`home_hearth`、`village_square`、`gigas_clearing`、`north_gate`。

## 推荐的扩展顺序

1. 先把卢利特村第一章做深：补足读书、砍树、送午餐、夜晚回家、边界异常调查这些循环，让玩家每天都有明确选择。
2. 再做第二张地图：建议从 `north_cave` 或 `forest_boundary` 开始，作为“边界副本/洞窟调查”的最小样板。
3. 再加实例玩法：战斗、剧情演出、梦境、训练场不要塞进当前 field 地图渲染器，另做 `instance` 视图，结束后把奖励、关系和记忆写回后端。
4. 最后再考虑更复杂的 AI 调度：NPC 的关键世界事实仍由后端规则决定，LLM 只负责表达、对话、情绪和细节补全。

## 新增一个场景活动

最小流程：

1. 在 `data/world/scene_activities.json` 添加活动：

```json
{
  "id": "forest_collect_herbs",
  "scene_ids": ["gigas_clearing"],
  "poi_id": "ix_gigas_tree",
  "title": "森林边缘 · 采集草药",
  "label": "采集可入药的草叶",
  "description": "在巨树清场边缘寻找能给晚餐和治疗用的草叶。",
  "result_text": "你把草叶收进布袋，Eugeo 认出其中几种能缓解疲劳。",
  "time_cost": 1,
  "repeat": "daily",
  "time_bands": ["morning", "afternoon"],
  "effects": {
    "flags": { "collected_herbs": 1 },
    "relationship": { "eugeo.trust": 1 },
    "memory": {
      "eugeo": {
        "type": "scene_activity",
        "summary": "玩家在巨树清场边缘帮忙采集草药。",
        "weight": 3
      }
    }
  }
}
```

2. 在 `data/world/world_map.json` 对应 POI 的 `actions` 里添加：

```json
{
  "id": "forest_collect_herbs",
  "label": "采集可入药的草叶",
  "type": "scene_activity",
  "activity_id": "forest_collect_herbs"
}
```

3. 如果是新地点，补 `scene_zones`、`frontend/src/field/sceneRegistry.js` 和 `data/world/schedules.json`。

## 新增一张地图

当前架构已经支持 `player.map_id` 切换后前端重建 Phaser 场景。建议新增地图时保持这个边界：

- 地图文件：`data/world/maps/<map_id>.json`
- 地图/场景注册：`frontend/src/field/sceneRegistry.js`
- 后端入口：优先通过 `POST /api/player/action` 的 `move_map` 迁移地图，或通过故事事件改变 `player.map_id`、`player.scene_id`、`player.tile_x`、`player.tile_y`
- 玩法结果：继续通过 `scene_activities` 或 `story events` 写回 flags、relationships、memories

## 新增地图/场景的最小配置

在地图 JSON 里给每个可发现区域加上这些字段：

```json
{
  "scene_id": "forest_boundary",
  "label": "北境森林边缘",
  "regionType": "interact",
  "x1": 10,
  "y1": 10,
  "x2": 22,
  "y2": 18,
  "entry_points": [{ "id": "trail", "x": 14, "y": 14 }],
  "transfers": [{ "to_scene_id": "village_square", "kind": "same_map", "label": "返回村道" }],
  "requirements": { "required_flags": { "surveyed_north_gate": 1 } }
}
```

`regionType` 推荐先用这几类：`interact`、`work`、`rest`、`locked`、`forbidden`。UI 会自动用它们显示高亮、图例和入口按钮。

## 动作接口约定

`POST /api/player/action` 的成功响应现在固定包含：

```json
{
  "ok": true,
  "state": {},
  "events": [],
  "camera": { "mode": "follow_player", "focus_tile": { "x": 24, "y": 24 } },
  "scene_update": { "changed": false, "map_id": "novice_open", "scene_id": "village_square" }
}
```

失败响应也会返回 `state/events/camera/scene_update/allowed_actions`，前端可以直接显示错误并保持服务器权威状态。

## 验证命令

```powershell
& 'C:\Users\liang\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest backend/tests -q
cd frontend
npm.cmd run build
npm.cmd run test:e2e
```

## 近期 TODO

- 给 `north_gate` 做真正的第二张边界地图，而不是只作为当前地图边缘 POI。
- 增加“夜晚回家后可复盘当天选择”的日记/梦境界面。
- 给 Alice/Eugeo 的 NPC profile 增加“最近承诺/最近紧张点”的 UI 摘要。
- 把活动的 `requirements` 在前端显示得更完整，例如需要某个线索或某个 NPC 信任值。
- 做一个轻量背包/物品系统，让采集、午餐、训练工具不只是 flags。
