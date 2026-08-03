# 客户端契约：Vue/Phaser 与 Cocos 共用接口

- **状态**：Current
- **主客户端**：Vue + Phaser；Cocos 冻结备用（ADR-0004）
- **更新日期**：2026-08-03

历史契约日期：2026-05-15  
契约版本：`client-contract-2026-05-15-v2`

## 目标

项目保留两个客户端目录，但不再并行开发同等功能：

- `frontend/`：Vue + Phaser，可玩基线和开发验证客户端。
- `cocos-client/`：Cocos Creator 备用骨架；只有新 ADR 明确恢复后才继续扩展。

两个客户端必须共享同一套后端事实：FastAPI 后端决定世界状态、合法行动、剧情后果、关系、记忆和存档；客户端只负责输入、表现、动画、轻量本地预演和失败回滚。

## 稳定 API

这些接口是客户端契约的一部分。允许新增可选字段，不允许删除字段或改名。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/health` | 后端健康检查 |
| `GET` | `/api/state` | 当前权威世界状态 |
| `GET` | `/api/events?limit=200` | 运行事件日志 |
| `GET` | `/api/world/map` | 默认地图 `novice_open` |
| `GET` | `/api/world/maps/{map_id}` | 按地图 id 读取地图 |
| `GET` | `/api/world/regions` | 场景/区域目录 |
| `GET` | `/api/world/scene_activities` | 场景活动目录 |
| `GET` | `/api/story/available_events` | 当前可触发剧情事件 |
| `POST` | `/api/player/action` | 玩家行动入口 |
| `POST` | `/api/story/choose` | 剧情选择 |
| `POST` | `/api/dialogue` | NPC 对话 |
| `GET` | `/api/npc/{npc_id}/profile` | NPC 关系/记忆档案 |
| `GET` | `/api/save/export` | 导出存档 |
| `POST` | `/api/save/import` | 导入存档 |

## 共享 DTO

客户端需要按这些逻辑对象组织代码，不必逐字段复制后端 Pydantic 类型。

- `WorldState`：`day`、`tick`、`time_band`、`weather`、`story_node_id`、`flags`、`relationships`、`player`、`agents`、`npc_intents`、`active_event_ids`、`completed_event_ids`。
- `PlayerState`：`map_id`、`scene_id`、`tile_x`、`tile_y`、`hp/mp/stamina`。
- `AgentState`：`id`、`map_id`、`scene_id`、`tile_x`、`tile_y`、`mood`、`current_goal`。
- `MapData`：`id`、`width`、`height`、`tile_size`、`visual`、`spawn`、`walkable`、`scene_zones`、`pois`、`rows`。
- `SceneActivity`：`id`、`scene_ids`、`time_bands`、`interaction_kind`、`choices`、`effects`。
- `StoryEvent`：`id`、`kind`、`title`、`description`、`location`、`participants`、`choices`。
- `NpcIntent`：`id`、`npc_id`、`kind`、`title`、`description`、`scene_id`、`tile_x/y`、`priority`、`reason`、`action`、`stakes`、`response_options`。
- `PlayerActionResult`：`ok`、`state`、`events`、`camera`、`scene_update`，可选 `path`、`activity_result`、`intent_result`、`relationship_changes`、`memory_written`、`error`。
- `NpcProfile`：`relationship`、`important_memories`、`promises`、`tensions`、`mind`、`attitude_source`。
- `SaveData`：完整存档 payload，客户端只做导入导出，不自行改写内部结构。

## 玩家行动

`POST /api/player/action` 的稳定 `kind`：

- `move_map` / `move_world`：移动到 tile。
- `move_scene` / `enter_scene`：进入同地图 scene。
- `interact_with_hub`：靠近 POI 后触发交互；带 `activity_id` 时后端会归一为 `scene_activity`。
- `scene_activity`：执行读书、训练、餐食、休息等活动，可带 `activity_choice`。
- `respond_npc_intent`：回应当前 `state.npc_intents` 中的 NPC 主动意图；带 `intent_id`、`response_id`，返回 `intent_result`、关系变化和记忆写入。
- `set_flag`：开发/剧情闸调试。
- `daily_tick`：推进日常 tick。
- `compound_sleep`、`rest_until_next_day`：休息和跨天。

移动体验约定：客户端可以先本地寻路和播放动画，但最终必须以 `PlayerActionResult.state.player` 为准；失败时使用 `error`、`scene_update` 和当前权威状态回滚。

## 地图表现配置

`MapData.visual` 是两个客户端共用的表现入口：

- `style`：渲染风格 id。
- `background`：是否使用大背景图。
- `tileset_manifest`：可选 tileset manifest 路径。
- `scale.character_height_tiles`：角色高度比例。
- `camera.default_zoom/min_zoom/max_zoom/wheel_step/follow_lerp`：镜头参数。
- `movement.walk_speed/min_walk_ms/max_walk_ms/left_drag_pan`：移动手感。
- `performance.bake_static_layers/guide_interval_ms/water_interval_ms/weather_interval_ms`：性能参数。

地图 `rows` 仍是可走、碰撞和地形逻辑的源；正式美术只替换表现，不改变规则源。
