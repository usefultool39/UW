# UW 素材现状审计

- **当前返工交接**：[MATERIALS_REWORK_HANDOFF_20260807.md](MATERIALS_REWORK_HANDOFF_20260807.md)
- **最新逐包快照**：[ASSET_HANDOFF_SNAPSHOT_20260807.md](ASSET_HANDOFF_SNAPSHOT_20260807.md)
- **返工版本规则**：失败的 v002/v003 保留审计；五个返工包统一交付 v004；素材智能体不修改正式台账或 runtime。

> **最新权威修订**：v003 五包已收到但全部 `changes_requested`；随后收件区出现地图/环境 v004 与角色 v005。它们同样没有通过 active v004 contract，不能进入 runtime。稳定门禁快照为 `check_materials.py = 7 errors`、active v004 runtime contract `= 52 issues`；v002/v003 评审数字仍保留为历史技术证据，最新逐包事实以 [ASSET_HANDOFF_SNAPSHOT_20260807.md](ASSET_HANDOFF_SNAPSHOT_20260807.md) 为准。

## 2026-08-07 Runtime/story checkpoint

- Pre-Capture story readiness is now `ready`: 31 combined events, 10 marked key nodes, four acts (`act_0` to `act_3`), fixed endpoint `alice_captured`, and 46 detected cross-node echoes. The 21 legacy events remain compatibility content.
- Overall readiness is `materials=pending, story=ready`. Narrative inputs pass, but first-phase runtime requests are now included in the materials gate.
- An ungoverned v002 batch appeared in `materials/inbox`, followed by a v003 delivery snapshot: `VIS-MAP-001`, `VIS-CHR-001` to `003`, `VIS-ENV-001`, `AUD-BGM-002`, `AUD-BGM-003`, and `AUD-AMB-002`. Both versions remain received/changes-requested evidence, not accepted assets.
- All eight requests are now `changes_requested`. The stable v003 check reports 7 unregistered intermediate-file errors; v003 files have request fragments but no formal manifest merge, and no file was promoted into runtime.
- The v002 technical review recorded 28 issues. The v003 technical review recorded 76 schema/path/visual-delivery issues: map layers/data, character frame metadata, environment scene mapping, audio naming/metadata/measurement, and intermediate-file registration. The active contract now targets non-destructive v004 replacements; the rework reviews retain v002/v003 evidence. The gate is part of `scripts/quality.sh`.
- The runtime asset gate now decodes 8-bit PNG scanlines and requires both visible and actual transparent pixels; an opaque RGBA sheet with a baked checkerboard is not accepted. It also validates OGG page framing rather than accepting an arbitrary file by extension. The focused runtime asset-spec tests pass `8` cases, including the v004 contract lock.
- `check_materials.py` now performs the inverse runtime audit: every file in `frontend/public/assets/runtime` must be registered, approved for runtime, reviewer-stamped, and hash-matched. Current runtime files have no orphan paths; the focused registry suite passes `5` cases.
- Engineering QA baseline remains healthy: backend `330 passed` with one existing Starlette/httpx deprecation warning, frontend unit `16 passed`, production build passed, and targeted Pre-Capture Playwright `2/2` passed on isolated ports. The previous fresh-port full-suite `22/22` is retained as historical evidence; a new full-suite attempt timed out in the legacy field smoke and is not claimed as passed. The materials gate remains intentionally failing until corrected v004 deliveries pass the full chain.

- Audit date: 2026-08-07
- Scope: generated visual/audio materials, sidecars, manifest, runtime status, and remaining production plan
- Authority: this document is the current snapshot; older audit documents remain historical evidence

## 中文速览

- 已生成并完成技术复核：视觉方向板、三组关键图、三名核心角色的双表情肖像样张、12 枚 UI 图标、村庄 BGM 两版、细雨环境声 v002 两版。
- 已有素材只能算候选或内测素材：关键图不能替代可走地图，肖像不能替代角色 Sprite，图标与音频也没有覆盖完整游戏状态。
- 尚未生成：卢利特村可走地图、核心角色与 NPC Sprite、互动动作、六场景背景、完整图标、VFX、第二批 BGM/环境声/SFX、抓捕终点关键图和整合骑士到场素材。
- 当前故事台账已通过 Pre-Capture authored contract：四幕、10 个关键节点、唯一抓捕终点和 46 次跨节点回响均已存在；素材台账仍 pending，不能把故事通过写成素材完成。
- 战斗动作、宣传素材和角色配音继续延后；先完成爱丽丝被带走前的可玩垂直切片。

