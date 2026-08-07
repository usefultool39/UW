# VIS-MAP-001_delivery_v003

- request_id: VIS-MAP-001
- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated
- expected_version: v003 (本包替换 v002，v002 文件保留作为审计证据)
- delivery_dir: materials/inbox/visual/world
- priority: P1, first-phase runtime blocker
- reviewed_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: Mavis（程序化绘制，读取项目自带的 data/world/world_map.json 108x64 瓦片网格）
- tool_model: procedural-map-v003 (Python Pillow 11.3.0 + numpy 2.3.5) reading data/world/world_map.json (108x64 tile grid, 28px/tile)
- created_at: 2026-08-07
- Pillow 11.3.0 (numpy 2.3.5) 渲染所有 PNG 图层 + 掩码 + atlas
- Python 3.13.9

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| 网格 | 108x64 tiles, 28 px/tile | 108x64 tiles, 28 px/tile |
| 每层像素 | 3024x1792 | 3024x1792 |
| 图层数 | 9 (terrain/water, roads, ground props, buildings, vegetation, occluders, foreground, lighting, weather) | 9 |
| 掩码 | collision, walkable, occlusion/depth | 3 (含 occlusion_depth) |
| Atlas | tile/prop reusable | 2 (tiles_atlas 256x256, props_atlas 256x256) |
| JSON metadata | VIS-MAP-001_map_v003.json | 29620 bytes |
| 图例 | 0=grass 1=forest 2=water 3=road 4=obstacle | 与 world_map.json 一致 |
| 可走瓦片 ID | 0, 3 | [0, 3] |
| 阻挡瓦片 ID | 1, 2, 4 | [1, 2, 4] |
| POI 数量 | 9 (pois in world_map.json) | 9 |
| 场景 zone | 12 scene_zones in world_map.json | 11 |

## 3. 创作提示词（合成描述）

```text
Original hand-painted 3/4 top-down tile-aligned map of Rulid Village. 108x64 grid, 28px/tile, 3024x1792 pixels per layer. Deliver grid-aligned PNG layers for terrain/water (grass + water bodies), roads (dirt path on tile id=3), ground props (grass tufts, small rocks, water ripples), buildings (church library, home hearth, teleport plaza stone ring, north gate, gigas cedar tree), vegetation (forest canopies + scattered small trees), occluders (alpha-200 on forest + alpha-160 on major buildings), foreground (road-adjacent grass blades), lighting (warm sun radial + forest shadow), weather (ambient cloud). Also deliver tile/prop atlas, collision/walkable/occlusion_depth masks, and POI/interaction JSON. No characters, no text, no UI, no checkerboard, no copyright composition.
```

### Negative prompt / 禁止项

```text
no characters; no text, labels, signs with words; no UI elements; no watermarks; no baked checkerboard; no copyrighted anime/game screenshot composition; no single flattened illustration as the only deliverable; no AI-copied material; no third-party art.
```

## 4. seed / settings / 修整

- 网格来源: data/world/world_map.json (项目自带 ground truth)
- 随机种子: 7001 (ground_props) / 7002 (vegetation) / 7003 (foreground) / 7004 (weather) / 7005 (props atlas)
- 滤镜: terrain GaussianBlur r=0.7, roads GaussianBlur r=0.5 (柔和手绘风)
- 输出格式: PNG, RGBA, optimize=True
- Layer compositing order (master): terrain → roads → ground_props → buildings → vegetation → occluders → foreground → lighting → weather

## 5. 来源与权利

- license: owned（procedural synthesis by Mavis, derived from project-owned data/world/world_map.json）
- source_url: none（项目内部数据，无外部素材/参考图）
- attribution_required: false
- intended_use: visual / world (phaser runtime map)
- rights statement: 本包由 Mavis 通过 Python + Pillow 程序化绘制，从 data/world/world_map.json 读取 ground truth 瓦片布局；不包含第三方素材、版权图像或 AI 训练集参考。

## 6. 文件清单（带 SHA-256）

