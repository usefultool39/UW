# Rework request: AUD-AMB-002

- request_id: AUD-AMB-002
- status: changes_requested
- expected_version: v003; do not overwrite or delete v002
- delivery_dir: materials/inbox/audio/ambience
- priority: P1, first-phase runtime blocker
- reviewed_at: 2026-08-07
- runtime_status: prohibited until the full acceptance chain passes

## Findings

- The normal and silent variants are about 16.65 and 34.66 seconds, so they cannot crossfade as a matched pair without authored loop metadata.
- Both report `-70.0 LUFS`; one report has a peak above 0 dBFS. The measurement/export chain is invalid for acceptance.
- The files lack request sidecars, source/rights records, `audio.meta.json` entries, MANIFEST rows, and hashes.

## Required replacement

1. Deliver matched normal-forest and silent-boundary loops with equal duration and aligned loop points, preferably 60-90 seconds.
2. The silent variant must not be digital silence: retain low air pressure, distant fine branches, and an unnatural frequency gap.
3. Deliver 48 kHz/24-bit stereo PCM WAV masters and 160-224 kbps OGG candidates with valid Ogg page framing.
4. Target integrated loudness -26 to -22 LUFS and true peak at or below -2 dBTP. Provide valid measurements and loop sample positions.
5. Add a complete sidecar, `audio.meta.json` entries, and MANIFEST fragments with SHA-256. Do not set runtime fields.

## Acceptance

- Both variants have identical duration, channel layout, sample rate, and loop boundaries.
- A 2-4 second crossfade sounds intentional, with no click, phase collapse, or sudden loudness step.
- The normal-to-silent change is audible on phone speakers without masking dialogue or becoming total silence.

## Copyable generation brief

```text
Create one original matched ambience pair for a 2D narrative RPG forest boundary: normal forest and unnatural silent boundary. Both files must be the same 60-90 second duration with identical seamless loop boundaries and must support a clean 2-4 second crossfade. The normal version uses restrained wind, distant birds, leaves, and fine branches. The silent version is not digital silence: keep low air pressure, distant branch detail, and a deliberate unnatural frequency gap while removing expected bird and wind continuity. Deliver 48 kHz/24-bit stereo PCM WAV masters and 160-224 kbps OGG candidates, integrated loudness between -26 and -22 LUFS, true peak <= -2 dBTP, and exact loop start/end sample metadata. No clipping, no DC offset, no obvious repeating event under 20 seconds, and no fake -70 LUFS measurement. Include request sidecar metadata, prompts, model/tool/version, source/rights statement, audio.meta entries, and SHA-256 manifest rows.
```
