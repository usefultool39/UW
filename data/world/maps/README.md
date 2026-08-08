# 地图数据

当前基础地图位于 `data/world/world_map.json`。其内部 ID `novice_open` 为兼容旧存档暂时保留，不代表当前玩家身份或产品方向。新地图不得继续使用该命名方式。

新增地图放在：

```text
data/world/maps/<map_id>.json
```

后端读取接口：

```text
GET /api/world/maps/<map_id>
```

`map_id` 只使用英文字母、数字、下划线和短横线。新序章地图建议采用 `rulid_village`、`end_mountains` 等稳定语义名称。

## 必要字段

地图结构与 `world_map.json` 保持兼容，至少包含：

- `id`、`width`、`height`、`tile_size`
- `spawn`
- `walkable`
- `scene_zones`
- `pois`
- `rows`
- `visual`

## visual 配置

`visual` 集中管理 tileset、比例、镜头、移动和性能参数，避免写死在 Phaser 场景中。

```json
{
  "style": "fine_tilemap",
  "background": false,
  "tileset_manifest": "/assets/runtime/maps/rulid-village/tileset.json",
  "scale": {
    "character_height_tiles": 1.85,
    "marker_density": "compact"
  },
  "camera": {
    "default_zoom": 1.24,
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

背景插图不能替代 collision、walkable、遮挡和 interaction 数据。地图进入 runtime 前必须通过桌面、移动、地标、碰撞、角色比例和遮挡验收。
