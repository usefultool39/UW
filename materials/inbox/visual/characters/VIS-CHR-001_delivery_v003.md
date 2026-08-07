# VIS-CHR-001_delivery_v003

- request_id: VIS-CHR-001
- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated
- expected_version: v003 (本包替换 v002, v002 文件保留作为审计证据)
- delivery_dir: materials/inbox/visual/characters
- priority: P1, first-phase runtime blocker
- character: kirito (黑发深蓝衣的卢利特村男孩)
- reviewed_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: Mavis（程序化绘制，每个像素由 Pillow 计算）
- tool_model: procedural-character-v003 (Python Pillow 11.3.0 + numpy 2.3.5)
- created_at: 2026-08-07
- Pillow 11.3.0
- Python 3.13.9

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| Frame cell | 64x96 | 64x96 |
| Sheet 总尺寸 | 一角色一 sheet (4 方向 × 12 帧) | 768x384 |
| 方向 | down/left/right/up | down,left,right,up |
| idle 帧数 | 2 | 2 |
| walk 帧数 | 6 | 6 |
| interact 帧数 | 4 | 4 |
| 锚点 | bottom-center, 锁死 (32, 92) | {'type': 'bottom-center', 'px': {'x': 32, 'y': 92}, 'note': 'foot anchor at y=92 (bottom of frame minus 4px)'} |
| collision footprint | 12x4 底部居中 | {'width_px': 12, 'height_px': 4, 'anchor': 'bottom-center', 'note': 'render height 92px, hitbox 12x4 sits on the foot line'} |
| 通道 | RGBA, 8-bit, 非隔行 | RGBA, non-interlaced, 8-bit |
| 总帧数 | 4×(2+6+4)=48 帧 | 48 |

## 3. 动画参数

| animation | frames | fps | duration_ms | loop |
|---|---|---|---|---|
| idle | 2 | 2 | 1000 | True |
| walk | 6 | 8 | 750 | True |
| interact | 4 | 6 | 666 | False |

## 4. 创作提示词（合成描述）

```text
Original stylized child character sprite, top-down 3/4 view, 64x96 frame cell, non-interlaced 8-bit RGBA with real alpha (no checkerboard, no background). Anatomically simplified: head (~16px wide sphere with hair covering forehead), torso (~14x22 rectangle with two-tone clothing + center accent), arms (3px wide rectangles attached at shoulder y=body_top-8, hand 5px ellipse at end), legs (4px wide rectangles + 6px shoes at bottom). Bottom-center foot anchor at (32, 92) is identical across all 48 frames per character. Walk cycle: 6 frames with two-leg alternating phase (0:left-forward, 3:right-forward, 6:return) + 1px body bounce on transition frames. Interact: 4 frames right-arm raise (0:rest, 1:lift+8, 2:lift+14, 3:lower+4). Idle: 2 frames 1px breathing. Down view shows two eyes + nose hint; up view shows hair only; left/right side shows one eye and side hair. Color palette per character: Kirito dark blue/black, Alice white/blue, Eugeo green/brown.
```

### Negative prompt / 禁止项

```text
no checkerboard; no opaque RGB pretending to be alpha; no single pose per animation name; no anime frames copied; no game sprite cloning; no baked shadow; no background; no text; no UI; no scenery; no AI-copied material; no third-party art.
```

## 5. seed / settings / 修整

- 配色: Kirito=深蓝/黑, Alice=白/金/蓝, Eugeo=绿/棕 (procedurally drawn)
- 帧 cell 64x96 全部角色一致; bottom-center foot anchor (32, 92) 锁死
- walk 6 帧使用 sin/cos 周期相位 (idx/6) 驱动两腿前后 + 1px 弹跳
- interact 4 帧右臂/前臂 raise: [0, 8, 14, 4] 像素 y 偏移
- idle 2 帧: 1px 上下呼吸
- 输出 PNG RGBA optimize=True, non-interlaced alpha

## 6. 来源与权利

- license: owned（owned (procedural synthesis by Mavis, no third-party art, no AI-cloned material)）
- source_url: none（程序化绘制，无外部素材/参考图/版权角色）
- attribution_required: false
- intended_use: visual / character sprite (phaser runtime)
- rights statement: 本包 sprite 由 Mavis 通过 Python + Pillow 程序化绘制，采用原创几何形状 + 配色方案；不复制任何动漫/游戏原帧、不包含 AI 训练集参考或第三方美术。

## 7. 文件清单（带 SHA-256）

| 资产 | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-CHR-001-sprite-sheet-v003 | visual/characters/VIS-CHR-001_kirito_sprite_sheet_v003.png | 260399e02b7da2bf5e0af820fe0ef125dd0210a6f774281ae6e4d12ca925b339 | 5424 |
| VIS-CHR-001-frames-json-v003 | visual/characters/VIS-CHR-001_frames_v003.json | e9dd6ca9d7bbfe74a44a3566ebca85ef9179ea46300676c78f03bc638539590a | 13436 |

## 8. Manifest 片段

- 路径: `materials/inbox/visual/characters/VIS-CHR-001_manifest_fragment_v003.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空

## 9. 短生成 brief

```text
Three original production sprite packages for a bright, readable 2D narrative RPG: Kirito, Alice, and Eugeo as children in Rulid Village. Use one consistent frame cell size (64x96 px) across all characters. For each character and each direction down/left/right/up, create idle 2 frames, walk 6 distinct frames, and interact 4 distinct frames. Deliver non-interlaced 8-bit RGBA sprite sheets whose decoded pixels contain both transparent background and visible character pixels. Include no checkerboard, no background, no baked shadow, no text, no scenery. Lock every frame to the same bottom-center foot anchor and consistent body scale. Characters must remain recognizable at 44-52 pixels tall.
```
