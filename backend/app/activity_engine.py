from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .item_engine import find_item
from .models import PlayerState
from .player_actions import merge_activity_effects


class ActivityValidationError(ValueError):
    """A user-facing activity rejection with structured response details."""

    def __init__(self, code: str, **details: Any) -> None:
        super().__init__(code)
        self.code = code
        self.details = details


@dataclass(frozen=True)
class ActivityPlan:
    effects: dict[str, Any]
    selected_choice: dict[str, Any] | None
    next_flags: dict[str, int]
    repeat: str
    time_cost: int
    tree_damage: int
    stamina_cost: int
    hp_cost: int
    mp_cost: int
    resource_changes: dict[str, dict[str, int]]
    next_player: PlayerState
    item_changes: dict[str, dict[str, int]]
    next_inventory: dict[str, int]
    collection_completions: list[dict[str, Any]]
    loadout_result: dict[str, Any]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_int_map(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, int] = {}
    for key, raw in value.items():
        try:
            amount = int(raw)
        except (TypeError, ValueError):
            continue
        if amount:
            out[str(key)] = amount
    return out


def _loadout_effects(base_effects: dict[str, Any], loadout_effects: dict[str, Any]) -> dict[str, Any]:
    """Apply authored loadout modifiers without trusting client-provided values."""
    effects = dict(base_effects)
    for key in ("stamina_cost_delta", "hp_cost_delta", "mp_cost_delta"):
        if key in loadout_effects:
            effects[key] = int(effects.get(key) or 0) + int(loadout_effects.get(key) or 0)
    for key in ("stamina_restore", "hp_restore", "mp_restore"):
        if key in loadout_effects:
            effects[key] = int(effects.get(key) or 0) + max(0, int(loadout_effects.get(key) or 0))
    authored_flag_deltas = loadout_effects.get("flag_deltas")
    if isinstance(authored_flag_deltas, dict):
        flag_deltas = dict(effects.get("flag_deltas") or {})
        for flag_key, amount in authored_flag_deltas.items():
            flag_deltas[str(flag_key)] = int(flag_deltas.get(str(flag_key)) or 0) + int(amount or 0)
        effects["flag_deltas"] = flag_deltas
    bonus_marks = int(loadout_effects.get("bonus_marks") or 0)
    if bonus_marks:
        flag_deltas = dict(effects.get("flag_deltas") or {})
        flag_deltas["boundary_marks"] = int(flag_deltas.get("boundary_marks") or 0) + bonus_marks
        effects["flag_deltas"] = flag_deltas
    return effects


