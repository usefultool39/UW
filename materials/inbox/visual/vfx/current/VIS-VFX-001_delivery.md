# 神圣术与静默线 VFX 当前候选

- request_id: VIS-VFX-001
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: Mavis image synthesis + local Pillow assembly
- intended_use: Phaser VFX sheets for UW 0.5.0
- license: project-original
- source_url: none
- runtime: prohibited

## 当前文件(v002)

- `VIS-VFX-001_holy_arts.png`:1024x256 RGBA,4 帧。沿用 v001 候选(方向可审,待 alpha 与播放节奏复核)。
- `VIS-VFX-001_silence_line_v002.png`:1024x256 RGBA,4 帧。**本次重做**。
- `VIS-VFX-001_silence_line_v002.assemble.json`:拼合元数据 + 4 帧 SHA256。
- `VIS-VFX-001_silence_line_frame_0_v002.png` ~ `frame_3_v002.png`:单帧 1024x1024 源,供后续复核与重拼。
- 4 帧叙事:正常 dusk(cyan)→ 紫雾靠近 → 雾带横切 + 鸟飞走 → 静默后空寂紫雾。

## 静默线 v001 → v002 差异

- v001 被否:偏科幻激光与声波可视化,违反"环境断裂"语义。
- v002 重做:用"环境断裂 + 鸟虫远离 + 雾消散"表达"声音消失";无任何发光、能量束、激光。
- 风格基线:方向 C,`void-950` / `violet-500` / `gold-400`。
- 边缘做了 24px 软羽化,贴到场景时不会出现硬切边。

## 结论

- 静默线 v002 已按评审意见重做,语义、风格基线和透明度全部对齐。
- 神圣术 v001 仍待 alpha、白底残留和播放节奏复核,本轮未动。
- 静默线在进入 runtime 之前仍需人眼审 + 实际播放节奏验证。

## 历史

- v001 静默线(激光/声波语义)已移至 `materials/archive/rejected/vfx/VIS-VFX-001_silence_line_v001.png`。
