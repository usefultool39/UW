# VIS-MAP-001_tiles_delivery_v006

- request_id: VIS-MAP-001
- status: received; 不得宣称 approved/integrated/materials=ready
- expected_version: v006 (tile/prop atlas 补充 v005 map layers)
- delivery_dir: materials/inbox/visual/world
- priority: P1, first-phase runtime blocker
- created_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: 项目自有程序化绘制
- tool_model: procedural-tile-atlas-v006 (Python 3.13.12 + Pillow 12.3.0)
- created_at: 2026-08-07

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| Tile cell | 28×28 px | 28×28 |
| Grid | 108×64 tiles | 108×64 |
| 合成地图 | 3024×1792 px | 3024×1792 |
| Terrain tiles | 草地/泥土/石板变体 | 16 tiles (4×4 grid) |
| Water tiles | 浅水/流动/深水 | 8 tiles (4×2 grid) |
| Road tiles | 鹅卵石/泥路 | 8 tiles (4×2 grid) |
| Vegetation props | 树/灌木/草丛/花 | 16 props (4×4 grid, 56×56) |
| Building props | 房屋/教会/井/市场/棚 | 9 props (3×3 grid, 112×112) |
| Occlusion | 3024×1792 RGBA 半透明 | 140 KB |
| Foreground | 3024×1792 RGBA 半透明 | 135 KB |
| Lighting | 3024×1792 RGBA screen blend | 121 KB |
| Weather | 3024×1792 RGBA 半透明 | 56 KB |
| Collision | 3024×1792 L mask | 14 KB |
| Walkable | 3024×1792 L mask | 14 KB |

## 3. 创作约束

- 风格匹配 v005 map painterly village
- 色彩：自然绿/木色/纸色为主，识别色冷蓝青
- 边角：所有 props 在透明背景，无烘焙阴影
- 道路/地形/水面：纹理在 28px 内可循环
- 教堂：钟楼顶、金色窗光、拱门
- 房屋：红/棕屋顶、烟囱冒烟
- 树木：多层圆形树冠 + 纹理树叶
- 无文字、UI、水印、棋盘格、调试网格

## 4. 通用负向约束

```
no text, no logo, no watermark, no trademark, no copyrighted character likeness,
no recognizable franchise architecture, no UI screenshot, no modern vehicles, no firearms,
no cyberpunk neon, no gothic horror, no apocalyptic ruins, no photobashed game screenshot,
no illegible pathways, no extreme fog, no oversaturated candy colors, no excessive bloom,
no checkerboard, no debug grid, no baked text or UI, no background scenery in props.
```

## 5. 来源与权利

- license: owned
- source_url: none（程序化绘制，无外部素材/参考图/版权角色/IP 复刻）
- attribution_required: false
- intended_use: visual / tile atlas + props for map composition (phaser runtime)
- rights statement: 本包 tile/prop atlas 由项目自有代码（Python + Pillow）程序化绘制，采用原创形状 + 配色方案；不复制任何动漫/游戏原素材、不包含 AI 训练集参考或第三方美术。

## 6. 文件清单（带 SHA-256）

| 资产 | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-MAP-001-terrain_atlas-v006 | visual/world/VIS-MAP-001_terrain_tile_atlas_v006.png | b14c43e1ee02e422d61a57c12f01c10ba751856dec68f6b66e9d3a9e16082c5d | 15847 |
| VIS-MAP-001-water_atlas-v006 | visual/world/VIS-MAP-001_water_tile_atlas_v006.png | f426d80ff0204112e45508b83ba81df08a350453d0e738ce8d70315eda1a7233 | 5066 |
| VIS-MAP-001-road_atlas-v006 | visual/world/VIS-MAP-001_road_tile_atlas_v006.png | 82fcd52a6f7c5c2496b1e45778cee79c1dd46b428c90a9c1c3931e63d865aace | 4206 |
| VIS-MAP-001-vegetation_atlas-v006 | visual/world/VIS-MAP-001_vegetation_props_atlas_v006.png | 748cdf692855eedf802bb9b67e0a425a5d94c181bdace32094f4f1487a71242d | 7227 |
| VIS-MAP-001-buildings_atlas-v006 | visual/world/VIS-MAP-001_buildings_props_atlas_v006.png | 4f1689b128aaf585ce0633086363e0b2af562184e8622fdb2de66193b134b65e | 9417 |
| VIS-MAP-001-occlusion_layer-v006 | visual/world/VIS-MAP-001_occlusion_layer_v006.png | 5f1efb7d4c326a7d22773d8e90967a3669ea66f7c04cbcd9db1a31dacad4151d | 140045 |
| VIS-MAP-001-foreground_layer-v006 | visual/world/VIS-MAP-001_foreground_layer_v006.png | ebb21421ddd0155d0538f9cdac8f94e371a1ddcb4c73843a77eb7586207a5193 | 135029 |
| VIS-MAP-001-lighting_layer-v006 | visual/world/VIS-MAP-001_lighting_layer_v006.png | 62d1fc1df9367eb01673d2e087bc7d025e15d2d9e108a0cead6b6228d927e134 | 120780 |
| VIS-MAP-001-weather_layer-v006 | visual/world/VIS-MAP-001_weather_layer_v006.png | 822353cfc391adbaf557d28f175a697739143460039562260140dc748da0827d | 55580 |
| VIS-MAP-001-collision-v006 | visual/world/VIS-MAP-001_collision_v006.png | 27a1d79df351c1b5af4c7dc6c93efdca3e7dc75aed9b42547411169f6c516889 | 13861 |
| VIS-MAP-001-walkable-v006 | visual/world/VIS-MAP-001_walkable_v006.png | 7ee2b66cf68d44b7da8ec5f40dc3efb0ae473c88826807f30f05a001c5f9a8b1 | 13917 |
| VIS-MAP-001-tiles_json-v006 | visual/world/VIS-MAP-001_tiles_v006.json | d34f7008adfcf8c277452ef083731b398ef8184cc150057ec040a664ad1e5eb2 | 3874 |

## 7. supersedes

- VIS-MAP-001 v003 tiles_atlas (basic colored squares)
- VIS-MAP-001 v005 individual layer PNGs (retained as master map; v006 atlases provide tile/prop slicing)
