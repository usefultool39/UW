# 30小镇项目说明

更新时间：2026-04-24

## 一句话定位

这是一个单人 AI RPG 新手村原型。玩家在一个小型封闭村庄中行动、对话、训练、阅读、休息和选择；NPC 有日程、关系和记忆；世界规则稳定可信；第一章围绕“日常、边界异常、规则冲突”展开。

当前阶段先把新手村做深，不扩成大世界。

## 当前版本状态

### v1.0 新手村试玩切片

已完成：

- 地图主界面默认可用。
- 玩家可在格子地图上移动。
- Alice / Eugeo 作为地图 NPC 显示，可点击交互。
- NPC 对话支持 LLM，失败或无 key 时自动 fallback。
- NPC 有关系档案：好感、信任、紧张、重要记忆、承诺、紧张点。
- 第一章三日事件已配置：Day 1 日常与线索，Day 2 异常与分歧，Day 3 边界选择。
- Day 3 有三个结局：遵守、越界、隐瞒。

### v1.1 体验与存档打磨

已完成：

- 章节选择后显示结果面板。
- 关系变化和“谁记住了什么”直接反馈给玩家。
- 后端支持 `GET /api/save/export` 与 `POST /api/save/import`。
- 前端支持导出/导入本地 JSON 存档。
- pytest 改用项目内临时目录，规避部分 Windows 用户 Temp ACL 锁死问题。
- 后端测试、前端构建、E2E smoke 已验证通过。

## 设计原则

核心原则：

> 规则定事实，AI 定表达，剧情导演定节奏，地图承载行动。

具体边界：

- 后端规则层决定状态变化、合法性、章节推进、关系效果和存档。
- AI 只负责 NPC 的话语、情绪、解释、短期意图和记忆候选。
- 主线事件由 JSON 配置和 `story_director.py` 控制，不交给 AI 随机生成。
- 前端地图是玩家主体验；旧控制台只作为开发调试入口。

## 关键代码入口

### 后端

| 文件 | 作用 |
|------|------|
| `backend/app/main.py` | FastAPI 路由入口 |
| `backend/app/models.py` | `WorldState`、玩家、NPC、关系、事件模型 |
| `backend/app/session.py` | 会话状态、tick、玩家行动、剧情选择、对话、存档 |
| `backend/app/world.py` | 世界规则、初始世界、NPC 日程应用 |
| `backend/app/story_director.py` | 第一章事件触发和选择效果 |
| `backend/app/dialogue_agent.py` | NPC 对话、LLM/fallback、记忆候选 |
| `backend/app/memory_store.py` | NPC JSONL 记忆与 summary |
| `backend/app/relationship.py` | 关系数值、关系变化、NPC 档案 |
| `backend/app/world_map.py` | 地图读取、寻路、scene 判定 |

### 前端

| 文件 | 作用 |
|------|------|
| `frontend/src/App.vue` | 应用入口、地图/调试台切换 |
| `frontend/src/components/FieldSlice.vue` | 地图主体验容器、HUD、热键、面板调度、存档按钮 |
| `frontend/src/field/createWorldFieldScene.js` | Phaser 地图渲染、玩家移动、NPC/事件/POI 标记 |
| `frontend/src/field/gameContentConfig.js` | 显示名、素材路径、场景名、时间段、目标提示 |
| `frontend/src/components/DialoguePanel.vue` | NPC 对话 UI |
| `frontend/src/components/StoryEventPanel.vue` | 章节事件选择 UI |
| `frontend/src/components/StoryResultPanel.vue` | 选择结果、关系变化、记忆反馈 |
| `frontend/src/components/NpcProfilePanel.vue` | NPC 关系档案 |
| `frontend/src/composables/useGameApi.js` | 前端 API 封装 |

### 数据

| 文件 | 作用 |
|------|------|
| `data/story/events_chapter_01.json` | 第一章三日事件、选择、后果、记忆 |
| `data/story/main_nodes.json` | 主线节点和闸锁 |
| `data/world/world_map.json` | 新手村地图、POI、可走层、场景分区 |
| `data/world/regions.json` | 区域/场景表 |
| `data/world/schedules.json` | NPC 按时间段移动和当前目标 |
| `characters/meta.json` | 角色注册和展示元数据 |
| `characters/<id>/persona.md` | 角色核心人设 |
| `characters/<id>/overlay_*.md` | 不同阶段的人设语气叠加 |

运行产物，不作为配置源：

