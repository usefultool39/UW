# AUD-AMB-002_delivery_v004

- request_id: AUD-AMB-002
- status: received; not approved/integrated/materials=ready
- expected_version: v004 active contract
- delivery_dir: materials/inbox/audio/ambience
- created_at: 2026-08-07
- creator/source: project-owned procedural synthesis from v003 normalized source; non-destructive v004 export
- tool_model: Python 3.13.9 + numpy/scipy + ffmpeg 8.1.1 (libvorbis, loudnorm, ebur128)
- intended_use: audio/ambience/runtime loop candidate
- license: owned
- source_url: none; original procedural synthesis, no external samples, no recognizable melody
- attribution_required: false
- rights statement: Original project-owned audio generated procedurally; no vocals, no sampled copyrighted material, no AI training-set reference.
- prompt: 
- AUD-AMB-002_forest_silence_normal_v004: Forest boundary normal ambience: low air pressure, distant birds, leaves, fine branches, restrained wind, seamless loop.
- AUD-AMB-002_forest_silence_silent_v004: Unnatural forest boundary silence: keeps low air pressure and distant branch detail, removes expected wind/bird continuity, deliberate 300-1800Hz frequency gap, not digital silence.
- negative_prompt: no vocals; no recognizable copyrighted melody; no clipping; no fake -70 LUFS report; no long silence in BGM; no digital silence in AMB-002 silent; no third-party samples.
- edits: copied v003 normalized 48k/24-bit stereo WAV into v004 master name, exported OGG 160-224 kbps, measured loudness/peak/loop seam, documented ducking QA.
- qa_status: algorithmic loop seam and ducking proxy passed; human-ear loop/ducking review remains part of project acceptance and is not claimed as complete.

## Per-stem measurements

| Stem | I LUFS | Peak dBFS | Duration s | Loop end sample | OGG kbps | Seam dB | 2s similarity |
|---|---|---|---|---|---|---|---|
| AUD-AMB-002_forest_silence_normal_v004 | -23.0 | -5.8 | 76.0 | 3648000 | 193.6 | -240.0 | 0.64 |
| AUD-AMB-002_forest_silence_silent_v004 | -22.9 | -10.9 | 76.0 | 3648000 | 193.6 | -240.0 | 0.786 |

## File list with SHA-256

| File | SHA-256 | Size |
|---|---|---|
| inbox\audio\ambience\AUD-AMB-002_forest_silence_normal_v004_48k24b.wav | eab9c899eaad1297fd51a03fc71e28ac8c48ba1e1a77975a7d6ca98f32739c31 | 21888044 |
| inbox\audio\ambience\AUD-AMB-002_forest_silence_normal_v004.ogg | 7d2c3aedb9d60bfccc038a01abfa6fd91f1ad3e16c9318d0b9a5bcfd2e0270a1 | 1839273 |
| inbox\audio\ambience\AUD-AMB-002_forest_silence_silent_v004_48k24b.wav | 79a50e099006626aa197aaef96f7fdcb9550217eee5539cbab50ce288a932179 | 21888044 |
| inbox\audio\ambience\AUD-AMB-002_forest_silence_silent_v004.ogg | 6bdb651e82915cfc4f5fdcce4ac43947331e9e34d7aa8f43c928bcb323da1193 | 1839243 |