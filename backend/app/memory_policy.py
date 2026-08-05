"""Deterministic gate for model-produced memory candidates.

Authored story effects are trusted data and use the existing Session paths.
Model text is not trusted as a permanent fact: it must pass this narrow schema
and content gate before it can enter ``important_memories``. Rejected or held
candidates remain in the dialogue audit row only.
"""

from __future__ import annotations

import re
from typing import Any

_ALLOWED_TYPES = {"dialogue", "observation", "promise", "tension", "npc_intent_response"}
_ALLOWED_SOURCES = {"fallback", "scripted", "llm", "agent"}
_BLOCKED_MARKERS = (
    "ignore previous",
    "忽略之前",
    "修改 flag",
    "修改关系",
    "修改日期",
    "剧情推进",
    "资源扣除",
    "系统提示",
    "<script",
    "```",
    "http://",
    "https://",
)


def _clean_text(value: Any, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def screen_memory_candidate(
    candidate: Any,
    *,
    source: str,
    player_message: str = "",
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Return a normalized candidate and an auditable deterministic decision."""
    decision: dict[str, Any] = {
        "accepted": False,
        "reason": "not_a_candidate",
        "source": str(source or "unknown"),
    }
    if not isinstance(candidate, dict):
        return None, decision
    if str(source) not in _ALLOWED_SOURCES:
        decision["reason"] = "source_not_allowed"
        return None, decision

    memory_type = _clean_text(candidate.get("type") or "dialogue", 40)
    summary = _clean_text(candidate.get("summary"), 180)
    try:
        weight = max(1, min(5, int(candidate.get("weight", 0))))
    except (TypeError, ValueError):
        weight = 0

    if memory_type not in _ALLOWED_TYPES:
        decision["reason"] = "type_not_allowed"
        return None, decision
    if len(summary) < 8:
        decision["reason"] = "summary_too_short"
        return None, decision
    if weight < 1:
        decision["reason"] = "invalid_weight"
        return None, decision
    lowered = summary.lower()
    if any(marker in lowered for marker in _BLOCKED_MARKERS):
        decision["reason"] = "blocked_content_marker"
        return None, decision
    if "{" in summary or "}" in summary or "\x00" in summary:
        decision["reason"] = "structured_or_control_content"
        return None, decision

    normalized = {"type": memory_type, "summary": summary, "weight": weight}

    # Ordinary fallback dialogue produces a low-weight conversational hint, not
    # a durable fact. Keep it in the event audit unless an authored path marks
    # it as genuinely important (weight >= 3).
    if str(source) in {"fallback", "scripted"} and weight < 3:
        decision["reason"] = "scripted_candidate_below_threshold"
        decision["normalized"] = normalized
        return None, decision

    # AI output is a suggestion. Only high-confidence candidates can become
    # important memories; low-confidence output stays visible in the audit.
    if str(source) in {"llm", "agent"} and weight < 4:
        decision["reason"] = "ai_candidate_held_low_confidence"
        decision["normalized"] = normalized
        return None, decision

    decision.update({"accepted": True, "reason": "schema_and_content_gate_passed", "normalized": normalized})
    return normalized, decision
