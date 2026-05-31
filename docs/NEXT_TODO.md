# Border Echo Next TODO

Updated: 2026-06-01

This file is the handoff list after the May 30 automation watch cycle. The current final checkpoint is intended to stay stable first, then continue toward a fuller playable game.

## Verified Checkpoint

- Main branch is synced to GitHub through the Week 07 anomaly convergence work.
- Day 46 shared anomaly convergence now has E2E smoke coverage.
- Same-scene NPC intent actions are exposed in the interaction panel, so a quest tracker instruction that says "go to this scene and respond" can be completed through UI.

## Next Highest-Value Tasks

- [x] Run one manual playtest from Day 1 to Day 46 and record friction points in `docs/PLAYTEST.md`. Day1-3 and Day46 baseline passed; Day46 name cleanup verified.
- [x] Clarify and verify the Day 4-6 debrief path separately from Day 46 convergence; keep future notes explicit as `Day 4-6` vs `Day 46`.
- [x] Unify Day 4-6 route copy so the quest target, NPC intent, and event location all describe the same destination (`村西书库` vs `村西书道`).
- [x] Add the first Ailin character-depth pass to Day 46 convergence: inscription markers, sister-letter touchpoint, and her safety-first judgment.
- [x] Clean up remaining player-visible old-name copy in Day39-45 Month02 order / quiet route text (`艾丽丝` -> `艾琳`) without changing internal `alice` ids or flags.
- [x] Add a Day1 Ailin character-depth pass when the player tells her the old boundary record: Lina practice page, inscription marker, and daily-safety concern.
- [x] Add a Day2 Ailin character-depth pass for the shared forest anomaly path: inscription marker, safety distance, and daily-boundary judgment.
- [x] Add one full E2E route for Day39 quiet branch before Day46 convergence, covering NPC intent, UI entry, result panel, and completion flags.
- [ ] Tonight focus: make one core character feel stronger before adding more systems. Recommended first pass: Ailin across Day1 library, Day2 anomaly, Day 4-6 debrief, and Day 46 convergence.
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
