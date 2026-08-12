from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any

from .agent_registry import load_agent_profiles
from .content_validation_visual import validate_visual_config
from .story_director import load_story_events
from .world_map import bfs_path, is_blocked_zone, is_walkable, zone_for_tile


Issue = dict[str, str]

RELATIONSHIP_FIELDS = {"affinity", "trust", "tension"}
TIME_BANDS = {"morning", "afternoon", "evening", "night"}
PRECAPTURE_ACTS = {"act_0", "act_1", "act_2", "act_3"}
PRECAPTURE_ENDPOINTS = {"alice_captured", "precapture_alice_captured"}
PRECAPTURE_VISIBLE_FIELDS = {
    "title", "summary", "description", "text", "result_text", "hint",
    "label", "body", "prompt", "opening_text", "closing_text",
}
PRECAPTURE_TERM_REPLACEMENTS = {
    "露茵村": "卢利特村",
    "艾琳": "爱丽丝",
    "悠吉欧": "尤吉欧",
    "尤里": "尤吉欧",
    "古誓树": "巨神树",
    "北境律令": "禁忌目录",
    "刻印术": "神圣术",
    "村西书库": "教会书库",
    "莉娜": "赛尔卡",
}
PRECAPTURE_SPOILER_TERMS = {"金木樨", "现实世界"}