| 资产 ID | 文件 | 角色 | SHA-256 | size |
|---|---|---|---|---|
| VIS-MAP-001-terrain-water-v003 | visual/world/VIS-MAP-001_rulid_village_terrain_v003.png | layer | 1122a3129cb9dc395eab58e8f93366882529c420d8a31ad5767502e9971befb2 | 111273 |
| VIS-MAP-001-roads-v003 | visual/world/VIS-MAP-001_rulid_village_roads_v003.png | layer | 9e65bd3826051c73804508227cb3731885f137c232ae5acc7770535326bac31a | 42572 |
| VIS-MAP-001-ground-props-v003 | visual/world/VIS-MAP-001_rulid_village_ground_props_v003.png | layer | 7b96fd0700c5262f742b1990c7469684953ab6fe642e2c2358b905dd0191651f | 52271 |
| VIS-MAP-001-buildings-v003 | visual/world/VIS-MAP-001_rulid_village_buildings_v003.png | layer | 2ce18248498ac9f0a4275d1e11529e6644f4def79e744c200cdf822551cb0e86 | 23334 |
| VIS-MAP-001-vegetation-v003 | visual/world/VIS-MAP-001_rulid_village_vegetation_v003.png | layer | b712bc8f42453213aee178cabddff60fc7a957cca6ce62d094c2ce8b22c00902 | 131756 |
| VIS-MAP-001-occluders-v003 | visual/world/VIS-MAP-001_rulid_village_occluders_v003.png | layer | 9c4d0cf3222f013c191bf6f788e600c3a1107fef46efe18fe4856403fd8a307f | 25953 |
| VIS-MAP-001-foreground-v003 | visual/world/VIS-MAP-001_rulid_village_foreground_v003.png | layer | adf05d15b9948474ccf1bec8152f8a9b815f334701245c3b334945fa33fa4ad2 | 22848 |
| VIS-MAP-001-lighting-v003 | visual/world/VIS-MAP-001_rulid_village_lighting_v003.png | layer | 28fa861e675a27214dce2c9e1783efb8af162e6991ff7c9226b948b85c63d120 | 210577 |
| VIS-MAP-001-weather-v003 | visual/world/VIS-MAP-001_rulid_village_weather_v003.png | layer | a911aa8b1854c7920f4495d608f2a220c9a5bafec2a0e504b7dc3da69817f3bc | 30903 |
| VIS-MAP-001-collision-v003 | visual/world/VIS-MAP-001_rulid_village_collision_v003.png | mask | 160c999e432cfb1db565313481028f528c43f39f24f63c10ec2ee12dfd1d7137 | 26228 |
| VIS-MAP-001-walkable-v003 | visual/world/VIS-MAP-001_rulid_village_walkable_v003.png | mask | 2dc7471bef951a1f5933162f0a5cf01aaa8fe1bc1d2ee1b7bcf5a3cf3438cf96 | 25983 |
| VIS-MAP-001-occlusion_depth-v003 | visual/world/VIS-MAP-001_rulid_village_occlusion_depth_v003.png | mask | 69d8718845bcd771217c409467543b39269ccd3e58823d5c023f5b0408a97ae7 | 26287 |
| VIS-MAP-001-tiles-atlas-v003 | visual/world/tiles_atlas_v003.png | tile atlas | 12beca9f5d2d66ff1d6856c7f6ffe8de0061625adee1709a5b62fdad8177f5d2 | 870 |
| VIS-MAP-001-props-atlas-v003 | visual/world/props_atlas_v003.png | prop atlas | 49c86e3f84e0f80ea5aa2c684f88d7a883d59309c1aad483ae6fbb99efa7fc10 | 1273 |
| VIS-MAP-001-master-composite-v003 | visual/world/VIS-MAP-001_rulid_village_master_v003.png | master composite | 9246a4a9fc8511c2002030e08efc560a70eaef64f07b6160d97913076fb38114 | 434381 |
| VIS-MAP-001-metadata-v003 | visual/world/VIS-MAP-001_map_v003.json | metadata JSON | d4a75880f2f8a0da959c8b7766b6a779070a1ce4ddd227afbf5a8f10b7a047dd | 29620 |

## 7. Manifest 片段

- 路径: `materials/inbox/visual/world/VIS-MAP-001_manifest_fragment_v003.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空
- 一文件一行, 含 SHA-256

## 8. 配套 JSON metadata

- 路径: `materials/inbox/visual/world/VIS-MAP-001_map_v003.json`
- 含 grid/legend/scene_zones/pois/spawn/walkable_tile_ids/blocked_tile_ids/poi_interaction_data/tiles_atlas/props_atlas/layers/masks/master_composite

## 9. 短生成 brief

```text
Create an original, production-ready 2D narrative RPG map package for Rulid Village. Use a clear, bright, hand-painted 3/4 top-down style with strong road readability and restrained detail. Target the existing Phaser grid exactly: 108x64 tiles, 28 pixels per tile, 3024x1792 pixels per runtime layer. Deliver separate registered PNG layers for terrain/water, roads, ground props, buildings, vegetation, occluders, foreground, lighting, and weather, plus a reusable tile/prop atlas, collision/walkable mask, occlusion/depth mask, and interaction metadata for church/library, village square, Gigas Cedar route, home, north gate, and End Mountains route. No characters, no text, no signs with words, no UI, no copyrighted game/anime composition, no baked checkerboard, and no single flattened illustration as the only deliverable.
```
