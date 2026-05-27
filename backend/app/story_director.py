from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import WorldState
from .relationship import apply_relationship_effects, ensure_relationships


def default_events_path(project_root: Path, chapter_id: str = "chapter_01") -> Path:
    suffix = chapter_id.replace("chapter_", "chapter_")
    if suffix == "chapter_01":
        return project_root / "data" / "story" / "events_chapter_01.json"
    return project_root / "data" / "story" / f"events_{chapter_id}.json"


def load_story_events(project_root: Path, chapter_id: str = "chapter_01") -> list[dict[str, Any]]:
    path = default_events_path(project_root, chapter_id)
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    events = raw.get("events") if isinstance(raw, dict) else raw
    return [e for e in events if isinstance(e, dict)] if isinstance(events, list) else []


def _flag_value(state: WorldState, key: str) -> int:
    return int((state.flags or {}).get(key, 0))


def _matches_required_flags(state: WorldState, required: dict[str, Any] | None) -> bool:
    if not required:
        return True
    for key, expected in required.items():
        if _flag_value(state, str(key)) < int(expected):
            return False
    return True


def _matches_forbidden_flags(state: WorldState, forbidden: dict[str, Any] | None) -> bool:
    if not forbidden:
        return True
    for key, value in forbidden.items():
        if _flag_value(state, str(key)) >= int(value):
            return False
    return True


def _relationship_value(state: WorldState, path: str) -> int:
    if "." not in path:
        return 0
    npc_id, field = path.split(".", 1)
    rel = (state.relationships or {}).get(npc_id)
    if rel is None or not hasattr(rel, field):
        return 0
    return int(getattr(rel, field))


def _matches_relationships(state: WorldState, required: dict[str, Any] | None) -> bool:
    if not required:
        return True
    for key, expected in required.items():
        if _relationship_value(state, str(key)) < int(expected):
            return False
    return True


def _matches_conditions(state: WorldState, conditions: dict[str, Any] | None) -> bool:
    if not conditions:
        return True

    day_min = conditions.get("day_min")
    day_max = conditions.get("day_max")
    if day_min is not None and state.day < int(day_min):
        return False
    if day_max is not None and state.day > int(day_max):
        return False

    time_bands = conditions.get("time_bands")
    if time_bands is None and conditions.get("time_band") is not None:
        time_bands = [conditions.get("time_band")]
    if isinstance(time_bands, list) and time_bands and state.time_band not in time_bands:
        return False

    story_nodes = conditions.get("story_nodes")
    if isinstance(story_nodes, list) and story_nodes and state.story_node_id not in story_nodes:
        return False

    if not _matches_required_flags(state, conditions.get("required_flags")):
        return False
    if not _matches_forbidden_flags(state, conditions.get("forbidden_flags")):
        return False
    if not _matches_relationships(state, conditions.get("required_relationship")):
        return False

    return True


def event_is_available(state: WorldState, event: dict[str, Any]) -> bool:
    if event.get("chapter") and event.get("chapter") != state.chapter_id:
        return False
    event_id = str(event.get("id") or "")
    if not event_id:
        return False
    if event_id in (state.completed_event_ids or []) and not event.get("repeatable"):
        return False

    trigger = event.get("trigger") if isinstance(event.get("trigger"), dict) else {}
    if not _matches_conditions(state, trigger):
        return False

    return True


def choice_is_available(state: WorldState | None, choice: dict[str, Any]) -> bool:
    if state is None:
        return True
    conditions = choice.get("conditions") or choice.get("trigger")
    if not isinstance(conditions, dict):
        return True
    return _matches_conditions(state, conditions)


def _event_variant(event: dict[str, Any], state: WorldState | None) -> dict[str, Any]:
    if state is None:
        return {}
    variants = event.get("variants") if isinstance(event.get("variants"), list) else []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        when = variant.get("when") if isinstance(variant.get("when"), dict) else {}
        if _matches_conditions(state, when):
            return variant
    return {}