## Executive Result

- Technical registry: pending. The v003 snapshot reports 7 unregistered intermediate-file errors; v003 sources and runtime hashes are not formally integrated. The active v004 contract is waiting for corrected delivery.
- Pre-Capture story readiness: ready. The authored route has four acts, 10 marked key nodes, one fixed capture endpoint, and 46 detected cross-node echoes.
- Asset production readiness: changes requested. Received map/character/scene/audio files fail one or more production gates and remain inbox-only.
- Runtime claim: the existing runtime candidates must remain treated as prototype integrations. A passing manifest check is not visual approval or a complete game-art pass.

## Incoming v002 Batch Review

| Requests | Status | Blocking findings | Rework record |
|---|---|---|---|
| `VIS-MAP-001` | `changes_requested` | 2752x1536 RGB overview; baked text; no grid/tile/collision/occlusion/interaction data; no sidecar/manifest | `materials/inbox/visual/world/REWORK_VIS-MAP-001_20260807.md` |
| `VIS-CHR-001` to `003` | `changes_requested` | 1024x1024 single-pose RGB files; baked checkerboard; no alpha, frame sequence, anchor, or frame manifest | `materials/inbox/visual/characters/REWORK_VIS-CHR-001-003_20260807.md` |
| `VIS-ENV-001` | `changes_requested` | 2752x1536 instead of 1920x1080; no sidecar/manifest; may only be an activity/transition background | `materials/inbox/visual/environments/REWORK_VIS-ENV-001_20260807.md` |
| `AUD-BGM-002` and `003` | `changes_requested` | 32-44 s, below requested ranges; invalid `-70 LUFS` reports; no sidecar/audio.meta/manifest | `materials/inbox/audio/bgm/REWORK_AUD-BGM-002-003_20260807.md` |
| `AUD-AMB-002` | `changes_requested` | 17/35 s variants are not matched; invalid loudness/peak report; no sidecar/audio.meta/manifest | `materials/inbox/audio/ambience/REWORK_AUD-AMB-002_20260807.md` |

No review memo is an asset sidecar and none may be used to satisfy provenance. The delivering agent must provide the real sidecars and rights data.

## Delivered And Reviewed

### `REF-STYLE-001`

- Status: approved for direction only.
- A is the primary village and opening direction, B supports archive/library presentation, and C is reserved for the abnormal boundary state.
- It is not a final asset pack and must not be used as a license to copy any existing game, anime, character, interface, or composition.

### `VIS-KA-001`

- Status: candidate; technical gate passed for v002.
- v002 village, library, and boundary desktop/mobile files are real PNG masters at `2560x1440` and `1440x1920`.
- The files are useful for opening, library, boundary, and exception-state presentation. The village key art is the only one currently registered as a runtime candidate.
- Missing: a navigable Rulid map, walkable-layer source, building/terrain layers, collision data, and a capture-endpoint scene.
- Review note: the current key art is painterly and relatively detailed. It cannot replace readable map tiles, small sprites, animation, or interaction feedback for a mainstream 2D RPG.

### `VIS-POR-001`

- Status: candidate; technical gate passed for v002 masters and 256px derivatives.
- v002 portrait files are `1024x1024` RGBA PNGs with transparent output; the derivatives are `256x256`.
- The set currently covers two expressions each for Alice, Eugeo, and the player-role portrait. It is not the full expression library.
- Review note: v001 Kirito files remain historical and must not be mixed into the current player-role set without the canon/display-name decision. The current portraits still need a consistency pass for line weight, lighting, silhouette, and in-game scale.
- Missing: five expressions per supporting character, capture-scene expressions, and the agreed portrait-to-character identity mapping.

### `VIS-UI-001`

- Status: prototype candidate; technically usable.
- Twelve icon IDs have SVG and PNG variants at 24/48/96px and are suitable for HUD, activity previews, results, and relationship/memory feedback.
- Review note: the sheet is a presentation reference, not the runtime atlas. Existing CSS and fallback icons still carry part of the player experience.
- Missing: the remaining 20 icons, state variants, accessibility checks at 24px, and a complete icon-to-data registry.

### `AUD-BGM-001`

- Status: internal-test candidate.
- A/B WAV masters and OGG runtime files are present, stereo, `48kHz`, and approximately 91s/83s.
- Suitable for village morning and library/recording states after runtime loop and ducking verification.
- Missing: suspense, relationship, and later chapter loops.

### `AUD-AMB-001`

