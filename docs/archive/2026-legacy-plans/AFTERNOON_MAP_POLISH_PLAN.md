# 下午地图与操作润色计划

更新日期：2026-05-13  
状态：可直接接手执行  
目标：在当前已经能流畅运行的基础上，把初始地图继续打磨成更像可试玩 Demo 的第一张地图。

## 当前基础

已经完成：

- 静态地图层、地形覆盖层、导航调试层烘焙为纹理，减少每帧重画。
- 地图 tile 从 `34px` 调到 `28px`，角色 token 缩小，默认镜头拉远。
- 左键短按点击移动，左键拖拽平移地图，右键/中键拖拽仍可用。
- 行走速度和镜头跟随已提升，操作从“慢动作”变成基本可玩。
- NPC、POI、剧情事件显示会吸附到可走格。
- 北境边门使用 `approach_tile_x/y`，支持“门在锁区内、玩家站门前调查”。
- `data/world/world_map.json.visual` 已成为第一版地图表现配置入口。

关键配置入口：

- `visual.camera.default_zoom`
- `visual.camera.min_zoom`
- `visual.camera.max_zoom`
- `visual.camera.follow_lerp`
- `visual.movement.walk_speed`
- `visual.movement.left_drag_pan`
- `visual.performance.bake_static_layers`
- `visual.performance.guide_interval_ms`
- `visual.performance.water_interval_ms`
- `visual.performance.weather_interval_ms`

## 下午优先目标

先不急着做正式美术资产。下午优先把“能玩起来”的基础继续压实：

1. **点击移动手感**
   - 点击后立即显示目标反馈，已做第一版。
   - 继续优化：远距离点击时先本地移动，不等待后端完整刷新。
   - 加入“连续点击更新目标”，让玩家能像 RTS/ARPG 一样修正路线。
   - 到达目标后轻微落点反馈，不弹过多 toast。

2. **镜头和拖拽**
   - 当前已支持左键拖拽平移。
   - 继续优化：拖拽时隐藏/淡化任务引导线，减少视觉干扰。
   - 松手后如果玩家移动，镜头自然回到跟随；如果只是看地图，则保持自由镜头。
   - 增加一个“回到角色”按钮或热键。

3. **初始地图可读性**
   - 继续减少草地格子感。
   - 道路宽度和边缘需要更自然，减少直尺感。
   - 水岸要进一步明确：哪里是岸，哪里是不能走的水。
   - 森林边缘需要像边界，不只是重复树格。

4. **地图数据结构**
   - 给 `visual` 增加更完整的 schema 文档。
   - 给 POI 支持 `display_label_offset`、`marker_size`、`show_marker`。
   - 给 landmark 支持多 tile 占地和遮挡层配置。
   - 把“可走格”和“视觉道路”继续保持一源驱动。

5. **性能基线**
   - 增加简单前端 perf 采样：最近移动耗时、FPS 粗估、地图绘制耗时。
   - 在开发模式显示一个小的 perf overlay。
   - E2E 继续保存桌面/手机截图。
   - 目标：普通操作保持 50-60 FPS，E2E 质量门稳定低于 30 秒。

## 中期美术接入

美术方向见 [ART_DIRECTION_PLAN.md](ART_DIRECTION_PLAN.md)。

下午如果还有余力，可以先做资产接入框架，而不是直接大批量画图：

- 建立 `frontend/public/assets/game/tiles/` 目录规范。
- 支持 tileset manifest，例如 `tileset_luin_village_v1.json`。
- 渲染器先查 manifest，没有资产时回退到当前程序化 tile。
- 给草地、道路、水岸做 1-2 张占位图片，验证替换路径。

## 推荐执行顺序

1. 调整点击移动和连续目标更新。
2. 加“回到角色”镜头能力。
3. 写 `visual` schema 文档。
4. 增加 perf overlay 或至少写入 `window.__UW_PERF`。
5. 跑 build / E2E / 后端测试。
6. 截图保存到 `runs/`。
7. 更新 `GAME_QUALITY_ROADMAP.md` 执行记录。

## 验收标准

- 玩家第一次进入地图，不需要说明也能知道道路在哪里。
- 点击目标后 100ms 内有视觉反馈。
- 单次移动体感明显快于上一版。
- 左键拖拽地图不误触移动。
- 长距离点击能顺滑移动，玩家可以中途改点。
- NPC 不站在水域、树冠、锁区。
- `npm.cmd run build` 通过。
- `npm.cmd run test:e2e` 通过。
- `.conda\uw-runtime\python.exe -m pytest -q` 通过。

## 可直接发给下一轮的任务

```text
请读取 docs/AFTERNOON_MAP_POLISH_PLAN.md、docs/ART_DIRECTION_PLAN.md 和 docs/GAME_QUALITY_ROADMAP.md。
先执行“下午优先目标”的第 1-3 项：
1. 点击移动手感
2. 镜头和拖拽
3. 初始地图可读性

完成后更新 GAME_QUALITY_ROADMAP.md，运行 build、E2E、后端 pytest，并把截图保存到 runs/。
```

