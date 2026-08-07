# VIS-ENV-001_delivery_v004

- request_id: VIS-ENV-001
- status: changes_requested → v003 程序化 + v004 AI 生图 双版本; 不得宣称 approved/integrated
- expected_version: v004 (本包补充 v003，不覆盖 v003 审计证据)
- delivery_dir: materials/inbox/visual/environments
- priority: P1
- reviewed_at: 2026-08-07
- intended_use: activity panels and chapter transitions only, never the playable map
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: Mavis（Mavis image_synthesize 2K 16:9, 然后 LANCZOS downscale 到 1920x1080）
- tool_model: AI-image-v004 (Mavis image_synthesize 2K + LANCZOS downscale to 1920x1080 RGB) via MiniMax image generation API, prompt authored by Mavis, no reference image
- created_at: 2026-08-07
- generation: Mavis image_synthesize (MiniMax image generation API), 2K 16:9
- postprocess: Pillow 11.3.0 LANCZOS downscale + RGB conversion
- Python 3.13.9

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| 场景数 | 6 | 6 |
| 尺寸 | 1920x1080 | 1920x1080 (从 2K 2752x1536 LANCZOS downscale) |
| 通道 | RGB | RGB (v003 的 RGBA 转 RGB 验证) |
| 16:9 构图 | 是 | 是 (2K 出图即 16:9) |
| AI 一次性 | 是 (image_synthesize 一次出 6 张) | 是 |

### 6 个场景

| id | 中文 | English | 文件 | size bytes | SHA-256 |
|---|---|---|---|---|---|
| church_library | 村西书库 | village west library / reading desk | visual/environments/VIS-ENV-001_church_library_v004.png | 2612161 | 6cc9a7eeb49b980e13ecb8a5c379f61256846cefc29a3abfc1d249e0c15ef465 |
| gigas_clearing | 古誓树清场 | ancient gigas cedar clearing | visual/environments/VIS-ENV-001_gigas_clearing_v004.png | 2614301 | c2ceab68a0c616b0eb05306c44aeaeac1f72714dff09da64814ea222f47c215b |
| home_hearth | 家中炉火 | village home interior with hearth | visual/environments/VIS-ENV-001_home_hearth_v004.png | 2845709 | 247085ad17b9c4ad17f056b887daa634dfdfe630eb7da92051dc259d2b471d57 |
| north_gate | 北境边门 | north boundary stone gate with fog wall | visual/environments/VIS-ENV-001_north_gate_v004.png | 2565562 | 93621461a04dbfd89fe44bdf057c66acaa0fe3f176ff2146d77bbaffd6581d05 |
| forest_path | 森林路径 | dense forest path with unnatural silence line | visual/environments/VIS-ENV-001_forest_path_v004.png | 2398373 | 31793d5242f1a9cc67cf88fc509c9a845b8a8f0121cef82b681e8a06e360d3df |
| end_mountains_cave | 终北山洞 | end-mountains cave / boundary approach | visual/environments/VIS-ENV-001_end_mountains_cave_v004.png | 2858742 | c21ebe5d54729c7d0baae7a0cb2d7c3ecb6ba42fe50a5ad161f012584750e3e9 |

## 3. 创作 prompt（v004 AI 生图）

每个场景独立 prompt，详见 `VIS-ENV-001_scenes_v004.json` 内的 generation_method 字段。
共同约束:

```text
All 6 scenes: original 2D hand-painted 2D narrative RPG style; no characters; no text/labels/UI/watermarks; no copyrighted game/anime screenshot recreation; no AI-copied material; no third-party art. 16:9 composition, readable middle-lower interaction area, crop-safe margins for desktop and mobile (390x844). Rulid Village village aesthetic, bright clear hand-painted linework, restrained detail.
```

### Negative prompt / 禁止项 (per scene)

```text
no characters; no text, labels, signs with words; no UI; no watermarks; no copyrighted game/anime composition; no AI-copied material; no third-party art; no map collision data; no frame/border/decorative trim (home_hearth v2 强化此条).
```

