# VIS-CHR-001/002/003 down sprite matte-clean candidate

- status: `sample_candidate`
- purpose: candidate-only technical review; **not runtime-approved**
- source: derived from existing candidate sprite sheets with local alpha/matte cleanup
- runtime: prohibited
- direction: down only

## Technical checks

- Cell size: 64x96
- Sheet size: 768x96
- Anchor: (32,94)
- Anchor alpha: 36/36 pass
- Processing: remove low-alpha haze and low-chroma semi-transparent matte pixels; preserve RGBA PNG

## Files and SHA-256

- `VIS-CHR-001_sprite_sheet_down_matte_candidate.png`: `073b47fc4a11ceb357acf58da6fcefd0b46360b7e3aa1c5ae30982b252b79fe8`
- `VIS-CHR-002_sprite_sheet_down_matte_candidate.png`: `a5a616933898eb13feabd8fed29c59137da59e976a1f812c1eb906da9b8625fd`
- `VIS-CHR-003_sprite_sheet_down_matte_candidate.png`: `87116749f1134746703debc2ae262854894d507366b0ce8736ffe331898a2780`

## Known issues requiring human review

- These are still AI-generated independent frames; action continuity, proportions, pose interpolation and visual consistency are not approved.
- Only down direction exists; left/right/up are not supplied.
- Candidate-only matte cleanup may remove low-contrast edge pixels; inspect on dark and light backgrounds.
- No MANIFEST runtime row is added and no runtime mapping is changed.
- This sidecar does not make any rights or canon claim.
