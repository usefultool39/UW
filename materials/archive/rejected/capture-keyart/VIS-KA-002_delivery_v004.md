# VIS-KA-002_delivery_v004

- request_id: VIS-KA-002
- status: received; not approved/integrated
- expected_version: v004 active contract (UW-UPGRADE-1.0 batch)
- delivery_dir: materials/inbox/visual/key_art
- created_at: 2026-08-07
- creator/source: WorkBuddy AI Asset Agent — ImageGen (Hunyuan) base generation + Python PIL processing
- tool_model: ImageGen Hunyuan (text-to-image) + Python 3.13 Pillow LANCZOS resize/crop
- intended_use: Game endpoint/loading screen key art; promotional materials; store page assets
- license: owned
- source_url: ImageGen (Hunyuan) AI generation — project-owned prompts
- attribution_required: false
- rights statement: Original project-owned key art generated via ImageGen with project-authored prompts; no copyrighted reference images, no third-party assets.

## Scene Description

**Title:** Boundary Capture Scene

**Depiction:** Alice stands at the edge of the misty forest boundary at dusk. Faint indigo ripples distort the air around her — the boundary between worlds. The forest behind her is dark with ancient trees and bioluminescent cyan clues. Rain falls gently. Warm golden village lantern light contrasts with cold indigo boundary energy. The atmosphere is melancholic and silent, capturing the pivotal moment of the "pre-capture" narrative arc.

**Visual Style:** Rulid Storybook — hand-painted aesthetic, soft brushstrokes, atmospheric depth, storybook color palette (moss green, rain teal, wood brown, wheat gold, indigo night).

## Deliverables

### Desktop (16:9 Landscape)

| File | Resolution | Format | Size | SHA-256 (prefix) |
|---|---|---|---|---|
| VIS-KA-002_UW-UPGRADE-1.0_desktop_2560x1440.png | 2560x1440 | PNG | 3,889,753 | afeff1a01d11a800... |
| VIS-KA-002_UW-UPGRADE-1.0_desktop_2560x1440.jpg | 2560x1440 | JPEG q92 | 629,579 | 30267eef27887aa1... |
| VIS-KA-002_UW-UPGRADE-1.0_desktop_thumb_640x360.png | 640x360 | PNG | 377,487 | 0e166b194c58dcbb... |

### Mobile (3:4 Portrait)

| File | Resolution | Format | Size | SHA-256 (prefix) |
|---|---|---|---|---|
| VIS-KA-002_UW-UPGRADE-1.0_mobile_1440x1920.png | 1440x1920 | PNG | 3,396,559 | 8bd2541c922a89b3... |
| VIS-KA-002_UW-UPGRADE-1.0_mobile_1440x1920.jpg | 1440x1920 | JPEG q92 | 554,852 | b5d61507e482f539... |
| VIS-KA-002_UW-UPGRADE-1.0_mobile_thumb_360x480.png | 360x480 | PNG | 303,043 | c215561f90c7b292... |

### Metadata

| File | Description |
|---|---|
| VIS-KA-002_UW-UPGRADE-1.0_metadata.json | Variant specs, source image info, intended use |

## Processing Pipeline

1. **Base generation:** Two ImageGen (Hunyuan) prompts — landscape (1536x1024) and portrait (1024x1536)
2. **Smart crop:** Aspect-ratio-aware crop with upper bias for character focus (portrait)
3. **Upscale:** LANCZOS resampling to target resolution (2560x1440 / 1440x1920)
4. **Thumbnail:** LANCZOS downscale to 640x360 / 360x480
5. **JPEG export:** Quality 92 with optimization for web delivery

## Manifest

- CSV: `VIS-KA-002_UW-UPGRADE-1.0_manifest_fragment.csv` — 7 rows
- All rows: status=received, license=owned, attribution_required=false

## QA Notes

- Desktop version provides full 16:9 coverage for standard and ultrawide displays
- Mobile version optimized for 3:4 portrait screens (phone loading screens)
- JPEG variants provided for web/store page use (smaller file size)
- PNG masters retain full quality for in-game rendering
- Thumbnails provided for preview/loading placeholders
- Source ImageGen files retained in delivery directory for traceability
