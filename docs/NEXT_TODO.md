# Border Echo Next TODO

Updated: 2026-05-30

This file is the handoff list after the May 30 automation watch cycle. The current final checkpoint is intended to stay stable first, then continue toward a fuller playable game.

## Verified Checkpoint

- Main branch is synced to GitHub through the Week 07 anomaly convergence work.
- Day 46 shared anomaly convergence now has E2E smoke coverage.
- Same-scene NPC intent actions are exposed in the interaction panel, so a quest tracker instruction that says "go to this scene and respond" can be completed through UI.

## Next Highest-Value Tasks

- [ ] Run one manual playtest from Day 1 to Day 46 and record friction points in `docs/PLAYTEST.md`.
- [ ] Add at least one full E2E route for Day 39 order, expedition, or quiet branch before the Day 46 convergence.
- [ ] Review the first-screen visual hierarchy: objective text, available actions, map readability, and NPC intent visibility.
- [ ] Improve player-facing text cleanup for any remaining development wording, internal ids, or garbled fallback copy.
- [ ] Add a save/load compatibility check after Month 02 flags and `required_any_flags` were introduced.
- [ ] Expand Week 07 after convergence into a concrete follow-up objective instead of ending at a shared signal.
- [ ] Build a small visual/audio pass for the reading hall, north gate, village square, and home hearth so the core loop feels less prototype-like.
- [ ] Keep CCL on bounded tasks only: read-only audits, content list generation, low-risk test suggestions, and report writing.

## Guardrails For Next Session

- Do not let CCL commit, push, or perform broad architecture rewrites.
- Keep each change small enough to verify with focused backend tests, frontend build, and targeted E2E.
- Prefer fixing player-visible flow breaks over adding more content on top of uncertain interaction paths.
- Record automation logs and reports under `runs/automation`.
