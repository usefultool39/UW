from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .agent_registry import get_agent_profile
from .ai_provider import adapter_enabled, generate_text, provider_meta
from .llm_agent import (
    _call_minimax_chat,
    _call_minimax_openai_chat,
    _extract_json_objects,
    _extract_text_blocks,
    _is_minimax_mode,
    _is_openai_chat_model,
    _resolve_base_url,
    _sanitize_api_key,
    _select_api_key,
)
from .llm_config import dialogue_model
from .models import AgentState, WorldState
from .npc_runtime import npc_runtime_for
from .scripted_dialogue import choose_scripted_line


def _agent_by_id(state: WorldState, npc_id: str) -> AgentState:
    for agent in state.agents:
        if agent.id == npc_id:
            return agent
    raise KeyError(npc_id)


def _read_persona_excerpt(project_root: Path, npc_id: str, limit: int = 220) -> str:
    path = project_root / "characters" / npc_id / "persona.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    text = " ".join(line.strip() for line in text.splitlines() if line.strip())
    return text[:limit]


def _mood_emotion(agent: AgentState) -> str:
    if agent.mood >= 72:
        return "calm"
    if agent.mood >= 45:
        return "focused"
    if agent.mood >= 25:
        return "tired"
    return "uneasy"


def _persona_text(project_root: Path, npc_id: str) -> str:
    path = project_root / "characters" / npc_id / "persona.md"
    if not path.is_file():
        return f"你是角色 {npc_id}。保持世界观一致，用短句回应玩家。"
    return path.read_text(encoding="utf-8").strip()[:1800]


def _memory_lines(memory_context: dict[str, Any] | None) -> str:
    if not memory_context:
        return "(none)"
    parts: list[str] = []
    for item in memory_context.get("important_memories") or []:
        if isinstance(item, dict) and item.get("summary"):
            parts.append(f"- 重要记忆: {item.get('summary')}")
    for item in memory_context.get("promises") or []:
        parts.append(f"- 承诺: {item}")
    for item in memory_context.get("tensions") or []:
        parts.append(f"- 紧张: {item}")
    return "\n".join(parts) if parts else "(none)"


def _relationship_lines(relationship: Any | None) -> str:
    if relationship is None:
        return "affinity=0, trust=0, tension=0, mood_note=平稳"
    getter = relationship.get if isinstance(relationship, dict) else lambda key, default=None: getattr(relationship, key, default)
    return (
        f"affinity={getter('affinity', 0)}, "
        f"trust={getter('trust', 0)}, "
        f"tension={getter('tension', 0)}, "
        f"mood_note={getter('mood_note', '平稳')}"
    )



def _relationship_number(relationship: Any | None, key: str) -> int:
    if relationship is None:
        return 0
    getter = relationship.get if isinstance(relationship, dict) else lambda k, default=None: getattr(relationship, k, default)
    try:
        return int(getter(key, 0))
    except (TypeError, ValueError):
        return 0


def _parse_dialogue_json(text: str, fallback_emotion: str) -> dict[str, Any]:
    candidates = _extract_json_objects(text) or [text]
    last_err: Exception | None = None
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as e:
            last_err = e
            continue
        reply = str(data.get("reply") or "").strip()
        if not reply:
            continue
        memory = data.get("memory_candidate")
        if isinstance(memory, dict):
            memory = {
                "type": str(memory.get("type") or "dialogue")[:40],
                "summary": str(memory.get("summary") or "")[:160],
                "weight": max(1, min(5, int(memory.get("weight", 2)))),
            }
            if not memory["summary"]:
                memory = None
        else:
            memory = None
        return {
            "reply": reply[:180],
            "emotion": str(data.get("emotion") or fallback_emotion)[:40],
            "intent": str(data.get("intent") or "respond")[:64],
            "memory_candidate": memory,
        }
    raise ValueError(f"无法解析对话 JSON: {last_err}")


