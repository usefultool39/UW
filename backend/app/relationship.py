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
    agent = next((item for item in state.agents if item.id == npc_id), None)
    active_intent = next(
        (item for item in state.npc_intents if item.npc_id == npc_id),
        None,
    )
    return {
        "npc_id": npc_id,
        "display": profile.display,
        "role": profile.role,
        "mind": _npc_mind_snapshot(state, npc_id, rel, agent, active_intent),
        "relationship": {
            **rel.model_dump(mode="json"),
            "note": relationship_note(rel),
        },
        "important_memories": summary.get("important_memories") or [],
        "promises": summary.get("promises") or [],
        "tensions": summary.get("tensions") or [],
    }


def _need_note(agent: Any | None) -> str:
    if agent is None:
        return "状态未知"
    stamina = int(getattr(agent, "stamina", 0))
    hunger = int(getattr(agent, "hunger", 0))
    mood = int(getattr(agent, "mood", 50))
    if stamina < 25:
        return "体力偏低，倾向保守行动"
    if hunger > 70:
        return "饥饿感明显，容易被日常安排影响"
    if mood < 35:
        return "情绪紧绷，需要更明确的安全感"
    if mood > 70:
        return "状态稳定，愿意主动推进计划"
    return "状态平稳，按今日目标行动"


def _npc_beliefs(state: WorldState, npc_id: str, rel: RelationshipState) -> list[str]:
    flags = state.flags or {}
    beliefs: list[str] = []
    if flags.get("clue_boundary_record"):
        beliefs.append("玩家已经读到北境旧记录，静默线不再只是传闻。")
    if flags.get("forest_anomaly_seen"):
        beliefs.append("森林异常已经被亲眼确认，后续行动需要选边站。")
    if flags.get("boundary_risk_taken"):
        beliefs.append("玩家曾独自靠近异常方向，风险判断需要被看紧。")
    if npc_id == "alice" and flags.get("alice_reassured_before_boundary_record"):
        beliefs.append("玩家曾主动承诺不会独自靠近北边。")
    if npc_id == "eugeo" and flags.get("eugeo_tree_rule_questioned"):
        beliefs.append("玩家把古誓树训练和世界规则联系在一起。")
    if rel.tension >= 8:
        beliefs.append("关系里有明显不安，下一次选择会被放大解读。")
    elif rel.trust >= 8:
        beliefs.append("玩家已经积累了一些可信信号，可以被纳入计划。")
    return beliefs[:4]


def _npc_mind_snapshot(
    state: WorldState,
    npc_id: str,
    rel: RelationshipState,
    agent: Any | None,
    active_intent: Any | None,
) -> dict[str, Any]:
    current_goal = getattr(agent, "current_goal", None) or "观察今天的村庄变化"
    focus = active_intent.title if active_intent is not None else "暂无主动邀约"
    reason = active_intent.reason if active_intent is not None else "当前没有新的主动事件，仍会按日程行动。"
    return {
        "current_goal": current_goal,
        "scene_id": getattr(agent, "scene_id", state.scene_id),
        "mood": getattr(agent, "mood", 50),
        "need": _need_note(agent),
        "attitude": relationship_note(rel),
        "active_focus": focus,
        "active_reason": reason,
        "beliefs": _npc_beliefs(state, npc_id, rel),
    }
