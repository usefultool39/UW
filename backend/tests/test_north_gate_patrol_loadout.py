import copy
import json
from pathlib import Path

from app.scene_activities import public_scene_activities
from app.session import Session

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACTIVITY_ID = "north_gate_boundary_patrol"


def _session(*, inventory=None):
    session = Session(run_id="north-gate-loadout-test")
    player = session.state.player.model_copy(
        update={"scene_id": "north_gate", "stamina": 50, "mp": 30, "hp": 40}
    )
    session.state = session.state.model_copy(
        update={
            "scene_id": "north_gate",
            "player": player,
            "time_band": "morning",
            "flags": {"forest_anomaly_seen": 1},
            "inventory": inventory or {},
        }
    )
    return session


def test_patrol_loadout_is_authored_and_public_projection_hides_effects():
    raw = json.loads((PROJECT_ROOT / "data/world/scene_activities.json").read_text(encoding="utf-8"))
    activity = next(item for item in raw["activities"] if item["id"] == ACTIVITY_ID)
    assert activity["loadout"]["max_items"] == 2
    assert [row["item_id"] for row in activity["loadout"]["allowed_items"]] == [
        "record_notebook", "dried_rations", "herb_soup"
    ]

    public = public_scene_activities(PROJECT_ROOT)
    row = next(item for item in public["activities"] if item["id"] == ACTIVITY_ID)
    assert row["loadout"]["max_items"] == 2
    assert {item["item_id"] for item in row["loadout"]["allowed_items"]} == {
        "record_notebook", "dried_rations", "herb_soup"
    }
    assert "effects" not in row["loadout"]["allowed_items"][0]


def test_valid_patrol_loadout_restores_resources_consumes_only_consumables_and_records_combo():
    session = _session(inventory={"record_notebook": 1, "dried_rations": 1})

    result = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="clean_clear",
        loadout=["record_notebook", "dried_rations"],
    )

    assert result["ok"] is True
    activity_result = result["activity_result"]
    assert activity_result["loadout"]["items"] == ["record_notebook", "dried_rations"]
    assert activity_result["loadout"]["combination"]["id"] == "recorded_supply_route"
    assert activity_result["loadout"]["consumed_items"] == ["dried_rations"]
    assert activity_result["loadout"]["retained_items"] == ["record_notebook"]
    assert activity_result["loadout"]["item_changes"]["dried_rations"]["delta"] == -1
    assert session.state.inventory == {"record_notebook": 1, "dried_rations": 0}
    # 50 stamina - (14 base - 2 combo) + 18 from rations.
    assert session.state.player.stamina == 56
    # 3 base marks + notebook bonus + pair bonus.
    assert session.state.flags["boundary_marks"] == 5


def test_invalid_or_unavailable_loadout_is_atomic_and_materials_are_rejected():
    session = _session(inventory={"field_mint": 1, "record_notebook": 1})

    for loadout, expected_error in (
        (["field_mint"], "invalid_loadout_item"),
        (["dried_rations"], "insufficient_loadout_item"),
        (["record_notebook", "record_notebook"], "invalid_loadout_item"),
        (["record_notebook", "dried_rations", "herb_soup"], "loadout_too_many_items"),
        (["not_in_catalog"], "invalid_loadout_item"),
    ):
        before = copy.deepcopy(session.state.model_dump(mode="json"))
        rejected = session.player_action(
            kind="scene_activity",
            activity_id=ACTIVITY_ID,
            activity_choice="clean_clear",
            loadout=loadout,
        )
        assert rejected["ok"] is False
        assert rejected["error"] == expected_error
        assert session.state.model_dump(mode="json") == before


def test_empty_loadout_keeps_legacy_patrol_contract():
    session = _session()
    result = session.player_action(
        kind="scene_activity",
        activity_id=ACTIVITY_ID,
        activity_choice="forced_retreat",
        loadout=[],
    )
    assert result["ok"] is True
    assert result["activity_result"]["loadout"]["items"] == []
    assert result["activity_result"]["item_changes"] == {}
