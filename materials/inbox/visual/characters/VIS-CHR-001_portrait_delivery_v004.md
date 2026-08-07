# VIS-CHR-001_portrait_delivery_v004

- request_id: VIS-CHR-001
- status: v003 程序化 sprite sheet + v004 AI 立绘参考 双版本; 不得宣称 approved/integrated
- expected_version: v004 portrait reference (不替代 v003 sprite sheet)
- delivery_dir: materials/inbox/visual/characters
- priority: P1 (美术重画的视觉参考)
- character: kirito
- reviewed_at: 2026-08-07
- intended_use: 美术重画 sprite 时的视觉参考, 不直接进入 runtime
- runtime_status: prohibited — 仅作美术依据, 需要重画后再走 sprite 验收

## 1. 工具栈与模型

- creator/source: Mavis（Mavis image_synthesize 2K 1:1）
- tool_model: AI-image-v004 (Mavis image_synthesize 2K 1:1, no downscale) via MiniMax image generation API, prompt authored by Mavis, no reference image
- created_at: 2026-08-07
- generation: Mavis image_synthesize (MiniMax image generation API), 2K 1:1
- no postprocess (2K 直接交付作为参考)
- Python 3.13.9

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| 尺寸 | AI 2K 1:1 (参考图) | 2048x2048 |
| 通道 | RGB | RGB (AI 输出) |
| 背景 | 纯白 (角色独立) | 纯白 |
| 姿势 | 全身正面, 手垂体侧, 微侧脸 | 同 |
| 文件 | VIS-CHR-001_kirito_portrait_v004.png | 1620232 bytes, SHA-256=a39a0037bf700403c93d4efe7328d9c9b28f6e80cf1515b0675ddaad44313239 |

## 3. 创作 prompt（v004 AI 生图）

```text
Original 2D hand-painted character concept art, full-body front-facing portrait of 10-12岁黑发深蓝衣男孩, 皮革腰带 + 棕色皮靴, 中性放松姿势, 2D hand-painted RPG concept art. Standing in a relaxed neutral pose, hands at sides, head slightly turned three-quarter, slight smile. Bright clear linework, 2D narrative RPG style. Isolated character on a pure white background, full body visible from head to feet, no scenery, no background, no floor, no shadow, no text, no labels, no UI, no watermarks, no checkerboard, no anime/game screenshot recreation.
```

### Negative prompt / 禁止项

```text
no characters other than the subject; no text, labels, signs with words; no UI; no watermarks; no copyrighted game/anime composition; no AI-copied material; no third-party art; no scenery, no background, no floor, no shadow, no checkerboard, no frame/border/trim.
```

## 4. 与 v003 sprite sheet 关系

- v003 (VIS-CHR-001_kirito_sprite_sheet_v003.png): 768x384 RGBA 程序化 sprite sheet, 4 方向 × 12 帧 = 48 帧, 64x96 frame cell, bottom-center foot anchor. **结构合格, 美术质量低 (几何抽象)。**
- v004 (VIS-CHR-001_kirito_portrait_v004.png): 2048x2048 RGB AI 立绘参考, 全身正面, 纯白背景, **视觉参考, 不进 runtime, 需美术重画 sprite 4 方向 × 12 帧时使用**。
- 替换关系: v004 不替代 v003, 而是给美术重画提供视觉锚点
- 如果美术重画完毕, 走 v005 sprite sheet, 然后再走 v003 → v005 替换流程

## 5. 来源与权利

- license: owned (Mavis 通过 MiniMax image_synthesize 程序化生成)
- source_url: none (无外部素材/参考图, 纯文字 prompt → AI 出图)
- attribution_required: false
- intended_use: visual / character concept art (美术参考)
- rights statement: 本包 AI 出图由 Mavis 编写 prompt 后通过 MiniMax image_synthesize 生成, 不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。

## 6. 文件清单（带 SHA-256）

| 资产 ID | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-CHR-001-portrait-v004 | visual/characters/VIS-CHR-001_kirito_portrait_v004.png | a39a0037bf700403c93d4efe7328d9c9b28f6e80cf1515b0675ddaad44313239 | 1620232 |

## 7. Manifest 片段

- 路径: `materials/inbox/visual/characters/VIS-CHR-001_v004_manifest_fragment.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空
- replaces_asset_id 指向 {req_id}-sprite-sheet-v003