def llm_dialogue_reply(
    *,
    state: WorldState,
    npc_id: str,
    message: str,
    project_root: Path,
    recent_memories: list[dict[str, Any]] | None = None,
    memory_context: dict[str, Any] | None = None,
    relationship: Any | None = None,
) -> dict[str, Any]:
    model = dialogue_model()
    if adapter_enabled():
        # Provider-specific keys are resolved by ai_provider.py.
        anthropic_key = minimax_key = api_key = "adapter"
    else:
        anthropic_key = _sanitize_api_key(os.getenv("ANTHROPIC_API_KEY") or "")
        minimax_key = _sanitize_api_key(os.getenv("MINIMAX_API_KEY") or "")
        api_key = _select_api_key(
            model=model, anthropic_key=anthropic_key, minimax_key=minimax_key
        )
        if not api_key:
            raise RuntimeError("llm_key_missing")

    agent = _agent_by_id(state, npc_id)
    profile = get_agent_profile(project_root, npc_id)
    persona = _persona_text(project_root, npc_id)
    memory_tail = recent_memories or []
    system = (
        "你是单人 AI RPG 中的 NPC 对话引擎。规则定事实，AI 只负责表达。\n"
        "你不能推进主线，不能修改 flags、关系值、剧情节点或世界状态。\n"
        "只输出一个 JSON 对象，不要 markdown，不要解释。\n"
        "JSON 字段: reply, emotion, intent, memory_candidate。\n"
        "reply 必须是中文短句，最多 80 字；memory_candidate 可为 null。"
    )
    user = "\n".join(
        [
            f"NPC={profile.display} ({npc_id})",
            f"角色定位={profile.role}",
            f"世界: day={state.day}, time_band={state.time_band}, story_node={state.story_node_id}, ending={state.chapter_ending_id or 'none'}",
            f"NPC状态: stamina={agent.stamina}, mood={agent.mood}, goal={agent.current_goal or 'none'}, scene={agent.scene_id}",
            f"关系: {_relationship_lines(relationship)}",
            f"重要记忆:\n{_memory_lines(memory_context)}",
            f"最近事件JSON: {json.dumps(memory_tail[-4:], ensure_ascii=False)}",
            f"Persona:\n{persona}",
            f"玩家说: {message[:160]}",
            '请输出: {"reply":"...","emotion":"calm|focused|uneasy|warm|guarded","intent":"...","memory_candidate":{"type":"dialogue","summary":"...","weight":1}}',
        ]
    )

    if adapter_enabled():
        content = generate_text(
            system=system,
            user=user,
            model=model,
            max_tokens=600,
            temperature=0.2,
        )
    elif _is_openai_chat_model(model):
        base_url = (
            os.getenv("MINIMAX_OPENAI_BASE_URL")
            or "https://api.minimax.io/v1"
        ).strip()
        content = _call_minimax_openai_chat(
            api_key=api_key,
            model=model,
            system=system,
            user=user,
            base_url=base_url,
            max_tokens=600,
        )
    elif _is_minimax_mode(model=model, has_minimax_key=bool(minimax_key)):
        base_url = (os.getenv("MINIMAX_BASE_URL") or "https://api.minimax.chat/v1").strip()
        content = _call_minimax_chat(
            api_key=api_key,
            model=model,
            system=system,
            user=user,
            base_url=base_url,
        )
    else:
        from anthropic import Anthropic

        base_url = _resolve_base_url(model=model, has_minimax_key=bool(minimax_key))
        client_kwargs: dict[str, str] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = Anthropic(**client_kwargs)
        message_obj = client.messages.create(
            model=model,
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": [{"type": "text", "text": user}]}],
        )
        content = _extract_text_blocks(message_obj.content)

    parsed = _parse_dialogue_json(content, _mood_emotion(agent))
    if parsed.get("memory_candidate") is None and message.strip():
        parsed["memory_candidate"] = {
            "type": "dialogue",
            "summary": f"玩家对{profile.display}说：{message.strip()[:60]}",
            "weight": 2,
        }
    return {
        "ok": True,
        "npc_id": npc_id,
        **parsed,
        "source": "llm",
        **({"llm_provider": provider_meta(model)} if adapter_enabled() else {}),
    }


