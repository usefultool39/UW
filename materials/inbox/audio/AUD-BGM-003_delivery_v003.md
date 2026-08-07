# AUD-BGM-003_delivery_v003

- request_id: AUD-BGM-003
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

- 目标规格: BGM-003: 60-100s, -20..-17 LUFS, TP<= -1 dBTP
- 实测（见 measurements_v003.json）:

| name | dur (s) | I LUFS | TP dBTP | OGG kbps | loop_safe | fade (s) |
|---|---|---|---|---|---|---|
| AUD-BGM-003_relationship_daily_a_v003 | 76.0 | -18.7 | -1.6 | 163.1 | True | 4.0 |
| AUD-BGM-003_relationship_daily_b_v003 | 66.0 | -18.8 | -1.8 | 163.2 | True | 4.0 |

## 3. 创作提示词（合成描述）

```text
Programmatic synthesis: Karplus-Strong pentatonic pluck on A3 + ratios [1, 9/8, 5/4, 3/2, 5/3, 2, 9/4, 5/2] with 0.6-1.6s gaps; low A1/E2/A2 warm pad (lowpass 280Hz) with 0.11Hz LFO tremolo; sub-300Hz pink noise floor (0.006 amplitude); occasional 2-3.5kHz distant chirps every 7-13s. Two versions /a (80s) and /b (70s) use seeds 4001/4002. No vocals, no sampled melody references, no epic percussion.
```

### Negative prompt / 禁止项

```text
no vocals; no recognizable copyrighted melody or motif; no clipping; no long silence; no fake -70 LUFS report; no repeated foreground event under 20s; no DC offset; no obvious 20s loop artifact; no third-party samples; no AI-voice, no AI-trained song references.
```

## 4. seed / settings / 循环 / 修整

| name | seed | 采样率 | 位深 | 通道 | loop start sample | loop end sample | fade sec |
|---|---|---|---|---|---|---|---|
| AUD-BGM-003_relationship_daily_a_v003 | 4001 | 48000 | 24 | 2 | 0 | 3648000 | 4.0 |
| AUD-BGM-003_relationship_daily_b_v003 | 4002 | 48000 | 24 | 2 | 0 | 3168000 | 4.0 |

Edits: ffmpeg loudnorm 两阶段归一至 -18 LUFS (BGM) / -23 LUFS (AMB)，TP target -2.0/-3.0 dBTP 实测在 spec 范围；OGG 用 -b:a 192k -minrate 160k -maxrate 224k 约束。

## 5. 来源与权利

- license: owned（owned (project-internal procedural synthesis by Mavis, no third-party samples, no AI-copied material)）
- source_url: none（程序化合成，无外部素材/采样/参考旋律）
- attribution_required: false
- intended_use: audio / bgm
- rights statement: 本包文件由项目成员 Mavis 通过 Python + ffmpeg 程序化生成，不包含人声、可识别版权旋律、第三方采样或 AI 训练集参考。

## 6. 文件清单（带 SHA-256）

| 文件 | 角色 | SHA-256 | size |
|---|---|---|---|
| audio/bgm/AUD-BGM-003_relationship_daily_a_v003.wav | master WAV | ce363e53b6319acfdd70b8f1e6d27a526e80ed591034291209ae3a2ce1797518 | 21888102 |
| audio/bgm/AUD-BGM-003_relationship_daily_a_v003.ogg | runtime OGG | 006b24a904074b9c79132fbcbc801d64f59c78fc7d797dee10f8e473627738d5 | 1549770 |
| audio/bgm/AUD-BGM-003_relationship_daily_b_v003.wav | master WAV | 82b6b3b91288c08137fce413dfaad72920827c56d20c0759c2a57e6f9bbf30ec | 19008102 |
| audio/bgm/AUD-BGM-003_relationship_daily_b_v003.ogg | runtime OGG | 2ee7c7f10900b8cf9d3556150bdc37ed3f20cb187aec942ccd8b0202e722e596 | 1346676 |

## 7. Manifest 片段

- 路径: `materials/inbox/audio/AUD-BGM-003_manifest_fragment_v003.csv`
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
Produce two original seamless BGM packages for AUD-BGM-003: two 60-100 second warm but unsentimental daily-relationship loops for meals, hearth conversations, and journal writing, with gentle forward motion and no copied melody. Two versions a/b share spec but differ in seed-driven event timing.
```
