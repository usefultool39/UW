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


def _public_choice_preview(choice: dict[str, Any]) -> dict[str, Any]:
    """Expose choice stakes without leaking authored memory text or control effects."""
    effects = choice.get("effects") if isinstance(choice.get("effects"), dict) else {}
    explicit = choice.get("preview") if isinstance(choice.get("preview"), dict) else {}
    relationship = effects.get("relationship") if isinstance(effects.get("relationship"), dict) else {}
    memory = effects.get("memory") if isinstance(effects.get("memory"), dict) else {}
    promises = effects.get("promises") if isinstance(effects.get("promises"), dict) else {}
    tensions = effects.get("tensions") if isinstance(effects.get("tensions"), dict) else {}
    resource_costs: dict[str, int] = {}
    resource_restores: dict[str, int] = {}
    for source_key, public_key in (("hp_cost", "hp"), ("mp_cost", "mp"), ("stamina_cost", "stamina")):
        try:
            amount = int(effects.get(source_key) or 0)
        except (TypeError, ValueError):
            amount = 0
        if amount > 0:
            resource_costs[public_key] = amount
    for source_key, public_key in (("hp_restore", "hp"), ("mp_restore", "mp"), ("stamina_restore", "stamina")):
        try:
            amount = int(effects.get(source_key) or 0)
        except (TypeError, ValueError):
            amount = 0
        if amount > 0:
            resource_restores[public_key] = amount
    return {
        "relationship": explicit.get("relationship") if isinstance(explicit.get("relationship"), dict) else relationship,
        "remembered_by": explicit.get("remembered_by") if isinstance(explicit.get("remembered_by"), list) else list(memory.keys()),
        "promises": explicit.get("promises") if isinstance(explicit.get("promises"), list) else list(promises.keys()),
        "tensions": explicit.get("tensions") if isinstance(explicit.get("tensions"), list) else list(tensions.keys()),
        "consequences": explicit.get("consequences") if isinstance(explicit.get("consequences"), list) else [],
        "resource_costs": resource_costs,
        "resource_restores": resource_restores,
    }


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
    if (
        isinstance(effects.get("item_deltas"), dict) and effects["item_deltas"]
    ) or (
        isinstance(effects.get("weather_item_deltas"), dict) and effects["weather_item_deltas"]
    ):
        reward_kinds.append("items")

    preview = {
        "resource_costs": resource_costs,
        "reward_kinds": reward_kinds,
        "variable_resource_cost": item.get("interaction_kind") == "boundary_patrol",
    }
    player_facing_benefit = item.get("player_facing_benefit")
    if isinstance(player_facing_benefit, str) and player_facing_benefit.strip():
        preview["benefit_text"] = player_facing_benefit.strip()
    return preview


def _public_loadout(item: dict[str, Any]) -> dict[str, Any] | None:
    """Expose only loadout choices; never expose authoritative effects."""
    config = item.get("loadout")
    if not isinstance(config, dict):
        return None
    rows = []
    for option in config.get("allowed_items") or []:
        if not isinstance(option, dict):
            continue
        item_id = str(option.get("item_id") or "").strip()
        if not item_id:
            continue
        rows.append({
            "item_id": item_id,
            "label": str(option.get("label") or item_id),
            "hint": str(option.get("hint") or ""),
            "consume": bool(option.get("consume", False)),
        })
    return {
        "max_items": max(0, int(config.get("max_items") or 0)),
        "allowed_items": rows,
        "combination_labels": [
            {
                "id": str(row.get("id") or ""),
                "label": str(row.get("label") or ""),
                "item_ids": [str(value) for value in row.get("item_ids") or []],
            }
            for row in config.get("combination_bonuses") or []
            if isinstance(row, dict) and row.get("id")
        ],
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
                "hidden",
            )
            if key in item
        }
        row["preview"] = _public_activity_preview(item)
        loadout = _public_loadout(item)
        if loadout is not None:
            row["loadout"] = loadout
        reading_chain = item.get("reading_chain")
        if isinstance(reading_chain, dict):
            public_steps = []
            for step in reading_chain.get("steps") or []:
                if not isinstance(step, dict):
                    continue
                public_options = []
                for option in step.get("options") or []:
                    if not isinstance(option, dict):
                        continue
                    public_options.append({
                        key: option.get(key)
                        for key in ("id", "label", "note", "feedback")
                        if key in option
                    })
                public_steps.append({
                    key: step.get(key)
                    for key in ("id", "label", "prompt", "helper")
                    if key in step
                } | {"options": public_options})
            public_paths = []
            for path in reading_chain.get("paths") or []:
                if not isinstance(path, dict):
                    continue
                public_paths.append({
                    key: path.get(key)
                    for key in ("choice_id", "steps", "label", "success_text")
                    if key in path
                })
            if len(public_steps) == 3 and public_paths:
                row["reading_chain"] = {
                    "intro": str(reading_chain.get("intro") or ""),
                    "steps": public_steps,
                    "paths": public_paths,
                }

        choices = item.get("choices")
        if isinstance(choices, list):
            row["choices"] = [
                {
                    **{
                        key: choice.get(key)
                        for key in ("id", "label", "hint", "tone")
                        if isinstance(choice, dict) and key in choice
                    },
                    "preview": _public_choice_preview(choice),
                }
                for choice in choices
                if isinstance(choice, dict)
            ]
        out.append(row)
    return {"v": raw.get("v", 1), "activities": out}
