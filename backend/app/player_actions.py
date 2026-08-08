from __future__ import annotations

from typing import Any

from .models import Location, PlayerState
from .world import LOCATION_MAP_ANCHORS


PLAYER_ACTIONS = {
    "move_world",
    "move_map",
    "move_scene",
    "enter_scene",
    "interact_with_hub",
    "set_location",
    "set_flag",
    "set_day",
    "scene_activity",
    "use_item",
    "respond_npc_intent",
    "daily_tick",
    "compound_sleep",
    "rest_until_next_day",
}

ACTION_ALIASES = {
    "enter_scene": "move_scene",
}


def normalize_player_action_kind(kind: str | None, *, activity_id: str | None = None) -> tuple[str, str]:
    original = str(kind or "").strip()
    normalized = ACTION_ALIASES.get(original, original)
    if normalized == "interact_with_hub" and activity_id:
        normalized = "scene_activity"
    return original, normalized


def player_at_location(player: PlayerState, loc: Location) -> PlayerState:
    updates: dict[str, object] = {"location": loc}
    anchor = LOCATION_MAP_ANCHORS.get(loc)
    if anchor:
        updates.update(
            {
                "tile_x": int(anchor["tile_x"]),
                "tile_y": int(anchor["tile_y"]),
                "scene_id": str(anchor["scene_id"]),
                "map_id": "novice_open",
            }
        )
    return player.model_copy(update=updates)


def camera_for_player(player: PlayerState) -> dict[str, Any]:
    return {
        "mode": "follow_player",
        "focus_tile": {"x": int(player.tile_x), "y": int(player.tile_y)},
        "map_id": player.map_id,
        "scene_id": player.scene_id,
    }


def zone_for_scene(world_map: dict[str, Any], scene_id: str | None) -> dict[str, Any] | None:
    if not scene_id:
        return None
    for zone in world_map.get("scene_zones") or []:
        if isinstance(zone, dict) and zone.get("scene_id") == scene_id:
            return dict(zone)
    return None


def poi_by_id(world_map: dict[str, Any], poi_id: str | None) -> dict[str, Any] | None:
    if not poi_id:
        return None
    for poi in world_map.get("pois") or []:
        if isinstance(poi, dict) and poi.get("id") == poi_id:
            return dict(poi)
    return None


def merge_activity_effects(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base or {})
    for key, value in (override or {}).items():
        if (
            key in {
                "flags",
                "flag_deltas",
                "relationship",
                "memory",
                "promises",
                "tensions",
                "item_deltas",
                "weather_item_deltas",
            }
            and isinstance(value, dict)
        ):
            merged = dict(out.get(key) or {}) if isinstance(out.get(key), dict) else {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict) and isinstance(merged.get(sub_key), dict):
                    merged[sub_key] = {**merged[sub_key], **sub_value}
                else:
                    merged[sub_key] = sub_value
            out[key] = merged
        else:
            out[key] = value
    return out


def rejected_action_envelope(
    *,
    state: Any,
    original_kind: str,
    normalized_kind: str,
    error: str,
    scene_update: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "error": error,
        "state": state.model_dump(mode="json"),
        "events": [
            {
                "type": "action_rejected",
                "action": original_kind,
                "normalized_action": normalized_kind,
                "reason": error,
            }
        ],
        "camera": camera_for_player(state.player),
        "scene_update": scene_update,
        "allowed_actions": sorted(PLAYER_ACTIONS),
        **(extra or {}),
    }
