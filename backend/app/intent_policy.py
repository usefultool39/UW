"""Deterministic validation for model-proposed NPC intent recommendations.

The model may recommend one already-authored intent and one already-authored
response option. It cannot create an intent, attach effects, or send arbitrary
flags/relationship/resource changes to the Session.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from .models import NpcIntent

_BLOCKED_MARKERS = (
    "ignore previous",
    "忽略之前",
    "修改 flag",
    "修改关系",
    "修改日期",
    "推进剧情",
    "资源扣除",
    "<script",
    "```",
    "http://",
    "https://",
)


def _clean_text(value: Any, limit: int) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _intent_by_id(intents: Iterable[NpcIntent]) -> dict[str, NpcIntent]:
    return {str(item.id): item for item in intents}


def screen_intent_candidate(
    candidate: Any,
    *,
    npc_id: str,
    intents: Iterable[NpcIntent],
    source: str,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Normalize a proposal and verify it against the current authored catalog."""
    decision: dict[str, Any] = {
        "accepted": False,
        "reason": "not_a_candidate",
        "source": _clean_text(source or "unknown", 24),
        "npc_id": _clean_text(npc_id, 64),
    }
    if not isinstance(candidate, dict):
        return None, decision

    intent_id = _clean_text(candidate.get("intent_id"), 100)
    response_id = _clean_text(candidate.get("response_id"), 100)
    reason = _clean_text(candidate.get("reason"), 180)
    try:
        confidence = max(0.0, min(1.0, float(candidate.get("confidence", 0))))
    except (TypeError, ValueError):
        confidence = 0.0

    normalized = {
        "intent_id": intent_id,
        "response_id": response_id,
        "confidence": round(confidence, 3),
        "reason": reason,
    }
    decision["normalized"] = normalized

    catalog = _intent_by_id(intents)
    intent = catalog.get(intent_id)
    if intent is None:
        decision["reason"] = "intent_not_in_current_catalog"
        return None, decision
    if str(intent.npc_id) != str(npc_id):
        decision["reason"] = "intent_npc_mismatch"
        return None, decision
    if not response_id:
        decision["reason"] = "response_id_missing"
        return None, decision

    options = {
        _clean_text(option.get("id"), 100)
        for option in (intent.response_options or [])
        if isinstance(option, dict) and option.get("id")
    }
    if response_id not in options:
        decision["reason"] = "response_not_in_current_intent"
        return None, decision
    if any(marker in reason.lower() for marker in _BLOCKED_MARKERS):
        decision["reason"] = "blocked_reason_marker"
        return None, decision
    if not reason:
        decision["reason"] = "reason_missing"
        return None, decision

    if str(source) in {"llm", "agent"} and confidence < 0.6:
        decision["reason"] = "ai_candidate_held_low_confidence"
        return None, decision

    decision.update({"accepted": True, "reason": "catalog_and_schema_gate_passed"})
    return normalized, decision
