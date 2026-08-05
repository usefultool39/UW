from __future__ import annotations

import pytest

from app import ai_provider
from app.ai_provider import ProviderError, generate_text, resolve_provider_config
from app.llm_config import dialogue_model, llm_is_configured, model_provider_hint


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeClient:
    last = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = None
        FakeClient.last = self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def post(self, url, *, headers, json):
        self.request = {"url": url, "headers": headers, "json": json}
        return FakeResponse({"choices": [{"message": {"content": '{"reply":"收到"}'}}]})


def _clear_provider_env(monkeypatch):
    for name in (
        "LLM_PROVIDER",
        "AI_PROVIDER",
        "LLM_API_KEY",
        "AI_API_KEY",
        "OPENAI_API_KEY",
        "LLM_BASE_URL",
        "OPENAI_BASE_URL",
        "LLM_MODEL",
        "LLM_DIALOGUE_MODEL",
        "LLM_ACTION_MODEL",
        "STEPFUN_API_KEY",
        "STEPFUN_BASE_URL",
        "SENSETIME_API_KEY",
        "SENSETIME_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_stepfun_alias_uses_provider_specific_key_and_generic_base_url(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "阶跃工坊")
    monkeypatch.setenv("STEPFUN_API_KEY", "Bearer step-secret")
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:9911/v1")
    monkeypatch.setenv("LLM_MODEL", "step-1")

    config = resolve_provider_config()

    assert config.provider == "stepfun"
    assert config.model == "step-1"
    assert config.api_key == "step-secret"
    assert config.base_url == "http://127.0.0.1:9911/v1"
    assert config.configured is True
    assert model_provider_hint() == "StepFun"
    assert llm_is_configured() is True
    assert dialogue_model() == "step-1"


def test_openai_compatible_adapter_posts_structured_chat_request(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("LLM_API_KEY", "test-secret")
    monkeypatch.setenv("LLM_BASE_URL", "http://provider.test/v1")
    monkeypatch.setenv("LLM_MODEL", "npc-model")
    monkeypatch.setattr(ai_provider.httpx, "Client", FakeClient)

    content = generate_text(
        system="只输出 JSON",
        user="玩家问候",
        model="npc-model",
        max_tokens=321,
        temperature=0.15,
    )

    assert content == '{"reply":"收到"}'
    assert FakeClient.last.request["url"] == "http://provider.test/v1/chat/completions"
    assert FakeClient.last.request["headers"]["Authorization"] == "Bearer test-secret"
    assert FakeClient.last.request["json"]["model"] == "npc-model"
    assert FakeClient.last.request["json"]["max_tokens"] == 321
    assert FakeClient.last.request["json"]["messages"][0]["role"] == "system"


def test_sensetime_requires_a_configured_base_url(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "商汤")
    monkeypatch.setenv("SENSETIME_API_KEY", "sense-secret")

    config = resolve_provider_config("sense-model")
    assert config.provider == "sensetime"
    assert config.configured is False
    with pytest.raises(ProviderError, match="provider_base_url_missing"):
        generate_text(system="s", user="u", model="sense-model")


def test_unknown_provider_is_rejected_without_network(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "unknown-provider")
    with pytest.raises(ProviderError, match="unsupported_llm_provider"):
        resolve_provider_config()


def test_dialogue_uses_explicit_provider_adapter_without_legacy_key(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "stepfun")
    monkeypatch.setenv("STEPFUN_API_KEY", "step-secret")
    monkeypatch.setenv("LLM_BASE_URL", "http://provider.test/v1")
    monkeypatch.setenv("LLM_MODEL", "step-dialogue")
    from app import dialogue_agent
    from app.world import initial_world

    monkeypatch.setattr(
        dialogue_agent,
        "generate_text",
        lambda **kwargs: '{"reply":"我听见了。","emotion":"focused","intent":"respond","memory_candidate":null}',
    )
    result = dialogue_agent.llm_dialogue_reply(
        state=initial_world(seed=11),
        npc_id="alice",
        message="你听见刚才的风声了吗？",
        project_root=__import__("pathlib").Path(__file__).resolve().parents[2],
    )

    assert result["source"] == "llm"
    assert result["reply"] == "我听见了。"
    assert result["llm_provider"]["provider"] == "stepfun"


def test_action_uses_explicit_provider_adapter_and_keeps_json_contract(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("LLM_API_KEY", "test-secret")
    monkeypatch.setenv("LLM_BASE_URL", "http://provider.test/v1")
    monkeypatch.setenv("LLM_MODEL", "npc-action")
    from app import llm_agent
    from app.world import initial_world

    monkeypatch.setattr(
        llm_agent,
        "generate_text",
        lambda **kwargs: '{"name":"rest","thinking":"先恢复体力"}',
    )
    action, thinking, meta = llm_agent.llm_choose_action(
        initial_world(seed=12),
        "alice",
        [],
        __import__("pathlib").Path(__file__).resolve().parents[2],
    )

    assert action.name.value == "rest"
    assert thinking == "先恢复体力"
    assert meta["llm_provider"]["provider"] == "openai_compatible"


def test_hybrid_dialogue_falls_back_when_explicit_provider_has_no_key(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("NPC_RUNTIME", "hybrid")
    monkeypatch.setenv("LLM_PROVIDER", "stepfun")
    monkeypatch.setenv("LLM_BASE_URL", "http://provider.test/v1")
    from app.dialogue_agent import dialogue_reply
    from app.world import initial_world
    from pathlib import Path

    result = dialogue_reply(
        state=initial_world(seed=13),
        npc_id="alice",
        message="你还好吗？",
        project_root=Path(__file__).resolve().parents[2],
    )

    assert result["source"] == "fallback"
    assert result["npc_runtime"] == "hybrid"
    assert result["llm_attempted"] is True
    assert "provider_api_key_missing" in result["llm_error"]
