from __future__ import annotations

from pathlib import Path
from typing import Any

from .agent_registry import get_agent_profile
from .models import RelationshipState, WorldState


RELATIONSHIP_FIELDS = {"affinity", "trust", "tension"}


def clamp_score(value: int) -> int:
    return max(-100, min(100, int(value)))


def default_relationships(agent_ids: list[str]) -> dict[str, RelationshipState]:
    return {agent_id: RelationshipState() for agent_id in agent_ids}


def ensure_relationships(state: WorldState) -> WorldState:
    relationships = dict(state.relationships or {})
    changed = False
    for agent in state.agents:
        if agent.id not in relationships:
            relationships[agent.id] = RelationshipState()
            changed = True
    if not changed:
        return state
    return state.model_copy(update={"relationships": relationships})


def relationship_note(rel: RelationshipState) -> str:
    if rel.tension >= 45:
        return "明显戒备"
    if rel.trust >= 45:
        return "愿意相信你"
    if rel.affinity >= 35:
        return "对你亲近"
    if rel.tension >= 18:
        return "有些担心"
    if rel.trust <= -25:
        return "仍在怀疑"
    return rel.mood_note or "平稳"


def apply_relationship_effects(
    state: WorldState,
    effects: dict[str, Any] | None,
) -> tuple[WorldState, list[dict[str, Any]]]:
    if not effects:
        return ensure_relationships(state), []

    state = ensure_relationships(state)
    relationships = {
        npc_id: rel.model_copy(deep=True)
        for npc_id, rel in (state.relationships or {}).items()
    }
    changes: list[dict[str, Any]] = []

    def add_delta(npc_id: str, field: str, delta: int) -> None:
        if field not in RELATIONSHIP_FIELDS:
            return
        rel = relationships.get(npc_id, RelationshipState())
        before = int(getattr(rel, field))
        after = clamp_score(before + int(delta))
        setattr(rel, field, after)
        rel.mood_note = relationship_note(rel)
        relationships[npc_id] = rel
        changes.append(
            {
                "npc_id": npc_id,
                "field": field,
                "before": before,
                "after": after,
                "delta": after - before,
            }
        )

    for raw_key, raw_value in effects.items():
        if isinstance(raw_value, dict):
            npc_id = str(raw_key)
            for field, delta in raw_value.items():
                add_delta(npc_id, str(field), int(delta))
            continue
        key = str(raw_key)
        if "." not in key:
            continue
        npc_id, field = key.split(".", 1)
        add_delta(npc_id, field, int(raw_value))

    return state.model_copy(update={"relationships": relationships}), changes


def npc_profile(
    *,
    project_root: Path,
    state: WorldState,
    npc_id: str,
    memory_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = ensure_relationships(state)
    profile = get_agent_profile(project_root, npc_id)
    rel = (state.relationships or {}).get(npc_id, RelationshipState())
    summary = memory_summary or {}
    return {
        "npc_id": npc_id,
        "display": profile.display,
        "role": profile.role,
        "relationship": {
            **rel.model_dump(mode="json"),
            "note": relationship_note(rel),
        },
        "important_memories": summary.get("important_memories") or [],
        "promises": summary.get("promises") or [],
        "tensions": summary.get("tensions") or [],
    }
