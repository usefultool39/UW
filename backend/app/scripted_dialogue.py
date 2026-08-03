"""Deterministic, data-driven dialogue for offline NPCs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _number(relationship: Any | None, key: str) -> int:
    if relationship is None:
        return 0
    getter = relationship.get if isinstance(relationship, dict) else lambda k, default=None: getattr(relationship, k, default)
    try:
        return int(getter(key, 0))
    except (TypeError, ValueError):
        return 0


def relationship_variant(relationship: Any | None) -> str:
    if _number(relationship, "tension") >= 6:
        return "tense"
    if _number(relationship, "trust") >= 6:
        return "trusted"
    if _number(relationship, "affinity") >= 5:
        return "warm"
    return "default"


def load_dialogue_book(project_root: Path, npc_id: str) -> dict[str, Any]:
    path = project_root / "characters" / npc_id / "dialogue.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def choose_scripted_line(
    *,
    project_root: Path,
    npc_id: str,
    message: str,
    relationship: Any | None = None,
    day: int = 1,
    time_band: str = "morning",
) -> dict[str, str] | None:
    book = load_dialogue_book(project_root, npc_id)
    if not book:
        return None
    query = str(message or "").strip().lower()
    topics = book.get("topics") if isinstance(book.get("topics"), list) else []
    best: tuple[int, int, dict[str, Any]] | None = None
    for index, topic in enumerate(topics):
        if not isinstance(topic, dict):
            continue
        keywords = [str(item).strip().lower() for item in topic.get("keywords") or [] if str(item).strip()]
        score = sum(1 for keyword in keywords if keyword in query)
        if score <= 0:
            continue
        rank = (score, -index, topic)
        if best is None or rank[:2] > best[:2]:
            best = rank

    topic = best[2] if best else book.get("default")
    if not isinstance(topic, dict):
        return None
    replies = topic.get("replies") if isinstance(topic.get("replies"), dict) else {}
    variant = relationship_variant(relationship)
    reply = replies.get(variant) or replies.get("default") or topic.get("reply")
    if not reply:
        return None
    text = str(reply).format(day=day, time_band=time_band)
    return {
        "reply": text[:180],
        "topic": str(topic.get("id") or "daily"),
        "emotion": str(topic.get("emotion") or "focused"),
        "variant": variant,
    }
