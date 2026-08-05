# AUD-AMB-001_drizzle_village_a_v002

- request_id: AUD-AMB-001
- creator/source: CodeBuddy Code / hy3（程序化合成：粉噪细雨 + 屋顶低频共鸣 + 远处水流 + 稀疏风铃 + 鸟鸣 + 偶尔木门）
- created_at: 2026-08-05
- tool_model: none
- prompt: none
- negative_prompt: none
- seed/settings: seed=2001，120 秒（裁切至 114 秒）
- license: owned
- source_url: none
- edits: ffmpeg loudnorm 重新校准至 **-24.6 LUFS**（v001 为 -18 LUFS，过响），TP -13.1 dBTP；6 秒 raised-cosine 交叉淡化保留
- intended_use: audio / ambience
- notes: |
  48 kHz / 24-bit / 立体声；OGG Vorbis q5。
  内容层：木檐+草地细雨（高+低双滤波）+ 远处水流（LFO 调制）+ 五音风铃 + 鸟鸣 chirp + 木门吱呀。
  约束：每 10 秒无强事件；左右声场稳定；循环点听不出；为后续静默线留对比。
  v002 变更：响度从 -18 LUFS 降到 -24.6 LUFS，进入 ambience 目标区间 -26 至 -22 LUFS；OGG 同步重导；sidecar 与 wav/ogg 一致。

## 配套版本

- B 版（水流更重、人声活动更稀）：AUD-AMB-001_drizzle_village_b_v002.wav / .ogg（v002）
- 上一版（v001，已变更请求）：AUD-AMB-001_drizzle_village_a_v001.wav / .ogg
