from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from anthropic import Anthropic

from .config import RECENT_EVENTS_K
from .llm_config import action_model, is_minimax_model, is_openai_chat_model
from .models import Action, ActionName, AgentState, WorldState
from .persona_phase import persona_phase_key
from .time_bands import circadian_band_name_en, circadian_hint_zh
from .world import _agent_by_id


def _sanitize_api_key(raw: str) -> str:
    key = (raw or "").strip().strip('"').strip("'")
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    return key


def _is_minimax_model(model: str) -> bool:
    return is_minimax_model(model)


def _resolve_base_url(model: str, has_minimax_key: bool) -> str | None:
    import os

    custom = (
        os.getenv("ANTHROPIC_BASE_URL") or os.getenv("MINIMAX_BASE_URL") or ""
    ).strip()
    if custom:
        return custom.rstrip("/")

    # Auto-route MiniMax models/keys to the MiniMax Anthropic-compatible endpoint.
    if has_minimax_key or _is_minimax_model(model):
        return "https://api.minimax.chat/v1"

    return None


def _is_minimax_mode(model: str, has_minimax_key: bool) -> bool:
    return has_minimax_key or _is_minimax_model(model)


def _is_openai_chat_model(model: str) -> bool:
    return is_openai_chat_model(model)


def _select_api_key(*, model: str, anthropic_key: str, minimax_key: str) -> str:
    if _is_minimax_mode(model=model, has_minimax_key=bool(minimax_key)):
        return minimax_key or anthropic_key
    return anthropic_key or minimax_key


def _call_minimax_chat(
    *,
    api_key: str,
    model: str,
    system: str,
    user: str,
    base_url: str,
) -> str:
    url = base_url.rstrip("/") + "/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 1000,
        "temperature": 0.2,
    }
    with httpx.Client(timeout=45.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"MiniMax 响应缺少 choices: {data}")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                txt = item.get("text") or item.get("content")
                if isinstance(txt, str) and txt.strip():
                    parts.append(txt.strip())
        if parts:
            return "\n".join(parts)

    raise RuntimeError(f"MiniMax 响应 message.content 格式不支持: {message}")


def _call_minimax_openai_chat(
    *,
    api_key: str,
    model: str,
    system: str,
    user: str,
    base_url: str,
    max_tokens: int = 1000,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "name": "NPC", "content": system},
            {"role": "user", "name": "Player", "content": user},
        ],
        "max_completion_tokens": max_tokens,
        "temperature": 1.0,
        "top_p": 0.95,
    }
    with httpx.Client(timeout=45.0) as client:
        resp = client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"MiniMax response missing choices: {data}")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()

    raise RuntimeError(f"Unsupported MiniMax message.content format: {message}")


# (content, mtime) 用于开发时改 system_base.md 后自动失效；设 DEV_RELOAD_PERSONA=1 则完全不缓存。
_SYSTEM_CACHE: dict[str, tuple[str, float]] = {}


def _dev_reload_persona() -> bool:
    return os.getenv("DEV_RELOAD_PERSONA", "").strip().lower() in ("1", "true", "yes", "on")


def _system_base(base: Path) -> str:
    p = (base / "characters" / "system_base.md").resolve()
    cache_key = str(p)
    if _dev_reload_persona():
        return p.read_text(encoding="utf-8")
    mtime = p.stat().st_mtime
    cached = _SYSTEM_CACHE.get(cache_key)
    if cached is not None and cached[1] == mtime:
        return cached[0]
    text = p.read_text(encoding="utf-8")
    _SYSTEM_CACHE[cache_key] = (text, mtime)
    return text


def _persona_text(base: Path, agent_id: str, state: WorldState) -> str:
    path = base / "characters" / agent_id / "persona.md"
    if path.is_file():
        core = path.read_text(encoding="utf-8")
    else:
        core = f"# Persona\n你是角色 {agent_id}。保持当前世界观，按状态、记忆和当前目标行动。"
    phase = persona_phase_key(state)
    overlay = base / "characters" / agent_id / f"overlay_{phase}.md"
    if overlay.is_file():
        core = core.rstrip() + "\n\n# 阶段叠加（主线进度）\n" + overlay.read_text(encoding="utf-8")
    return core


