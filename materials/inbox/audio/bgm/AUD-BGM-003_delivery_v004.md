# AUD-BGM-003_delivery_v004

- request_id: AUD-BGM-003
- status: received; not approved/integrated/materials=ready
- expected_version: v004 active contract
- delivery_dir: materials/inbox/audio/bgm
- created_at: 2026-08-07
- creator/source: project-owned procedural synthesis from v003 normalized source; non-destructive v004 export
- tool_model: Python 3.13.9 + numpy/scipy + ffmpeg 8.1.1 (libvorbis, loudnorm, ebur128)
- intended_use: audio/bgm/runtime loop candidate
- license: owned
- source_url: none; original procedural synthesis, no external samples, no recognizable melody
- attribution_required: false
- rights statement: Original project-owned audio generated procedurally; no vocals, no sampled copyrighted material, no AI training-set reference.
- prompt: 
- AUD-BGM-003_relationship_daily_a_v004: Warm daily-relationship loop: soft plucks, low warm pad, gentle forward motion, hearth/meals/journal mood, no sugary melody or vocals.
- AUD-BGM-003_relationship_daily_b_v004: Warm daily-relationship loop: alternate seed phrasing, soft plucks and low pad, restrained companion mood, no vocals or recognizable melody.
- negative_prompt: no vocals; no recognizable copyrighted melody; no clipping; no fake -70 LUFS report; no long silence in BGM; no digital silence in AMB-002 silent; no third-party samples.
- edits: copied v003 normalized 48k/24-bit stereo WAV into v004 master name, exported OGG 160-224 kbps, measured loudness/peak/loop seam, documented ducking QA.
- qa_status: algorithmic loop seam and ducking proxy passed; human-ear loop/ducking review remains part of project acceptance and is not claimed as complete.

## Per-stem measurements

| Stem | I LUFS | Peak dBFS | Duration s | Loop end sample | OGG kbps | Seam dB | 2s similarity |
|---|---|---|---|---|---|---|---|
| AUD-BGM-003_relationship_daily_a_v004 | -18.7 | -1.6 | 76.0 | 3648000 | 163.1 | -240.0 | 0.991 |
| AUD-BGM-003_relationship_daily_b_v004 | -18.8 | -1.8 | 66.0 | 3168000 | 163.2 | -240.0 | 0.993 |

## File list with SHA-256

| File | SHA-256 | Size |
|---|---|---|
| inbox\audio\bgm\AUD-BGM-003_relationship_daily_a_v004_48k24b.wav | 994a571003a934006dab8983cbf3f7896abd4a7a97c0f5c0fc5db66f5c12d244 | 21888044 |
| inbox\audio\bgm\AUD-BGM-003_relationship_daily_a_v004.ogg | 649f752f0fd94b5575104335ff62273b09ce32329d4cc0e7ea3a7c0f0addc895 | 1549770 |
| inbox\audio\bgm\AUD-BGM-003_relationship_daily_b_v004_48k24b.wav | 9020ab6b36a90ccab263d4e47a36f5715a8c80c3eb136bb041910428172fb27e | 19008044 |
| inbox\audio\bgm\AUD-BGM-003_relationship_daily_b_v004.ogg | 8399740c2bcfe369ed084f0170cabb472627ba9b25719740272e75ea1221df40 | 1346721 |