- `runs/`
- `data/memory/`
- `backend/data/memory/`
- `frontend/dist/`
- `.pytest-tmp/`、`pytest_tmp/`、`backend/_test_tmp/`

## API 摘要

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/state` | 当前权威世界状态 |
| `GET` | `/api/events` | 运行事件日志 |
| `GET` | `/api/world/map` | 地图数据 |
| `GET` | `/api/world/regions` | 区域数据 |
| `GET` | `/api/story/available_events` | 当前可触发章节事件 |
| `POST` | `/api/story/choose` | 选择事件选项并应用后果 |
| `GET` | `/api/npc/{npc_id}/profile` | NPC 关系和记忆档案 |
| `POST` | `/api/dialogue` | NPC 对话 |
| `POST` | `/api/player/action` | 玩家移动、旗标、休息等意图 |
| `GET` | `/api/save/export` | 导出完整原型存档 |
| `POST` | `/api/save/import` | 导入完整原型存档 |

## 第一章结构

目标：玩家在新手村中过完三天，和两个核心 NPC 建立关系，发现边界异常，并在第三天面对是否触碰规则的选择。

- Day 1：书库线索、巨树训练。
- Day 2：森林异常、晚餐分歧。
- Day 3：边界选择，形成三个结局。

体验重点：

- 少数 NPC 要比大量空壳 NPC 更重要。
- 每个关键选择都要改变关系或记忆。
- 玩家要知道“为什么某人态度变了”。
- 事件不要只改变数值，要有可读反馈和余韵。

## 扩展规则

### 新增章节事件

优先改：

1. `data/story/events_chapter_01.json`
2. 必要时改 `backend/app/story_director.py`
3. 如果新增地点或 POI，改 `data/world/world_map.json`
4. 如果新增前端显示名，改 `frontend/src/field/gameContentConfig.js`

事件必须包含：

- `id`
- `chapter`
- `title`
- `description`
- `trigger`
- `location`
- `participants`
- `choices`
- 每个 choice 的 `effects`

关键主线不要交给 AI 生成。

### 新增 NPC

优先改：

1. `characters/meta.json`
2. `characters/<id>/persona.md`
3. `characters/<id>/backstory.md`
4. `data/world/schedules.json`
5. `frontend/src/field/gameContentConfig.js`
6. 如果有地图素材，放入 `frontend/public/assets/game/`

新增 NPC 后确认：

- `/api/state` 返回该 NPC。
- 地图能显示该 NPC。
- 对话 fallback 有合理通用回复。
- 关系档案能打开。

### 新增地图区域

优先改：

1. `data/world/world_map.json`
2. `data/world/regions.json`
3. `data/world/schedules.json`
4. `frontend/src/field/gameContentConfig.js`

地图约定：

- `0`、`3` 是可走层。
- POI 的 `tile_x` / `tile_y` 必须落在可走或可接近位置。
- `scene_zones` 用于把格子映射到 `scene_id`。

### 修改 AI 行为

优先改：

- `backend/app/dialogue_agent.py`
- `characters/system_base.md`
- `characters/<id>/persona.md`
- `characters/<id>/overlay_*.md`

不要让 AI 直接写入关键世界事实。AI 可以给 `memory_candidate`，由后端校验后决定是否入库。

## 测试与验证

后端：

```bat
cd /d C:\Users\liang\Downloads\30小镇\30小镇\backend
python -m pytest -q
```

前端：

```bat
cd /d C:\Users\liang\Downloads\30小镇\30小镇\frontend
npm.cmd run build
npm.cmd run test:e2e
```

当前验证结果：

- `116 passed`
- `npm.cmd run build` 通过
- `npm.cmd run test:e2e` 通过

说明：Codex 沙箱里前端构建或 Playwright 可能出现 `spawn EPERM`，因为 esbuild / Playwright 要启动子进程。在正常 Windows 环境或获准提权后可通过。

## 下一步建议

优先级从高到低：

1. 打磨第一章过场演出：镜头、音效、事件进入/退出、结局余韵。
2. 让对话 UI 支持更完整的历史、情绪和关键记忆提示。
3. 增加 2-3 个新手村 POI，但每个都要服务第一章体验。
4. 开始原创化角色名、村名、规则名和世界设定。
5. 再考虑第二章或新区域，不要提前铺开大世界。

当前不要优先做：

- MMO 联机。
- 大量职业/装备/经济系统。
- 大地图扩张。
- 完整战斗系统。
- 直接依赖官方 IP 名称发布。
