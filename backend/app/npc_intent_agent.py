"""Optional AI recommendation loop for authored NPC intents.

This module is intentionally preview-only: it recommends an existing intent
and response option, while Session remains the only code allowed to execute
flags, relationship changes, memories, rewards, or day transitions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ai_provider import adapter_enabled, generate_text, provider_meta
from .intent_policy import screen_intent_candidate
from .llm_config import dialogue_model
from .models import NpcIntent, WorldState
from .npc_intents import build_npc_intents
from .world import _agent_by_id


def _extract_object(raw: str) -> dict[str, Any]:
    text = str(raw or "").strip().replace("```json", "").replace("```", "").strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        value = json.loads(text[start : end + 1])
        if isinstance(value, dict):
            return value
    raise ValueError("intent_candidate_json_invalid")


def _fallback_candidate(intents: list[NpcIntent], npc_id: str) -> dict[str, Any] | None:
    available = [item for item in intents if item.npc_id == npc_id and item.response_options]
    if not available:
        return None
    intent = sorted(available, key=lambda item: (-int(item.priority), item.id))[0]
    option = intent.response_options[0]
    return {
        "intent_id": intent.id,
        "response_id": option.get("id"),
        "confidence": 0.5,
        "reason": "当前最高优先级的已 authored NPC 事件。",
    }


def build_intent_user_message(
    state: WorldState,
    npc_id: str,
    intents: list[NpcIntent],
    memory_context: dict[str, Any] | None = None,
) -> str:
    agent = _agent_by_id(state, npc_id)
    rows = []
    for intent in intents:
        if intent.npc_id != npc_id or not intent.response_options:
            continue
        rows.append(
            {
                "intent_id": intent.id,
                "title": intent.title,
                "description": intent.description,
                "priority": intent.priority,
                "scene_id": intent.scene_id,
                "response_options": [
                    {"id": item.get("id"), "label": item.get("label"), "hint": item.get("hint")}
                    for item in intent.response_options
                    if isinstance(item, dict)
                ],
            }
        )
    return "\n".join(
        [
            f"NPC={npc_id}",
            f"day={state.day}, time_band={state.time_band}, story_node={state.story_node_id}",
            f"scene={agent.scene_id}, mood={agent.mood}, goal={agent.current_goal or 'none'}",
            f"important_memory_context={json.dumps(memory_context or {}, ensure_ascii=False)}",
            f"current_authored_intents={json.dumps(rows, ensure_ascii=False)}",
            '只推荐当前列表中的一项，严格输出 JSON：{"intent_id":"...","response_id":"...","confidence":0.0,"reason":"..."}',
            "不得创建新 ID，不得输出 flags、relationship、memory、reward、day 或任意世界状态修改。",
        ]
    )


def propose_npc_intent(
    *,
    state: WorldState,
    npc_id: str,
    project_root: Path,
    memory_context: dict[str, Any] | None = None,
    allow_agent: bool = True,
) -> dict[str, Any]:
    intents = build_npc_intents(project_root, state)
    fallback = _fallback_candidate(intents, npc_id)
    source = "fallback"
    raw: str | None = None
    error: str | None = None

    if allow_agent and adapter_enabled():
        try:
            raw = generate_text(
                system=(
                    "你是单人 RPG 的 NPC 意图推荐器。规则和 authored 内容是唯一事实。"
                    "你只能从给定列表选择 intent_id 和 response_id，不能改世界。只输出 JSON。"
                ),
                user=build_intent_user_message(state, npc_id, intents, memory_context),
                model=dialogue_model(),
                max_tokens=300,
                temperature=0.1,
            )
            candidate = _extract_object(raw)
            source = "agent"
        except Exception as exc:
            candidate = fallback
            error = str(exc)
    else:
        candidate = fallback

    normalized, decision = screen_intent_candidate(
        candidate,
        npc_id=npc_id,
        intents=intents,
        source=source,
    )
    return {
        "ok": normalized is not None,
        "npc_id": npc_id,
        "candidate": normalized or candidate,
        "decision": decision,
        "source": source,
        "provider": provider_meta() if source == "agent" else {"provider": "fallback"},
        "raw": raw,
        "error": error,
    }
