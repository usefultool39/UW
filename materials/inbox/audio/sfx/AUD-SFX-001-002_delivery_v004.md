# AUD-SFX-001/002_delivery_v004

- request_id: AUD-SFX-001 / AUD-SFX-002
- status: received; not approved/integrated
- expected_version: v004 active contract (UW-UPGRADE-1.0 batch)
- delivery_dir: materials/inbox/audio/sfx
- created_at: 2026-08-07
- creator/source: WorkBuddy AI Asset Agent — procedural synthesis via Python numpy/scipy
- tool_model: Python 3.13 + numpy + scipy signal processing + soundfile (OGG encode)
- intended_use: Phaser 3 game audio; UI feedback + world/activity sound effects
- license: owned
- source_url: none; original procedural synthesis, no external samples
- attribution_required: false
- rights statement: Original project-owned SFX generated procedurally; no vocals, no sampled copyrighted material, no AI training-set reference.

## AUD-SFX-001: UI/Feedback SFX (12 sounds)

| SFX ID | Description | Duration | LUFS | Peak dBFS |
|---|---|---|---|---|
| button_click | Crisp UI click | 0.10s | -20.9 | -3.1 |
| button_hover | Subtle hover tone | 0.15s | -13.2 | -3.1 |
| tab_switch | Two-tone slide | 0.20s | -13.0 | -3.1 |
| menu_open | Rising swoosh | 0.30s | -9.7 | -3.1 |
| menu_close | Descending swoosh | 0.25s | -10.2 | -3.1 |
| notification | Two-note bell | 0.50s | -14.1 | -3.1 |
| success | Rising arpeggio | 0.40s | -13.6 | -3.1 |
| error | Low descending buzz | 0.30s | -6.6 | -3.1 |
| quest_accept | Parchment seal | 0.50s | -19.6 | -3.1 |
| quest_complete | Short fanfare | 0.80s | -14.0 | -3.1 |
| day_settle | Gentle bell + page | 1.00s | -16.1 | -3.1 |
| page_turn | Paper rustle | 0.30s | -20.3 | -3.1 |

## AUD-SFX-002: World/Activity SFX (14 sounds)

| SFX ID | Description | Duration | LUFS | Peak dBFS |
|---|---|---|---|---|
| footstep_grass | Soft grass crunch | 0.15s | -19.4 | -3.1 |
| footstep_stone | Hard stone click | 0.15s | -25.5 | -3.1 |
| footstep_wood | Hollow wood thud | 0.15s | -16.7 | -3.1 |
| door_open | Slow wood creak | 0.60s | -12.7 | -3.1 |
| door_close | Thud + latch | 0.40s | -18.1 | -3.1 |
| item_pickup | Light chime + rustle | 0.30s | -19.2 | -3.1 |
| book_open | Cover + page | 0.40s | -14.4 | -3.1 |
| clue_select | Cyan ping + reveal | 0.50s | -14.7 | -3.1 |
| sacred_ink | Golden hum + ink write | 0.80s | -14.6 | -3.1 |
| boundary_ripple | Low boom + shimmer | 0.60s | -17.6 | -3.1 |
| relationship_up | Warm rising tone | 0.40s | -15.0 | -3.1 |
| reward | Coin/sparkle | 0.50s | -16.0 | -3.1 |
| capture_silence | Convergence + impact + fade | 1.50s | -18.2 | -3.1 |
| rain_drop | Tiny plink | 0.10s | -21.0 | -3.1 |

## Technical Specifications

- Sample rate: 48000 Hz
- Bit depth: 24-bit
- Channels: 2 (stereo)
- Format: WAV (master) + OGG Vorbis (runtime)
- Normalization: Peak normalized to -3.1 dBFS (0.7 linear)
- All SFX are one-shot (non-looping)

## VFX-SFX Mapping

| VFX Trigger | Paired SFX ID |
|---|---|
| clue_found | clue_select |
| sacred_ink | sacred_ink |
| boundary_ripple | boundary_ripple |
| relationship_up | relationship_up |
| reward | reward |
| capture_silence | capture_silence |

## Manifest

- CSV: `AUD-SFX-001-002_manifest_fragment.csv` — 53 rows (52 audio files + 1 metadata)
- All rows: status=received, license=owned, attribution_required=false

## QA Notes

- All SFX use procedurally synthesized waveforms (sine, sawtooth, noise) with scipy filters
- No external samples or copyrighted source material
- Footstep variants provided for grass, stone, and wood surfaces
- capture_silence is the longest SFX at 1.5s, designed to sync with VIS-VFX-001 capture-silence animation
- Measurements JSON includes per-SFX duration, loudness, and peak data
