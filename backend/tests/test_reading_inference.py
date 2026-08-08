import json
from pathlib import Path

import pytest

from app.activity_engine import ActivityValidationError, plan_scene_activity
from app.models import PlayerState
from app.scene_activities import public_scene_activities


ROOT = Path(__file__).resolve().parents[2]
ACTIVITY_DOCUMENT = json.loads((ROOT / "data/world/scene_activities.json").read_text())
ACTIVITIES = ACTIVITY_DOCUMENT["activities"]
READING = next(item for item in ACTIVITIES if item["id"] == "church_read_sacred_arts")


def test_reading_chain_is_authored_as_three_ordered_steps():
    chain = READING["reading_chain"]
    assert [step["id"] for step in chain["steps"]] == ["phenomenon", "rule", "conclusion"]
    assert len(chain["paths"]) == 3
    choice_ids = {choice["id"] for choice in READING["choices"]}
    for path in chain["paths"]:
        assert len(path["steps"]) == 3
        assert path["choice_id"] in choice_ids
        assert path["steps"][2] == path["choice_id"]


def test_each_correct_reading_path_uses_existing_atomic_activity_effects():
    initial_flags = {"existing_memory": 1}
    player = PlayerState(scene_id="reading_hall", stamina=20)
    for path in READING["reading_chain"]["paths"]:
        plan = plan_scene_activity(
            READING,
            activity_id=READING["id"],
            activity_choice=path["choice_id"],
            mini_game_result={
                "choice_id": path["choice_id"],
                "path_id": path["choice_id"],
                "inference_chain": path["steps"],
            },
            scene_id="reading_hall",
            time_band="morning",
            day=1,
            flags=initial_flags,
            player=player,
        )
        assert plan.next_flags["studied_sacred_arts"] == 1
        assert plan.next_flags["prologue_reading_done"] == 1
        assert plan.next_flags[f"activity_done.{READING['id']}"] == 1
        assert initial_flags == {"existing_memory": 1}
        assert player.stamina == 20


def test_reading_rejects_a_forged_path_without_mutating_inputs():
    initial_flags = {"existing_memory": 1}
    player = PlayerState(scene_id="reading_hall", stamina=20)
    with pytest.raises(ActivityValidationError) as error:
        plan_scene_activity(
            READING,
            activity_id=READING["id"],
            activity_choice="trace_silence",
            mini_game_result={
                "choice_id": "trace_silence",
                "path_id": "trace_silence",
                "inference_chain": ["bird_silence", "north_law", "trace_silence"],
            },
            scene_id="reading_hall",
            time_band="morning",
            day=1,
            flags=initial_flags,
            player=player,
        )
    assert error.value.code == "mini_game_result_mismatch"
    assert initial_flags == {"existing_memory": 1}
    assert player.stamina == 20


def test_invalid_choice_is_rejected_without_a_partial_plan():
    initial_flags = {"existing_memory": 1}
    player = PlayerState(scene_id="reading_hall", stamina=20)
    with pytest.raises(ActivityValidationError) as error:
        plan_scene_activity(
            READING,
            activity_id=READING["id"],
            activity_choice="not_a_reading_conclusion",
            scene_id="reading_hall",
            time_band="morning",
            day=1,
            flags=initial_flags,
            player=player,
        )
    assert error.value.code == "unknown_activity_choice"
    assert initial_flags == {"existing_memory": 1}
    assert player.stamina == 20


def test_public_reading_activity_exposes_sanitized_three_step_chain():
    public = public_scene_activities(ROOT)
    activity = next(item for item in public["activities"] if item["id"] == "church_read_sacred_arts")
    chain = activity["reading_chain"]
    assert [step["id"] for step in chain["steps"]] == ["phenomenon", "rule", "conclusion"]
    assert all("effects" not in option for step in chain["steps"] for option in step["options"])
    assert {path["choice_id"] for path in chain["paths"]} == {"trace_silence", "map_boundary", "quiet_observe"}
