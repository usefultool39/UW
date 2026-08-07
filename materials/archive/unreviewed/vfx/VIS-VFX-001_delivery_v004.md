# VIS-VFX-001_delivery_v004

- request_id: VIS-VFX-001
- status: received; not approved/integrated
- expected_version: v004 active contract (UW-UPGRADE-1.0 batch)
- delivery_dir: materials/inbox/visual/vfx
- created_at: 2026-08-07
- creator/source: WorkBuddy AI Asset Agent — procedural generation via Python PIL/numpy
- tool_model: Python 3.13 + Pillow + numpy; frame-by-frame procedural pixel synthesis
- intended_use: Phaser 3 sprite-sheet VFX overlays; screen/add blend modes
- license: owned
- source_url: none; original procedural synthesis
- attribution_required: false
- rights statement: Original project-owned VFX generated procedurally; no external sprites, no AI training-set reference.

## VFX Summary

| VFX ID | Name | Frames | FPS | Duration | Blend | Trigger | SFX Pair |
|---|---|---|---|---|---|---|---|
| clue-pulse | Clue Pulse | 10 | 15 | 0.7s | screen | clue_found | clue_select |
| sacred-ink | Sacred Ink | 13 | 12 | 1.1s | add | sacred_ink | sacred_ink |
| boundary-ripple | Boundary Ripple | 17 | 12 | 1.4s | screen | boundary_ripple | boundary_ripple |
| relationship-warmth | Relationship Warmth | 12 | 15 | 0.8s | add | relationship_up | relationship_up |
| reward-spark | Reward Spark | 9 | 15 | 0.6s | add | reward | reward |
| capture-silence | Capture Silence | 20 | 10 | 2.0s | screen | capture_silence | capture_silence |

## Deliverables per VFX

Each VFX type includes 3 variants:
1. **sheet.png** — Full frame sheet (frames * 128px wide, 128px tall), RGBA with transparency
2. **fallback.png** — Single static representative frame (128x128) for low-end devices
3. **reduced.png** — Reduced-motion version (2-frame max) for accessibility compliance

## Frame Specifications

- Frame size: 128x128 px
- Anchor: center (64, 64)
- Color palette: INK #2B2521, CLUE_CYAN #72B8C4, INDIGO #3C4668, RAIN_TEAL #46777A, GOLD #F6D36E, WHEAT #D8B767
- No white flash in any VFX (per design contract)
- Max radius <= 80px (1.25 character height at 64px scale)

## File list with SHA-256

| File | SHA-256 | Size |
|---|---|---|
| VIS-VFX-001_UW-UPGRADE-1.0_clue-pulse_sheet.png | d16bfc61631b50bcc0206c8031d699d97f509da93ec9d42eca7f00f172e1e9c6 | 6960 |
| VIS-VFX-001_UW-UPGRADE-1.0_clue-pulse_fallback.png | 6cad332f931b927a1acd6f46cd4cc638e550f5eb8cd9b41e16ec2e10063f8971 | 290 |
| VIS-VFX-001_UW-UPGRADE-1.0_clue-pulse_reduced.png | fcfc4dae14b64257e046bf50ef8d726e14bd4514e4ee3c743429ed3ca7e13484 | 2187 |
| VIS-VFX-001_UW-UPGRADE-1.0_sacred-ink_sheet.png | 5ad5708ffcf78093672da305b103ab21f23061474804b5c7b758d0cc439a0880 | 11220 |
| VIS-VFX-001_UW-UPGRADE-1.0_sacred-ink_fallback.png | 3b86f83a233898d97369bd4673074f39b19262ad04f019f399c3f5f36529b908 | 336 |
| VIS-VFX-001_UW-UPGRADE-1.0_sacred-ink_reduced.png | 11a15787c5908f02eb3405861dbf78d66f7687af3f41db2c0b9261d83ba65c15 | 2612 |
| VIS-VFX-001_UW-UPGRADE-1.0_boundary-ripple_sheet.png | b699468a030d314389c9e8fd232496d259602aaa01a40c98b067b64c2ed424ae | 28378 |
| VIS-VFX-001_UW-UPGRADE-1.0_boundary-ripple_fallback.png | 6935c8975a8f8523cef00283b940727144c94fd8875d1dd6c440bbcbc79c940f | 1437 |
| VIS-VFX-001_UW-UPGRADE-1.0_boundary-ripple_reduced.png | 5338bd1e6fa0089ec499978dcb22ecf94e53e5f114c2e408fb3db713300fe4a0 | 4774 |
| VIS-VFX-001_UW-UPGRADE-1.0_relationship-warmth_sheet.png | fb95fcaf786e6046c9dab91397b0e6a48b2276b13a004961413c974eb576ebae | 7237 |
| VIS-VFX-001_UW-UPGRADE-1.0_relationship-warmth_fallback.png | 05855787d078728a0d1a5c009936ef1344204416512131e3ffb9654968463c5b | 1041 |
| VIS-VFX-001_UW-UPGRADE-1.0_relationship-warmth_reduced.png | fec2b253348836d1ed4871e02282cfe4270ca6a47e4c45304d1e0d51d3eec223 | 2598 |
| VIS-VFX-001_UW-UPGRADE-1.0_reward-spark_sheet.png | 2fe0585dc7745c3f026f68d8182f89535f1210339afceacda42cf6d15b95ea08 | 5733 |
| VIS-VFX-001_UW-UPGRADE-1.0_reward-spark_fallback.png | 5db26b9e3b25ae83b152374846f3cba9a0fecbdcf2d4366d88b2082f038e8541 | 350 |
| VIS-VFX-001_UW-UPGRADE-1.0_reward-spark_reduced.png | da5beabac3e4b92c8f88100f5e55023aba86847c9920f766c281dde768d37164 | 2157 |
| VIS-VFX-001_UW-UPGRADE-1.0_capture-silence_sheet.png | 6715f2f84ce83e7681d102d5c935ad6ad443b207129390aecd003ff0584a093b | 16670 |
| VIS-VFX-001_UW-UPGRADE-1.0_capture-silence_fallback.png | fefa2221c0434efb6677d1b35638f61bde1535f16f38464a40f7d6da3f9bbcfa | 961 |
| VIS-VFX-001_UW-UPGRADE-1.0_capture-silence_reduced.png | 48316ee2aebeb88ccc076599f74266a358cd1fa3301d114e99ae21f012b23d48 | 2978 |
| VIS-VFX-001_UW-UPGRADE-1.0_metadata.json | 0a39bed91848b0fc9e77406ca8286580b1c4a3c5d06fa718819dc7825fa0b8cb | 19570 |

## Manifest

- CSV: `VIS-VFX-001_UW-UPGRADE-1.0_manifest_fragment.csv` — 19 rows (18 assets + 1 metadata)
- All rows: status=received, license=owned, attribution_required=false

## QA Notes

- All VFX frames use RGBA with proper transparency
- No white flash frames in capture-silence (convergence/fade only)
- Reduced-motion variants provided for accessibility (WCAG 2.1 AA)
- Fallback single-frame images provided for low-end rendering
- Metadata JSON includes per-frame rect coordinates for Phaser sprite atlas loading
- trigger_id fields map to game event bus; sfx_id fields map to AUD-SFX-002 sound effects
