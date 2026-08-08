import copy
import json
from pathlib import Path

from app.activity_engine import plan_scene_activity
from app.item_engine import find_item
from app.models import PlayerState
from app.scene_activities import public_scene_activities
from app.session import Session
from app.world_map import is_blocked_zone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACTIVITY_ID = "south_lake_fishing"


def _lake_session(run_id: str) -> Session:
    """Simulate a chapter-authorized lake scene for settlement contract tests.

    The production map remains locked; this only exercises the existing activity
    engine after a future chapter has legitimately placed the player in the scene.
    """
    session = Session(run_id=run_id)
    player = session.state.player.model_copy(
        update={"scene_id": "south_lake_gate", "stamina": 100}
    )
    session.state = session.state.model_copy(
        update={
            "scene_id": "south_lake_gate",
            "player": player,
            "time_band": "morning",
            "weather": "mist",
        }
    )
    return session


def test_south_lake_fishing_is_authored_as_daily_qte_with_two_fish_choices():
    raw = json.loads((PROJECT_ROOT / "data/world/scene_activities.json").read_text(encoding="utf-8"))
    activity = next(item for item in raw["activities"] if item["id"] == ACTIVITY_ID)
    assert activity["scene_id"] == "south_lake_gate"
    assert activity["poi_id"] == "ix_south_lake_gate"
    assert activity["interaction_kind"] == "fishing_qte"
    assert activity["repeat"] == "daily"
    assert [choice["id"] for choice in activity["choices"]] == [
        "catch_common_fish",
        "catch_rare_fish",
    ]
    assert activity["choices"][0]["effects"]["item_deltas"] == {"south_lake_common_fish": 1}
    assert activity["choices"][1]["effects"]["item_deltas"] == {"south_lake_rare_fish": 1}

    assert find_item(PROJECT_ROOT, "south_lake_common_fish")["type"] == "material"
    assert find_item(PROJECT_ROOT, "south_lake_rare_fish")["type"] == "material"

    public = public_scene_activities(PROJECT_ROOT)
    row = next(item for item in public["activities"] if item["id"] == ACTIVITY_ID)
    assert [choice["id"] for choice in row["choices"]] == [
        "catch_common_fish",
        "catch_rare_fish",
    ]
    assert "每天一次" in row["preview"]["benefit_text"]


def test_south_lake_fishing_settles_inventory_atomically_and_refreshes_next_day():
    session = _lake_session("south-lake-fishing-test")
    before_reject = copy.deepcopy(session.state.model_dump(mode="json"))

    missing_choice = session.player_action(kind="scene_activity", activity_id=ACTIVITY_ID)
    assert missing_choice["ok"] is False
    assert missing_choice["error"] == "activity_choice_required"
    assert session.state.model_dump(mode="json") == before_reject

    common = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="catch_common_fish",
        mini_game_result={"choice_id": "catch_common_fish", "fish_id": "south_lake_common_fish", "fish_rarity": "common", "timing_ms": 420},
    )
    assert common["ok"] is True
    assert common["activity_result"]["item_changes"] == {
        "south_lake_common_fish": {"before": 0, "after": 1, "delta": 1}
    }
    assert common["activity_result"]["inventory"] == {"south_lake_common_fish": 1}
    assert session.state.inventory == {"south_lake_common_fish": 1}

    after_common = copy.deepcopy(session.state.model_dump(mode="json"))
    repeated = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="catch_rare_fish",
        mini_game_result={"choice_id": "catch_rare_fish", "fish_id": "south_lake_rare_fish", "fish_rarity": "rare", "timing_ms": 120},
    )
    assert repeated["ok"] is False
    assert repeated["error"] == "already_done_today"
    assert session.state.model_dump(mode="json") == after_common

    session.state = session.state.model_copy(update={"day": 2, "time_band": "afternoon"})
    rare = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="catch_rare_fish",
        mini_game_result={"choice_id": "catch_rare_fish", "fish_id": "south_lake_rare_fish", "fish_rarity": "rare", "timing_ms": 120},
    )
    assert rare["ok"] is True
    assert rare["activity_result"]["activity_choice"]["id"] == "catch_rare_fish"
    assert rare["activity_result"]["item_changes"] == {
        "south_lake_rare_fish": {"before": 0, "after": 1, "delta": 1}
    }
    assert session.state.inventory == {
        "south_lake_common_fish": 1,
        "south_lake_rare_fish": 1,
    }


def test_south_lake_fishing_activity_plan_keeps_choice_effects_separate():
    raw = json.loads((PROJECT_ROOT / "data/world/scene_activities.json").read_text(encoding="utf-8"))
    activity = next(item for item in raw["activities"] if item["id"] == ACTIVITY_ID)
    plan = plan_scene_activity(
        activity,
        activity_id=ACTIVITY_ID,
        activity_choice="catch_rare_fish",
        mini_game_result={"choice_id": "catch_rare_fish", "fish_id": "south_lake_rare_fish", "fish_rarity": "rare", "timing_ms": 120},
        scene_id="south_lake_gate",
        time_band="morning",
        day=1,
        flags={},
        player=PlayerState(scene_id="south_lake_gate", stamina=10),
        inventory={},
        weather="mist",
    )
    assert plan.next_inventory == {"south_lake_rare_fish": 1}
    assert plan.item_changes["south_lake_rare_fish"]["delta"] == 1


def test_south_lake_fishing_rejects_a_forged_rare_result_without_mutating_state():
    session = _lake_session("south-lake-fishing-forgery-test")
    session._refresh_runtime_views()
    before = copy.deepcopy(session.state.model_dump(mode="json"))

    rejected = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="catch_rare_fish",
        mini_game_result={"choice_id": "catch_rare_fish", "fish_id": "south_lake_rare_fish", "fish_rarity": "rare", "timing_ms": 420},
    )

    assert rejected["ok"] is False
    assert rejected["error"] == "mini_game_result_mismatch"
    assert session.state.model_dump(mode="json") == before


def test_south_lake_gate_stays_locked_until_planned_chapter_three_unlock():
    raw = json.loads((PROJECT_ROOT / "data/world/world_map.json").read_text(encoding="utf-8"))
    zone = next(item for item in raw["scene_zones"] if item["scene_id"] == "south_lake_gate")
    assert zone["regionType"] == "locked"
    assert zone["requirements"] == {"planned_unlock": "chapter_03"}
    assert is_blocked_zone(zone) is True
    assert zone["transfers"] == [{"kind": "planned", "label": "渡口修复后开放"}]

    session = Session(run_id="south-lake-gate-lock-test")
    before = copy.deepcopy(session.state.model_dump(mode="json"))
    rejected = session.player_action(
        kind="move_map",
        map_id="novice_open",
        tile_x=35,
        tile_y=49,
    )
    assert rejected["ok"] is False
    assert rejected["error"] == "zone_locked"
    assert session.state.model_dump(mode="json") == before
