# 边境回声项目说明

更新时间：2026-05-25

## 产品定位页

一句话定位：

> 单人 AI RPG 纵切 Demo。玩家以露茵村见习记录员的身份，在 20-30 分钟内完成第一天日常、发现北境异常、影响艾琳和尤里的态度，并愿意继续追 Day 2 的静默线。

玩家幻想：

- 我不是旁观日志的人，而是村里正在行动的人。
- NPC 会记住我如何读书、训练、吃饭和表态。
- 安静的村庄背后有一条规则边界正在松动。

核心体验：

- 地图探索：走到书库、古誓树、炉火等地点，自然出现调查和行动入口。
- 轻量玩法：读书关键词拼接、巨树节奏训练、午餐/晚餐关系选择。
- 关系记忆：每个关键行为写入 flags、关系变化、NPC 重要记忆、承诺或紧张点。
- 后端权威：世界状态、章节推进、关系和存档由 FastAPI 后端决定，前端负责表现与输入。

首个 20 分钟目标：

1. 玩家知道自己在露茵村，是一名见习记录员。
2. 玩家自然完成 Day 1：书库调查 -> 艾琳反应 -> 古誓树训练 -> 午餐/晚餐态度 -> 休息结算。
3. 玩家至少做出 3 次主动选择，并能说出艾琳或尤里为什么态度变了。
4. 日结算给出 Day 2 目标预告。

当前原创化基线：

| 内部原型占位 | 公开表达 |
| --- | --- |
| 30小镇 / UW小镇 | 边境回声 |
| 新手村 / 旧原型村名 | 露茵村 |
| Alice / alice | 艾琳 |
| Eugeo / eugeo | 尤里 |
| Kirito / kirito | 凛斗，当前不作为可操作 NPC 公开登场 |
| Underworld | 边境世界 |
| 基家斯西达 | 古誓树 |
| 神圣术 | 刻印术 |
| 禁忌目录 / Taboo Index | 北境律令 |
| 边界异常 | 静默线 |

说明：内部 id 暂时保留 `alice/eugeo/kirito`，避免破坏存档、测试和资源路径；玩家可见文本按上表迁移。

## 当前版本状态

### v1.0 纵切基础

- 地图主界面默认可用，调试台只在 `?dev=1` 显示。
- 玩家可点击移动，也可用 WASD / 方向键移动。
- 艾琳 / 尤里作为地图 NPC 显示，可点击交互。
- NPC 对话支持 LLM，失败或无 key 时自动 fallback。
- 关系档案展示好感、信任、紧张、重要记忆、承诺、紧张点。
- 第一章三日事件已配置：Day 1 日常与线索，Day 2 异常与分歧，Day 3 边界选择。

### v1.1 体验与存档

- 章节选择后显示结果面板。
- 关系变化、“谁记住了什么”、承诺和紧张暗线直接反馈给玩家。
- 后端支持 `GET /api/save/export` 与 `POST /api/save/import`。
- 前端支持导出/导入本地 JSON 存档。
- 休息会进入日结算，并显示 Day 2 目标预告。

### v1.2 Day 1 自然玩法循环

- 书库/古誓树等地点会注入自然触发入口，右侧事件按钮仅作兜底。
- 新增线索/记忆日志，可回看线索、NPC 记忆和关系暗线。
- 巨树训练已接入节奏小游戏。
- 读书已接入关键词拼接玩法。
- 午餐和晚餐已接入关系选择，选择会写入 flags、关系、NPC 记忆。
- NPC Profile 顶部展示“最近态度来源”。

### v1.3 第一月和村庄社会骨架

- 赛尔卡、加雷特、罗温已进入角色注册、persona/backstory 和日程系统。
- 新增第一月 `month_01_plan.json`，覆盖 Day 1-30 的周结构、里程碑、路线奖励和前置条件。
- 后端提供第一月计划公开视图，能根据当前 Day、flags 和 Day 3 路线返回当前目标。
- NPC 主动意图已有基础骨架，可把玩家行为、关系和当前场景转成可回应的 NPC 行动入口。
- 内容校验已有基础骨架，用于检查事件、地图、场景活动、NPC 日程和配置一致性。

## 架构边界

核心原则：

