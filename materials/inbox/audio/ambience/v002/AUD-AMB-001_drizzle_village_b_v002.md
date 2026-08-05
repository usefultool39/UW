# AUD-AMB-001_drizzle_village_b_v002

- request_id: AUD-AMB-001
- creator/source: CodeBuddy Code / hy3（程序化合成）
- created_at: 2026-08-05
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: seed=2002，110 秒（裁切至 104 秒）
- license: owned
- source_url: none
- edits: ffmpeg loudnorm 重新校准至 **-24.6 LUFS**（v001 为 -18 LUFS，过响），TP -12.4 dBTP；6 秒 raised-cosine 交叉淡化保留
- intended_use: audio / ambience
- notes: |
  48 kHz / 24-bit / 立体声；OGG Vorbis q5。
  与 A 版对比：远处水流权重显著增大（0.22 vs 0.12），风铃与鸟鸣更稀，木门事件减少。
  整体更"湿润、安静、人迹稀少"，更接近边界溪边，可为静默线埋伏笔。
  v002 变更：响度从 -18 LUFS 降到 -24.6 LUFS，与 A 版对齐到 ambience 目标区间 -26 至 -22 LUFS；OGG 同步重导；sidecar 与 wav/ogg 一致。

## 配套版本

- A 版（雨声主导、人声活动更明显）：AUD-AMB-001_drizzle_village_a_v002.wav / .ogg（v002）
- 上一版（v001，已变更请求）：AUD-AMB-001_drizzle_village_b_v001.wav / .ogg
