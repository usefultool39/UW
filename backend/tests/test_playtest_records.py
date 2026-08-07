from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "check_playtest_round.py"
spec = importlib.util.spec_from_file_location("check_playtest_round", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _write_record(path: Path, *, player_id: str, status: str, complete: bool) -> None:
    values = {
        "status": status,
        "player_id": player_id,
        "session_date": "2026-08-06" if complete else "",
        "device_input": "Mac + mouse" if complete else "",
        "prior_experience": "farming RPG" if complete else "",
        "recording_file": "private-recording.mp4",
        "consent_recorded": "yes" if complete else "",
        "first_effective_interaction_seconds": "32" if complete else "",
        "understood_day_goal": "yes" if complete else "",
        "named_action_cost": "partial" if complete else "",
        "named_action_benefit": "yes" if complete else "",
        "bypassed_day_gate": "no" if complete else "",
        "continue_interest": "yes" if complete else "",
        "completed_precapture_route": "yes" if complete else "",
        "reached_alice_captured": "yes" if complete else "",
        "post_capture_progress_blocked": "yes" if complete else "",
        "recognized_choice_echo": "yes" if complete else "",
        "understood_capture_reason": "yes" if complete else "",
        "hint_count": "0" if complete else "",
        "total_session_minutes": "42" if complete else "",
        "highest_frequency_blocker": "none observed" if complete else "",
        "endpoint_explanation": "Alice crossed the boundary while helping the injured person." if complete else "",
    }
    path.write_text("\n".join(f"- {key}: {value}" for key, value in values.items()), encoding="utf-8")


def test_repository_templates_remain_pending_human_run():
    result = module.evaluate_round()

    assert result["status"] == "pending-human-run"
    assert result["complete_count"] == 0
    assert result["invalid_count"] == 0


def test_completed_human_records_are_only_accepted_with_required_evidence(tmp_path):
    for player_id, name in zip(module.PLAYER_IDS, module.RECORD_NAMES):
        _write_record(tmp_path / name, player_id=player_id, status=module.COMPLETE_STATUS, complete=True)

    result = module.evaluate_round(tmp_path)

    assert result["status"] == "received-human-run"
    assert result["complete_count"] == 3
    assert result["invalid_count"] == 0


def test_incomplete_record_cannot_claim_received_human_run(tmp_path):
    for player_id, name in zip(module.PLAYER_IDS, module.RECORD_NAMES):
        _write_record(tmp_path / name, player_id=player_id, status=module.PENDING_STATUS, complete=False)
    _write_record(
        tmp_path / module.RECORD_NAMES[0],
        player_id=module.PLAYER_IDS[0],
        status=module.COMPLETE_STATUS,
        complete=False,
    )

    result = module.evaluate_round(tmp_path)

    assert result["status"] == "pending-human-run"
    assert result["invalid_count"] == 1
    assert any("required" in error or "must be" in error for error in result["records"][0]["errors"])


def test_day_one_only_record_cannot_satisfy_full_precapture_playtest(tmp_path):
    for player_id, name in zip(module.PLAYER_IDS, module.RECORD_NAMES):
        _write_record(tmp_path / name, player_id=player_id, status=module.COMPLETE_STATUS, complete=True)

    first_record = tmp_path / module.RECORD_NAMES[0]
    text = first_record.read_text(encoding="utf-8").replace(
        "- completed_precapture_route: yes",
        "- completed_precapture_route: no",
    )
    first_record.write_text(text, encoding="utf-8")

    result = module.evaluate_round(tmp_path)

    assert result["status"] == "pending-human-run"
    assert result["invalid_count"] == 1
    assert any("completed_precapture_route" in error for error in result["records"][0]["errors"])
