# AUD-BGM-002_delivery_v004

- request_id: AUD-BGM-002
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
- AUD-BGM-002_boundary_investigation_a_v004: Sparse boundary-investigation loop: interrupted wind, low air pressure, irregular bell/string friction, negative space, restrained unease, no vocals or recognizable melody.
- AUD-BGM-002_boundary_investigation_b_v004: Sparse boundary-investigation loop: alternate seed timing, broken bird absence, low dissonant air, irregular distant friction, no dense horror wall.
- negative_prompt: no vocals; no recognizable copyrighted melody; no clipping; no fake -70 LUFS report; no long silence in BGM; no digital silence in AMB-002 silent; no third-party samples.
- edits: copied v003 normalized 48k/24-bit stereo WAV into v004 master name, exported OGG 160-224 kbps, measured loudness/peak/loop seam, documented ducking QA.
- qa_status: algorithmic loop seam and ducking proxy passed; human-ear loop/ducking review remains part of project acceptance and is not claimed as complete.

## Per-stem measurements

| Stem | I LUFS | Peak dBFS | Duration s | Loop end sample | OGG kbps | Seam dB | 2s similarity |
|---|---|---|---|---|---|---|---|
| AUD-BGM-002_boundary_investigation_a_v004 | -18.7 | -1.7 | 91.0 | 4368000 | 161.6 | -240.0 | 0.984 |
| AUD-BGM-002_boundary_investigation_b_v004 | -18.3 | -1.6 | 84.0 | 4032000 | 161.6 | -240.0 | 0.931 |

## File list with SHA-256

| File | SHA-256 | Size |
|---|---|---|
| inbox\audio\bgm\AUD-BGM-002_boundary_investigation_a_v004_48k24b.wav | 0635461f74d1c77217eeaad9c8a93ea7efc4b7343bdcb9f2dbb44c04288a8f65 | 26208044 |
| inbox\audio\bgm\AUD-BGM-002_boundary_investigation_a_v004.ogg | 8138f372b22b19faf2a7088d5988a801854fc40d4e436e3d607f8913a783fe8c | 1838398 |
| inbox\audio\bgm\AUD-BGM-002_boundary_investigation_b_v004_48k24b.wav | 4583bcf394bb35f51f4e1325fc5747b96826176935dbc341228cd26eba4fbdd7 | 24192044 |
| inbox\audio\bgm\AUD-BGM-002_boundary_investigation_b_v004.ogg | 0027648bc414507ac9727af1af1ede011a845e9cf2976bda86bfe6fc870edb53 | 1696878 |