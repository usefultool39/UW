from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import WorldState
from .relationship import apply_relationship_effects, ensure_relationships
from .story_catalog import default_catalog_path, load_main_nodes


TERMINAL_CHAPTER_ENDINGS = frozenset({"alice_captured", "precapture_alice_captured"})


def chapter_is_terminal(state: WorldState) -> bool:
    return state.chapter_ending_id in TERMINAL_CHAPTER_ENDINGS


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
    rows = raw.get("events") if isinstance(raw, dict) else raw
    return [e for e in rows if isinstance(e, dict)] if isinstance(rows, list) else []


def _flag_value(state: WorldState, key: str) -> int:
    return int((state.flags or {}).get(key, 0))


def _is_precapture_event(event: dict[str, Any]) -> bool:
    event_id = str(event.get("id") or "")
    return bool(event.get("precapture_key_node") or event.get("precapture_act") or event_id.startswith("ch1pc_"))


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


def _matches_required_any_flags(state: WorldState, required: dict[str, Any] | None) -> bool:
    if not required:
        return True
    return any(_flag_value(state, str(key)) >= int(expected) for key, expected in required.items())


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


def _matches_conditions(
    state: WorldState,
    conditions: dict[str, Any] | None,
    *,
    allow_time_slip: bool = False,
) -> bool:
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
    if (
        isinstance(time_bands, list)
        and time_bands
        and state.time_band not in time_bands
        and not allow_time_slip
    ):
        return False

    story_nodes = conditions.get("story_nodes")
    if isinstance(story_nodes, list) and story_nodes and state.story_node_id not in story_nodes:
        return False

    if not _matches_required_flags(state, conditions.get("required_flags")):
        return False
    if not _matches_required_any_flags(state, conditions.get("required_any_flags")):
        return False
    if not _matches_forbidden_flags(state, conditions.get("forbidden_flags")):
        return False
    if not _matches_relationships(state, conditions.get("required_relationship")):
        return False

    return True


def event_is_available(state: WorldState, event: dict[str, Any]) -> bool:
    if chapter_is_terminal(state):
        return False
    if event.get("chapter") and event.get("chapter") != state.chapter_id:
        return False
    event_id = str(event.get("id") or "")
    if not event_id:
        return False
    precapture_event = _is_precapture_event(event)
    if _flag_value(state, "precapture_mode") >= 1 and not precapture_event:
        return False
    if _flag_value(state, "legacy_story_mode") >= 1 and precapture_event:
        return False
    if event_id in (state.completed_event_ids or []) and not event.get("repeatable"):
        return False

    trigger = event.get("trigger") if isinstance(event.get("trigger"), dict) else {}
    if not _matches_conditions(state, trigger, allow_time_slip=precapture_event):
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
        explicit = choice.get("preview") if isinstance(choice.get("preview"), dict) else {}
        effects = choice.get("effects") if isinstance(choice.get("effects"), dict) else {}
        relationship = effects.get("relationship") if isinstance(effects.get("relationship"), dict) else {}
        memory = effects.get("memory") if isinstance(effects.get("memory"), dict) else {}
        promises = effects.get("promises") if isinstance(effects.get("promises"), dict) else {}
        tensions = effects.get("tensions") if isinstance(effects.get("tensions"), dict) else {}
        return {
            "relationship": explicit.get("relationship") if isinstance(explicit.get("relationship"), dict) else relationship,
            "remembered_by": explicit.get("remembered_by") if isinstance(explicit.get("remembered_by"), list) else list(memory.keys()),
            "promises": explicit.get("promises") if isinstance(explicit.get("promises"), list) else list(promises.keys()),
            "tensions": explicit.get("tensions") if isinstance(explicit.get("tensions"), list) else list(tensions.keys()),
            "consequences": explicit.get("consequences") if isinstance(explicit.get("consequences"), list) else [],
            "ending_id": explicit.get("ending_id", effects.get("ending_id")),
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
        "required_for_day": bool(event.get("required_for_day", False)),
        "day_end_gate": bool(event.get("day_end_gate", False)),
        "advance_policy": event.get("advance_policy"),
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
    if not _is_precapture_event(event):
        flags["legacy_story_mode"] = 1
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

    authored_time_band = event.get("advance_to_time_band")
    if authored_time_band in {"morning", "afternoon", "evening", "night"}:
        next_state = next_state.model_copy(update={"time_band": authored_time_band})

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


def load_day_gates(project_root: Path) -> dict[str, Any]:
    """Load explicit narrative day gates from the main story catalog."""
    catalog = load_main_nodes(default_catalog_path(project_root))
    raw = catalog.get("day_gates") if isinstance(catalog, dict) else {}
    return raw if isinstance(raw, dict) else {}


def day_gate_status(project_root: Path, state: WorldState, day: int | None = None) -> dict[str, Any]:
    """Return whether the current day may be resolved.

    Days without an explicit gate remain legacy-compatible for older month-plan
    tests/content. Day 1-3 are explicitly gated by the new data contract.
    """
    current_day = int(day if day is not None else state.day)
    catalog = load_main_nodes(default_catalog_path(project_root))
    gate_key = "precapture_day_gates"
    raw_gates = catalog.get(gate_key) if isinstance(catalog, dict) else {}
    gates = raw_gates if isinstance(raw_gates, dict) else {}
    gate = gates.get(str(current_day))
    if not isinstance(gate, dict):
        return {
            "ready": True,
            "mode": "legacy_no_gate",
            "day": current_day,
            "missing": [],
            "gate": None,
        }

    missing: list[dict[str, Any]] = []
    required_flags = gate.get("required_flags") if isinstance(gate.get("required_flags"), dict) else {}
    for key, expected in required_flags.items():
        actual = _flag_value(state, str(key))
        if actual < int(expected):
            missing.append({"type": "flag", "key": str(key), "expected": int(expected), "actual": actual})

    required_events = gate.get("required_events") if isinstance(gate.get("required_events"), list) else []
    completed = set(state.completed_event_ids or [])
    for event_id in required_events:
        if str(event_id) not in completed:
            missing.append({"type": "event", "id": str(event_id)})

    any_groups = gate.get("required_any_flags") if isinstance(gate.get("required_any_flags"), list) else []
    for group in any_groups:
        if not isinstance(group, dict):
            continue
        if not any(_flag_value(state, str(key)) >= int(expected) for key, expected in group.items()):
            missing.append({"type": "any_flags", "options": {str(k): int(v) for k, v in group.items()}})

    return {
        "ready": not missing,
        "mode": "explicit",
        "day": current_day,
        "missing": missing,
        "gate": gate,
    }