def _recent_lines(events: list[dict], k: int) -> str:
    tail = events[-k:] if events else []
    lines = [json.dumps(e, ensure_ascii=False) for e in tail]
    return "\n".join(lines) if lines else "(none)"


def build_user_message(state: WorldState, agent_id: str, events: list[dict]) -> str:
    me = _agent_by_id(state, agent_id)
    others = [a for a in state.agents if a.id != agent_id]
    ratio = state.tree.hp / max(1, state.tree.hp_max)

    def stamina_band(a: AgentState) -> str:
        if a.stamina < 30:
            return "低"
        elif a.stamina < 70:
            return "中"
        return "高"

    def hunger_band(a: AgentState) -> str:
        if a.hunger < 30:
            return "低"
        elif a.hunger < 70:
            return "中"
        return "高"

    def mood_desc(mood: int) -> str:
        if mood >= 80:
            return "非常好"
        elif mood >= 60:
            return "不错"
        elif mood >= 40:
            return "一般"
        elif mood >= 20:
            return "低落"
        return "很差"

    others_info = ", ".join(
        f"{a.id}: loc={a.location.value}, stamina={stamina_band(a)}({a.stamina}), hunger={hunger_band(a)}({a.hunger}), mood={mood_desc(a.mood)}"
        for a in others
    )
    phase = persona_phase_key(state)
    circ = circadian_hint_zh(state.tick)
    circ_en = circadian_band_name_en(state.tick)
    lines = [
        f"天数={state.day}, 回合={state.tick}",
        f"人格阶段键={phase}（露茵村第一章线；随主线/旗标自动叠加 overlay）",
        f"昼夜氛围={circ}（{circ_en}）",
        f"你的ID={agent_id}",
        f"你:",
        f"  stamina={me.stamina}/{me.stamina_max} ({'充足' if me.stamina > 50 else '不足'})",
        f"  hunger={me.hunger}/{me.hunger_max} ({'饱' if me.hunger < 30 else '饿' if me.hunger > 60 else '一般'})",
        f"  mood={me.mood}/100 ({mood_desc(me.mood)})",
        f"  motivation={me.motivation:.2f}x",
        f"  today_contribution={me.daily_contribution}次",
        f"  location={me.location.value}",
        f"  上次动作={me.last_action} (成功={me.last_action_ok})",
        f"  内心想法: {me.thought or '(无)'}",
        f"",
        f"其他角色:",
        f"  {others_info}",
        f"",
        f"巨树: 生命值={state.tree.hp}/{state.tree.hp_max} ({ratio:.2%}), 状态={state.tree.state.value}",
        f"",
        f"最近事件:",
        _recent_lines(events, RECENT_EVENTS_K),
        f"",
        f"输出规则:",
        f"1) 只输出一个 JSON 对象，不要额外解释，不要 markdown 代码块。",
        f"2) JSON 必须包含 name，可选 target 与 thinking。",
        f"3) name 只能是: noop/move/chop/rest/eat/sleep/go_home/cook。",
        f"4) 当 name=move 时，target 必须是: at_tree/bench/home/table。",
        f'请严格按此格式输出: {{"name":"chop","thinking":"..."}}',
    ]
    return "\n".join(lines)


def _strip_think_tags(text: str) -> str:
    """Strip MiniMax-style redacted_reasoning / redacted_thinking blocks before JSON parse."""
    for kind in ("reasoning", "thinking"):
        o = f"<redacted_{kind}>"
        c = f"</redacted_{kind}>"
        text = re.sub(
            re.escape(o) + r"[\s\S]*?" + re.escape(c), "", text, flags=re.IGNORECASE
        )
    return text.strip()


