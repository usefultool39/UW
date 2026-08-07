# VIS-CHR-001/002/003 UW-UPGRADE-1.0 Delivery Sidecar

- **request_id**: VIS-CHR-001, VIS-CHR-002, VIS-CHR-003
- **batch**: UW-UPGRADE-1.0
- **creator/source**: WorkBuddy AI Asset Agent
- **created_at**: 2026-08-07T18:00:00+08:00
- **tool/model/version**: Hunyuan Image Generation (character base art, transparent background), Python PIL (sprite sheet composition, walk/idle/interact frame generation)
- **supersedes**: VIS-CHR-001/002/003 v008
- **license**: Project original - UW 0.5.0-pre-capture
- **source_url**: AI generated, no external URL
- **attribution_required**: false
- **intended_use**: Core character sprites for Pre-Capture vertical slice map exploration
- **rights_statement**: Original AI-generated character art. No copyrighted character likenesses, franchise costumes, or official anime frames used. Characters are original designs inspired by the project's narrative requirements.

## Characters

| Request ID | Character | Description |
|---|---|---|
| VIS-CHR-001 | Kirito | Young boy, black hair, dark navy village worker outfit with record book |
| VIS-CHR-002 | Alice | Young girl, wheat-golden hair, cream village dress with blue-gold accessories |
| VIS-CHR-003 | Eugeo | Young boy, light brown hair, cold blue-grey worker outfit with axe |

## Sprite Sheet Specification

- Cell size: 64x96 px
- Sheet layout: 12 columns x 4 rows = 48 frames per character
- Format: 8-bit RGBA PNG with transparency
- Anchor: bottom-center [32, 96]
- Collision footprint: [24, 84, 40, 94]
- Display height: 48px (when rendered in-game)

## Animation Breakdown

Each character has 4 directions (down, left, right, up), each with:
- **idle**: 2 frames (base + breathing), 4 fps, loop
- **walk**: 6 frames (full walk cycle with leg/arm/body movement), 8 fps, loop
- **interact**: 4 frames (lean/raise/crouch/reach), 4 fps, non-loop

### Character-specific interact actions:
- Kirito: record, point, crouch_observe, reach_stop
- Alice: hand_item, basic_aid, check_record, farewell_look
- Eugeo: axe_ready,协作_hand_item, check_route, protective_stance

## Direction Generation

- **down**: Original AI-generated art
- **left**: Horizontal mirror of down
- **right**: Horizontal mirror of down
- **up**: Back view (face area darkened to suggest back of head)

## Walk Cycle Details

Walk frames use sinusoidal phase for natural movement:
- Leg shift: sin(phase) * 3px horizontal
- Arm shift: -sin(phase) * 2px horizontal (opposite to legs)
- Vertical bob: |sin(phase*2)| * 2px
- Body lean: sin(phase) * 1px

## Prompts (per character)

### Kirito
```
Pixel art RPG character sprite, a young boy with short black hair wearing a dark navy village worker outfit with a small record book and pen tucked in belt. Standing pose facing forward. Dark ink outlines (#2B2521), dark navy clothing with cold blue accents. Transparent background.
```

### Alice
```
Pixel art RPG character sprite, a young girl with wheat-golden blonde hair wearing a light cream village dress with small blue-gold accessories. Standing pose facing forward. Wheat golden hair (#D8B767), cream dress with blue-green accents. Transparent background.
```

### Eugeo
```
Pixel art RPG character sprite, a young boy with light brown hair wearing a cold blue-grey village worker outfit with a small axe on belt. Standing pose facing forward. Cold blue-grey clothing with wood/brown accents. Transparent background.
```

## Negative Prompt (shared)
```
no text, no logo, no watermark, no shadow, no ground, no background scene, no copyrighted character likeness, no franchise costume, no weapons (except small axe for Eugeo), no modern clothing
```

## Edits

1. Generated 3 character base images with Hunyuan (transparent background, 1024x1024)
2. Cropped to content bounding box and fitted into 64x96 cells
3. Generated walk cycle (6 frames) with sinusoidal leg/arm/bob movement
4. Generated idle frames (2) with breathing compression
5. Generated interact frames (4) with lean/raise/crouch/reach poses
6. Created left/right via horizontal mirror, up via back view
7. Composed 48-frame sprite sheets (768x384)
8. Generated frames JSON with per-frame rect, anchor, fps, loop
9. Generated contact sheets and 48px display previews
10. Computed SHA-256 for all files

## Automated Checks

- All 3 sprite sheets: 768x384, RGBA - PASS
- All 3 frames JSON: valid, 48 frames each, all rects within sheet bounds - PASS
- Frame count: 48 per character (12 per direction x 4 directions) - PASS
- Animation counts: idle=2, walk=6, interact=4 per direction - PASS
- Alpha: transparent background confirmed - PASS
- Manifest fragment: 18 columns, 12 rows - PASS

## Human Review Required

- Character distinctiveness at 48px display height
- Walk cycle smoothness (no jarring jumps)
- Interact action readability
- Up direction back view quality
- Style consistency with VIS-ENV-001 and VIS-MAP-001
- Game-in animation testing (Phaser sprite loading)
- Copyright/originality verification (no resemblance to official SAO character designs)

## Known Issues

- Up direction uses darkened face area rather than true back-view art
- Left and right are mirrors of each other (not independently drawn)
- Walk cycle uses body-part shifting rather than redrawn frames
- Interact frames use transformations rather than unique action art
- Characters may need refinement for production-quality animation
