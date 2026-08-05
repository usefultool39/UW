"""Centralized model and provider configuration for LLM calls."""

from __future__ import annotations

import os

from .ai_provider import adapter_enabled, provider_meta
from .npc_runtime import npc_runtime_meta

DEFAULT_ACTION_MODEL = "M2-H"
DEFAULT_DIALOGUE_MODEL = "M2-H"
DEFAULT_PROVIDER_HINT = "MiniMax"


def _read_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if not value:
        return default
    value = str(value).strip().strip().strip('"').strip("'")
    return value or default


def is_minimax_model(model: str) -> bool:
    normalized = (model or "").lower()
    return "minimax" in normalized or normalized in {"m2-her", "m2-h", "m2-max"}


def is_openai_chat_model(model: str) -> bool:
    normalized = (model or "").strip().lower()
    return normalized in {"m2-her", "m2-h", "m2-max"}


def _coalesce_model(*candidates: str | None, default: str) -> str:
    for candidate in candidates:
        if candidate:
            return candidate
    return default


def action_model() -> str:
    return _coalesce_model(
        _read_env("LLM_ACTION_MODEL"),
        _read_env("LLM_MODEL"),
        _read_env("ACTION_MODEL"),
        _read_env("ANTHROPIC_MODEL"),
        _read_env("MINIMAX_MODEL"),
        _read_env("MINIMAX_DIALOGUE_MODEL"),
        default=DEFAULT_ACTION_MODEL,
    )


def dialogue_model() -> str:
    return _coalesce_model(
        _read_env("LLM_DIALOGUE_MODEL"),
        _read_env("LLM_MODEL"),
        _read_env("DIALOGUE_MODEL"),
        _read_env("MINIMAX_DIALOGUE_MODEL"),
        action_model(),
        default=DEFAULT_DIALOGUE_MODEL,
    )


def sanitize_key(raw: str | None) -> str:
    key = (raw or "").strip().strip().strip('"').strip("'")
    return key


def model_provider_hint() -> str:
    if adapter_enabled():
        provider = str(provider_meta(action_model()).get("provider") or "invalid")
        return {"stepfun": "StepFun", "sensetime": "SenseTime", "openai_compatible": "OpenAI-compatible", "minimax": "MiniMax", "anthropic": "Anthropic SDK"}.get(provider, provider)
    am = action_model()
    dm = dialogue_model()
    has_minimax_key = bool(_read_env("MINIMAX_API_KEY"))
    if has_minimax_key or is_minimax_model(am) or is_minimax_model(dm):
        return "MiniMax"
    if _read_env("ANTHROPIC_API_KEY"):
        return "Anthropic SDK"
    return "Not configured"


def llm_is_configured() -> bool:
    if adapter_enabled():
        return bool(provider_meta(action_model()).get("configured"))
    return bool(_read_env("MINIMAX_API_KEY") or _read_env("ANTHROPIC_API_KEY"))


def model_meta() -> dict[str, str | bool]:
    return {
        **npc_runtime_meta(),
        **({"llm_provider": provider_meta(action_model())} if adapter_enabled() else {}),
        "action_model": action_model(),
        "dialogue_model": dialogue_model(),
        "provider_hint": model_provider_hint(),
        "llm_configured": llm_is_configured(),
    }