def fallback_dialogue_reply(
    *,
    state: WorldState,
    npc_id: str,
    message: str,
    project_root: Path,
    recent_memories: list[dict[str, Any]] | None = None,
    memory_context: dict[str, Any] | None = None,
    relationship: Any | None = None,
) -> dict[str, Any]:
    agent = _agent_by_id(state, npc_id)
    name = get_agent_profile(project_root, npc_id).display
    msg = (message or "").strip()
    lower = msg.lower()
    persona = _read_persona_excerpt(project_root, npc_id)
    memories = recent_memories or []
    important = (memory_context or {}).get("important_memories") or []
    memory_hint = ""
    if important:
        top = important[0]
        if isinstance(top, dict) and top.get("summary"):
            memory_hint = f" 我还记得：{str(top['summary'])[:32]}。"
    rel_text = _relationship_lines(relationship)
    rel_affinity = _relationship_number(relationship, "affinity")
    rel_trust = _relationship_number(relationship, "trust")
    rel_tension = _relationship_number(relationship, "tension")
    scripted_line = choose_scripted_line(
        project_root=project_root,
        npc_id=npc_id,
        message=msg,
        relationship=relationship,
        day=state.day,
        time_band=state.time_band,
    )

    if scripted_line:
        reply = scripted_line["reply"]
    elif any(key in msg for key in ("北", "边界", "禁忌", "异常")):
        if npc_id == "alice":
            reply = "别急着靠近边界。那里太安静了，安静到不像是自然的沉默。"
        elif npc_id == "eugeo":
            reply = "我也注意到了。我们可以去看，但最好先想清楚该怎么回来。"
        else:
            reply = "边界不是普通的地点。先收集线索，再决定要不要越线。"
    elif any(key in msg for key in ("树", "斧", "训练", "砍")):
        if npc_id == "eugeo":
            reply = "巨树不会因为一两下挥斧改变什么，但每天的节奏会留下痕迹。"
        elif npc_id == "alice":
            reply = "训练可以继续，但别把自己累到听不见风里的变化。"
        else:
            reply = "把训练当成观察世界规则的方式，会比单纯消耗体力更有用。"
    elif any(key in msg for key in ("书", "阅读", "图书", "典籍")):
        if npc_id == "alice":
            reply = "书里的规则总写得很清楚，可真正站到规则面前时，人会犹豫。"
        elif npc_id == "eugeo":
            reply = "如果书库里有线索，我们应该把它和今天看到的事放在一起想。"
        else:
            reply = "书本给的是旧答案，今天发生的事可能需要新的问题。"
    elif any(key in msg for key in ("你好", "在吗", "嗨", "hello", "hi")):
        reply = f"我在，{name}看向你，像是刚从自己的思绪里回过神来。"
    elif agent.stamina < 30:
        reply = "我有点累，不过还能听你说完。你刚才想确认什么？"
    elif state.time_band == "night":
        reply = "夜里声音会变得很远。要说重要的事，现在反而合适。"
    else:
        if rel_tension >= 6:
            reply = "嗯，我听着。只是我还在担心你会不会把危险说得太轻。"
        elif rel_trust >= 6:
            reply = "嗯，我相信你不是随口问问。把你看到的细节说完，我们一起判断。"
        elif rel_affinity >= 5:
            reply = "嗯，我听着。今天的事有点怪，但和你一起想会容易些。"
        elif rel_tension > 0:
            reply = "嗯，我听着。只是今天有些话说出口以后，就很难再当作没发生过。"
        else:
            reply = "嗯，我听着。今天的村子和平时有一点不一样，你也感觉到了吗？"

    if memory_hint and len(reply) < 70:
        reply = f"{reply}{memory_hint}"

    if persona:
        reply = reply[:140]

    return {
        "ok": True,
        "npc_id": npc_id,
        "reply": reply,
        "emotion": scripted_line.get("emotion", _mood_emotion(agent)) if scripted_line else _mood_emotion(agent),
        "intent": scripted_line.get("topic", "daily") if scripted_line else "daily",
        "scripted_variant": scripted_line.get("variant") if scripted_line else None,
        "memory_candidate": {
            "type": "dialogue",
            "summary": f"玩家对{name}说：{msg[:60] or '（沉默）'}",
            "weight": 2 if msg else 1,
        },
        "source": "fallback",
    }


def dialogue_reply(
    *,
    state: WorldState,
    npc_id: str,
    message: str,
    project_root: Path,
    recent_memories: list[dict[str, Any]] | None = None,
    memory_context: dict[str, Any] | None = None,
    relationship: Any | None = None,
) -> dict[str, Any]:
    runtime = npc_runtime_for(npc_id)
    if runtime == "scripted":
        scripted = fallback_dialogue_reply(
            state=state,
            npc_id=npc_id,
            message=message,
            project_root=project_root,
            recent_memories=recent_memories,
            memory_context=memory_context,
            relationship=relationship,
        )
        scripted["source"] = "fallback"
        scripted["npc_runtime"] = runtime
        return scripted

    try:
        result = llm_dialogue_reply(
            state=state,
            npc_id=npc_id,
            message=message,
            project_root=project_root,
            recent_memories=recent_memories,
            memory_context=memory_context,
            relationship=relationship,
        )
        result["npc_runtime"] = runtime
        return result
    except Exception as exc:
        fallback = fallback_dialogue_reply(
            state=state,
            npc_id=npc_id,
            message=message,
            project_root=project_root,
            recent_memories=recent_memories,
            memory_context=memory_context,
            relationship=relationship,
        )
        fallback["llm_error"] = str(exc)
        fallback["llm_attempted"] = str(exc) != "llm_key_missing"
        fallback["source"] = "fallback"
        fallback["npc_runtime"] = runtime
        return fallback
