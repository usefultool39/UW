from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .models import PlayerState, WorldState


ITEM_TYPES = {"material", "consumable", "key_item"}
RESOURCE_KEYS = ("hp", "mp", "stamina")


class ItemValidationError(ValueError):
    """Structured, user-facing rejection raised before state mutation."""

    def __init__(self, code: str, **details: Any) -> None:
        super().__init__(code)
        self.code = code
        self.details = details


@dataclass(frozen=True)
class ItemUsePlan:
    item: dict[str, Any]
    item_id: str
    quantity: int
    next_player: PlayerState
    next_inventory: dict[str, int]
    next_flags: dict[str, int]
    item_changes: dict[str, dict[str, int]]
    resource_changes: dict[str, dict[str, int]]
    result_text: str


def default_items_path(project_root: Path) -> Path:
    return project_root / "data" / "world" / "items.json"


def load_items(project_root: Path) -> dict[str, Any]:
    path = default_items_path(project_root)
    if not path.is_file():
        return {"version": 1, "items": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "items": []}
    if not isinstance(raw, dict):
        return {"version": 1, "items": []}
    items = raw.get("items")
    if not isinstance(items, list):
        raw["items"] = []
    return raw


def find_item(project_root: Path, item_id: str) -> dict[str, Any] | None:
    normalized = str(item_id or "").strip()
    if not normalized:
        return None
    for item in load_items(project_root).get("items") or []:
        if isinstance(item, dict) and str(item.get("id") or "").strip() == normalized:
            return item
    return None


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_int_map(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, int] = {}
    for key, raw in value.items():
        amount = _as_int(raw)
        if amount:
            out[str(key)] = amount
    return out


def _condition_block(item: dict[str, Any]) -> dict[str, Any]:
    use = _as_dict(item.get("use"))
    conditions = _as_dict(use.get("conditions"))
    # Accept the flat form as well, so authored data remains easy to review.
    for key in (
        "scenes",
        "scene_ids",
        "allowed_scenes",
        "time_bands",
        "allowed_time_bands",
        "required_flags",
        "forbidden_flags",
        "required_items",
    ):
        if key not in conditions and key in use:
            conditions[key] = use[key]
    return conditions


def _effect_block(item: dict[str, Any]) -> dict[str, Any]:
    use = _as_dict(item.get("use"))
    effects = _as_dict(use.get("effects"))
    # The short form is also accepted for data-only item definitions.
    for key in ("restore", "resource_restore", "flag_deltas", "flags", "result_text"):
        if key not in effects and key in use:
            effects[key] = use[key]
    return effects


def _allowed_values(conditions: dict[str, Any], *keys: str) -> list[str]:
    for key in keys:
        raw = conditions.get(key)
        if isinstance(raw, list) and raw:
            return [str(value) for value in raw]
    return []


def _validate_flag_conditions(flags: dict[str, int], conditions: dict[str, Any]) -> None:
    required = _as_int_map(conditions.get("required_flags"))
    missing = {
        key: value for key, value in required.items() if _as_int(flags.get(key)) < value
    }
    if missing:
        raise ItemValidationError("item_requirements_not_met", required_flags=missing)

    forbidden = _as_int_map(conditions.get("forbidden_flags"))
    blocked = {
        key: value for key, value in forbidden.items() if _as_int(flags.get(key)) >= value
    }
    if blocked:
        raise ItemValidationError("item_requirements_not_met", forbidden_flags=blocked)


def _resource_changes(player: PlayerState, next_player: PlayerState) -> dict[str, dict[str, int]]:
    return {
        key: {
            "before": int(getattr(player, key)),
            "after": int(getattr(next_player, key)),
            "delta": int(getattr(next_player, key)) - int(getattr(player, key)),
        }
        for key in RESOURCE_KEYS
    }


