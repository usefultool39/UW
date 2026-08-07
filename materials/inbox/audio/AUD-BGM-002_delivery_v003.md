# AUD-BGM-002_delivery_v003

- request_id: AUD-BGM-002
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

- 目标规格: BGM-002: 75-110s, -20..-17 LUFS, TP<= -1 dBTP
- 实测（见 measurements_v003.json）:

| name | dur (s) | I LUFS | TP dBTP | OGG kbps | loop_safe | fade (s) |
|---|---|---|---|---|---|---|
| AUD-BGM-002_boundary_investigation_a_v003 | 91.0 | -18.7 | -1.7 | 161.6 | True | 4.0 |
| AUD-BGM-002_boundary_investigation_b_v003 | 84.0 | -18.3 | -1.6 | 161.6 | True | 4.0 |

## 3. 创作提示词（合成描述）

```text
Programmatic synthesis: pink noise lowpass @240Hz (slow LFO 'breathing') + low-octave D/Bb dissonant pad (D2 73.42Hz + Bb2 116.54Hz with sub-cent detune for beating) + Karplus-Strong plucked bell on G/A/C/D/F5 with deliberately irregular 4-9s timing + sparse 1.2s 800-1600Hz bandpass noise bursts every 11-17s. A 12% mid-track envelope dip (0.62-0.74 for /a, 0.45-0.55 for /b) models an 'absence' event. Two versions /a and /b use different seeds (3001, 3002) for timing/scoring variation; no melody, no lyrics, no recognizable copyrighted motif.
```

### Negative prompt / 禁止项

```text
no vocals; no recognizable copyrighted melody or motif; no clipping; no long silence; no fake -70 LUFS report; no repeated foreground event under 20s; no DC offset; no obvious 20s loop artifact; no third-party samples; no AI-voice, no AI-trained song references.
```

## 4. seed / settings / 循环 / 修整

| name | seed | 采样率 | 位深 | 通道 | loop start sample | loop end sample | fade sec |
|---|---|---|---|---|---|---|---|
| AUD-BGM-002_boundary_investigation_a_v003 | 3001 | 48000 | 24 | 2 | 0 | 4368000 | 4.0 |
| AUD-BGM-002_boundary_investigation_b_v003 | 3002 | 48000 | 24 | 2 | 0 | 4032000 | 4.0 |

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
| audio/bgm/AUD-BGM-002_boundary_investigation_a_v003.wav | master WAV | 5930881cf18af0fac524546d0711722c79b1a100afdac1e03ec8004edfda2439 | 26208102 |
| audio/bgm/AUD-BGM-002_boundary_investigation_a_v003.ogg | runtime OGG | c5c3152e79b42e0dc577e1ec2b629b5e106ce546e2503503fa163bd900763521 | 1838398 |
| audio/bgm/AUD-BGM-002_boundary_investigation_b_v003.wav | master WAV | 15802d4184fdaf55b75aaafd071f0a0f76669a71cc3754b15b3c18baedaa2998 | 24192102 |
| audio/bgm/AUD-BGM-002_boundary_investigation_b_v003.ogg | runtime OGG | 10a8c9259bf266fbd75c78ddd413ee3a4f7f2ef707be629b219698fe2522c6bd | 1696878 |

## 7. Manifest 片段

- 路径: `materials/inbox/audio/AUD-BGM-002_manifest_fragment_v003.csv`
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
Produce two original seamless BGM packages for AUD-BGM-002: two 75-110 second restrained boundary-investigation loops with sparse texture, silence gaps, subtle irregular bell or string friction, and controlled low end; create unease through negative space, not a dense horror wall. Two versions a/b share spec but differ in seed-driven event timing.
```
