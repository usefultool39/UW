"""Provider adapter for model-backed NPC expression and intent proposals.

The adapter deliberately exposes text generation only. It cannot commit world
state, advance story flags, or write memories; callers still validate output
and Session remains the only authority for game state.

By default the game keeps its existing MiniMax/Anthropic path. Set
``LLM_PROVIDER`` (or ``AI_PROVIDER``) to explicitly enable this adapter for a
provider such as ``stepfun`` or ``sensetime``. This makes API-shop experiments
configurable without making any provider a hard dependency of the game.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx
from anthropic import Anthropic


class ProviderError(RuntimeError):
    """A provider could not produce a usable text response."""


_PROVIDER_ALIASES = {
    "openai": "openai_compatible",
    "openai-compatible": "openai_compatible",
    "openai_compatible": "openai_compatible",
    "chat_completions": "openai_compatible",
    "step": "stepfun",
    "stepfun": "stepfun",
    "阶跃": "stepfun",
    "阶跃星辰": "stepfun",
    "阶跃工坊": "stepfun",
    "sense": "sensetime",
    "sensetime": "sensetime",
    "商汤": "sensetime",
    "商汤工坊": "sensetime",
    "minimax": "minimax",
    "anthropic": "anthropic",
}


def _read_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return str(value).strip().strip('"').strip("'")
    return ""


def _sanitize_key(value: str) -> str:
    key = str(value or "").strip().strip('"').strip("'")
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    return key


def explicit_provider_name() -> str:
    """Return the normalized explicitly requested provider, or an empty string."""
    raw = _read_env("LLM_PROVIDER", "AI_PROVIDER").lower()
    if not raw:
        return ""
    normalized = _PROVIDER_ALIASES.get(raw, raw.replace(" ", "_"))
    if normalized not in {"openai_compatible", "stepfun", "sensetime", "minimax", "anthropic"}:
        raise ProviderError(f"unsupported_llm_provider:{raw}")
    return normalized


def adapter_enabled() -> bool:
    """Only an explicit provider selection opts into this adapter."""
    return bool(_read_env("LLM_PROVIDER", "AI_PROVIDER"))


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model: str
    api_key: str
    base_url: str
    timeout_seconds: float = 45.0

    @property
    def configured(self) -> bool:
        if not self.api_key:
            return False
        if self.provider == "anthropic":
            return True
        return bool(self.base_url)

    def public_meta(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "configured": self.configured,
            "base_url_configured": bool(self.base_url),
        }


def resolve_provider_config(model: str | None = None) -> ProviderConfig:
    provider = explicit_provider_name()
    if not provider:
        raise ProviderError("llm_provider_not_explicit")

    generic_key = _sanitize_key(_read_env("LLM_API_KEY", "AI_API_KEY", "OPENAI_API_KEY"))
    if provider == "stepfun":
        api_key = generic_key or _sanitize_key(_read_env("STEPFUN_API_KEY"))
        base_url = _read_env("LLM_BASE_URL", "STEPFUN_BASE_URL")
    elif provider == "sensetime":
        api_key = generic_key or _sanitize_key(_read_env("SENSETIME_API_KEY", "SENSENOVA_API_KEY"))
        base_url = _read_env("LLM_BASE_URL", "SENSETIME_BASE_URL", "SENSENOVA_BASE_URL")
    elif provider == "minimax":
        api_key = generic_key or _sanitize_key(_read_env("MINIMAX_API_KEY"))
        base_url = _read_env("LLM_BASE_URL", "MINIMAX_OPENAI_BASE_URL", "MINIMAX_BASE_URL")
    elif provider == "anthropic":
        api_key = generic_key or _sanitize_key(_read_env("ANTHROPIC_API_KEY"))
        base_url = _read_env("LLM_BASE_URL", "ANTHROPIC_BASE_URL")
    else:
        api_key = generic_key
        base_url = _read_env("LLM_BASE_URL", "OPENAI_BASE_URL")

    selected_model = model or _read_env("LLM_MODEL", "ACTION_MODEL", "DIALOGUE_MODEL")
    if not selected_model:
        selected_model = "M2-H"
    try:
        timeout = float(_read_env("LLM_TIMEOUT_SECONDS") or "45")
    except ValueError:
        timeout = 45.0
    return ProviderConfig(
        provider=provider,
        model=selected_model,
        api_key=api_key,
        base_url=base_url.rstrip("/"),
        timeout_seconds=max(5.0, min(timeout, 120.0)),
    )


def provider_meta(model: str | None = None) -> dict[str, Any]:
    if not adapter_enabled():
        return {"provider": "legacy_auto", "configured": False, "base_url_configured": False}
    try:
        return resolve_provider_config(model).public_meta()
    except ProviderError as exc:
        return {"provider": "invalid", "configured": False, "base_url_configured": False, "provider_error": str(exc)}


def _chat_completions_url(base_url: str) -> str:
    if base_url.endswith("/chat/completions"):
        return base_url
    return base_url.rstrip("/") + "/chat/completions"


def _extract_openai_content(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices or not isinstance(choices[0], dict):
        raise ProviderError("provider_response_missing_choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        if parts:
            return "\n".join(parts)
    raise ProviderError("provider_response_missing_content")


def _generate_openai_compatible(config: ProviderConfig, system: str, user: str, max_tokens: int, temperature: float) -> str:
    body = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {"Authorization": f"Bearer {config.api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=config.timeout_seconds) as client:
        response = client.post(_chat_completions_url(config.base_url), headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
    return _extract_openai_content(data)


def _generate_anthropic(config: ProviderConfig, system: str, user: str, max_tokens: int) -> str:
    kwargs: dict[str, Any] = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url
    client = Anthropic(**kwargs)
    message = client.messages.create(
        model=config.model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": [{"type": "text", "text": user}]}],
    )
    parts = [getattr(block, "text", "") for block in message.content if getattr(block, "type", None) == "text"]
    content = "\n".join(part for part in parts if part).strip()
    if not content:
        raise ProviderError("provider_response_missing_content")
    return content


def generate_text(*, system: str, user: str, model: str, max_tokens: int = 1000, temperature: float = 0.2) -> str:
    """Generate text through an explicitly selected adapter.

    This function never mutates game state. Callers must parse and validate
    the result; any error is intentionally raised so the caller can use its
    scripted fallback.
    """
    config = resolve_provider_config(model)
    if not config.api_key:
        raise ProviderError("provider_api_key_missing")
    if config.provider != "anthropic" and not config.base_url:
        raise ProviderError("provider_base_url_missing")
    if config.provider == "anthropic":
        return _generate_anthropic(config, system, user, max_tokens)
    return _generate_openai_compatible(config, system, user, max_tokens, temperature)