## 4. seed / settings / 修整

- 2K 出图由 Mavis image_synthesize 生成, prompt 显式禁止违禁元素
- 修整: 1) 2K → 1920x1080 LANCZOS downscale; 2) RGBA → RGB (去除 alpha); 3) 目视 QA
- home_hearth v1: 底部出现木色装饰踢脚线, 影响互动区 → 重做 v2 显式禁止 frame/border/trim → 通过
- 其余 5 张: 一次通过, 无违禁元素, 中央互动区保留

## 5. 来源与权利

- license: owned (Mavis 通过 MiniMax image generation API 程序化生成)
- source_url: none (无外部素材/参考图, 纯文字 prompt → AI 出图)
- attribution_required: false
- intended_use: visual / environment (activity panel / chapter transition)
- rights statement: 本包 AI 出图由 Mavis 编写 prompt 后通过 MiniMax image_synthesize 生成, 不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。

## 6. 文件清单（带 SHA-256）

| 资产 ID | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-ENV-001-church_library-v004 | visual/environments/VIS-ENV-001_church_library_v004.png | 6cc9a7eeb49b980e13ecb8a5c379f61256846cefc29a3abfc1d249e0c15ef465 | 2612161 |
| VIS-ENV-001-gigas_clearing-v004 | visual/environments/VIS-ENV-001_gigas_clearing_v004.png | c2ceab68a0c616b0eb05306c44aeaeac1f72714dff09da64814ea222f47c215b | 2614301 |
| VIS-ENV-001-home_hearth-v004 | visual/environments/VIS-ENV-001_home_hearth_v004.png | 247085ad17b9c4ad17f056b887daa634dfdfe630eb7da92051dc259d2b471d57 | 2845709 |
| VIS-ENV-001-north_gate-v004 | visual/environments/VIS-ENV-001_north_gate_v004.png | 93621461a04dbfd89fe44bdf057c66acaa0fe3f176ff2146d77bbaffd6581d05 | 2565562 |
| VIS-ENV-001-forest_path-v004 | visual/environments/VIS-ENV-001_forest_path_v004.png | 31793d5242f1a9cc67cf88fc509c9a845b8a8f0121cef82b681e8a06e360d3df | 2398373 |
| VIS-ENV-001-end_mountains_cave-v004 | visual/environments/VIS-ENV-001_end_mountains_cave_v004.png | c21ebe5d54729c7d0baae7a0cb2d7c3ecb6ba42fe50a5ad161f012584750e3e9 | 2858742 |

## 7. Manifest 片段

- 路径: `materials/inbox/visual/environments/VIS-ENV-001_v004_manifest_fragment.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空
- replaces_asset_id 指向对应 v003 (如 VIS-ENV-001-church_library-v003)

## 8. 配套 JSON metadata

- 路径: `materials/inbox/visual/environments/VIS-ENV-001_scenes_v004.json`
- 含 schema_version=v004, supersedes=v003, generation_method, scenes[6], qa_pass
- 注明 v003 + v004 双版本共存, 由项目负责人决定哪个进 runtime

## 9. v003 vs v004 关系

- v003 (程序化 Pillow 绘制, 9.6-16 KB): 结构合格, 美术质量低, 适合作为技术 fallback
- v004 (AI 生图 + LANCZOS 缩放, 2.4-2.9 MB): 美术质量高, AI 一次性出 6 张, 适合正式进入候选
- 两版都保留, 不覆盖, 由项目负责人做最终美术选择
- 如果 v004 进 runtime, 需要再做一次 in-game panel QA (390x844 裁切、文本对比度、互动区)

## 10. 短生成 brief

```text
Create six original 1920x1080 character-free environment backgrounds for a clear, bright 2D narrative RPG: church library/reading desk, Gigas Cedar clearing, village home hearth, north gate, forest path with an unnatural silent boundary, and End Mountains cave/boundary approach. These are activity-panel and chapter-transition backgrounds, not playable maps.
```
