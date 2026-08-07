# VIS-MAP-001 UW-UPGRADE-1.0 Delivery Sidecar

- **request_id**: VIS-MAP-001
- **batch**: UW-UPGRADE-1.0
- **creator/source**: WorkBuddy AI Asset Agent
- **created_at**: 2026-08-07T17:56:00+08:00
- **tool/model/version**: Hunyuan Image Generation (terrain base texture), Python PIL (all layers, data, atlases)
- **supersedes**: VIS-MAP-001 v005/v006
- **license**: Project original - UW 0.5.0-pre-capture
- **source_url**: AI generated, no external URL
- **attribution_required**: false
- **intended_use**: Playable Rulid Village map for Pre-Capture vertical slice
- **rights_statement**: Original procedurally-generated and AI-assisted artwork for the UW project. No copyrighted character likenesses, franchise costumes, or official anime frames used.

## Map Specification

- Runtime size: 3024x1792 px
- Grid: 108x64 tiles at 28x28 px/tile
- 9 independent visual layers
- 3 data layers (collision, walkable, interaction)
- 2 atlases (tile, prop)

## Layer Independence

Each layer is a separate PNG file containing ONLY its designated elements:

| Layer | Content | Alpha |
|---|---|---|
| terrain | Ground textures only (grass, dirt, stone) - no roads, buildings, or vegetation baked in | No (RGB) |
| water | River and water bodies only | Yes (RGBA) |
| roads | Village path network only | Yes (RGBA) |
| buildings | Structure footprints and roofs only | Yes (RGBA) |
| vegetation | Trees, bushes, hedges, crops only | Yes (RGBA) |
| occlusion | Building roofs and tree canopies that hide characters | Yes (RGBA) |
| foreground | Edge elements (fences, rocks, foreground bushes) | Yes (RGBA) |
| lighting | Warm light overlays with transparency | Yes (RGBA) |
| weather | Rain, mist, boundary atmosphere | Yes (RGBA) |

## Data Layers

- **collision**: 108x64 grid, 1=blocked (buildings, water, tree trunks, borders), 0=passable
- **walkable**: 108x64 grid, inverse of collision
- **interaction**: 10 interaction points (church_library, home_entrance_n/s, gigas_tree, north_gate, forest_entrance, plaza_center, river_bridge, farmland, end_mountains)

## Village Layout

- Plaza: center (tiles 42-62, 24-36) - N08-N10 declaration/farewell/capture space
- Church Library: upper-left of center (tiles 28-40, 12-24)
- Gigas Cedar Clearing: left side (tiles 8-24, 28-46)
- Houses: north and south of plaza
- North Gate: top-center (tiles 50-60, 3-10)
- Forest Path: leading north from gate
- River: diagonal from top-left to bottom-right
- Farmland: bottom area (tiles 20-90, 48-60)

## Prompt

```
Top-down 2D RPG game map terrain texture, seamless grass field with patches of dirt and worn stone path. No buildings, no trees, no roads, no water, no characters, no text. Hand-painted storybook illustration style. Color palette: moss green (#5F7D4A), rain teal (#46777A), wood brown (#8A5A3B), wheat gold (#D8B767).
```

## Negative Prompt

```
no text, no logo, no watermark, no buildings, no trees, no characters, no UI, no checkerboard, no debug grid, no copyrighted assets
```

## Edits

1. Generated base terrain texture with Hunyuan (1536x1024)
2. Tiled and varied terrain across 3024x1792 with per-tile color variation
3. Generated 8 additional layers programmatically with PIL (water, roads, buildings, vegetation, occlusion, foreground, lighting, weather)
4. Generated collision/walkable grids and interaction data
5. Generated tile atlas (16 tile types) and prop atlas (10 prop types)
6. Generated composite preview and collision visualization
7. Computed SHA-256 for all files

## Automated Checks

- All 9 layers: 3024x1792 - PASS
- Alpha layers (occlusion, foreground, lighting, weather, water, roads, buildings, vegetation): RGBA mode - PASS
- Terrain: RGB mode (no alpha needed) - PASS
- Map JSON: valid, all source paths exist - PASS
- Collision grid: 108x64 - PASS
- Walkable grid: 108x64 - PASS
- Interaction points: 10 - PASS
- Manifest fragment: 18 columns, 14 rows - PASS

## Human Review Required

- Village layout readability at 100%/50%/25% zoom
- Collision/walkable consistency with visual layers
- Interaction point accessibility (not blocked by collision)
- Style consistency with VIS-ENV-001 and VIS-CHR packages
- Game-in overlay testing (Phaser tilemap rendering)
- Desktop/mobile viewport testing

## Known Issues

- Terrain texture is procedurally tiled; may need more organic variation
- River path is approximate; bridge crossing needs verification
- Building styles are simplified; may need refinement for production
- Tile atlas has limited tile types (16); full production may need more