def _extract_thinking(text: str) -> str:
    chunks: list[str] = []
    for kind in ("reasoning", "thinking"):
        m = re.finditer(
            rf"<redacted_{kind}>[\s\S]*?</redacted_{kind}>",
            text,
            flags=re.IGNORECASE,
        )
        for item in m:
            block = item.group(0)
            block = re.sub(r"^<[^>]+>", "", block).strip()
            block = re.sub(r"</[^>]+>$", "", block).strip()
            if block:
                chunks.append(block)
    return "\n\n".join(chunks)


def _extract_json_objects(text: str) -> list[str]:
    """Extract top-level JSON object slices from arbitrary text."""
    out: list[str] = []
    depth = 0
    start = -1
    in_str = False
    esc = False

    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            continue

        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start >= 0:
                    out.append(text[start : i + 1])
                    start = -1

    return out


def parse_action_json(text: str) -> tuple[Action, str | None]:
    text = _strip_think_tags(text.strip())
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1).strip()

    candidates = _extract_json_objects(text) or [text]
    last_err: Exception | None = None
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate)
            name = ActionName(data["name"])
            target = data.get("target")
            thinking = data.get("thinking")
            return Action(name=name, target=target), thinking
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            last_err = e
            continue

    raise json.JSONDecodeError(f"invalid action json: {last_err}", text, 0)


def _extract_text_blocks(blocks: list[object]) -> str:
    texts: list[str] = []
    for block in blocks:
        if getattr(block, "type", None) == "text":
            texts.append(getattr(block, "text", ""))
    return "\n".join(t for t in texts if t).strip()


def llm_choose_action(
    state: WorldState,
    agent_id: str,
    events: list[dict],
    project_root: Path,
) -> tuple[Action, str | None, dict[str, Any]]:
    import os

    model = action_model()
    anthropic_key = _sanitize_api_key(os.getenv("ANTHROPIC_API_KEY") or "")
    minimax_key = _sanitize_api_key(os.getenv("MINIMAX_API_KEY") or "")
    api_key = _select_api_key(
        model=model, anthropic_key=anthropic_key, minimax_key=minimax_key
    )
    if not api_key:
        raise RuntimeError(
            "请设置 ANTHROPIC_API_KEY 或 MINIMAX_API_KEY（见 .env.example）"
        )

    system_base = _system_base(project_root)
    persona = _persona_text(project_root, agent_id, state)
    system = system_base + "\n\n# Persona\n" + persona

    user = build_user_message(state, agent_id, events)

    if _is_openai_chat_model(model):
        minimax_base = (
            os.getenv("MINIMAX_OPENAI_BASE_URL")
            or "https://api.minimax.io/v1"
        ).strip()
        content = _call_minimax_openai_chat(
            api_key=api_key,
            model=model,
            system=system,
            user=user,
            base_url=minimax_base,
        )
    elif _is_minimax_mode(model=model, has_minimax_key=bool(minimax_key)):
        minimax_base = (
            os.getenv("MINIMAX_BASE_URL") or "https://api.minimax.chat/v1"
        ).strip()
        content = _call_minimax_chat(
            api_key=api_key,
            model=model,
            system=system,
            user=user,
            base_url=minimax_base,
        )
    else:
        base_url = _resolve_base_url(model=model, has_minimax_key=bool(minimax_key))
        client_kwargs: dict[str, str] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = Anthropic(**client_kwargs)
        message = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user},
                    ],
                }
            ],
        )
        content = _extract_text_blocks(message.content)

    thinking = _extract_thinking(content) or None
    meta: dict[str, Any] = {
        "llm_model": model,
        "llm_prompt_system": system,
        "llm_prompt_user": user,
        "llm_raw": content,
        "llm_thinking": thinking,
    }
    try:
        action, llm_thinking = parse_action_json(content)
        if llm_thinking:
            thinking = llm_thinking
            meta["llm_thinking"] = llm_thinking
        return action, thinking, meta
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        candidates = _extract_json_objects(content)
        for candidate in reversed(candidates):
            try:
                result, llm_thinking = parse_action_json(candidate)
                if llm_thinking:
                    thinking = llm_thinking
                    meta["llm_thinking"] = llm_thinking
                return result, thinking, meta
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        raise RuntimeError(f"无法从响应中解析有效JSON: {e!s}") from e
