# 三位核心角色当前候选

- request_id: VIS-CHR-001, VIS-CHR-002, VIS-CHR-003
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: ImageGen + local Pillow postprocess
- intended_use: down-direction sprite baseline for UW 0.5.0
- license: project-original
- source_url: none
- runtime: prohibited

## 当前文件

- `VIS-CHR-001_sprite_sheet_down.png`：桐人，768x96 RGBA，12 帧。
- `VIS-CHR-002_sprite_sheet_down.png`：爱丽丝，768x96 RGBA，12 帧。
- `VIS-CHR-003_sprite_sheet_down.png`：尤吉欧，768x96 RGBA，12 帧。
- `VIS-CHR-001_002_003_frame_metadata.json`：逐帧检查结果。
- 每个角色各有稳定命名的 desktop 和 mobile 预览。

每个 cell 为 64x96，帧序为 idle 2、walk 6、interact 4，逻辑锚点为 `(32,94)`。

## 未通过

- 桐人、爱丽丝、尤吉欧各有 11/12 帧在 `(32,94)` 出现非零 alpha。
- 爱丽丝 `walk_2` 非透明像素量明显偏低。
- 独立生成的帧存在比例、姿态、服装和道具连续性风险。
- 透明边缘和潜在水印残留仍需逐帧复核。
- 当前只有 down 方向。

必须先让 36 帧锚点 alpha 全部为 0，并通过动作连续性和透明边缘检查，再扩展其他方向或进入 runtime。
