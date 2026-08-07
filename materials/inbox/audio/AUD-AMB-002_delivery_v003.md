# AUD-AMB-002_delivery_v003

- request_id: AUD-AMB-002
- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated
- expected_version: v003 (本包替换 v002，v002 文件保留作为审计证据)
- delivery_dir: materials/inbox/audio/{bgm,ambience}
- priority: P1, first-phase runtime blocker
- reviewed_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: Mavis（程序化合成：numpy/scipy）
- tool_model: procedural-audio-v003 (Python numpy/scipy + ffmpeg-8.1 libvorbis) + ffmpeg loudnorm (EBU R128, two-pass) + ffmpeg ebur128 measurement
- created_at: 2026-08-07
- ffmpeg: 8.1.1 (libvorbis + loudnorm + ebur128)
- Python: 3.13.9 (numpy 2.3.5, scipy 1.16.3)

## 2. 规格目标与实测

- 目标规格: AMB-002: 60-90s normal/silent equal length, -26..-22 LUFS, TP<= -2 dBTP
- 实测（见 measurements_v003.json）:

| name | dur (s) | I LUFS | TP dBTP | OGG kbps | loop_safe | fade (s) |
|---|---|---|---|---|---|---|
| AUD-AMB-002_forest_silence_normal_v003 | 76.0 | -23.0 | -5.8 | 193.6 | True | 4.0 |
| AUD-AMB-002_forest_silence_silent_v003 | 76.0 | -22.9 | -10.9 | 193.6 | True | 4.0 |

- 等长校验: normal=76.0s, silent=76.0s, 差=0.000s（< 0.1s, 满足 2-4s 交叉淡化前提）

## 3. 创作提示词（合成描述）

```text
Programmatic synthesis: 80s matched loop pair. /normal: pink-noise wind lowpass 600Hz with 0.08Hz LFO + sparse 1800-4300Hz bird chirps every 4-9s + 2-5kHz leaf bandpass with 0.13Hz LFO + 4kHz+ highpass fine-branch bursts every 6-12s + sub-80Hz air pressure. /silent: same 80s but with 300-1800Hz bandstop creating an unnatural frequency gap, sparser 14-22s bird timing, finer branch events at 8-16s, sub-80Hz air pressure retained, and a 0.04Hz sub-audible drift to model instability. Equal length (76s) verified; both files start loop at sample 0 and share the same 4s raised-cosine xfade, supporting a clean 2-4s external crossfade.
```

### Negative prompt / 禁止项

```text
no vocals; no recognizable copyrighted melody or motif; no clipping; no long silence; no fake -70 LUFS report; no repeated foreground event under 20s; no DC offset; no obvious 20s loop artifact; no third-party samples; no AI-voice, no AI-trained song references.
```

## 4. seed / settings / 循环 / 修整

| name | seed | 采样率 | 位深 | 通道 | loop start sample | loop end sample | fade sec |
|---|---|---|---|---|---|---|---|
| AUD-AMB-002_forest_silence_normal_v003 | 5001 | 48000 | 24 | 2 | 0 | 3648000 | 4.0 |
| AUD-AMB-002_forest_silence_silent_v003 | 5002 | 48000 | 24 | 2 | 0 | 3648000 | 4.0 |

Edits: ffmpeg loudnorm 两阶段归一至 -18 LUFS (BGM) / -23 LUFS (AMB)，TP target -2.0/-3.0 dBTP 实测在 spec 范围；OGG 用 -b:a 192k -minrate 160k -maxrate 224k 约束。

## 5. 来源与权利

- license: owned（owned (project-internal procedural synthesis by Mavis, no third-party samples, no AI-copied material)）
- source_url: none（程序化合成，无外部素材/采样/参考旋律）
- attribution_required: false
- intended_use: audio / ambience
- rights statement: 本包文件由项目成员 Mavis 通过 Python + ffmpeg 程序化生成，不包含人声、可识别版权旋律、第三方采样或 AI 训练集参考。

## 6. 文件清单（带 SHA-256）

| 文件 | 角色 | SHA-256 | size |
|---|---|---|---|
| audio/ambience/AUD-AMB-002_forest_silence_normal_v003.wav | master WAV | 8de77828afcce147423536fbcb89cb5d81d58da799e2720942c7a4fac61a77aa | 21888102 |
| audio/ambience/AUD-AMB-002_forest_silence_normal_v003.ogg | runtime OGG | 47b494cbc4b1ca83a722ca293ec5789f789a5afb122da983083993851f1939c9 | 1839285 |
| audio/ambience/AUD-AMB-002_forest_silence_silent_v003.wav | master WAV | 998b65ca1e624462a6d49dbaa6e32b336e4a102d91dc41bc35140a19c23d3d61 | 21888102 |
| audio/ambience/AUD-AMB-002_forest_silence_silent_v003.ogg | runtime OGG | 104eda166c6e0296201412bf26dbddb8720f51cebfc6d66210aca915501cb92a | 1839165 |

## 7. Manifest 片段

- 路径: `materials/inbox/audio/AUD-AMB-002_manifest_fragment_v003.csv`
- 列顺序严格按 18 列 schema (asset_id, request_id, status, source_file, runtime_file, sha256, creator, tool_model, created_at, license, source_url, attribution_required, attribution_text, approved_by, approved_at, integrated_at, replaces_asset_id, notes)
- 每文件一行, status=received, runtime_file/approved_by/approved_at/integrated_at 留空

## 8. 配套 audio.meta fragment

- 路径: `materials/inbox/audio/audio.meta_v003.fragment.json`
- 含 type/version/duration/sample_rate_hz/bit_depth/channels/lufs/true_peak_dbtp/loop_safe/loop_fade_sec/loop_start_sample/loop_end_sample/master_file/runtime_file/ogg_bitrate_bps

## 9. measurements_v003.json

- 路径: `materials/inbox/audio/measurements_v003.json`
- 含 schema_version, target_lufs, target_true_peak_dbtp, tool, 每曲目 measured_lufs/measured_true_peak_dbtp/first_pass_*_lufs/... 完整字段

## 10. 简短生成 brief

```text
Create one original matched ambience pair for AUD-AMB-002 forest boundary: normal forest and unnatural silent boundary. Both files must be the same 60-90 second duration with identical seamless loop boundaries and must support a clean 2-4 second crossfade. The normal version uses restrained wind, distant birds, leaves, and fine branches. The silent version is not digital silence: keeps low air pressure, distant branch detail, and a deliberate unnatural frequency gap (300-1800Hz bandstop) while removing expected bird/wind continuity.
```
