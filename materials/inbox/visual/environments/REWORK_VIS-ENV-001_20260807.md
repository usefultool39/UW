# Rework request: VIS-ENV-001

- request_id: VIS-ENV-001
- status: changes_requested
- expected_version: v003; do not overwrite or delete v002
- delivery_dir: materials/inbox/visual/environments
- priority: P1
- reviewed_at: 2026-08-07
- intended_use: activity panels and chapter transitions only, never the playable map

## Findings

- Six painted backgrounds are present, but the reviewed file is 2752x1536 rather than the requested 1920x1080 delivery size.
- The files have no sidecars, source/rights records, safe-area notes, MANIFEST rows, or hash registration.
- These images may be reviewed as activity/transition backgrounds only. They are not collision, walkable, occlusion, or interaction data.

## Required replacement

1. Deliver exactly six 1920x1080 RGB PNG masters: church library, Gigas clearing, home hearth, north gate, forest path/silent line, and End Mountains cave/boundary approach.
2. Keep them character-free and text-free, with a clear middle/lower interaction area and safe margins for desktop/mobile panel crops.
3. Provide an optional separate RGBA foreground overlay only where it helps panel depth; do not imply that it is map collision data.
4. Add a complete request sidecar and one MANIFEST fragment row per file with SHA-256.

## Acceptance

- Correct scene identity, 16:9 composition, exact dimensions, no baked text/watermark, and no critical detail lost in center-cropped mobile preview.
- Canon, style, source/rights, technical, and in-game panel QA all pass before runtime promotion.

## Copyable generation brief

```text
Create six original 1920x1080 character-free environment backgrounds for a clear, bright 2D narrative RPG: church library/reading desk, Gigas Cedar clearing, village home hearth, north gate, forest path with an unnatural silent boundary, and End Mountains cave/boundary approach. These are activity-panel and chapter-transition backgrounds, not playable maps. Use consistent hand-painted linework and color language, no text, no labels, no UI, no watermarks, no copyrighted screenshot composition, and no characters. Preserve a readable middle/lower interaction area and desktop/mobile crop-safe margins. If foreground depth is useful, deliver it as a separately registered transparent RGBA overlay. Include request sidecar metadata, exact prompts, model/tool/version, source/rights statement, intended use, and SHA-256 manifest rows.
```
