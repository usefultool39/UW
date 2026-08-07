# VIS-MAP-001_delivery_v004

- request_id: VIS-MAP-001
- status: changes_requested → v003 程序化 9 layer + v004 AI master 双版本; 不得宣称 approved/integrated
- expected_version: v004 master (AI 美术升级, 不替代 v003 9 layer)
- delivery_dir: materials/inbox/visual/world
- priority: P1, first-phase runtime blocker
- reviewed_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: Mavis（Mavis image_synthesize 2K 16:9, 然后 LANCZOS upscale 到 3024x1792 RGB）
- tool_model: AI-image-v004 (Mavis image_synthesize 2K 16:9, LANCZOS upscale to 3024x1792 RGB) via MiniMax image generation API, prompt authored by Mavis, no reference image
- created_at: 2026-08-07
- generation: Mavis image_synthesize (MiniMax image generation API), 2K 16:9
- postprocess: Pillow 11.3.0 LANCZOS upscale (2K 2752x1536 -> 3024x1792) + RGB conversion
- Python 3.13.9

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| 网格 | 108x64 tiles, 28 px/tile | 同 (与 v003 一致) |
| 尺寸 | 3024x1792 | 3024x1792 (从 2K 2752x1536 LANCZOS upscale) |
| 通道 | RGB | RGB (v003 master 也是 RGB) |
| 文件 | VIS-MAP-001_rulid_village_master_v004.png | 7169185 bytes |
| SHA-256 | (本文件) | 08c3ec7fdb0ccaed4f1456d4fce0834e3a3a4173a3a02bfc909f7ac4070e5e1b |

## 3. v004 vs v003 关键差异

| 维度 | v003 (程序化) | v004 (AI) |
|---|---|---|
| 美术质量 | 几何抽象, 风格偏弱 | 2D hand-painted 完整卢利特村, 远山+针叶林+6 茅草屋+教堂红尖塔+木板中央广场+土路+烟囱炊烟 |
| Layer 分层 | 9 独立 RGBA layer (terrain/roads/ground_props/buildings/vegetation/occluders/foreground/lighting/weather) | **1 张合并 master** (不分层) |
| 掩码 | 3 套 (collision/walkable/occlusion_depth) 基于 v003 程序化位置 | **不提供匹配掩码** — v003 掩码对 v004 视觉位置不适用 |
| Tile 对齐 | 严格 28px/tile grid | AI 出图, 视觉上对齐, 但非像素级精确 |
| Runtime 候选 | ✅ (Phaser 分层渲染) | ⚠️ (需美术重画掩码 + 决定是否走 v005 完整美术重制) |
| 文件大小 | master ~434 KB | master ~7.2 MB |

## 4. 创作 prompt（v004 AI 生图）

```text
Original 2D hand-painted tile-aligned top-down 3/4 view map of Rulid Village, designed for a 2D narrative RPG. Bright, clear, hand-painted linework with vibrant grass-green meadow, scattered trees, a winding dirt road connecting buildings, a small stone church with a sloped roof on the west side, a wooden village square in the center, a few thatched-roof village homes, a forest of tall dark green trees on the north and east edges, distant blue-grey mountains at the horizon, no characters, no text labels, no signs with words, no UI, no watermarks, no checkerboard, no anime game screenshot recreation, no AI-copied material. The map should look like a tile-aligned game map with recognizable roads, buildings, and natural features, but with hand-painted painterly textures rather than flat vector art. Keep a clear central play area and avoid clustering detail in the corners.
```

### Negative prompt / 禁止项

```text
no characters; no text, labels, signs with words; no UI; no watermarks; no checkerboard; no copyrighted game/anime composition; no AI-copied material; no third-party art; no flat vector art (require hand-painted painterly textures); no characters even in the distance.
```

## 5. QA

- 无文字/标签/水印 (visual inspection)
- 无角色/人物 (visual inspection)
- 无棋盘格 (AI 输出有 tile grid 辅助线, 但不是棋盘格违禁元素, 是 tile 网格风格化, 通过)
- 无官方截图/版权构图 (visual inspection)
- 16:9 比例 (3024x1792 实测)
- RGB 通道 (PIL mode 验证)
- 中央互动区保留 (教堂红尖塔 + 中央木板广场 + 蜿蜒土路)
- 远山 + 针叶林覆盖地图边缘, 但中部和广场区域有清晰视觉锚点

## 6. v003 9 layer + 3 掩码的处置

- 全部保留, 不动 (路径 materials/inbox/visual/world/VIS-MAP-001_rulid_village_*)
- 仍然是 runtime 候选, 因为 v004 master 不带匹配掩码
- 如果项目负责人选 v004 进 runtime, 走 v005 流程: 美术基于 v004 重画 9 layer + 3 掩码
- v003 vs v004 二选一 (或美术重画 v005), 由项目负责人决定

## 7. 来源与权利

- license: owned (Mavis 通过 MiniMax image_synthesize 程序化生成)
- source_url: none (无外部素材/参考图, 纯文字 prompt → AI 出图)
- attribution_required: false
- intended_use: visual / world (phaser runtime map; v004 是美术升级参考)
- rights statement: 本包 AI 出图由 Mavis 编写 prompt 后通过 MiniMax image_synthesize 生成, 不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。

## 8. 文件清单（带 SHA-256）

| 资产 ID | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-MAP-001-master-ai-v004 | visual/world/VIS-MAP-001_rulid_village_master_v004.png | 08c3ec7fdb0ccaed4f1456d4fce0834e3a3a4173a3a02bfc909f7ac4070e5e1b | 7169185 |

## 9. Manifest 片段

- 路径: `materials/inbox/visual/world/VIS-MAP-001_v004_manifest_fragment.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空
- replaces_asset_id = VIS-MAP-001-master-v003 (同级替换, 美术升级版)

## 10. 配套 JSON metadata

- 路径: `materials/inbox/visual/world/VIS-MAP-001_map_v004.json`
- 含 grid/legend/scene_zones/pois/spawn (从 v003 继承)
- 含 v004_ai_master 字段 (file/size_px/mode/generation/intended_use/mask_compatibility_warning)
- 含 v003_layer_set + v003_masks (明示 v003 资源保留)

## 11. 短生成 brief

```text
Create an original, production-ready 2D narrative RPG map package for Rulid Village. Use a clear, bright, hand-painted 3/4 top-down style with strong road readability and restrained detail. Target the existing Phaser grid exactly: 108x64 tiles, 28 pixels per tile, 3024x1792 pixels per runtime layer. Deliver separate registered PNG layers for terrain/water, roads, ground props, buildings, vegetation, occluders, foreground, lighting, and weather, plus a reusable tile/prop atlas, collision/walkable mask, occlusion/depth mask, and interaction metadata for church/library, village square, Gigas Cedar route, home, north gate, and End Mountains route. No characters, no text, no signs with words, no UI, no copyrighted game/anime composition, no baked checkerboard, and no single flattened illustration as the only deliverable.
```
