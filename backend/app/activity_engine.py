from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


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

    next_flags = dict(flags)
    repeat = str(activity.get("repeat") or "free")
    activity_day = int(day)
    done_key = f"activity_done.{activity_id}"
    day_key = f"activity_day.{activity_id}"
    if repeat == "once" and int(next_flags.get(done_key, 0)) >= 1:
        raise ActivityValidationError("already_done")
    if repeat == "daily" and int(next_flags.get(day_key, -1)) == activity_day:
        raise ActivityValidationError("already_done_today")

    tree_damage = max(0, int(effects.get("tree_damage") or 0))
    stamina_cost = max(0, int(effects.get("stamina_cost") or 8))
    hp_cost = max(0, int(effects.get("hp_cost") or 0))
    mp_cost = max(0, int(effects.get("mp_cost") or 0))
    stamina_restore = max(0, int(effects.get("stamina_restore") or 0))
    hp_restore = max(0, int(effects.get("hp_restore") or 0))
    mp_restore = max(0, int(effects.get("mp_restore") or 0))

    if player.stamina < stamina_cost:
        raise ActivityValidationError("insufficient_stamina", required=stamina_cost, current=player.stamina)
    if hp_cost and player.hp <= hp_cost:
        raise ActivityValidationError("insufficient_hp", required=hp_cost + 1, current=player.hp)
    if player.mp < mp_cost:
        raise ActivityValidationError("insufficient_mp", required=mp_cost, current=player.mp)

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
    )