def public_event_view(event: dict[str, Any], state: WorldState | None = None) -> dict[str, Any]:
    variant = _event_variant(event, state)
    choices = event.get("choices") if isinstance(event.get("choices"), list) else []
    choice_overrides = variant.get("choice_overrides") if isinstance(variant.get("choice_overrides"), dict) else {}

    def choice_preview(choice: dict[str, Any]) -> dict[str, Any]:
        effects = choice.get("effects") if isinstance(choice.get("effects"), dict) else {}
        relationship = effects.get("relationship") if isinstance(effects.get("relationship"), dict) else {}
        memory = effects.get("memory") if isinstance(effects.get("memory"), dict) else {}
        promises = effects.get("promises") if isinstance(effects.get("promises"), dict) else {}
        tensions = effects.get("tensions") if isinstance(effects.get("tensions"), dict) else {}
        return {
            "relationship": relationship,
            "remembered_by": list(memory.keys()),
            "promises": list(promises.keys()),
            "tensions": list(tensions.keys()),
            "ending_id": effects.get("ending_id"),
        }

    description = variant.get("description") or event.get("description")
    if variant.get("append_description"):
        description = f"{description} {variant.get('append_description')}"

    return {
        "id": event.get("id"),
        "chapter": event.get("chapter"),
        "title": variant.get("title") or event.get("title"),
        "description": description,
        "day": (event.get("trigger") or {}).get("day_min") if isinstance(event.get("trigger"), dict) else None,
        "day_range": [
            (event.get("trigger") or {}).get("day_min"),
            (event.get("trigger") or {}).get("day_max"),
        ] if isinstance(event.get("trigger"), dict) else None,
        "location": event.get("location") or {},
        "participants": event.get("participants") or [],
        "kind": event.get("kind") or "event",
        "choices": [
            {
                "id": c.get("id"),
                "label": (choice_overrides.get(str(c.get("id") or "")) or {}).get("label") or c.get("label"),
                "hint": (choice_overrides.get(str(c.get("id") or "")) or {}).get("hint") or c.get("hint"),
                "preview": choice_preview(c),
            }
            for c in choices
            if isinstance(c, dict) and choice_is_available(state, c)
        ],
        "variant_id": variant.get("id"),
    }


def available_events(project_root: Path, state: WorldState) -> list[dict[str, Any]]:
    state = ensure_relationships(state)
    events = load_story_events(project_root, state.chapter_id)
    return [public_event_view(e, state) for e in events if event_is_available(state, e)]


def _apply_flags(flags: dict[str, int], effects: dict[str, Any]) -> dict[str, int]:
    out = dict(flags)
    for key, value in (effects.get("flags") or {}).items():
        out[str(key)] = int(value)
    for key, value in (effects.get("flag_deltas") or {}).items():
        out[str(key)] = int(out.get(str(key), 0)) + int(value)
    return out


def _memory_rows(
    *,
    event_id: str,
    day: int,
    effects: dict[str, Any],
) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    memory = effects.get("memory") or {}
    if isinstance(memory, dict):
        for npc_id, raw in memory.items():
            if isinstance(raw, dict):
                row = dict(raw)
            else:
                row = {"summary": str(raw)}
            row.setdefault("day", day)
            row.setdefault("type", "choice")
            row.setdefault("weight", 4)
            row.setdefault("source_event", event_id)
            rows.append((str(npc_id), row))
    return rows


def choose_event(
    *,
    project_root: Path,
    state: WorldState,
    event_id: str,
    choice_id: str,
) -> tuple[WorldState, dict[str, Any]]:
    events = load_story_events(project_root, state.chapter_id)
    event = next((e for e in events if e.get("id") == event_id), None)
    if event is None:
        return state, {"ok": False, "error": "unknown_event"}
    if not event_is_available(state, event):
        return state, {"ok": False, "error": "event_not_available"}

    raw_choices = event.get("choices") if isinstance(event.get("choices"), list) else []
    choices = [c for c in raw_choices if isinstance(c, dict) and choice_is_available(state, c)]
    choice = next((c for c in choices if isinstance(c, dict) and c.get("id") == choice_id), None)
    if choice is None:
        return state, {"ok": False, "error": "unknown_choice"}

    effects = choice.get("effects") if isinstance(choice.get("effects"), dict) else {}
    next_state = ensure_relationships(state)
    flags = _apply_flags(next_state.flags or {}, effects)
    next_state = next_state.model_copy(update={"flags": flags})

    next_state, relationship_changes = apply_relationship_effects(
        next_state,
        effects.get("relationship") if isinstance(effects, dict) else {},
    )

    completed = list(next_state.completed_event_ids or [])
    for completed_id in [event_id, *(effects.get("complete_events") or [])]:
        if completed_id and completed_id not in completed:
            completed.append(str(completed_id))

    active = [eid for eid in (next_state.active_event_ids or []) if eid != event_id]
    story_node_id = effects.get("story_node_id") or next_state.story_node_id
    ending_id = effects.get("ending_id") or next_state.chapter_ending_id

    unlocked = list(next_state.unlocked_scenes or [])
    for sid in effects.get("unlock_scenes") or []:
        if sid not in unlocked:
            unlocked.append(str(sid))

    next_state = next_state.model_copy(
        update={
            "story_node_id": story_node_id,
            "chapter_ending_id": ending_id,
            "completed_event_ids": completed,
            "active_event_ids": active,
            "unlocked_scenes": unlocked,
        }
    )

    memory_writes = _memory_rows(event_id=event_id, day=next_state.day, effects=effects)
    promises = effects.get("promises") or {}
    tensions = effects.get("tensions") or {}

    result = {
        "ok": True,
        "event": public_event_view(event, state),
        "choice": {
            "id": choice.get("id"),
            "label": choice.get("label"),
            "result_text": choice.get("result_text") or effects.get("result_text"),
        },
        "relationship_changes": relationship_changes,
        "memory_writes": memory_writes,
        "promises": promises,
        "tensions": tensions,
        "ending_id": ending_id,
    }
    return next_state, result
