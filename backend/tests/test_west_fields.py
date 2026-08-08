import json

from app.activity_engine import ActivityValidationError, plan_scene_activity
from app.models import PlayerState
from app.scene_activities import public_scene_activities
from app.session import Session


def test_activity_plan_settles_weather_item_and_collection_progress():
    activity = {
        "id": "field_foraging",
        "scene_id": "west_fields",
        "repeat": "daily",
        "effects": {
            "stamina_cost": 2,
            "weather_item_deltas": {"mist": {"dewgrass": 1}},
        },
    }
    plan = plan_scene_activity(
        activity,
        activity_id="field_foraging",
        activity_choice=None,
        scene_id="west_fields",
        time_band="morning",
        day=1,
        flags={},
        player=PlayerState(scene_id="west_fields", stamina=10),
        inventory={},
        weather="mist",
    )

    assert plan.next_inventory == {"dewgrass": 1}
    assert plan.item_changes["dewgrass"] == {"before": 0, "after": 1, "delta": 1}

    fragment = {
        "id": "fragment_3",
        "scene_id": "west_fields",
        "repeat": "once",
        "collection": {
            "id": "tablet",
            "required_item": "stone_tablet_fragment",
            "required_count": 3,
            "complete_flag": "tablet_complete",
        },
        "effects": {"stamina_cost": 0, "item_deltas": {"stone_tablet_fragment": 1}},
    }
    completed = plan_scene_activity(
        fragment,
        activity_id="fragment_3",
        activity_choice=None,
        scene_id="west_fields",
        time_band="morning",
        day=1,
        flags={},
        player=PlayerState(scene_id="west_fields"),
        inventory={"stone_tablet_fragment": 2},
    )
    assert completed.next_inventory["stone_tablet_fragment"] == 3
    assert completed.next_flags["tablet_complete"] == 1
    assert completed.collection_completions == [
        {
            "id": "tablet",
            "required_item": "stone_tablet_fragment",
            "required_count": 3,
            "complete_flag": "tablet_complete",
        }
    ]


def _west_session(run_id: str) -> Session:
    session = Session(run_id=run_id)
    player = session.state.player.model_copy(update={"scene_id": "west_fields"})
    session.state = session.state.model_copy(
        update={
            "scene_id": "west_fields",
            "player": player,
            "time_band": "morning",
            "weather": "clear",
        }
    )
    return session


def test_west_fields_herbs_are_daily_and_refresh_on_next_day():
    session = _west_session("west-fields-herb-test")

    first = session.player_action(
        kind="scene_activity",
        activity_id="west_fields_herb_gather",
    )
    assert first["ok"] is True
    assert first["activity_result"]["item_changes"] == {
        "field_mint": {"before": 0, "after": 1, "delta": 1}
    }
    assert session.state.inventory == {"field_mint": 1}
    day_one_inventory = dict(session.state.inventory)

    rejected = session.player_action(
        kind="scene_activity",
        activity_id="west_fields_herb_gather",
    )
    assert rejected["ok"] is False
    assert rejected["error"] == "already_done_today"
    assert session.state.inventory == day_one_inventory

    session.state = session.state.model_copy(update={"day": 2, "time_band": "morning", "weather": "mist"})
    second = session.player_action(
        kind="scene_activity",
        activity_id="west_fields_herb_gather",
    )
    assert second["ok"] is True
    assert session.state.inventory == {"field_mint": 1, "dewgrass": 1}


def test_west_fields_hidden_fragments_are_once_only_and_complete_collection():
    session = _west_session("west-fields-fragment-test")
    for activity_id in (
        "west_fields_tablet_fragment_1",
        "west_fields_tablet_fragment_2",
        "west_fields_tablet_fragment_3",
    ):
        result = session.player_action(kind="scene_activity", activity_id=activity_id)
        assert result["ok"] is True

    assert session.state.inventory["stone_tablet_fragment"] == 3
    assert session.state.flags["west_fields.stone_tablet_complete"] == 1
    assert session.events[-1]["activity_result"]["collection_completions"] == [
        {
            "id": "west_fields_stone_tablet",
            "required_item": "stone_tablet_fragment",
            "required_count": 3,
            "complete_flag": "west_fields.stone_tablet_complete",
        }
    ]

    before = session.state.model_dump(mode="json")
    rejected = session.player_action(
        kind="scene_activity",
        activity_id="west_fields_tablet_fragment_1",
    )
    assert rejected["ok"] is False
    assert rejected["error"] == "already_done"
    assert session.state.model_dump(mode="json") == before


def test_inventory_is_backward_compatible_in_save_import():
    session = _west_session("west-fields-save-test")
    session.state = session.state.model_copy(update={"inventory": {"field_mint": 2}})
    payload = session.export_save()

    restored = _west_session("west-fields-save-restore-test")
    result = restored.import_save(payload)

    assert result["ok"] is True
    assert restored.state.inventory == {"field_mint": 2}


def test_west_fields_are_available_in_world_activity_catalog():
    catalog = public_scene_activities(Session(run_id="west-fields-catalog-test").root)
    ids = {item["id"] for item in catalog["activities"]}
    assert {
        "west_fields_herb_gather",
        "west_fields_tablet_fragment_1",
        "west_fields_tablet_fragment_2",
        "west_fields_tablet_fragment_3",
    } <= ids
    hidden = next(item for item in catalog["activities"] if item["id"] == "west_fields_tablet_fragment_1")
    assert hidden["hidden"] is True
    assert "items" in hidden["preview"]["reward_kinds"]