- Status: v002 internal-test candidate; v001 remains changes requested and is not a fallback.
- v002 A/B WAV masters and OGG runtime files are present, stereo, `48kHz`, and approximately 114s/104s. The v002 sidecars and audio metadata are registered.
- Suitable for village rain and quieter boundary-stream states after in-game loop and weather-transition verification.
- Missing: forest normal/silent variants and event-specific ambience transitions.

## Not Generated

The following list is the first-phase production queue. Items called out in the incoming-v002 table are now `changes_requested`; the remaining items are still `deferred` and undelivered.

### Pre-Capture vertical slice blockers

- `VIS-MAP-001`: navigable Rulid village map with separated layers.
- `VIS-CHR-001` to `VIS-CHR-003`: player, Alice, and Eugeo four-direction map Sprites with idle/walk/interact.
- `VIS-CHR-004`: supporting village NPC map Sprites.
- `VIS-ENV-001`: six activity/location backgrounds.
- `VIS-VFX-001`: sacred-art, boundary, silence-line, relationship, reward, and lock feedback effects.
- `AUD-BGM-002`: boundary investigation suspense loop.
- `AUD-BGM-003`: relationship and daily-schedule warm loop.
- `AUD-AMB-002`: forest normal/silent-line ambience pair.
- `AUD-SFX-001`: UI, clue, reward, relationship, memory, promise, and day-transition SFX.
- `AUD-SFX-002`: footsteps, page/record actions, sacred-art, boundary, and activity SFX.

### Completeness and polish

- `VIS-POR-002`: full six-character portrait package with five approved expression states each.
- `VIS-UI-002`: complete 32-icon package.
- `VIS-MARKETING-001`: store/marketing banner; correctly deferred until blind testing.
- `AUD-VOICE-001`: temporary voice samples; correctly deferred until the narrative and voice bible are stable.

## Newly Registered Completeness Requests

The gaps found by this audit now have request IDs. They remain `P1/deferred`: registration records future work, but does not mean generation or acceptance has started.

- `VIS-KA-002`: Pre-Capture capture scene key art, including desktop/mobile composition and text-safe space.
- `VIS-CHR-005`: Integrity Knight arrival silhouettes/Sprites and capture-scene poses; not a combat-unit package.
- `VIS-ANIM-001`: reading, writing, handing an item, boundary examination, concern, and farewell interaction animations.
- `VIS-TILE-001`: tile atlas, object/prop sheets, layer manifest, collision/walkability data, occluder rules, and activity props.

Activate these only after the relevant event cards, camera framing, character scale, and map specification are frozen. The earlier `VIS-MAP-*`, `VIS-CHR-001` to `004`, `VIS-ENV-*`, `VIS-VFX-*`, and `AUD-*` requests remain the first production queue for the playable slice.

## Future Production Plan

### 0.5.0-pre-capture

- Keep the reviewed canon story package locked at the N01-N10 `story=ready` contract; do not extend beyond the capture endpoint.
- Generate and review `VIS-MAP-001`, core Sprites, activity backgrounds, boundary VFX, and the two missing music/ambience layers.
- Implement the capture endpoint presentation and verify that all player choices converge on the same Alice-captured event.
- Keep procedural map, token, and audio fallbacks until the new assets pass runtime checks.

### 0.6.x life-sim and presentation maturity

- Complete portraits, icon coverage, map props, interaction animation, NPC schedules, weather transitions, and event feedback.
- Add real runtime tests for desktop/mobile safe areas, asset loading, loops, ducking, and 24px icon readability.
- Conduct the first three-player blind test before large-scale asset expansion.

### 0.7.x combat prototype

- Design the combat rules first, then generate idle, walk, attack, skill/cast, hit, recover, defeat/escape, and direction-specific animation sets.
- Do not generate or integrate combat assets into the current Pre-Capture slice as if combat were already implemented.

### 0.8.x and later

- Expand chapter maps, supporting character packages, equipment, enemy sets, VFX, BGM, SFX, and voice only after each chapter has its own playable loop and QA evidence.

## Next Acceptance Gate

1. Receive the missing registered visual/audio batches and keep them in `materials/inbox`.
2. Verify every binary against its sidecar, dimensions, alpha, loop metadata, license, and manifest hash.
3. Review visual consistency against A/B/C direction and reject painterly key art when it is being used as a substitute for map/Sprite assets.
4. Integrate only approved candidates into runtime and capture desktop/mobile screenshots.
5. Complete the authored Pre-Capture story gate and three-player blind test before declaring the first full slice complete.