def plan_item_use(
    item: dict[str, Any] | None,
    *,
    item_id: str,
    quantity: int | None,
    state: WorldState,
) -> ItemUsePlan:
    """Purely validate and plan an item use; never mutates ``state``."""
    normalized_id = str(item_id or "").strip()
    if not normalized_id or item is None:
        raise ItemValidationError("unknown_item", item_id=normalized_id)

    item_type = str(item.get("type") or "").strip()
    if item_type not in ITEM_TYPES:
        raise ItemValidationError("invalid_item_definition", item_id=normalized_id)
    if item_type == "material":
        raise ItemValidationError("item_not_usable", item_id=normalized_id, item_type=item_type)

    use = _as_dict(item.get("use"))
    if not use or item.get("usable") is False:
        raise ItemValidationError("item_not_usable", item_id=normalized_id, item_type=item_type)

    raw_quantity = 1 if quantity is None else quantity
    if isinstance(raw_quantity, bool):
        raise ItemValidationError("invalid_item_quantity", quantity=raw_quantity)
    use_quantity = _as_int(raw_quantity, default=-1)
    if use_quantity < 1 or use_quantity > 99:
        raise ItemValidationError("invalid_item_quantity", quantity=raw_quantity)
    if item_type != "consumable" and use_quantity != 1:
        raise ItemValidationError("invalid_item_quantity", quantity=use_quantity, max_quantity=1)

    inventory_before = {
        str(key): max(0, _as_int(value))
        for key, value in (state.inventory or {}).items()
    }
    current = inventory_before.get(normalized_id, 0)
    if current < use_quantity:
        raise ItemValidationError(
            "insufficient_item",
            item_id=normalized_id,
            required=use_quantity,
            current=current,
        )

    conditions = _condition_block(item)
    allowed_scenes = _allowed_values(conditions, "scenes", "scene_ids", "allowed_scenes")
    current_scene = str(state.player.scene_id or state.scene_id)
    if allowed_scenes and current_scene not in allowed_scenes:
        raise ItemValidationError("wrong_scene", allowed_scenes=allowed_scenes, scene_id=current_scene)

    allowed_time_bands = _allowed_values(conditions, "time_bands", "allowed_time_bands")
    if allowed_time_bands and state.time_band not in allowed_time_bands:
        raise ItemValidationError(
            "wrong_time_band",
            allowed_time_bands=allowed_time_bands,
            time_band=state.time_band,
        )

    _validate_flag_conditions(state.flags or {}, conditions)

    required_items = _as_int_map(conditions.get("required_items"))
    missing_items = {
        key: amount
        for key, amount in required_items.items()
        if inventory_before.get(key, 0) < amount
    }
    if missing_items:
        raise ItemValidationError("item_requirements_not_met", required_items=missing_items)

    effects = _effect_block(item)
    restore = _as_int_map(effects.get("resource_restore"))
    if not restore:
        restore = _as_int_map(effects.get("restore"))
    invalid_resources = sorted(set(restore) - set(RESOURCE_KEYS))
    if invalid_resources:
        raise ItemValidationError("invalid_item_definition", item_id=normalized_id)
    if any(amount < 0 for amount in restore.values()):
        raise ItemValidationError("invalid_item_definition", item_id=normalized_id)

    next_player = state.player.model_copy(
        update={
            resource: min(
                int(getattr(state.player, f"max_{resource}")),
                max(0, int(getattr(state.player, resource)) + amount * use_quantity),
            )
            for resource, amount in restore.items()
        }
    )
    consumes = item_type == "consumable" or bool(use.get("consume", False))
    consumed_quantity = use_quantity if consumes else 0
    next_inventory = dict(inventory_before)
    next_inventory[normalized_id] = current - consumed_quantity
    item_changes = {
        normalized_id: {
            "before": current,
            "after": next_inventory[normalized_id],
            "delta": -consumed_quantity,
        }
    }

    next_flags = dict(state.flags or {})
    for key, value in _as_int_map(effects.get("flags")).items():
        next_flags[key] = value
    for key, value in _as_int_map(effects.get("flag_deltas")).items():
        next_flags[key] = _as_int(next_flags.get(key)) + value * use_quantity

    result_text = str(
        effects.get("result_text")
        or item.get("use_result_text")
        or item.get("description")
        or "道具已使用。"
    )
    return ItemUsePlan(
        item=item,
        item_id=normalized_id,
        quantity=use_quantity,
        next_player=next_player,
        next_inventory=next_inventory,
        next_flags=next_flags,
        item_changes=item_changes,
        resource_changes=_resource_changes(state.player, next_player),
        result_text=result_text,
    )
