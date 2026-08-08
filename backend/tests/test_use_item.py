from __future__ import annotations

import copy
import json
from pathlib import Path

from app.item_engine import find_item, plan_item_use
from app.models import WorldState
from app.session import Session


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ITEMS_PATH = PROJECT_ROOT / "data/world/items.json"


def _session(*, scene_id: str = "gigas_clearing", time_band: str = "morning") -> Session:
    session = Session(seed=23, run_id=f"use-item-test-{scene_id}-{time_band}")
    player = session.state.player.model_copy(
        update={"scene_id": scene_id, "stamina": 50, "mp": 40}
    )
    session.state = session.state.model_copy(
        update={"scene_id": scene_id, "player": player, "time_band": time_band}
    )
    return session


def test_item_catalog_has_material_consumable_and_key_item_contracts():
    raw = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    items = {item["id"]: item for item in raw["items"]}

    assert {items["field_mint"]["type"], items["dried_rations"]["type"], items["stone_tablet_fragment"]["type"]} == {
        "material",
        "consumable",
        "key_item",
    }
    assert items["dried_rations"]["use"]["effects"]["resource_restore"] == {"stamina": 24}
    assert items["herb_soup"]["use"]["effects"]["resource_restore"] == {"mp": 20}


def test_use_item_consumes_one_stack_and_returns_all_change_envelopes():
    session = _session()
    session.state = session.state.model_copy(update={"inventory": {"dried_rations": 2}})

    result = session.player_action(kind="use_item", item_id="dried_rations")

    assert result["ok"] is True
    assert result["item_changes"] == {
        "dried_rations": {"before": 2, "after": 1, "delta": -1}
    }
    assert result["inventory"] == {"dried_rations": 1}
    assert result["resource_changes"]["stamina"] == {
        "before": 50,
        "after": 74,
        "delta": 24,
    }
    assert result["item_result"]["item"]["type"] == "consumable"
    assert session.state.player.stamina == 74


def test_use_item_clamps_restore_and_supports_quantity_without_partial_commit():
    session = _session()
    session.state = session.state.model_copy(
        update={
            "inventory": {"dried_rations": 3},
            "player": session.state.player.model_copy(update={"stamina": 90}),
        }
    )

    result = session.player_action(kind="use_item", item_id="dried_rations", quantity=2)

    assert result["ok"] is True
    assert session.state.inventory == {"dried_rations": 1}
    assert session.state.player.stamina == 100
    assert result["resource_changes"]["stamina"] == {
        "before": 90,
        "after": 100,
        "delta": 10,
    }

    before = copy.deepcopy(session.state.model_dump(mode="json"))
    rejected = session.player_action(kind="use_item", item_id="dried_rations", quantity=2)
    assert rejected["ok"] is False
    assert rejected["error"] == "insufficient_item"
    assert session.state.model_dump(mode="json") == before


def test_material_and_key_fragment_cannot_be_directly_used():
    session = _session()
    session.state = session.state.model_copy(
        update={"inventory": {"field_mint": 1, "stone_tablet_fragment": 1}}
    )

    for item_id in ("field_mint", "stone_tablet_fragment"):
        before = copy.deepcopy(session.state.model_dump(mode="json"))
        rejected = session.player_action(kind="use_item", item_id=item_id)
        assert rejected["ok"] is False
        assert rejected["error"] == "item_not_usable"
        assert session.state.model_dump(mode="json") == before


def test_unknown_missing_and_invalid_quantity_are_atomic_rejections():
    session = _session()
    session.state = session.state.model_copy(update={"inventory": {"dried_rations": 1}})

    for kwargs, expected_error in (
        ({"item_id": "not_in_catalog"}, "unknown_item"),
        ({"item_id": "herb_soup"}, "insufficient_item"),
        ({"item_id": "dried_rations", "quantity": 0}, "invalid_item_quantity"),
        ({"item_id": "dried_rations", "quantity": 100}, "invalid_item_quantity"),
    ):
        before = copy.deepcopy(session.state.model_dump(mode="json"))
        rejected = session.player_action(kind="use_item", **kwargs)
        assert rejected["ok"] is False
        assert rejected["error"] == expected_error
        assert session.state.model_dump(mode="json") == before


def test_scene_and_time_conditions_reject_then_key_item_can_be_used_without_consuming():
    session = _session(scene_id="gigas_clearing")
    session.state = session.state.model_copy(update={"inventory": {"herb_soup": 1, "record_notebook": 1}})

    before = copy.deepcopy(session.state.model_dump(mode="json"))
    wrong_scene = session.player_action(kind="use_item", item_id="herb_soup")
    assert wrong_scene["ok"] is False
    assert wrong_scene["error"] == "wrong_scene"
    assert session.state.model_dump(mode="json") == before

    session.state = session.state.model_copy(
        update={
            "scene_id": "reading_hall",
            "player": session.state.player.model_copy(update={"scene_id": "reading_hall"}),
            "time_band": "night",
        }
    )
    before = copy.deepcopy(session.state.model_dump(mode="json"))
    wrong_time = session.player_action(kind="use_item", item_id="record_notebook")
    assert wrong_time["ok"] is False
    assert wrong_time["error"] == "wrong_time_band"
    assert session.state.model_dump(mode="json") == before

    session.state = session.state.model_copy(update={"time_band": "afternoon"})
    opened = session.player_action(kind="use_item", item_id="record_notebook")
    assert opened["ok"] is True
    assert opened["item_changes"]["record_notebook"]["delta"] == 0
    assert session.state.inventory["record_notebook"] == 1
    assert session.state.flags["record_notebook_opened"] == 1


def test_pure_item_plan_accepts_legacy_state_without_inventory():
    session = _session()
    raw = session.state.model_dump(mode="json")
    raw.pop("inventory", None)
    restored = WorldState.model_validate(raw)

    assert restored.inventory == {}
    plan = plan_item_use(
        find_item(PROJECT_ROOT, "dried_rations"),
        item_id="dried_rations",
        quantity=1,
        state=restored.model_copy(update={"inventory": {"dried_rations": 1}}),
    )
    assert plan.next_inventory == {"dried_rations": 0}
    assert plan.next_player.stamina == 74
