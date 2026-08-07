# Handoff: Next Agent 20260807

## 1. 当前项目状态

- 目标版本：`0.5.0-pre-capture`
- 故事终点：`alice_captured`，不得制作抓捕后剧情，不得扩写 Day 118+
- 当前 readiness：`story=ready`，`materials=pending`
- 后端：FastAPI，当前测试 `232 passed`
- 前端：Vue 3 + Phaser 3，单元测试 `16 passed`，生产 build 已通过
- Git：当前工作区有未提交改动；已建立恢复分支 `cleanup-before-slim-20260807`

## 2. 已完成的结构精简

旧内容已通过 Git 归档，不删除：

- `data/archive/story/legacy/events_chapter_01_v0.4.json`
- `data/archive/story/legacy/main_nodes_v0.4.json`
- `data/archive/story/legacy/month_02_plan.json`
- `data/archive/story/legacy/month_03_plan.json`
- `data/archive/story/legacy/month_04_plan.json`
- `data/archive/tests/`
- `data/archive/code/npc_intents_v0.4.py`
- `archive/cocos-client-2026-08/`
- `data/archive/assets/20260807/`

Active 故事数据：

- `data/story/events_chapter_01.json`：只包含 `ch1pc_n01` 到 `ch1pc_n10`
- `data/story/main_nodes.json`：只保留 `mq00_tutorial`、`mq01_tree_arc`、`precapture_day_gates`
- `backend/app/npc_intents.py`：已替换为精简版 Pre-Capture 意图
- `data/story/month_01_plan.json`：已改为 Pre-Capture 四幕进度

## 3. 当前素材状态

### 角色 v008

- 路径：`materials/inbox/visual/characters/VIS-CHR-001/002/003_*_v008.*`
- 尺寸：768x384，64x96 cell，RGBA
- 动画：idle 2 / walk 6 / interact 4，共 48 帧
- 已修复：idle 两帧重复问题；当前 frame diff 大于 0
- `materials/runtime_asset_requirements.json` 已指向 `*_frames_v008.json`
- `check_runtime_asset_specs.py --require-complete`：`ready | issues=0`

### 地图 v006

- 路径：`materials/inbox/visual/world/VIS-MAP-001_*_v006.*`
- v006 tile/prop atlas 已挂到 `materials/inbox/visual/world/VIS-MAP-001_map_v005.json`
- 新增字段：`tile_metadata_file`、`tile_atlases`、`overlay_layers_v006`、`data_v006`
- 地图 runtime gate 当前通过

### 尚未接入前端 runtime

以下内容还没有完成，不能由“存在文件”误判为已接入游戏：

1. v008 sprite sheet 未复制到 `frontend/public/assets/runtime/characters/`
2. `MANIFEST.csv` 没有 v008/v006 runtime 注册行
3. `frontend/src/field/gameContentConfig.js` 仍使用 `proceduralPixel` 和旧 token
4. `frontend/src/field/createWorldFieldScene.js` 只加载静态 image，未加载 spritesheet，也没有 idle/walk/interact 动画
5. `frontend/src/field/worldMapDrawing.js` 仍使用程序化 tile，v006 atlas 未参与前端渲染
6. “开始按钮”本身没有坏，但它启动的是旧素材流程，不会显示 v008

## 4. 下一个智能体建议执行顺序

A. 先读：

- `docs/delivery/PROJECT_HANDOFF_20260807.md`
- `docs/delivery/ASSET_HANDOFF_SNAPSHOT_20260807.md`
- `docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md`
- `docs/archive/2026-08-repo-slim/README.md`
- `materials/runtime_asset_requirements.json`
- `data/story/events_chapter_01.json`
- `data/story/main_nodes.json`

B. 检查当前未提交 diff：

```bash
git status --short
git diff --stat
git diff --check
```

C. 接入 v008 角色：

1. 将三个 v008 sprite sheet 复制到 `frontend/public/assets/runtime/characters/`
2. 在 `MANIFEST.csv` 增加 runtime 注册行，status 使用 `approved-candidate` 或 `integrated`
3. 修改 `gameContentConfig.js`：
   - `artMode: AGENT_ART_MODES.spriteAsset`
   - `asset` 指向 runtime sprite sheet
   - `textureKey` 使用 v008 spritesheet key
4. 修改 `createWorldFieldScene.js`：
   - `preload()` 使用 `this.load.spritesheet(...)`
   - 为 player/alice/eugeo 创建 idle/walk/interact 动画
   - 角色锚点使用 bottom-center，避免脚底偏移

D. 接入 v006 地图：

1. 决定是否用 v006 atlas 替换程序化 tile
2. 若使用，修改 `frontend/src/field/worldMapDrawing.js` 或新增 tile renderer，从 `VIS-MAP-001_tiles_v006.json` 读取 atlas grid
3. 保留程序化 fallback，防止图片缺失时地图不可玩

E. 完成后验证：

```bash
cd backend
.venv/python.exe -m pytest -q

cd frontend
npm run test:unit
npm run build
```

F. 最后做游戏内截图、移动、碰撞、遮蔽、开始按钮、390x844 移动端验证。

## 5. 恢复方式

如果精简或素材接入误操作，可用：

```bash
git checkout cleanup-before-slim-20260807
```

已归档文件可通过 `git mv` 从 `data/archive/` 和 `archive/` 恢复。

## 6. 未提交内容

当前改动尚未 commit。下一个智能体应先 `git status --short` 确认改动范围，再决定是否提交；不要用 `git reset --hard` 或 `git checkout --` 覆盖工作区。
