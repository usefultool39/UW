# UI 反馈音当前候选

- request_id: AUD-SFX-001
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: procedural synthesis with Python, numpy and ffmpeg
- intended_use: UI one-shot feedback for UW 0.5.0
- license: project-original
- source_url: none
- runtime: prohibited

## 当前文件

confirm、cancel、fail、clue、relation 各有稳定命名的 WAV master 和 OGG derivative。技术数据见 `audio.meta.json`，响度数据见 `measurements.json`。

## 已确认

- 48 kHz、24-bit、mono。
- 每条文件时长约 0.667 秒；其中有效音色仍按描述中的 0.18–0.50 秒语义设计。
- integrated loudness 约 -23 LUFS。
- 五种事件语义已经区分。

## 未通过

- 尚未完成人耳试听。
- 尚未完成游戏内混音和连续触发刺耳度检查。
- 尚未验证移动端自动播放限制和音量设置。
- 尚未决定最终 one-shot 路由与 runtime 稳定文件名。

人工试听和游戏内验证完成前，不得进入 runtime。