> 规则定事实，AI 定表达，剧情导演定节奏，地图承载行动。

- 后端规则层决定状态变化、合法性、章节推进、关系效果和存档。
- AI 只负责 NPC 的话语、情绪、解释、短期意图和记忆候选。
- 主线事件由 JSON 配置和 `story_director.py` 控制。
- 前端地图是玩家主体验；旧控制台只作为开发调试入口。
- `frontend/` 是当前可玩基线；`cocos-client/` 是并行迁移的 Cocos Creator 正式表现层骨架。两个客户端必须遵守 [CLIENT_CONTRACT.md](CLIENT_CONTRACT.md)。

## 关键代码入口

### 后端

| 文件 | 作用 |
| --- | --- |
| `backend/app/main.py` | FastAPI 路由入口 |
| `backend/app/models.py` | `WorldState`、玩家、NPC、关系、事件模型 |
| `backend/app/session.py` | 会话状态、玩家行动、剧情选择、对话、存档 |
| `backend/app/scene_activities.py` | 场景活动读取和公开视图 |
| `backend/app/story_director.py` | 第一章事件触发和选择效果 |
| `backend/app/dialogue_agent.py` | NPC 对话、LLM/fallback、记忆候选 |
| `backend/app/memory_store.py` | NPC JSONL 记忆与 summary |
| `backend/app/relationship.py` | 关系数值、NPC 档案 |
| `backend/app/world_map.py` | 地图读取、寻路、scene 判定 |
| `backend/app/npc_intents.py` | NPC 主动意图构建与回应 |
| `backend/app/month_plan.py` | 第一月计划读取和公开视图 |
| `backend/app/content_validator.py` | 内容配置校验 |

### 前端

| 文件 | 作用 |
| --- | --- |
| `frontend/src/App.vue` | 应用入口、地图/调试台切换 |
| `frontend/src/components/FieldSlice.vue` | 地图主体验容器、面板调度、热键、存档按钮 |
| `frontend/src/components/ReadingMiniGamePanel.vue` | 读书关键词拼接玩法 |
| `frontend/src/components/MealChoicePanel.vue` | 午餐/晚餐关系选择 |
| `frontend/src/components/TrainingMiniGamePanel.vue` | 巨树训练节奏小游戏 |
| `frontend/src/components/ClueJournalPanel.vue` | 线索和记忆日志 |
| `frontend/src/components/StoryResultPanel.vue` | 结果、关系、记忆、日结算 |
| `frontend/src/components/NpcProfilePanel.vue` | NPC 关系档案与态度来源 |
| `frontend/src/field/createWorldFieldScene.js` | Phaser 地图渲染、玩家移动、NPC/事件/POI 标记 |
| `frontend/src/field/sceneRegistry.js` | map/scene 注册表 |
| `frontend/src/field/gameContentConfig.js` | 显示名、素材路径、目标提示 |
| `frontend/src/contracts/clientContract.js` | Vue 客户端使用的 API 路由、行动 kind 和契约版本 |

### Cocos 并行客户端

| 文件 | 作用 |
| --- | --- |
| `cocos-client/project.json` | Cocos Creator 工程元数据和契约版本 |
| `cocos-client/assets/scripts/api/contracts.ts` | Cocos 客户端 DTO 和 API 路由常量 |
| `cocos-client/assets/scripts/api/GameApi.ts` | Cocos 客户端后端请求封装 |
| `cocos-client/assets/scripts/field/FieldController.ts` | 地图同步、点击移动、本地预演和后端确认 |
| `cocos-client/assets/scripts/field/MapRenderer.ts` | 程序化 tile 渲染、玩家/NPC/POI/事件显示 |
| `cocos-client/assets/scripts/field/LocalPath.ts` | 客户端 BFS 路径预演 |
| `cocos-client/assets/scripts/ui/OverlayUI.ts` | 最小状态 UI 绑定 |

### 数据

