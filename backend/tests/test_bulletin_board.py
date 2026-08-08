import copy
import json
from pathlib import Path

from app.scene_activities import public_scene_activities
from app.session import Session


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACTIVITY_ID = "village_square_bulletin_board"


def _session_at_village_square() -> Session:
    session = Session(seed=11, run_id="bulletin-test")
    player = session.state.player.model_copy(
        update={"scene_id": "village_square", "stamina": 100}
    )
    session.state = session.state.model_copy(
        update={"scene_id": "village_square", "player": player, "time_band": "morning"}
    )
    return session


def test_bulletin_board_is_data_driven_and_exposes_three_daily_choices():
    raw = json.loads((PROJECT_ROOT / "data/world/scene_activities.json").read_text(encoding="utf-8"))
    activity = next(item for item in raw["activities"] if item["id"] == ACTIVITY_ID)
    assert activity["repeat"] == "daily"
    assert activity["scene_id"] == "village_square"
    assert [choice["id"] for choice in activity["choices"]] == [
        "pass_message",
        "deliver_supplies",
        "check_records",
    ]

    public = public_scene_activities(PROJECT_ROOT)
    row = next(item for item in public["activities"] if item["id"] == ACTIVITY_ID)
    assert row["choices"][1]["preview"]["consequences"] == []
    assert "field_mint" not in json.dumps(row["choices"][1]["preview"], ensure_ascii=False)
    assert "每天一次" in row["preview"]["benefit_text"]


def test_bulletin_board_choice_rewards_relationship_and_blocks_repeat_without_mutation():
    session = _session_at_village_square()
    before_reject = copy.deepcopy(session.state.model_dump(mode="json"))

    missing_choice = session.player_action(kind="scene_activity", activity_id=ACTIVITY_ID)
    assert missing_choice["ok"] is False
    assert missing_choice["error"] == "activity_choice_required"
    assert session.state.model_dump(mode="json") == before_reject

    completed = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="pass_message",
    )
    assert completed["ok"] is True
    result = completed["activity_result"]
    assert result["activity_choice"]["id"] == "pass_message"
    assert result["relationship_changes"] == [
        {"npc_id": "alice", "field": "trust", "before": 0, "after": 1, "delta": 1},
        {"npc_id": "eugeo", "field": "affinity", "before": 0, "after": 1, "delta": 1},
    ]
    assert session.state.flags[f"activity_day.{ACTIVITY_ID}"] == 1
    assert session.state.flags["bulletin_pass_message_done"] == 1
    assert session.state.player.stamina == 97

    after_complete = copy.deepcopy(session.state.model_dump(mode="json"))
    repeated = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="check_records",
    )
    assert repeated["ok"] is False
    assert repeated["error"] == "already_done_today"
    assert session.state.model_dump(mode="json") == after_complete


def test_bulletin_board_refreshes_next_day_and_can_grant_material_without_touching_story_node():
    session = _session_at_village_square()
    story_node_before = session.state.story_node_id
    first = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="deliver_supplies",
    )
    assert first["ok"] is True
    assert first["activity_result"]["item_changes"]["field_mint"] == {
        "before": 0,
        "after": 1,
        "delta": 1,
    }
    assert session.state.inventory == {"field_mint": 1}

    session.state = session.state.model_copy(update={"day": 2, "time_band": "afternoon"})
    second = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="check_records",
    )
    assert second["ok"] is True
    assert second["activity_result"]["activity_choice"]["id"] == "check_records"
    assert session.state.flags[f"activity_day.{ACTIVITY_ID}"] == 2
    assert session.state.relationships["eugeo"].trust == 1
    assert session.state.relationships["alice"].affinity == 1
    assert session.state.inventory == {"field_mint": 1}
    assert session.state.story_node_id == story_node_before


def test_existing_village_square_activity_remains_available_after_bulletin_slice():
    session = _session_at_village_square()
    result = session.player_action(
        kind="scene_activity",
        activity_id="village_square_listen",
    )
    assert result["ok"] is True
    assert result["activity_result"]["activity"]["id"] == "village_square_listen"
    assert session.state.flags["heard_village_rumor"] == 1
