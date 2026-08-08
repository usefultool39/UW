from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_release_gate_is_fail_closed_for_materials_and_human_playtest():
    source = (ROOT / "scripts/release.sh").read_text(encoding="utf-8")
    assert 'check_precapture_readiness.py" --require-complete' in source
    assert 'check_playtest_round.py" --require-complete' in source
