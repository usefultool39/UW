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

地图结构保持和 `world_map.json` 一致：`id`、`width`、`height`、`tile_size`、`spawn`、`walkable`、`scene_zones`、`pois`、`rows`。
