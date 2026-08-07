# Rework request: VIS-MAP-001

- request_id: VIS-MAP-001
- status: changes_requested
- expected_version: v003; do not overwrite or delete v002
- delivery_dir: materials/inbox/visual/world
- priority: P1, first-phase runtime blocker
- reviewed_at: 2026-08-07
- runtime_status: prohibited until the full acceptance chain passes

## Findings

- The received master is a 2752x1536, 24-bit RGB painted overview. It is not the requested 4096x2304 source or a grid-aligned runtime map.
- The image contains baked text (for example, `LIBRARY`) and cannot be localized.
- The apparent layer PNGs do not provide a tile atlas, collision data, walkable mask, occlusion mask, foreground depth, interaction points, or scene metadata.
- A single illustration cannot replace a playable Phaser map. No received binary may be copied into runtime.
- Every received binary lacks a complete versioned sidecar and has no request-scoped MANIFEST/hash row.

## Required replacement

1. Match `data/world/world_map.json`: 108x64 tiles, 28 px per tile, 3024x1792 runtime layer dimensions.
2. Deliver grid-aligned PNG layers for terrain/water, roads, ground props, buildings, vegetation, occluders, foreground, lighting, and weather. Transparent layers must use real RGBA alpha.
3. Deliver a reusable tile/prop atlas plus Tiled-compatible JSON or equivalent frame metadata.
4. Deliver collision, walkable, occlusion/depth, and interaction/POI data for the church/library, square, Gigas Cedar route, home, north gate, and End Mountains route.
5. Remove all text, labels, characters, UI, and baked checkerboards.
6. Add a complete sidecar with creator/tool/model/version, exact prompts, edits, creation date, rights/license, source URL or explicit no-URL reason, and intended use.
7. Add a MANIFEST fragment with one row per source file and SHA-256. Do not populate `runtime_file` or `integrated_at`.

## Acceptance

- All layers have identical dimensions and registration; roads remain continuous at 50% zoom.
- Collision and walkable data align to the visible roads and entrances with no one-tile traps.
- Occluders can render above a 52 px-tall runtime character without hiding the character's feet incorrectly.
- Desktop and 390x844 touch layouts retain a readable central play area.
- `check_materials.py` passes, then the package passes an in-game screenshot, movement, collision, occlusion, and interaction QA pass.

## Copyable generation brief

```text
Create an original, production-ready 2D narrative RPG map package for Rulid Village. Use a clear, bright, hand-painted 3/4 top-down style with strong road readability and restrained detail. Target the existing Phaser grid exactly: 108x64 tiles, 28 pixels per tile, 3024x1792 pixels per runtime layer. Deliver separate registered PNG layers for terrain/water, roads, ground props, buildings, vegetation, occluders, foreground, lighting, and weather, plus a reusable tile/prop atlas, collision/walkable mask, occlusion/depth mask, and interaction metadata for church/library, village square, Gigas Cedar route, home, north gate, and End Mountains route. No characters, no text, no signs with words, no UI, no copyrighted game/anime composition, no baked checkerboard, and no single flattened illustration as the only deliverable. Keep roads continuous at half-scale and reserve a readable central play area under desktop and mobile HUD safe areas. Include exact dimensions, layer names, alpha mode, tile IDs, prompts, model/tool/version, source/rights statement, and SHA-256 manifest fragment.
```
