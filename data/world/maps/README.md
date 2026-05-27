# 未来地图目录

当前正式地图仍是 `data/world/world_map.json`，它的 `id` 是 `novice_open`。

之后新增地图时，把文件放在这里：

```text
data/world/maps/<map_id>.json
```

后端会通过：

```text
GET /api/world/maps/<map_id>
```

读取这些地图。`map_id` 只能使用英文字母、数字、下划线和短横线，避免路径穿越或读到项目外文件。

地图结构保持和 `world_map.json` 一致：`id`、`width`、`height`、`tile_size`、`visual`、`spawn`、`walkable`、`scene_zones`、`pois`、`rows`。

## visual 配置

`visual` 是地图表现和手感的第一版配置入口，避免把镜头、速度和性能参数写死在 Phaser 场景里。

推荐结构：

```json
{
  "style": "fine_tilemap_v1",
  "background": false,
  "tileset_manifest": "/assets/game/tilesets/luin_village_v1.json",
  "scale": {
    "profile": "fine_readable_demo",
    "character_height_tiles": 1.85,
    "marker_density": "compact"
  },
  "camera": {
    "default_zoom": 1.24,
    "background_zoom": 1.18,
    "min_zoom": 0.55,
    "max_zoom": 2.15,
    "wheel_step": 0.065,
    "follow_lerp": 0.18
  },
  "movement": {
    "walk_speed": 720,
    "min_walk_ms": 110,
    "max_walk_ms": 2400,
    "left_drag_pan": true
  },
  "performance": {
    "bake_static_layers": true,
    "guide_interval_ms": 180,
    "water_interval_ms": 180,
    "weather_interval_ms": 80
  }
}
```

调参建议：

- 觉得移动慢，先提高 `movement.walk_speed`。
- 觉得镜头追人慢，先提高 `camera.follow_lerp`，范围建议 `0.12-0.28`。
- 觉得地图太近，降低 `camera.default_zoom`。
- 觉得嵌入式浏览器卡，保持 `performance.bake_static_layers=true`，并提高动态层 interval。
- `tileset_manifest` 是 Vue/Phaser 与 Cocos 共用的美术资产入口；没有正式 tile 图片时保留 `fallback=procedural_tilemap_v1`。
