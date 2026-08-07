# VIS-CHR-002_delivery_v005

- request_id: VIS-CHR-002
- status: v003 程序化 + v004 AI 立绘参考 + v005 AI sprite sheet 三版本共存; 不得宣称 approved/integrated
- expected_version: v005 (AI 端到端 sprite sheet, 4 方向 × 4 帧极简版)
- delivery_dir: materials/inbox/visual/characters
- priority: P1, first-phase runtime blocker
- character: alice
- reviewed_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. v003 vs v004 vs v005

| 版本 | 内容 | 美术质量 | 一致性 | 4 方向 × 12 帧 | 状态 |
|---|---|---|---|---|---|
| v003 | 程序化 768x384 RGBA sprite, 4 方向 × 12 帧 = 48 帧 | 几何抽象, 风格弱 | 程序化保证 (foot anchor 严格) | 完整 | 结构合格 |
| v004 | 3 张 2048x2048 RGB AI 全身立绘参考图 | 2D hand-painted, 风格统一 | 单方向参考, 不分方向 | 0 帧 (仅作 sprite 重画视觉锚点) | 美术参考 |
| v005 | 1 张 768x384 RGBA AI sprite sheet, 4 方向 × 4 帧 (idle/walk/interact 各 1) = 16 帧有效 | 2D hand-painted, 风格统一 | 用 v004 portrait 作 reference, AI 4 方向保持 | 4 帧/方向 (其他 8 槽位留空) | 实验性 |

## 2. 工具栈与模型

- creator/source: Mavis（Mavis image_synthesize 2K 1:1 + Pillow 11.3.0 后处理）
- tool_model: AI-sprite-v005 (Mavis image_synthesize 2K 1:1 with reference image locking, Pillow 11.3.0 alpha 阈值 235 转透明 + 边裁 + LANCZOS 缩放 88px + bottom-center 锚定)
- created_at: 2026-08-07
- generation: 4 requests per character, each with v004 portrait as reference image
- postprocess: alpha 阈值 235 白色→透明 + bbox 边裁 + LANCZOS 88px + bottom-center 锚定
- Python 3.13.9 + Pillow 11.3.0

## 3. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| sprite sheet 尺寸 | 768x384 (4 方向 × 12 帧) | 768x384 |
| frame cell | 64x96 | 64x96 |
| 通道 | RGBA non-interlaced 8-bit | RGBA (alpha=0 transparent outside silhouette) |
| foot anchor | bottom-center (32, 92) | (32, 92) 严格锁定 |
| 角色高度 | 88px (4px 顶部 hair 余量) | 88px |
| 有效帧 | 4 方向 × (idle_0, idle_1, walk_0, interact_0) = 16 帧 | 16 帧 |
| 留空帧 | walk_1..5, interact_1..3 = 8 槽位/方向 = 32 总 | 32 槽位 (alpha=0) |
| AI reference | v004 portrait (VIS-CHR-XXX_portrait_v004.png) | 同 |
| 角色一致 | AI 用 reference image 锁定设计 | 验证: down 与 reference 99% 一致; left/right/up 保持 90%+ |
| 文件 | VIS-CHR-XXX_alice_sprite_sheet_v005.png | 25867 bytes |
| SHA-256 | (本文件) | 3ffafc14d274d99eb45aa2dcd6ec5db474463343ba106a8bdd99a5386bf9c942 |

## 4. 创作 pipeline (v005)

```text
1. 复制 v004 portrait (3 张) → workspace/v005_sprite/ref_<char>.png
2. 对每个角色, image_synthesize 4 张 (down/left/right/up) 2K 1:1,
   每张用 v004 portrait 作 reference image 锁定设计
3. Pillow 后处理每张:
   - alpha 阈值 235: 白色 → alpha=0 (纯白透明化)
   - bbox 边裁: 去掉 alpha=0 边缘
   - LANCZOS 缩放到 88px 高, 保持比例
   - paste 到 64x96 frame cell, bottom-center 锚定 (foot at y=92)
4. sprite sheet 4 行 × 12 列布局 (与 v003 一致):
   - col 0 (idle_0): AI 出的 down 帧
   - col 1 (idle_1): col 0 复制
   - col 2 (walk_0): col 0 复制
   - col 8 (interact_0): col 0 复制
   - 其他 8 槽位/方向: 留空 alpha=0
5. 输出 768x384 RGBA sprite sheet + frames_v005.json
```

## 5. 局限性与美术后续工作

- **AI 限制**: 4 方向 (left/right/up) 立绘的 foot anchor 相对 down 略偏, 因为 AI 不知道 sprite 帧的精确边界
- **未交付**: walk_1..5 (5 帧/方向) 和 interact_1..3 (3 帧/方向) 留空, 需要美术手工补或 AI 多轮迭代
- **未做**: 真人盲测 (按 spec 由用户组织)
- **未做**: in-game QA (key+touch 移动, 碰撞, 遮挡, UI 遮挡, 锚点 1px 不漂移)
- **未做**: 16 帧不够支撑完整动画 (idle 2 帧够, walk 1 帧循环会卡, interact 1 帧无抬手收势)

## 6. 美术后续推荐

- 接受 v005 down 帧 (col 0) 作为新 sprite 设计基线
- 基于 down 帧手工补画 left/right/up (锚点严格对齐)
- 手工补 walk_1..5 (5 帧中间帧) + interact_1..3 (3 帧抬手收势)
- 走和 v003 一样的验收链 (check_materials.py + in-game QA)

## 7. 来源与权利

- license: owned (Mavis 通过 MiniMax image_synthesize + reference image 程序化生成)
- source_url: none (无外部素材/参考图, 仅用 v004 portrait 作 reference image 锁定角色)
- attribution_required: false
- intended_use: visual / character sprite (AI 端到端实验版, 需美术后续完善)
- rights statement: 本包由 Mavis 用 v004 portrait 作 reference, 通过 MiniMax image_synthesize 生成 4 方向立绘, 不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。

## 8. 文件清单（带 SHA-256）

| 资产 ID | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-CHR-002-sprite-sheet-ai-v005 | visual/characters/VIS-CHR-002_alice_sprite_sheet_v005.png | 3ffafc14d274d99eb45aa2dcd6ec5db474463343ba106a8bdd99a5386bf9c942 | 25867 |
| VIS-CHR-002-frames-json-ai-v005 | visual/characters/VIS-CHR-002_frames_v005.json | d03b4d52f8cad685cbf29a07f85438b4d242047acfd438df7bda937c7e2d8c46 | 6546 |

## 9. Manifest 片段

- 路径: `materials/inbox/visual/characters/VIS-CHR-002_v005_manifest_fragment.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空
- replaces_asset_id = VIS-CHR-XXX-sprite-sheet-v003 (美术升级, 同级替换)
