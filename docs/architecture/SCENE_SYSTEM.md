# 场景、地图与后续扩展

- **状态**：Current
- **更新时间**：2026-08-03
- **客户端决策**：Vue + Phaser 为主，Cocos 冻结备用（ADR-0004）

历史初稿：2026-04-25

## 当前判断

现在不需要换架构。项目已经适合继续做成“单人玩家 + AI NPC + 稳定世界规则 + 地图探索 + 章节剧情”的纵切片。

更重要的是保持边界清楚：

- 后端保存权威世界状态、合法行动、剧情后果、NPC 位置和记忆。
- Vue/Phaser 与 Cocos 客户端都只负责渲染、输入、动画、面板和镜头体验。
- AI 负责角色表达，不直接决定关键世界事实。
- 新地图、新场景、新 NPC、新事件优先走配置，不优先改核心循环。

## 现有扩展点

| 层 | 文件 | 用途 |
|---|---|---|
| 地图数据 | `data/world/world_map.json` | 当前默认大地图：格子、POI、scene_zones |
| 未来地图 | `data/world/maps/<map_id>.json` | 之后新增洞窟、副本、村外区域 |
| 区域目录 | `data/world/regions.json` | 给 UI 和规则层看的区域/场景列表 |
| 前端注册 | `frontend/src/field/sceneRegistry.js` | map_id、scene_id、背景、模式、未来切换方式 |
| 地图渲染 | `frontend/src/field/createWorldFieldScene.js` | Phaser 探索地图、移动、NPC、事件点 |
| 地图容器 | `frontend/src/components/FieldSlice.vue` | 根据玩家 `map_id` 加载地图并重建 Phaser 场景 |
| Cocos 客户端 | `archive/cocos-client-2026-08/assets/scripts/field/` | 并行客户端读取同一地图/API，先复刻 Day 1 地图纵切片 |
| 后端地图 API | `GET /api/world/maps/{map_id}` | 按 map_id 读取地图，默认仍兼容 `/api/world/map` |
| NPC 日程 | `data/world/schedules.json` | NPC 按时间段进入不同 map/scene/tile |
| 主线事件 | `data/story/events_chapter_01.json` | 事件地点、参与者、选择、后果 |

## 三种场景切换

### 1. 同地图分区

当前已经在用。玩家仍在同一张地图上，只是 `scene_zones` 改变 `scene_id`。

适合：

- 村西书库到巨树清场。
- 田地、教会、家门口这种连续空间。
- 小地图仍显示整张区域。

主要改：

- `data/world/world_map.json` 的 `scene_zones` 和 `pois`
- `frontend/src/field/sceneRegistry.js` 的 `SCENE_DEFINITIONS`
- `data/world/schedules.json` 的 NPC 位置

### 2. 多地图入口

已经留好了入口，但还没做第二张正式地图。玩家状态里的 `player.map_id` 变化后，前端会请求 `/api/world/maps/{map_id}`，并用新的 key 重建 Phaser 场景。

适合：

- 北境洞窟。
- 村外森林。
- 中央都市、教会内部等更大场景。

主要改：

- 新增 `data/world/maps/<map_id>.json`
- `data/world/regions.json` 增加 scene
- `frontend/src/field/sceneRegistry.js` 增加 map/scene 定义
- 后端行动逻辑里把玩家 `map_id`、`scene_id`、`tile_x`、`tile_y` 切过去

### 3. 实例场景

如果后续想做类似弹弹堂的战斗、小副本、剧情演出，不建议塞进当前探索地图渲染器里。更好的方式是新增一个 instance renderer，让状态机决定当前是 `field` 还是 `instance`。

适合：

- 弹弹堂式抛物线战斗。
- 洞窟遭遇战。
- 关键剧情演出。
- 梦境、记忆、训练场。

建议结构：

- `field`：当前 Phaser 探索地图，负责移动和日常互动。
- `instance`：独立战斗/演出组件，读同一个后端状态，但有自己的 UI 和结束条件。
- `result`：实例结束后把奖励、关系、记忆、位置变化写回后端。

这样以后做“网游感”不会把探索地图、战斗、剧情演出混成一团。

## 新增一张地图的最小流程

1. 在 `data/world/maps/` 下新增 `north_cave_stub.json` 这类地图文件。
2. 在 `frontend/src/field/sceneRegistry.js` 里新增 `MAP_DEFINITIONS` 和 `SCENE_DEFINITIONS`。
3. 在 `data/world/regions.json` 里把场景标为 locked 或 unlocked。
4. 在后端玩家行动里实现入口，例如靠近边界 POI 后把 `player.map_id` 改成新地图。
5. 给新地图加 POI、事件和 NPC 日程。
6. 跑：

```bat
cd /d F:\usefultool39\02-UW小镇\backend
python -m pytest -q

cd /d F:\usefultool39\02-UW小镇\frontend
npm.cmd run build
```

## 现在先不要做的事

- 不要为了“像 MMO”马上上多人同步。
- 不要把每个房间都拆成独立前端路由。
- 不要让 LLM 动态生成关键地图结构。
- 不要把战斗逻辑写进 `createWorldFieldScene.js`。

当前最稳的路线是：先把露茵村第一章做深，再加一个小洞窟或边界副本作为第二个场景切换样板。

## 日期与场景闸（2026-08-05）

场景活动不再默认意味着“时间推进”或“跨日”。每个活动必须明确属于以下类别之一：

- `free_activity`：消耗时间/资源，但不满足日结算条件。
- `required_story_event`：完成当日必需剧情。
- `day_end_settlement`：在安全地点整理当日结果并触发日期变化。
- `auto_simulation`：NPC/环境自动运行，不直接绕过剧情闸。

新增地图或活动时，内容校验必须检查：

- 是否错误地把普通活动标为跨日；
- `next_day` 是否连续且符合章节计划；
- 必需事件是否存在可达地点和可执行时间段；
- 日期推进后是否存在明确的 `next_goal`。
