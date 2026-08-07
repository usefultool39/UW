# VIS-UI-002_delivery_v004

- request_id: VIS-UI-002
- status: received; not approved/integrated
- expected_version: v004 active contract (UW-UPGRADE-1.0 batch)
- delivery_dir: materials/inbox/visual/ui_icons
- created_at: 2026-08-07
- creator/source: WorkBuddy AI Asset Agent — procedural generation via Python PIL
- tool_model: Python 3.13 + Pillow; SVG path definitions + PNG rasterization
- intended_use: Vue 3 UI layer icon assets; Phaser 3 HUD elements
- license: owned
- source_url: none; original procedural synthesis
- attribution_required: false
- rights statement: Original project-owned UI icons generated procedurally; no external icon packs, no AI training-set reference.

## Icon Summary

- Total icons: 32
- Sizes per icon: 24px, 48px, 96px (3 variants)
- State variants per icon (at 48px): default, hover, selected, disabled, warning (5 states)
- SVG source per icon: 1 file
- Total files per icon: 3 sizes + 4 states + 1 SVG = 8 files
- Total asset files: 32 * 8 = 256
- Plus: contact sheet, registry JSON, manifest CSV = 259 total

## Categories

| Category | Count | Icons |
|---|---|---|
| Navigation | 5 | location, route, arrival, interact, back |
| Resource | 5 | time, stamina, sacred_power, health, recovery |
| Investigation | 5 | clue, record, observe, anomaly, boundary |
| Relationship | 5 | relationship, memory, promise, tension, companion |
| Activity | 6 | reading, training, meal, patrol, delivery, capture |
| Result | 6 | success, warning, locked, completed, retry, day_settle |

## Color Palette

| Color | Hex | Usage |
|---|---|---|
| INK | #2B2521 | Default stroke |
| PARCHMENT | #E6D5B8 | Background |
| MOSS | #5F7D4A | Success/recovery |
| RAIN_TEAL | #46777A | Navigation/relationship |
| WOOD | #8A5A3B | Activity/delivery |
| WHEAT | #D8B767 | Warning/arrival |
| SKY | #9AC0CF | Secondary accent |
| INDIGO | #3C4668 | Boundary/anomaly/capture |
| CLUE_CYAN | #72B8C4 | Clue/interaction |
| TENSION | #B65F62 | Health/locked |
| GOLD | #F6D36E | Sacred power/promise |

## File Naming Convention

```
VIS-UI-002_UW-UPGRADE-1.0_<icon_id>_<size>.png        (default state)
VIS-UI-002_UW-UPGRADE-1.0_<icon_id>_48_<state>.png    (state variant)
VIS-UI-002_UW-UPGRADE-1.0_<icon_id>.svg               (vector source)
```

## State Variants

| State | Visual Treatment |
|---|---|
| default | Standard stroke, no fill |
| hover | Accent fill at 30% opacity, accent background circle |
| selected | Accent stroke, accent fill, border rectangle |
| disabled | 40% opacity, muted stroke |
| warning | WHEAT stroke, WHEAT border rectangle |

## Manifest

- CSV: `VIS-UI-002_UW-UPGRADE-1.0_manifest_fragment.csv` — 258 rows
- All rows: status=received, license=owned, attribution_required=false
- Replaces: VIS-UI-001_v001

## QA Notes

- All PNG files are RGBA with transparent backgrounds
- SVG sources use 24x24 viewBox with 2px stroke width
- Contact sheet: 768x384 (8 columns x 4 rows, 48px icons scaled 2x)
- Registry JSON includes icon_id, category, description, accent_color, and file paths
- "capture" icon added to Activity category (was missing in initial generation)
