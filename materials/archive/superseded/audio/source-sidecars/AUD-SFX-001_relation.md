# AUD-SFX-001 relation v001

- request_id: AUD-SFX-001
- event: relation
- description: C5+E5+G5 三和音温暖上扬，0.45s，关系变化
- duration_sec: 0.500
- sample_rate_hz: 48000
- bit_depth: 24
- channels: 1
- lufs_target: -23.0 (短 SFX)
- true_peak_target_db: -1.0
- measured_input_i: -23.0
- one_shot: True
- loop_safe: False
- intended_use: SFX / UI 反馈
- created_at: 2026-08-08

## 工具栈

- 工具: Python 3.13 + numpy 2.5 + ffmpeg 8.0.1
- 方法: 加法合成 (MIDI 音 C5/E5/G5/A4/D4/A3/G4) + ADSR 包络 + 2 次谐波 + 失谐副本
- peak limit: -3 dBFS（合成后）
- loudnorm: ffmpeg loudnorm 两遍 pass (I=-23, TP=-1, LRA=11)

## 来源与权利

- license: project-original
- 程序化合成，不引用任何第三方采样或旋律
- 无可识别版权旋律