def _plan_loadout(
    activity: dict[str, Any],
    *,
    requested_loadout: list[str] | None,
    inventory: dict[str, int],
    project_root: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate a candidate loadout against authored rules, catalog and inventory."""
    requested = [] if requested_loadout is None else requested_loadout
    if not isinstance(requested, list):
        raise ActivityValidationError("invalid_loadout", reason="loadout_must_be_a_list")
    config = _as_dict(activity.get("loadout"))
    max_items = max(0, int(config.get("max_items") or 0))
    if len(requested) > max_items:
        raise ActivityValidationError("loadout_too_many_items", max_items=max_items)

    allowed_rows = config.get("allowed_items") if isinstance(config.get("allowed_items"), list) else []
    allowed = {
        str(row.get("item_id") or "").strip(): row
        for row in allowed_rows
        if isinstance(row, dict) and str(row.get("item_id") or "").strip()
    }
    normalized: list[str] = []
    for raw_id in requested:
        item_id = str(raw_id or "").strip()
        if not item_id or item_id in normalized:
            raise ActivityValidationError("invalid_loadout_item", item_id=item_id, reason="duplicate_or_empty")
        row = allowed.get(item_id)
        item = find_item(project_root, item_id)
        if row is None or item is None:
            raise ActivityValidationError("invalid_loadout_item", item_id=item_id, reason="not_allowed")
        if str(item.get("type") or "") == "material":
            raise ActivityValidationError("invalid_loadout_item", item_id=item_id, reason="materials_not_allowed")
        current = max(0, int(inventory.get(item_id, 0)))
        if current < 1:
            raise ActivityValidationError("insufficient_loadout_item", item_id=item_id, required=1, current=current)
        normalized.append(item_id)

    option_effects: dict[str, Any] = {}
    consumed: list[str] = []
    retained: list[str] = []
    for item_id in normalized:
        row = allowed[item_id]
        option_effects = _loadout_effects(option_effects, _as_dict(row.get("effects")))
        if bool(row.get("consume", False)):
            consumed.append(item_id)
        else:
            retained.append(item_id)

    combination = None
    requested_set = set(normalized)
    for row in config.get("combination_bonuses") if isinstance(config.get("combination_bonuses"), list) else []:
        if not isinstance(row, dict):
            continue
        ids = [str(value or "").strip() for value in row.get("item_ids") or []]
        if ids and set(ids) == requested_set and len(ids) == len(normalized):
            combination = row
            option_effects = _loadout_effects(option_effects, _as_dict(row.get("effects")))
            break

    item_deltas = {item_id: -1 for item_id in consumed}
    loadout_result = {
        "items": normalized,
        "consumed_items": consumed,
        "retained_items": retained,
        "combination": {
            "id": combination.get("id"),
            "label": combination.get("label"),
        } if combination else None,
        "effects": {
            key: value for key, value in option_effects.items()
            if key in {"stamina_cost_delta", "hp_cost_delta", "mp_cost_delta", "stamina_restore", "hp_restore", "mp_restore", "bonus_marks"}
        },
        "item_deltas": item_deltas,
    }
    return option_effects, loadout_result


def _result_value(result: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in result:
            return result[key]
    return None


def _as_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number else None


def _validate_mini_game_result(
    activity: dict[str, Any],
    *,
    activity_choice: str,
    mini_game_result: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Validate the small, deterministic performance contract for QTE activities.

    Authored effects remain the only source of state changes. The result is used
    only to prove that the selected authored choice agrees with the reported
    performance, so a client cannot request a perfect/rare branch with an
    inconsistent result payload.
    """
    interaction_kind = str(activity.get("interaction_kind") or "")
    if interaction_kind not in {"cooking_qte", "fishing_qte", "reading_keywords"}:
        return None
    if not isinstance(mini_game_result, dict):
        raise ActivityValidationError(
            "mini_game_result_required",
            activity_id=str(activity.get("id") or ""),
            interaction_kind=interaction_kind,
        )

    reported_choice = _result_value(mini_game_result, "choice_id", "choiceId")
    if reported_choice is not None and str(reported_choice) != activity_choice:
        raise ActivityValidationError(
            "mini_game_result_mismatch",
            activity_choice=activity_choice,
            reported_choice=str(reported_choice),
            reason="choice_id_mismatch",
        )

    choices = activity.get("choices") if isinstance(activity.get("choices"), list) else []
    authored_ids = {str(choice.get("id") or "") for choice in choices if isinstance(choice, dict)}
    if activity_choice not in authored_ids:
        raise ActivityValidationError("unknown_activity_choice", activity_choice=activity_choice)

    if interaction_kind == "reading_keywords":
        chain = _as_dict(activity.get("reading_chain"))
        paths = chain.get("paths") if isinstance(chain.get("paths"), list) else []
        authored_path = next(
            (path for path in paths if isinstance(path, dict) and str(path.get("choice_id") or "") == activity_choice),
            None,
        )
        inference_chain = _result_value(mini_game_result, "inference_chain")
        if authored_path is None or not isinstance(inference_chain, list):
            raise ActivityValidationError(
                "mini_game_result_invalid",
                reason="reading_path_missing",
            )
        expected_steps = [str(step) for step in authored_path.get("steps") or []]
        reported_steps = [str(step) for step in inference_chain]
        reported_path = _result_value(mini_game_result, "path_id", "pathId", "choice_id", "choiceId")
        if reported_steps != expected_steps or (reported_path is not None and str(reported_path) != activity_choice):
            raise ActivityValidationError(
                "mini_game_result_mismatch",
                activity_choice=activity_choice,
                expected_steps=expected_steps,
                reported_steps=reported_steps,
                reason="reading_path_mismatch",
            )
        return {"path_id": activity_choice, "inference_chain": expected_steps}

    if interaction_kind == "cooking_qte":
        hits = _as_number(_result_value(mini_game_result, "cutting_hits", "cuttingHits"))
        heat = _as_number(_result_value(mini_game_result, "heat_power", "heatPower"))
        if hits is None or heat is None or hits < 0 or heat < 0 or heat > 100:
            raise ActivityValidationError(
                "mini_game_result_invalid",
                reason="cooking_performance_missing_or_out_of_range",
            )
        expected_tier = "perfect" if hits == 5 and 68 <= heat <= 82 else "normal"
        expected_suffix = f"_{expected_tier}"
        if not activity_choice.endswith(expected_suffix):
            raise ActivityValidationError(
                "mini_game_result_mismatch",
                activity_choice=activity_choice,
                expected_tier=expected_tier,
                reason="cooking_tier_mismatch",
            )
        reported_tier = _result_value(mini_game_result, "tier")
        if reported_tier is not None and str(reported_tier) != expected_tier:
            raise ActivityValidationError(
                "mini_game_result_mismatch",
                activity_choice=activity_choice,
                expected_tier=expected_tier,
                reported_tier=str(reported_tier),
                reason="reported_tier_mismatch",
            )
        return {"tier": expected_tier, "cutting_hits": int(hits), "heat_power": heat}

    timing_ms = _as_number(_result_value(mini_game_result, "timing_ms", "timingMs"))
    if timing_ms is None or timing_ms < 0:
        raise ActivityValidationError(
            "mini_game_result_invalid",
            reason="fishing_timing_missing_or_negative",
        )
    expected_rarity = "rare" if timing_ms <= 240 else "common"
    expected_choice = "catch_rare_fish" if expected_rarity == "rare" else "catch_common_fish"
    if activity_choice != expected_choice:
        raise ActivityValidationError(
            "mini_game_result_mismatch",
            activity_choice=activity_choice,
            expected_choice=expected_choice,
            reason="fishing_rarity_mismatch",
        )
    reported_rarity = _result_value(mini_game_result, "fish_rarity", "rarity")
    if reported_rarity is not None and str(reported_rarity) != expected_rarity:
        raise ActivityValidationError(
            "mini_game_result_mismatch",
            activity_choice=activity_choice,
            expected_rarity=expected_rarity,
            reported_rarity=str(reported_rarity),
            reason="reported_rarity_mismatch",
        )
    expected_fish_id = f"south_lake_{expected_rarity}_fish"
    reported_fish_id = _result_value(mini_game_result, "fish_id")
    if reported_fish_id is not None and str(reported_fish_id) != expected_fish_id:
        raise ActivityValidationError(
            "mini_game_result_mismatch",
            activity_choice=activity_choice,
            expected_fish_id=expected_fish_id,
            reported_fish_id=str(reported_fish_id),
            reason="fish_id_mismatch",
        )
    return {"rarity": expected_rarity, "timing_ms": timing_ms}


def plan_scene_activity(
    activity: dict[str, Any],
    *,
    activity_id: str,
    activity_choice: str | None,
    scene_id: str,
    time_band: str,
    day: int,
    flags: dict[str, int],
    player: PlayerState,
    inventory: dict[str, int] | None = None,
    weather: str | None = None,
    loadout: list[str] | None = None,
    mini_game_result: dict[str, Any] | None = None,
    project_root: Any = None,
) -> ActivityPlan:
    """Purely validate and plan an activity; it performs no IO or Session mutation."""
    scene_ids = activity.get("scene_ids")
    if isinstance(scene_ids, list) and scene_ids:
        allowed_scenes = {str(scene) for scene in scene_ids}
    else:
        scene_req = str(activity.get("scene_id") or "")
        allowed_scenes = {scene_req} if scene_req else set()
    if allowed_scenes and scene_id not in allowed_scenes:
        raise ActivityValidationError("wrong_scene", allowed_scenes=sorted(allowed_scenes))

    time_bands = activity.get("time_bands") or []
    if isinstance(time_bands, list) and time_bands and time_band not in time_bands:
        raise ActivityValidationError("wrong_time_band", allowed_time_bands=time_bands)

    requirements = _as_dict(activity.get("requirements"))
    day_min = requirements.get("day_min")
    day_max = requirements.get("day_max")
    if day_min is not None and int(day) < int(day_min):
        raise ActivityValidationError(
            "wrong_day_range",
            day=int(day),
            day_min=int(day_min),
            day_max=int(day_max) if day_max is not None else None,
        )
    if day_max is not None and int(day) > int(day_max):
        raise ActivityValidationError(
            "wrong_day_range",
            day=int(day),
            day_min=int(day_min) if day_min is not None else None,
            day_max=int(day_max),
        )

    required_flags = _as_dict(requirements.get("required_flags"))
    for key, value in required_flags.items():
        if int(flags.get(str(key), 0)) < int(value):
            raise ActivityValidationError("requirements_not_met", required_flags=required_flags)

    required_any_flags = _as_dict(requirements.get("required_any_flags"))
    if required_any_flags and not any(
        int(flags.get(str(key), 0)) >= int(value)
        for key, value in required_any_flags.items()
    ):
        raise ActivityValidationError("requirements_not_met", required_any_flags=required_any_flags)

    effects = _as_dict(activity.get("effects"))
    selected_choice: dict[str, Any] | None = None
    choice_id = str(activity_choice or "").strip()
    choices = activity.get("choices") if isinstance(activity.get("choices"), list) else []
    if choices and not choice_id:
        raise ActivityValidationError(
            "activity_choice_required",
            activity_id=activity_id,
            choice_ids=[str(choice.get("id") or "") for choice in choices if isinstance(choice, dict)],
        )
    if choice_id:
        selected_choice = next(
            (choice for choice in choices if isinstance(choice, dict) and str(choice.get("id") or "") == choice_id),
            None,
        )
        if selected_choice is None:
            raise ActivityValidationError("unknown_activity_choice", activity_id=activity_id, activity_choice=choice_id)
        choice_effects = selected_choice.get("effects")
        if isinstance(choice_effects, dict):
            effects = merge_activity_effects(effects, choice_effects)

    loadout_effects: dict[str, Any] = {}
    loadout_result: dict[str, Any] = {
        "items": [], "consumed_items": [], "retained_items": [], "combination": None,
        "effects": {}, "item_deltas": {},
    }
    if loadout is not None or isinstance(activity.get("loadout"), dict):
        if project_root is None:
            raise ActivityValidationError("invalid_loadout", reason="missing_project_root")
        inventory_for_loadout = {str(key): max(0, int(value)) for key, value in (inventory or {}).items()}
        loadout_effects, loadout_result = _plan_loadout(
            activity,
            requested_loadout=loadout,
            inventory=inventory_for_loadout,
            project_root=project_root,
        )
        effects = _loadout_effects(effects, loadout_effects)

    next_flags = dict(flags)
    repeat = str(activity.get("repeat") or "free")
    activity_day = int(day)
    done_key = f"activity_done.{activity_id}"
    day_key = f"activity_day.{activity_id}"
    if repeat == "once" and int(next_flags.get(done_key, 0)) >= 1:
        raise ActivityValidationError("already_done")
    if repeat == "daily" and int(next_flags.get(day_key, -1)) == activity_day:
        raise ActivityValidationError("already_done_today")

    inventory_before = {
        str(key): max(0, int(value))
        for key, value in (inventory or {}).items()
    }
    item_deltas = _as_int_map(effects.get("item_deltas"))
    for item_id, delta in _as_int_map(loadout_result.get("item_deltas")).items():
        item_deltas[item_id] = item_deltas.get(item_id, 0) + delta
    weather_item_deltas = _as_dict(effects.get("weather_item_deltas"))
    if weather:
        item_deltas.update(
            {
                key: item_deltas.get(key, 0) + amount
                for key, amount in _as_int_map(weather_item_deltas.get(str(weather))).items()
            }
        )
    next_inventory = dict(inventory_before)
    item_changes: dict[str, dict[str, int]] = {}
    for item_id, delta in item_deltas.items():
        before = inventory_before.get(item_id, 0)
        after = before + delta
        if after < 0:
            raise ActivityValidationError(
                "insufficient_item",
                item_id=item_id,
                required=abs(delta),
                current=before,
            )
        next_inventory[item_id] = after
        item_changes[item_id] = {"before": before, "after": after, "delta": delta}
    if loadout_result.get("items"):
        loadout_result["item_changes"] = {
            item_id: item_changes[item_id]
            for item_id in loadout_result.get("consumed_items", [])
            if item_id in item_changes
        }

    collection_completions: list[dict[str, Any]] = []
    collection = _as_dict(activity.get("collection"))
    collection_id = str(collection.get("id") or "").strip()
    required_item = str(collection.get("required_item") or "").strip()
    complete_flag = str(collection.get("complete_flag") or "").strip()
    if collection_id and required_item and complete_flag:
        required_count = max(1, int(collection.get("required_count") or 1))
        if next_inventory.get(required_item, 0) >= required_count and int(next_flags.get(complete_flag, 0)) < 1:
            next_flags[complete_flag] = 1
            collection_completions.append(
                {
                    "id": collection_id,
                    "required_item": required_item,
                    "required_count": required_count,
                    "complete_flag": complete_flag,
                }
            )

    tree_damage = max(0, int(effects.get("tree_damage") or 0))
    # An authored zero is meaningful for route resource choices. Preserve the
    # legacy default of 8 stamina only when the field is absent.
    stamina_cost = max(0, int(effects["stamina_cost"])) if "stamina_cost" in effects else 8
    stamina_cost = max(0, stamina_cost + int(effects.get("stamina_cost_delta") or 0))
    hp_cost = max(0, int(effects.get("hp_cost") or 0) + int(effects.get("hp_cost_delta") or 0))
    mp_cost = max(0, int(effects.get("mp_cost") or 0) + int(effects.get("mp_cost_delta") or 0))
    stamina_restore = max(0, int(effects.get("stamina_restore") or 0))
    hp_restore = max(0, int(effects.get("hp_restore") or 0))
    mp_restore = max(0, int(effects.get("mp_restore") or 0))

    if player.stamina + stamina_restore < stamina_cost:
        raise ActivityValidationError("insufficient_stamina", required=stamina_cost, current=player.stamina)
    if hp_cost and player.hp <= hp_cost:
        raise ActivityValidationError("insufficient_hp", required=hp_cost + 1, current=player.hp)
    if player.mp + mp_restore < mp_cost:
        raise ActivityValidationError("insufficient_mp", required=mp_cost, current=player.mp)

    _validate_mini_game_result(
        activity,
        activity_choice=choice_id,
        mini_game_result=mini_game_result,
    )
    for key, value in _as_dict(effects.get("flags")).items():
        next_flags[str(key)] = int(value)
    for key, value in _as_dict(effects.get("flag_deltas")).items():
        flag_key = str(key)
        next_flags[flag_key] = int(next_flags.get(flag_key, 0)) + int(value)
    if repeat == "once":
        next_flags[done_key] = 1
    elif repeat == "daily":
        next_flags[day_key] = activity_day

    next_player = player.model_copy(
        update={
            "stamina": min(player.max_stamina, max(0, player.stamina - stamina_cost + stamina_restore)),
            "hp": min(player.max_hp, max(1, player.hp - hp_cost + hp_restore)),
            "mp": min(player.max_mp, max(0, player.mp - mp_cost + mp_restore)),
        }
    )
    resource_changes = {
        "hp": {"before": player.hp, "after": next_player.hp, "delta": next_player.hp - player.hp},
        "mp": {"before": player.mp, "after": next_player.mp, "delta": next_player.mp - player.mp},
        "stamina": {"before": player.stamina, "after": next_player.stamina, "delta": next_player.stamina - player.stamina},
    }

    return ActivityPlan(
        effects=effects,
        selected_choice=selected_choice,
        next_flags=next_flags,
        repeat=repeat,
        time_cost=max(0, min(12, int(activity.get("time_cost") or 0))),
        tree_damage=tree_damage,
        stamina_cost=stamina_cost,
        hp_cost=hp_cost,
        mp_cost=mp_cost,
        resource_changes=resource_changes,
        next_player=next_player,
        item_changes=item_changes,
        next_inventory=next_inventory,
        collection_completions=collection_completions,
        loadout_result=loadout_result,
    )