def _add_issue(
    issues: list[Issue],
    *,
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append({"code": code, "path": path, "message": message})


def _load_json_file(path: Path, errors: list[Issue]) -> Any:
    if not path.is_file():
        _add_issue(
            errors,
            code="missing_file",
            path=str(path),
            message="Required content file is missing.",
        )
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _add_issue(
            errors,
            code="invalid_json",
            path=str(path),
            message=f"Invalid JSON: {exc}",
        )
    return None


def _dict_rows(
    raw: Any,
    key: str,
    path: str,
    errors: list[Issue],
) -> list[tuple[int, dict[str, Any]]]:
    if not isinstance(raw, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return []
    rows = raw.get(key)
    if not isinstance(rows, list):
        _add_issue(
            errors,
            code="invalid_shape",
            path=f"{path}.{key}",
            message="Expected list.",
        )
        return []
    out: list[tuple[int, dict[str, Any]]] = []
    for idx, row in enumerate(rows):
        if isinstance(row, dict):
            out.append((idx, row))
        else:
            _add_issue(
                errors,
                code="invalid_row",
                path=f"{path}.{key}[{idx}]",
                message="Expected object row.",
            )
    return out


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _validate_int_map(
    value: Any,
    path: str,
    errors: list[Issue],
    *,
    code: str = "invalid_int_value",
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return
    for key, raw in value.items():
        if _as_int(raw) is None:
            _add_issue(
                errors,
                code=code,
                path=f"{path}.{key}",
                message="Expected integer-like value.",
            )


def _validate_relationship_map(
    value: Any,
    path: str,
    known_agents: set[str],
    errors: list[Issue],
    *,
    require_int: bool,
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return
    for raw_key, raw_value in value.items():
        key = str(raw_key)
        if "." not in key:
            _add_issue(
                errors,
                code="invalid_relationship_key",
                path=f"{path}.{key}",
                message="Expected npc_id.field.",
            )
            continue
        npc_id, field = key.split(".", 1)
        if npc_id not in known_agents:
            _add_issue(
                errors,
                code="unknown_relationship_agent",
                path=f"{path}.{key}",
                message=f"Unknown relationship agent '{npc_id}'.",
            )
        if field not in RELATIONSHIP_FIELDS:
            _add_issue(
                errors,
                code="unknown_relationship_field",
                path=f"{path}.{key}",
                message=f"Unknown relationship field '{field}'.",
            )
        if require_int and _as_int(raw_value) is None:
            _add_issue(
                errors,
                code="invalid_relationship_value",
                path=f"{path}.{key}",
                message="Expected integer-like value.",
            )


def _validate_agent_keys(
    value: Any,
    path: str,
    known_agents: set[str],
    errors: list[Issue],
) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return
    for raw_key in value:
        npc_id = str(raw_key)
        if npc_id not in known_agents:
            _add_issue(
                errors,
                code="unknown_agent",
                path=f"{path}.{npc_id}",
                message=f"Unknown agent '{npc_id}'.",
            )


def _validate_conditions(
    conditions: Any,
    path: str,
    *,
    known_agents: set[str],
    story_node_ids: set[str],
    errors: list[Issue],
) -> None:
    if conditions is None:
        return
    if not isinstance(conditions, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return
    for key in ("day_min", "day_max"):
        if key in conditions and _as_int(conditions.get(key)) is None:
            _add_issue(
                errors,
                code="invalid_day_gate",
                path=f"{path}.{key}",
                message="Expected integer-like day gate.",
            )

    time_bands = conditions.get("time_bands")
    if time_bands is None and "time_band" in conditions:
        time_bands = [conditions.get("time_band")]
    if time_bands is not None:
        if not isinstance(time_bands, list):
            _add_issue(
                errors,
                code="invalid_time_bands",
                path=f"{path}.time_bands",
                message="Expected list.",
            )
        else:
            for idx, band in enumerate(time_bands):
                if str(band) not in TIME_BANDS:
                    _add_issue(
                        errors,
                        code="unknown_time_band",
                        path=f"{path}.time_bands[{idx}]",
                        message=f"Unknown time band '{band}'.",
                    )

    nodes = conditions.get("story_nodes")
    if nodes is not None:
        if not isinstance(nodes, list):
            _add_issue(
                errors,
                code="invalid_story_nodes",
                path=f"{path}.story_nodes",
                message="Expected list.",
            )
        else:
            for idx, node_id in enumerate(nodes):
                if str(node_id) not in story_node_ids:
                    _add_issue(
                        errors,
                        code="unknown_story_node",
                        path=f"{path}.story_nodes[{idx}]",
                        message=f"Unknown story node '{node_id}'.",
                    )

    _validate_int_map(conditions.get("required_flags"), f"{path}.required_flags", errors)
    _validate_int_map(conditions.get("required_any_flags"), f"{path}.required_any_flags", errors)
    _validate_int_map(conditions.get("forbidden_flags"), f"{path}.forbidden_flags", errors)
    _validate_relationship_map(
        conditions.get("required_relationship"),
        f"{path}.required_relationship",
        known_agents,
        errors,
        require_int=True,
    )


def _validate_effects(
    effects: Any,
    path: str,
    *,
    known_agents: set[str],
    story_node_ids: set[str],
    scene_ids: set[str],
    event_ids: set[str] | None,
    errors: list[Issue],
) -> None:
    if effects is None:
        return
    if not isinstance(effects, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return
    _validate_int_map(effects.get("flags"), f"{path}.flags", errors)
    _validate_int_map(effects.get("flag_deltas"), f"{path}.flag_deltas", errors)
    _validate_relationship_map(
        effects.get("relationship"),
        f"{path}.relationship",
        known_agents,
        errors,
        require_int=True,
    )
    _validate_agent_keys(effects.get("memory"), f"{path}.memory", known_agents, errors)
    _validate_agent_keys(effects.get("promises"), f"{path}.promises", known_agents, errors)
    _validate_agent_keys(effects.get("tensions"), f"{path}.tensions", known_agents, errors)

    story_node_id = effects.get("story_node_id")
    if story_node_id and str(story_node_id) not in story_node_ids:
        _add_issue(
            errors,
            code="unknown_story_node",
            path=f"{path}.story_node_id",
            message=f"Unknown story node '{story_node_id}'.",
        )

    unlock_scenes = effects.get("unlock_scenes")
    if unlock_scenes is not None:
        if not isinstance(unlock_scenes, list):
            _add_issue(
                errors,
                code="invalid_unlock_scenes",
                path=f"{path}.unlock_scenes",
                message="Expected list.",
            )
        else:
            for idx, scene_id in enumerate(unlock_scenes):
                if str(scene_id) not in scene_ids:
                    _add_issue(
                        errors,
                        code="unknown_scene",
                        path=f"{path}.unlock_scenes[{idx}]",
                        message=f"Unknown scene '{scene_id}'.",
                    )

    complete_events = effects.get("complete_events")
    if event_ids is not None and complete_events is not None:
        if not isinstance(complete_events, list):
            _add_issue(
                errors,
                code="invalid_complete_events",
                path=f"{path}.complete_events",
                message="Expected list.",
            )
        else:
            for idx, event_id in enumerate(complete_events):
                if str(event_id) not in event_ids:
                    _add_issue(
                        errors,
                        code="unknown_event",
                        path=f"{path}.complete_events[{idx}]",
                        message=f"Unknown event '{event_id}'.",
                    )


def _rect(zone: dict[str, Any]) -> tuple[int, int, int, int] | None:
    vals = [_as_int(zone.get(k)) for k in ("x1", "y1", "x2", "y2")]
    if any(v is None for v in vals):
        return None
    x1, y1, x2, y2 = vals  # type: ignore[misc]
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def _rects_overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def _point_in_bounds(world_map: dict[str, Any], x: int, y: int) -> bool:
    rows = world_map.get("rows")
    return isinstance(rows, list) and 0 <= y < len(rows) and isinstance(rows[y], str) and 0 <= x < len(rows[y])


def _point_in_scene_zone(world_map: dict[str, Any], scene_id: str, x: int, y: int) -> bool:
    zones = world_map.get("scene_zones")
    if not isinstance(zones, list):
        return False
    for zone in zones:
        if not isinstance(zone, dict) or str(zone.get("scene_id") or "") != scene_id:
            continue
        rect = _rect(zone)
        if rect is None:
            continue
        x1, y1, x2, y2 = rect
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    return False


def _validate_visual_config(raw: dict[str, Any], rel_path: str, errors: list[Issue], warnings: list[Issue]) -> None:
    validate_visual_config(raw, rel_path, errors, warnings)


def _map_files(project_root: Path) -> list[Path]:
    default_map = project_root / "data" / "world" / "world_map.json"
    extra_dir = project_root / "data" / "world" / "maps"
    extras = sorted(extra_dir.glob("*.json")) if extra_dir.is_dir() else []
    return [default_map, *extras]


def _validate_location(
    location: Any,
    path: str,
    *,
    scene_ids: set[str],
    maps_by_scene: dict[str, list[dict[str, Any]]],
    errors: list[Issue],
    warnings: list[Issue],
) -> None:
    if location is None:
        return
    if not isinstance(location, dict):
        _add_issue(errors, code="invalid_shape", path=path, message="Expected object.")
        return
    scene_id = str(location.get("scene_id") or "")
    if not scene_id:
        _add_issue(errors, code="missing_scene", path=f"{path}.scene_id", message="Missing scene_id.")
        return
    if scene_id not in scene_ids:
        _add_issue(
            errors,
            code="unknown_scene",
            path=f"{path}.scene_id",
            message=f"Unknown scene '{scene_id}'.",
        )
        return

    x = _as_int(location.get("tile_x"))
    y = _as_int(location.get("tile_y"))
    if x is None or y is None:
        return
    candidates = maps_by_scene.get(scene_id) or []
    if not any(_point_in_bounds(world_map, x, y) for world_map in candidates):
        _add_issue(
            errors,
            code="location_out_of_bounds",
            path=path,
            message=f"Tile ({x}, {y}) is outside maps containing scene '{scene_id}'.",
        )
        return
    if not any(_point_in_scene_zone(world_map, scene_id, x, y) for world_map in candidates):
        _add_issue(
            warnings,
            code="location_scene_mismatch",
            path=path,
            message=f"Tile ({x}, {y}) is not inside a scene zone for '{scene_id}'.",
        )
    if not any(is_walkable(world_map, x, y) for world_map in candidates):
        _add_issue(
            warnings,
            code="location_not_walkable",
            path=path,
            message=f"Tile ({x}, {y}) is not walkable in scene '{scene_id}'.",
        )


def _collect_agents(project_root: Path, errors: list[Issue]) -> set[str]:
    meta_path = project_root / "characters" / "meta.json"
    raw = _load_json_file(meta_path, errors)
    if isinstance(raw, dict):
        seen: set[str] = set()
        for idx, row in _dict_rows(raw, "agents", "characters/meta.json", errors):
            agent_id = str(row.get("id") or "")
            if not agent_id:
                _add_issue(
                    errors,
                    code="missing_agent_id",
                    path=f"characters/meta.json.agents[{idx}].id",
                    message="Agent id is required.",
                )
                continue
            if agent_id in seen:
                _add_issue(
                    errors,
                    code="duplicate_agent_id",
                    path=f"characters/meta.json.agents[{idx}].id",
                    message=f"Duplicate agent id '{agent_id}'.",
                )
            seen.add(agent_id)
    return set(load_agent_profiles(project_root).keys())


def _validate_gate_shape(
    gate: Any,
    gate_path: str,
    raw_day: Any,
    nodes: dict[str, Any],
    errors: list[Issue],
) -> None:
    day = _as_int(raw_day)
    if day is None or day < 1:
        _add_issue(errors, code="invalid_day_gate", path=gate_path, message="Day gate key must be a positive integer.")
    if not isinstance(gate, dict):
        _add_issue(errors, code="invalid_shape", path=gate_path, message="Expected object.")
        return
    target = _as_int(gate.get("advance_to"))
    if target is not None and target <= (day or 0):
        _add_issue(errors, code="invalid_day_transition", path=f"{gate_path}.advance_to", message="advance_to must be greater than the source day.")
    next_node = gate.get("next_story_node_id")
    if next_node and str(next_node) not in {str(key) for key in nodes}:
        _add_issue(errors, code="unknown_story_node", path=f"{gate_path}.next_story_node_id", message=f"Unknown story node '{next_node}'.")
    required_flags = gate.get("required_flags")
    _validate_int_map(required_flags, f"{gate_path}.required_flags", errors)
    required_events = gate.get("required_events")
    if required_events is not None and not isinstance(required_events, list):
        _add_issue(errors, code="invalid_required_events", path=f"{gate_path}.required_events", message="Expected list.")
    any_flags = gate.get("required_any_flags")
    if any_flags is not None:
        if not isinstance(any_flags, list):
            _add_issue(errors, code="invalid_shape", path=f"{gate_path}.required_any_flags", message="Expected list of objects.")
        else:
            for idx, group in enumerate(any_flags):
                _validate_int_map(group, f"{gate_path}.required_any_flags[{idx}]", errors)


def _collect_story_nodes(project_root: Path, errors: list[Issue]) -> set[str]:
    path = project_root / "data" / "story" / "main_nodes.json"
    raw = _load_json_file(path, errors)
    nodes = raw.get("nodes") if isinstance(raw, dict) else None
    if nodes is None:
        return set()
    if not isinstance(nodes, dict):
        _add_issue(errors, code="invalid_shape", path="data/story/main_nodes.json.nodes", message="Expected object.")
        return set()

    gates = raw.get("day_gates") if isinstance(raw, dict) else None
    if gates is not None:
        if not isinstance(gates, dict):
            _add_issue(errors, code="invalid_shape", path="data/story/main_nodes.json.day_gates", message="Expected object.")
        else:
            for raw_day, gate in gates.items():
                gate_path = f"data/story/main_nodes.json.day_gates.{raw_day}"
                _validate_gate_shape(gate, gate_path, raw_day, nodes, errors)
    precapture_gates = raw.get("precapture_day_gates") if isinstance(raw, dict) else None
    if precapture_gates is not None:
        if not isinstance(precapture_gates, dict):
            _add_issue(errors, code="invalid_shape", path="data/story/main_nodes.json.precapture_day_gates", message="Expected object.")
        else:
            for raw_day, gate in precapture_gates.items():
                gate_path = f"data/story/main_nodes.json.precapture_day_gates.{raw_day}"
                _validate_gate_shape(gate, gate_path, raw_day, nodes, errors)
    return {str(key) for key in nodes}


def _collect_maps(
    project_root: Path,
    errors: list[Issue],
    warnings: list[Issue],
) -> tuple[
    dict[str, dict[str, Any]],
    set[str],
    dict[str, list[dict[str, Any]]],
    dict[str, dict[str, Any]],
    list[tuple[str, str]],
]:
    maps_by_id: dict[str, dict[str, Any]] = {}
    scene_ids: set[str] = set()
    maps_by_scene: dict[str, list[dict[str, Any]]] = {}
    poi_by_id: dict[str, dict[str, Any]] = {}
    activity_refs: list[tuple[str, str]] = []

    pending_transfers: list[tuple[str, str, str]] = []
    for map_path in _map_files(project_root):
        raw = _load_json_file(map_path, errors)
        if not isinstance(raw, dict):
            continue
        map_id = str(raw.get("id") or map_path.stem)
        rel_path = str(map_path.relative_to(project_root))
        if map_id in maps_by_id:
            _add_issue(
                errors,
                code="duplicate_map_id",
                path=rel_path,
                message=f"Duplicate map id '{map_id}'.",
            )
        maps_by_id[map_id] = raw
        _validate_visual_config(raw, rel_path, errors, warnings)

        width = _as_int(raw.get("width"))
        height = _as_int(raw.get("height"))
        rows = raw.get("rows")
        if width is None or height is None or not isinstance(rows, list):
            _add_issue(errors, code="invalid_map_shape", path=rel_path, message="Map needs width, height and rows.")
        else:
            if len(rows) != height:
                _add_issue(
                    errors,
                    code="map_height_mismatch",
                    path=f"{rel_path}.rows",
                    message=f"Expected {height} rows, found {len(rows)}.",
                )
            for idx, row in enumerate(rows):
                if not isinstance(row, str) or len(row) != width:
                    _add_issue(
                        errors,
                        code="map_width_mismatch",
                        path=f"{rel_path}.rows[{idx}]",
                        message=f"Expected width {width}.",
                    )

        spawn = raw.get("spawn") if isinstance(raw.get("spawn"), dict) else {}
        spawn_x = _as_int(spawn.get("x"))
        spawn_y = _as_int(spawn.get("y"))
        if spawn_x is None or spawn_y is None or not is_walkable(raw, spawn_x, spawn_y):
            _add_issue(
                errors,
                code="invalid_spawn",
                path=f"{rel_path}.spawn",
                message="Spawn must be an in-bounds walkable tile.",
            )

        zone_rects: list[tuple[str, tuple[int, int, int, int]]] = []
        for idx, zone in _dict_rows(raw, "scene_zones", rel_path, errors):
            zone_path = f"{rel_path}.scene_zones[{idx}]"
            scene_id = str(zone.get("scene_id") or "")
            if not scene_id:
                _add_issue(errors, code="missing_scene", path=zone_path, message="Scene zone needs scene_id.")
                continue
            scene_ids.add(scene_id)
            maps_by_scene.setdefault(scene_id, []).append(raw)
            rect = _rect(zone)
            if rect is None:
                _add_issue(errors, code="invalid_zone_rect", path=zone_path, message="Invalid zone bounds.")
            else:
                zone_rects.append((scene_id, rect))
                x1, y1, x2, y2 = rect
                if width is not None and height is not None and (x1 < 0 or y1 < 0 or x2 >= width or y2 >= height):
                    _add_issue(
                        errors,
                        code="zone_out_of_bounds",
                        path=zone_path,
                        message="Zone bounds must stay inside the map.",
                    )

            for entry_idx, entry in enumerate(zone.get("entry_points") or []):
                if not isinstance(entry, dict):
                    _add_issue(
                        errors,
                        code="invalid_entry_point",
                        path=f"{zone_path}.entry_points[{entry_idx}]",
                        message="Expected object.",
                    )
                    continue
                ex = _as_int(entry.get("x"))
                ey = _as_int(entry.get("y"))
                if ex is None or ey is None or not is_walkable(raw, ex, ey):
                    _add_issue(
                        errors,
                        code="entry_not_walkable",
                        path=f"{zone_path}.entry_points[{entry_idx}]",
                        message="Entry point must be a walkable tile.",
                    )

            for transfer_idx, transfer in enumerate(zone.get("transfers") or []):
                if isinstance(transfer, dict):
                    to_scene = str(transfer.get("to_scene_id") or "")
                    to_map = str(transfer.get("to_map_id") or map_id)
                    pending_transfers.append((to_scene, to_map, f"{zone_path}.transfers[{transfer_idx}]"))

        for (scene_a, rect_a), (scene_b, rect_b) in combinations(zone_rects, 2):
            if scene_a != scene_b and _rects_overlap(rect_a, rect_b):
                _add_issue(
                    warnings,
                    code="zone_overlap",
                    path=rel_path,
                    message=f"Scene zones '{scene_a}' and '{scene_b}' overlap.",
                )

        for idx, poi in _dict_rows(raw, "pois", rel_path, errors):
            poi_path = f"{rel_path}.pois[{idx}]"
            poi_id = str(poi.get("id") or "")
            if not poi_id:
                _add_issue(errors, code="missing_poi_id", path=poi_path, message="POI id is required.")
                continue
            if poi_id in poi_by_id:
                _add_issue(errors, code="duplicate_poi_id", path=poi_path, message=f"Duplicate POI id '{poi_id}'.")
            poi_by_id[poi_id] = poi
            scene_id = str(poi.get("scene_id") or "")
            if scene_id not in scene_ids:
                _add_issue(
                    errors,
                    code="unknown_scene",
                    path=f"{poi_path}.scene_id",
                    message=f"Unknown scene '{scene_id}'.",
                )
            px = _as_int(poi.get("tile_x"))
            py = _as_int(poi.get("tile_y"))
            approach_x = _as_int(poi.get("approach_tile_x"))
            approach_y = _as_int(poi.get("approach_tile_y"))
            has_approach = approach_x is not None or approach_y is not None
            approach_valid = False
            if px is None or py is None or not _point_in_bounds(raw, px, py):
                _add_issue(errors, code="poi_out_of_bounds", path=poi_path, message="POI tile is out of bounds.")
            elif has_approach and (
                approach_x is None
                or approach_y is None
                or not _point_in_bounds(raw, approach_x, approach_y)
                or not is_walkable(raw, approach_x, approach_y)
            ):
                _add_issue(
                    errors,
                    code="poi_approach_not_walkable",
                    path=poi_path,
                    message="POI approach tile must be an in-bounds walkable tile.",
                )
            else:
                approach_valid = has_approach and approach_x is not None and approach_y is not None
            if px is not None and py is not None and _point_in_bounds(raw, px, py) and not is_walkable(raw, px, py) and not approach_valid:
                _add_issue(warnings, code="poi_not_walkable", path=poi_path, message="POI tile is not walkable.")
            elif px is not None and py is not None and _point_in_bounds(raw, px, py) and spawn_x is not None and spawn_y is not None:
                reach_x = approach_x if approach_valid and approach_x is not None else px
                reach_y = approach_y if approach_valid and approach_y is not None else py
                path_to_poi = bfs_path(raw, spawn_x, spawn_y, reach_x, reach_y)
                if path_to_poi is None:
                    zone = zone_for_tile(raw, reach_x, reach_y)
                    severity_target = warnings if is_blocked_zone(zone) else errors
                    _add_issue(
                        severity_target,
                        code="poi_unreachable",
                        path=poi_path,
                        message="POI cannot be reached from spawn with current walkability and zone locks.",
                    )

            for action_idx, action in enumerate(poi.get("actions") or []):
                if not isinstance(action, dict):
                    _add_issue(
                        errors,
                        code="invalid_poi_action",
                        path=f"{poi_path}.actions[{action_idx}]",
                        message="Expected object.",
                    )
                    continue
                if action.get("type") == "scene_activity":
                    activity_id = str(action.get("activity_id") or action.get("id") or "")
                    activity_refs.append((activity_id, f"{poi_path}.actions[{action_idx}]"))

    for to_scene, to_map, path in pending_transfers:
        if to_map not in maps_by_id:
            _add_issue(errors, code="unknown_map", path=path, message=f"Unknown transfer map '{to_map}'.")
        if to_scene and to_scene not in scene_ids:
            _add_issue(errors, code="unknown_scene", path=path, message=f"Unknown transfer scene '{to_scene}'.")

    return maps_by_id, scene_ids, maps_by_scene, poi_by_id, activity_refs


def _validate_precapture_event_contract(
    event: dict[str, Any],
    event_path: str,
    errors: list[Issue],
) -> None:
    """Validate optional Pre-Capture authoring metadata without affecting legacy events."""
    act = event.get("precapture_act")
    if act is None:
        for container_key in ("metadata", "authored"):
            container = event.get(container_key)
            if isinstance(container, dict) and container.get("precapture_act") is not None:
                act = container.get("precapture_act")
                break
    if act is not None and str(act) not in PRECAPTURE_ACTS:
        _add_issue(
            errors,
            code="invalid_precapture_act",
            path=f"{event_path}.precapture_act",
            message=f"Pre-Capture act must be one of {sorted(PRECAPTURE_ACTS)}.",
        )

    key_node = event.get("precapture_key_node")
    if key_node is not None and not isinstance(key_node, bool):
        _add_issue(
            errors,
            code="invalid_precapture_key_node",
            path=f"{event_path}.precapture_key_node",
            message="Pre-Capture key-node marker must be boolean.",
        )

    if key_node is True and act is None:
        _add_issue(
            errors,
            code="precapture_key_node_act_missing",
            path=f"{event_path}.precapture_act",
            message="A Pre-Capture key node must declare one of the four authored acts.",
        )

    if key_node is not None or act is not None or event.get("precapture_endpoint") is not None:
        text_fields: list[tuple[str, str]] = []
        for field in PRECAPTURE_VISIBLE_FIELDS:
            value = event.get(field)
            if isinstance(value, str):
                text_fields.append((field, value))
        choices = event.get("choices") if isinstance(event.get("choices"), list) else []
        for choice_idx, choice in enumerate(choices):
            if not isinstance(choice, dict):
                continue
            for field in PRECAPTURE_VISIBLE_FIELDS:
                value = choice.get(field)
                if isinstance(value, str):
                    text_fields.append((f"choices[{choice_idx}].{field}", value))
        for field, value in text_fields:
            for forbidden, replacement in PRECAPTURE_TERM_REPLACEMENTS.items():
                if forbidden in value:
                    _add_issue(
                        errors,
                        code="precapture_legacy_term",
                        path=f"{event_path}.{field}",
                        message=f"Visible Pre-Capture text uses '{forbidden}'; use '{replacement}'.",
                    )
            for spoiler in PRECAPTURE_SPOILER_TERMS:
                if spoiler in value:
                    _add_issue(
                        errors,
                        code="precapture_spoiler_term",
                        path=f"{event_path}.{field}",
                        message=f"Visible Pre-Capture text reveals post-capture spoiler '{spoiler}'.",
                    )

    endpoint = event.get("precapture_endpoint")
    if endpoint is None:
        return
    if str(endpoint) not in PRECAPTURE_ENDPOINTS:
        _add_issue(
            errors,
            code="invalid_precapture_endpoint",
            path=f"{event_path}.precapture_endpoint",
            message=f"Pre-Capture endpoint must be one of {sorted(PRECAPTURE_ENDPOINTS)}.",
        )
        return
    if key_node is not True:
        _add_issue(
            errors,
            code="precapture_endpoint_not_key_node",
            path=f"{event_path}.precapture_key_node",
            message="The fixed capture endpoint must be marked as a key node.",
        )

    choices = event.get("choices") if isinstance(event.get("choices"), list) else []
    ending_ids = {
        str(choice.get("effects", {}).get("ending_id"))
        for choice in choices
        if isinstance(choice, dict) and isinstance(choice.get("effects"), dict)
        and choice.get("effects", {}).get("ending_id") is not None
    }
    if not ending_ids.intersection(PRECAPTURE_ENDPOINTS):
        _add_issue(
            errors,
            code="precapture_endpoint_effect_missing",
            path=f"{event_path}.choices",
            message="A marked Pre-Capture endpoint must set an allowed ending_id in a choice effect.",
        )
    elif str(endpoint) not in ending_ids:
        _add_issue(
            errors,
            code="precapture_endpoint_effect_mismatch",
            path=f"{event_path}.choices",
            message="The endpoint marker and choice ending_id must use the same capture endpoint.",
        )


def _validate_story_events(
    project_root: Path,
    *,
    known_agents: set[str],
    story_node_ids: set[str],
    scene_ids: set[str],
    maps_by_scene: dict[str, list[dict[str, Any]]],
    errors: list[Issue],
    warnings: list[Issue],
) -> set[str]:
    story_paths = [
        project_root / "data" / "story" / "events_chapter_01.json",
    ]
    source_rows: list[tuple[str, int, dict[str, Any]]] = []
    for story_path in story_paths:
        if not story_path.is_file() and story_path.name.startswith("events_precapture_"):
            continue
        raw = _load_json_file(story_path, errors)
        source_path = story_path.relative_to(project_root).as_posix()
        rows = _dict_rows(raw, "events", source_path, errors) if isinstance(raw, dict) else []
        source_rows.extend((source_path, idx, event) for idx, event in rows)
    event_ids = {str(event.get("id") or "") for _, _, event in source_rows if event.get("id")}
    seen: set[str] = set()
    for source_path, idx, event in source_rows:
        event_path = f"{source_path}.events[{idx}]"
        event_id = str(event.get("id") or "")
        if not event_id:
            _add_issue(errors, code="missing_event_id", path=event_path, message="Event id is required.")
        elif event_id in seen:
            _add_issue(errors, code="duplicate_event_id", path=event_path, message=f"Duplicate event id '{event_id}'.")
        seen.add(event_id)

        _validate_precapture_event_contract(event, event_path, errors)

        advance_band = event.get("advance_to_time_band")
        if advance_band is not None and str(advance_band) not in TIME_BANDS:
            _add_issue(
                errors,
                code="unknown_time_band",
                path=f"{event_path}.advance_to_time_band",
                message=f"Unknown authored time band '{advance_band}'.",
            )

        _validate_conditions(
            event.get("trigger"),
            f"{event_path}.trigger",
            known_agents=known_agents,
            story_node_ids=story_node_ids,
            errors=errors,
        )
        _validate_location(
            event.get("location"),
            f"{event_path}.location",
            scene_ids=scene_ids,
            maps_by_scene=maps_by_scene,
            errors=errors,
            warnings=warnings,
        )
        for part_idx, npc_id in enumerate(event.get("participants") or []):
            if str(npc_id) not in known_agents:
                _add_issue(
                    errors,
                    code="unknown_participant",
                    path=f"{event_path}.participants[{part_idx}]",
                    message=f"Unknown participant '{npc_id}'.",
                )

        choices = event.get("choices") if isinstance(event.get("choices"), list) else []
        choice_ids: set[str] = set()
        for choice_idx, choice in enumerate(choices):
            if not isinstance(choice, dict):
                _add_issue(
                    errors,
                    code="invalid_choice",
                    path=f"{event_path}.choices[{choice_idx}]",
                    message="Expected object.",
                )
                continue
            choice_path = f"{event_path}.choices[{choice_idx}]"
            choice_id = str(choice.get("id") or "")
            if not choice_id:
                _add_issue(errors, code="missing_choice_id", path=choice_path, message="Choice id is required.")
            elif choice_id in choice_ids:
                _add_issue(errors, code="duplicate_choice_id", path=choice_path, message=f"Duplicate choice id '{choice_id}'.")
            choice_ids.add(choice_id)
            _validate_conditions(
                choice.get("conditions") or choice.get("trigger"),
                f"{choice_path}.conditions",
                known_agents=known_agents,
                story_node_ids=story_node_ids,
                errors=errors,
            )
            _validate_effects(
                choice.get("effects"),
                f"{choice_path}.effects",
                known_agents=known_agents,
                story_node_ids=story_node_ids,
                scene_ids=scene_ids,
                event_ids=event_ids,
                errors=errors,
            )

        variant_ids: set[str] = set()
        for variant_idx, variant in enumerate(event.get("variants") or []):
            if not isinstance(variant, dict):
                _add_issue(
                    errors,
                    code="invalid_variant",
                    path=f"{event_path}.variants[{variant_idx}]",
                    message="Expected object.",
                )
                continue
            variant_path = f"{event_path}.variants[{variant_idx}]"
            variant_id = str(variant.get("id") or "")
            if variant_id and variant_id in variant_ids:
                _add_issue(errors, code="duplicate_variant_id", path=variant_path, message=f"Duplicate variant id '{variant_id}'.")
            if variant_id:
                variant_ids.add(variant_id)
            _validate_conditions(
                variant.get("when"),
                f"{variant_path}.when",
                known_agents=known_agents,
                story_node_ids=story_node_ids,
                errors=errors,
            )
            overrides = variant.get("choice_overrides")
            if overrides is not None:
                if not isinstance(overrides, dict):
                    _add_issue(errors, code="invalid_choice_overrides", path=f"{variant_path}.choice_overrides", message="Expected object.")
                else:
                    for choice_id in overrides:
                        if str(choice_id) not in choice_ids:
                            _add_issue(
                                errors,
                                code="unknown_choice_override",
                                path=f"{variant_path}.choice_overrides.{choice_id}",
                                message=f"Override references unknown choice '{choice_id}'.",
                            )

    return event_ids


def _validate_scene_activities(
    project_root: Path,
    *,
    known_agents: set[str],
    story_node_ids: set[str],
    scene_ids: set[str],
    poi_by_id: dict[str, dict[str, Any]],
    activity_refs: list[tuple[str, str]],
    errors: list[Issue],
) -> set[str]:
    raw = _load_json_file(project_root / "data" / "world" / "scene_activities.json", errors)
    rows = _dict_rows(raw, "activities", "data/world/scene_activities.json", errors) if isinstance(raw, dict) else []
    activity_ids: set[str] = set()
    for idx, activity in rows:
        activity_path = f"data/world/scene_activities.json.activities[{idx}]"
        activity_id = str(activity.get("id") or "")
        if not activity_id:
            _add_issue(errors, code="missing_activity_id", path=activity_path, message="Activity id is required.")
        elif activity_id in activity_ids:
            _add_issue(errors, code="duplicate_activity_id", path=activity_path, message=f"Duplicate activity id '{activity_id}'.")
        activity_ids.add(activity_id)

        scene_id = str(activity.get("scene_id") or "")
        if scene_id and scene_id not in scene_ids:
            _add_issue(errors, code="unknown_scene", path=f"{activity_path}.scene_id", message=f"Unknown scene '{scene_id}'.")
        scene_ids_raw = activity.get("scene_ids")
        allowed_scenes: set[str] = set()
        if isinstance(scene_ids_raw, list):
            for scene_idx, sid in enumerate(scene_ids_raw):
                sid = str(sid)
                allowed_scenes.add(sid)
                if sid not in scene_ids:
                    _add_issue(
                        errors,
                        code="unknown_scene",
                        path=f"{activity_path}.scene_ids[{scene_idx}]",
                        message=f"Unknown scene '{sid}'.",
                    )
        elif scene_id:
            allowed_scenes.add(scene_id)

        poi_id = str(activity.get("poi_id") or "")
        if poi_id:
            poi = poi_by_id.get(poi_id)
            if poi is None:
                _add_issue(errors, code="unknown_poi", path=f"{activity_path}.poi_id", message=f"Unknown POI '{poi_id}'.")
            elif allowed_scenes and str(poi.get("scene_id") or "") not in allowed_scenes:
                _add_issue(
                    errors,
                    code="activity_poi_scene_mismatch",
                    path=f"{activity_path}.poi_id",
                    message=f"POI '{poi_id}' is not in one of the activity scenes.",
                )

        for band_idx, band in enumerate(activity.get("time_bands") or []):
            if str(band) not in TIME_BANDS:
                _add_issue(
                    errors,
                    code="unknown_time_band",
                    path=f"{activity_path}.time_bands[{band_idx}]",
                    message=f"Unknown time band '{band}'.",
                )

        for part_idx, npc_id in enumerate(activity.get("participants") or []):
            if str(npc_id) not in known_agents:
                _add_issue(
                    errors,
                    code="unknown_participant",
                    path=f"{activity_path}.participants[{part_idx}]",
                    message=f"Unknown participant '{npc_id}'.",
                )

        requirements = activity.get("requirements")
        if requirements is not None:
            _validate_conditions(
                requirements,
                f"{activity_path}.requirements",
                known_agents=known_agents,
                story_node_ids=story_node_ids,
                errors=errors,
            )

        _validate_effects(
            activity.get("effects"),
            f"{activity_path}.effects",
            known_agents=known_agents,
            story_node_ids=story_node_ids,
            scene_ids=scene_ids,
            event_ids=None,
            errors=errors,
        )

        choice_ids: set[str] = set()
        for choice_idx, choice in enumerate(activity.get("choices") or []):
            if not isinstance(choice, dict):
                _add_issue(
                    errors,
                    code="invalid_activity_choice",
                    path=f"{activity_path}.choices[{choice_idx}]",
                    message="Expected object.",
                )
                continue
            choice_path = f"{activity_path}.choices[{choice_idx}]"
            choice_id = str(choice.get("id") or "")
            if not choice_id:
                _add_issue(errors, code="missing_choice_id", path=choice_path, message="Choice id is required.")
            elif choice_id in choice_ids:
                _add_issue(errors, code="duplicate_choice_id", path=choice_path, message=f"Duplicate choice id '{choice_id}'.")
            choice_ids.add(choice_id)
            _validate_effects(
                choice.get("effects"),
                f"{choice_path}.effects",
                known_agents=known_agents,
                story_node_ids=story_node_ids,
                scene_ids=scene_ids,
                event_ids=None,
                errors=errors,
            )

    for activity_id, path in activity_refs:
        if activity_id not in activity_ids:
            _add_issue(errors, code="unknown_activity", path=path, message=f"Unknown scene activity '{activity_id}'.")

    return activity_ids


def _validate_schedules(
    project_root: Path,
    *,
    known_agents: set[str],
    scene_ids: set[str],
    maps_by_scene: dict[str, list[dict[str, Any]]],
    errors: list[Issue],
) -> int:
    path = project_root / "data" / "world" / "schedules.json"
    if not path.is_file():
        return 0
    raw = _load_json_file(path, errors)
    if not isinstance(raw, dict):
        return 0

    checked = 0
    for npc_id, schedule in raw.items():
        if npc_id == "v":
            continue
        schedule_path = f"data/world/schedules.json.{npc_id}"
        if str(npc_id) not in known_agents:
            _add_issue(
                errors,
                code="unknown_schedule_agent",
                path=schedule_path,
                message=f"Unknown scheduled agent '{npc_id}'.",
            )
        if not isinstance(schedule, dict):
            _add_issue(errors, code="invalid_schedule", path=schedule_path, message="Expected object.")
            continue
        table = schedule.get("default")
        if not isinstance(table, dict):
            _add_issue(errors, code="invalid_schedule", path=f"{schedule_path}.default", message="Expected object.")
            continue
        for time_band, entry in table.items():
            entry_path = f"{schedule_path}.default.{time_band}"
            if str(time_band) not in TIME_BANDS:
                _add_issue(errors, code="unknown_time_band", path=entry_path, message=f"Unknown time band '{time_band}'.")
            if not isinstance(entry, dict):
                _add_issue(errors, code="invalid_schedule_entry", path=entry_path, message="Expected object.")
                continue
            checked += 1
            scene_id = str(entry.get("scene_id") or "")
            if scene_id not in scene_ids:
                _add_issue(errors, code="unknown_scene", path=f"{entry_path}.scene_id", message=f"Unknown scene '{scene_id}'.")
                continue
            x = _as_int(entry.get("tile_x"))
            y = _as_int(entry.get("tile_y"))
            if x is None or y is None:
                _add_issue(errors, code="missing_schedule_tile", path=entry_path, message="Schedule entry needs tile_x and tile_y.")
                continue
            candidates = maps_by_scene.get(scene_id) or []
            if not any(_point_in_bounds(world_map, x, y) for world_map in candidates):
                _add_issue(
                    errors,
                    code="schedule_out_of_bounds",
                    path=entry_path,
                    message=f"Tile ({x}, {y}) is outside maps containing scene '{scene_id}'.",
                )
            elif not any(_point_in_scene_zone(world_map, scene_id, x, y) for world_map in candidates):
                _add_issue(
                    errors,
                    code="schedule_scene_mismatch",
                    path=entry_path,
                    message=f"NPC schedule tile ({x}, {y}) is not inside scene zone '{scene_id}'.",
                )
            elif not any(is_walkable(world_map, x, y) for world_map in candidates):
                _add_issue(
                    errors,
                    code="schedule_not_walkable",
                    path=entry_path,
                    message=f"NPC schedule tile ({x}, {y}) is not walkable in scene '{scene_id}'.",
                )
    return checked




def _collect_written_flags(project_root: Path) -> set[str]:
    """Collect authored flags that can satisfy a narrative date gate."""
    written: set[str] = set()

    def collect_effects(raw: Any) -> None:
        if not isinstance(raw, dict):
            return
        for key in ("flags", "flag_deltas"):
            values = raw.get(key)
            if isinstance(values, dict):
                written.update(str(item) for item in values)

    for story_path in (
        project_root / "data" / "story" / "events_chapter_01.json",
    ):
        if not story_path.is_file():
            continue
        story = _load_json_file(story_path, [])
        if isinstance(story, dict):
            for event in story.get("events") or []:
                if not isinstance(event, dict):
                    continue
                for choice in event.get("choices") or []:
                    if isinstance(choice, dict):
                        collect_effects(choice.get("effects"))

    activity_path = project_root / "data" / "world" / "scene_activities.json"
    activities = _load_json_file(activity_path, [])
    if isinstance(activities, dict):
        for activity in activities.get("activities") or []:
            if not isinstance(activity, dict):
                continue
            collect_effects(activity.get("effects"))
            for choice in activity.get("choices") or []:
                if isinstance(choice, dict):
                    collect_effects(choice.get("effects"))
    return written


def _validate_day_gate_producers(
    project_root: Path,
    *,
    event_ids: set[str],
    errors: list[Issue],
) -> None:
    path = project_root / "data" / "story" / "main_nodes.json"
    raw = _load_json_file(path, errors)
    gates = raw.get("day_gates") if isinstance(raw, dict) else {}
    precapture_gates = raw.get("precapture_day_gates") if isinstance(raw, dict) else {}
    if not isinstance(gates, dict):
        gates = {}
    if not isinstance(precapture_gates, dict):
        precapture_gates = {}
    written_flags = _collect_written_flags(project_root)
    for raw_day, gate in {**gates, **precapture_gates}.items():
        if not isinstance(gate, dict):
            continue
        gate_path = (
            f"data/story/main_nodes.json.precapture_day_gates.{raw_day}"
            if raw_day in precapture_gates
            else f"data/story/main_nodes.json.day_gates.{raw_day}"
        )
        for key in (gate.get("required_flags") or {}):
            if str(key) not in written_flags:
                _add_issue(
                    errors,
                    code="unproducible_day_gate_flag",
                    path=f"{gate_path}.required_flags.{key}",
                    message=f"No authored story/activity effect writes day-gate flag '{key}'.",
                )
        for group_index, group in enumerate(gate.get("required_any_flags") or []):
            if not isinstance(group, dict):
                continue
            for key in group:
                if str(key) not in written_flags:
                    _add_issue(
                        errors,
                        code="unproducible_day_gate_flag",
                        path=f"{gate_path}.required_any_flags[{group_index}].{key}",
                        message=f"No authored story/activity effect writes day-gate flag '{key}'.",
                    )
        for index, event_id in enumerate(gate.get("required_events") or []):
            if str(event_id) not in event_ids:
                _add_issue(
                    errors,
                    code="unknown_day_gate_event",
                    path=f"{gate_path}.required_events[{index}]",
                    message=f"Unknown day-gate event '{event_id}'.",
                )

def validate_project(project_root: Path) -> dict[str, Any]:
    """Validate content config references without mutating world state."""
    project_root = project_root.resolve()
    errors: list[Issue] = []
    warnings: list[Issue] = []

    known_agents = _collect_agents(project_root, errors)
    story_node_ids = _collect_story_nodes(project_root, errors)
    maps_by_id, scene_ids, maps_by_scene, poi_by_id, activity_refs = _collect_maps(
        project_root,
        errors,
        warnings,
    )
    event_ids = _validate_story_events(
        project_root,
        known_agents=known_agents,
        story_node_ids=story_node_ids,
        scene_ids=scene_ids,
        maps_by_scene=maps_by_scene,
        errors=errors,
        warnings=warnings,
    )
    activity_ids = _validate_scene_activities(
        project_root,
        known_agents=known_agents,
        story_node_ids=story_node_ids,
        scene_ids=scene_ids,
        poi_by_id=poi_by_id,
        activity_refs=activity_refs,
        errors=errors,
    )
    _validate_day_gate_producers(
        project_root,
        event_ids=event_ids,
        errors=errors,
    )

    schedule_entries = _validate_schedules(
        project_root,
        known_agents=known_agents,
        scene_ids=scene_ids,
        maps_by_scene=maps_by_scene,
        errors=errors,
    )

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "agents": len(known_agents),
            "maps": len(maps_by_id),
            "scenes": len(scene_ids),
            "pois": len(poi_by_id),
            "scene_activities": len(activity_ids),
            "story_nodes": len(story_node_ids),
            "story_events": len(load_story_events(project_root)),
            "validated_story_events": len(event_ids),
            "schedule_entries": schedule_entries,
        },
    }