| 文件 | 作用 |
| --- | --- |
| `data/story/events_chapter_01.json` | 第一章事件、选择、后果、记忆 |
| `data/story/month_01_plan.json` | 第一月 30 天路线和里程碑 |
| `data/story/main_nodes.json` | 主线节点和闸锁 |
| `data/world/scene_activities.json` | 读书、训练、午餐、晚餐、休息等场景活动 |
| `data/world/world_map.json` | 地图、POI、可走层、场景分区 |
| `frontend/public/assets/game/tilesets/luin_village_v1.json` | Vue/Phaser 与 Cocos 共用 tileset manifest 第一版 |
| `data/world/maps/` | 未来多地图文件目录 |
| `data/world/regions.json` | 区域/场景表 |
| `data/world/schedules.json` | NPC 按时间段移动和当前目标 |
| `characters/meta.json` | 角色注册和展示元数据 |
| `characters/<id>/persona.md` | 角色核心人设 |

运行产物，不作为配置源：

- `runs/`
- `data/memory/`
- `backend/data/memory/`
- `frontend/dist/`

## 第一章结构

目标：玩家在露茵村中过完三天，和两个核心 NPC 建立关系，发现静默线，并在第三天面对是否触碰北境律令的选择。

- Day 1：书库线索、艾琳反应、古誓树训练、午餐/晚餐态度、休息结算。
- Day 2：森林异常、餐桌分歧。
- Day 3：边界选择，形成遵守、越界、隐瞒三个结局。

Day 1 完整脚本见 [DAY1_VERTICAL_SLICE.md](DAY1_VERTICAL_SLICE.md)。

## API 摘要

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/state` | 当前权威世界状态 |
| `GET` | `/api/events` | 运行事件日志 |
| `GET` | `/api/world/map` | 默认地图数据 |
| `GET` | `/api/world/maps/{map_id}` | 按 map_id 读取地图 |
| `GET` | `/api/world/scene_activities` | 场景活动公开目录 |
| `GET` | `/api/story/available_events` | 当前可触发章节事件 |
| `POST` | `/api/story/choose` | 选择事件选项并应用后果 |
| `POST` | `/api/player/action` | 玩家移动、活动、旗标、休息等意图 |
| `GET` | `/api/npc/{npc_id}/profile` | NPC 关系和记忆档案 |
| `POST` | `/api/dialogue` | NPC 对话 |
| `GET` | `/api/save/export` | 导出完整原型存档 |
| `POST` | `/api/save/import` | 导入完整原型存档 |

`/api/player/action` 的 `scene_activity` 支持 `activity_choice`，用于读书关键词、午餐和晚餐选择写入不同效果；`respond_npc_intent` 支持 `intent_id` + `response_id`，用于回应 NPC 主动意图并写入关系和记忆。

## 扩展规则

新增章节事件优先改：

1. `data/story/events_chapter_01.json`
2. `backend/app/story_director.py`
3. `data/world/world_map.json`
4. `frontend/src/field/gameContentConfig.js`

新增场景活动优先改：

1. `data/world/scene_activities.json`
2. `backend/app/session.py`
3. `frontend/src/components/FieldSlice.vue`
4. 必要时新增玩法面板组件

新增 NPC 优先改：

1. `characters/meta.json`
2. `characters/<id>/persona.md`
3. `data/world/schedules.json`
4. `frontend/src/field/gameContentConfig.js`

不要让 AI 直接写入关键世界事实。AI 可以给 `memory_candidate`，由后端校验后决定是否入库。

## 测试与验证

后端：

```bat
cd /d F:\usefultool39\02-UW小镇\backend
F:\usefultool39\02-UW小镇\.conda\uw-runtime\python.exe -m pytest -q
```

前端：

```bat
cd /d F:\usefultool39\02-UW小镇\frontend
npm.cmd run build
npm.cmd run test:e2e
```

视觉 smoke 截图输出到 `runs/`。

## 下一步建议

优先级从高到低：

1. 按 [EXECUTION_BOARD.md](EXECUTION_BOARD.md) 跑质量门：后端 pytest、前端 build、E2E、桌面/手机截图。
2. 完整回归 Day 1-3，确认三条 Day 3 路线能影响第一月目标提示。
3. 补第一月 Day 4-10：事后复盘、北门巡查演练、村务信任。
4. 让赛尔卡、加雷特、罗温各有至少一条主动意图和关系反馈。
5. 做开发者世界观察器，并继续扩展内容校验。

完整未来计划见 [FUTURE_DETAILED_PLAN.md](FUTURE_DETAILED_PLAN.md)。
