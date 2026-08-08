from __future__ import annotations

import copy
import json
from pathlib import Path

from app.session import Session


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACTIVITIES_PATH = PROJECT_ROOT / "data/world/scene_activities.json"
MAP_PATH = PROJECT_ROOT / "data/world/world_map.json"
ACTIVITY_ID = "home_hearth_cooking"


def _session(inventory: dict[str, int] | None = None) -> Session:
    session = Session(seed=41, run_id="home-cooking-test")
    player = session.state.player.model_copy(
        update={"scene_id": "home_hearth", "stamina": 40}
    )
    session.state = session.state.model_copy(
        update={
            "scene_id": "home_hearth",
            "time_band": "evening",
            "player": player,
            "inventory": inventory or {},
        }
    )
    return session


def _activity() -> dict:
    raw = json.loads(ACTIVITIES_PATH.read_text(encoding="utf-8"))
    return next(item for item in raw["activities"] if item["id"] == ACTIVITY_ID)


def test_home_hearth_cooking_is_reachable_from_ix_home_bed_and_keeps_meal_compatible():
    raw = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    poi = next(item for item in raw["pois"] if item["id"] == "ix_home_bed")
    activity_ids = [action.get("activity_id") for action in poi["actions"]]
    assert "home_hearth_cooking" in activity_ids
    assert "home_evening_meal" in activity_ids

    activity = _activity()
    assert activity["scene_id"] == "home_hearth"
    assert activity["poi_id"] == "ix_home_bed"
    assert activity["interaction_kind"] == "cooking_qte"
    assert activity["repeat"] == "free"
    assert {choice["id"] for choice in activity["choices"]} == {
        "cook_herb_soup_normal",
        "cook_herb_soup_perfect",
        "cook_dried_rations_common_normal",
        "cook_dried_rations_common_perfect",
        "cook_dried_rations_rare_normal",
        "cook_dried_rations_rare_perfect",
    }


def test_perfect_herb_soup_consumes_field_mint_and_doubles_output_atomically():
    session = _session({"field_mint": 1})

    result = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="cook_herb_soup_perfect",
        mini_game_result={"choice_id": "cook_herb_soup_perfect", "tier": "perfect", "cuttingHits": 5, "heatPower": 75},
    )

    assert result["ok"] is True
    assert result["activity_result"]["activity_choice"]["id"] == "cook_herb_soup_perfect"
    assert result["activity_result"]["item_changes"] == {
        "field_mint": {"before": 1, "after": 0, "delta": -1},
        "herb_soup": {"before": 0, "after": 2, "delta": 2},
    }
    assert session.state.inventory == {"field_mint": 0, "herb_soup": 2}
    assert session.state.player.stamina == 38


def test_normal_fish_cooking_produces_dried_rations_from_either_defined_fish():
    session = _session({"south_lake_common_fish": 1})

    result = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="cook_dried_rations_common_normal",
        mini_game_result={"choice_id": "cook_dried_rations_common_normal", "tier": "normal", "cuttingHits": 4, "heatPower": 55},
    )

    assert result["ok"] is True
    assert result["activity_result"]["item_changes"] == {
        "south_lake_common_fish": {"before": 1, "after": 0, "delta": -1},
        "dried_rations": {"before": 0, "after": 1, "delta": 1},
    }
    assert session.state.inventory == {"south_lake_common_fish": 0, "dried_rations": 1}

    rare_session = _session({"south_lake_rare_fish": 1})
    rare_result = rare_session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="cook_dried_rations_rare_perfect",
        mini_game_result={"choice_id": "cook_dried_rations_rare_perfect", "tier": "perfect", "cuttingHits": 5, "heatPower": 70},
    )
    assert rare_result["ok"] is True
    assert rare_session.state.inventory == {"south_lake_rare_fish": 0, "dried_rations": 2}


def test_home_cooking_rejects_a_forged_perfect_result_without_mutating_state():
    session = _session({"field_mint": 1})
    session._refresh_runtime_views()
    before = copy.deepcopy(session.state.model_dump(mode="json"))

    rejected = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="cook_herb_soup_perfect",
        mini_game_result={"choice_id": "cook_herb_soup_perfect", "tier": "perfect", "cuttingHits": 3, "heatPower": 50},
    )

    assert rejected["ok"] is False
    assert rejected["error"] == "mini_game_result_mismatch"
    assert session.state.model_dump(mode="json") == before


def test_home_cooking_without_material_is_an_explicit_atomic_rejection():
    session = _session()
    # Non-use_item actions refresh authored NPC runtime views before validation;
    # establish that deterministic view before taking the atomicity snapshot.
    session._refresh_runtime_views()
    before = copy.deepcopy(session.state.model_dump(mode="json"))

    rejected = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="cook_herb_soup_perfect",
    )

    assert rejected["ok"] is False
    assert rejected["error"] == "insufficient_item"
    assert rejected["item_id"] == "field_mint"
    assert session.state.model_dump(mode="json") == before
