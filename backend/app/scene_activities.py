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


def public_scene_activities(project_root: Path) -> dict[str, Any]:
    raw = load_scene_activities(project_root)
    out = []
    for item in raw.get("activities") or []:
        if not isinstance(item, dict):
            continue
        out.append(
            {
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
                )
                if key in item
            }
        )
    return {"v": raw.get("v", 1), "activities": out}
