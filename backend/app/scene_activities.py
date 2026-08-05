from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def default_scene_activities_path(project_root: Path) -> Path:
    return project_root / "data" / "world" / "scene_activities.json"


def load_scene_activities(project_root: Path) -> dict[str, Any]:
    path = default_scene_activities_path(project_root)
    if not path.is_file():
        return {"v": 1, "activities": []}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"v": 1, "activities": []}
    if not isinstance(raw, dict):
        return {"v": 1, "activities": []}
    activities = raw.get("activities")
    if not isinstance(activities, list):
        raw["activities"] = []
    return raw


def find_scene_activity(project_root: Path, activity_id: str) -> dict[str, Any] | None:
    aid = str(activity_id or "").strip()
    if not aid:
        return None
    for item in load_scene_activities(project_root).get("activities") or []:
        if isinstance(item, dict) and item.get("id") == aid:
            return item
    return None


def _public_activity_preview(item: dict[str, Any]) -> dict[str, Any]:
    """Expose decision-relevant categories without leaking authored effects or memory text."""
    effects = item.get("effects") if isinstance(item.get("effects"), dict) else {}
    resource_costs: dict[str, int] = {}
    for source_key, public_key in (
        ("hp_cost", "hp"),
        ("mp_cost", "mp"),
        ("stamina_cost", "stamina"),
    ):
        try:
            amount = int(effects.get(source_key) or 0)
        except (TypeError, ValueError):
            amount = 0
        if amount > 0:
            resource_costs[public_key] = amount

    reward_kinds: list[str] = []
    if isinstance(effects.get("relationship"), dict) and effects["relationship"]:
        reward_kinds.append("relationship")
    if isinstance(effects.get("memory"), dict) and effects["memory"]:
        reward_kinds.append("memory")
    if isinstance(effects.get("flags"), dict) and effects["flags"]:
        reward_kinds.append("progress")
    if isinstance(effects.get("resource_changes"), dict) and effects["resource_changes"]:
        reward_kinds.append("resources")

    return {
        "resource_costs": resource_costs,
        "reward_kinds": reward_kinds,
        "variable_resource_cost": item.get("interaction_kind") == "boundary_patrol",
    }


def public_scene_activities(project_root: Path) -> dict[str, Any]:
    raw = load_scene_activities(project_root)
    out = []
    for item in raw.get("activities") or []:
        if not isinstance(item, dict):
            continue
        row = {
            key: item.get(key)
            for key in (
                "id",
                "scene_id",
                "scene_ids",
                "poi_id",
                "title",
                "label",
                "description",
                "repeat",
                "time_cost",
                "time_bands",
                "requirements",
                "participants",
                "tags",
                "interaction_kind",
            )
            if key in item
        }
        row["preview"] = _public_activity_preview(item)
        choices = item.get("choices")
        if isinstance(choices, list):
            row["choices"] = [
                {
                    key: choice.get(key)
                    for key in ("id", "label", "hint", "tone")
                    if isinstance(choice, dict) and key in choice
                }
                for choice in choices
                if isinstance(choice, dict)
            ]
        out.append(row)
    return {"v": raw.get("v", 1), "activities": out}
