from app import npc_intent_agent
from app.session import Session


def test_fallback_proposal_is_preview_only_and_catalog_bound():
    sess = Session(run_id="intent-preview-test")
    before = sess.state.model_dump(mode="json")

    result = sess.propose_npc_intent("alice")

    assert result["ok"] is True
    assert result["source"] == "fallback"
    assert result["decision"]["accepted"] is True
    assert result["candidate"]["intent_id"] in {
        item.id for item in sess.state.npc_intents if item.npc_id == "alice"
    }
    assert sess.state.model_dump(mode="json") == before
    assert sess.events[-1]["kind"] == "npc_intent_proposal"


def test_provider_candidate_is_validated_before_return(monkeypatch):
    sess = Session(run_id="intent-agent-test")
    monkeypatch.setattr(npc_intent_agent, "adapter_enabled", lambda: True)
    monkeypatch.setattr(
        npc_intent_agent,
        "provider_meta",
        lambda: {"provider": "fake", "configured": True},
    )
    monkeypatch.setattr(npc_intent_agent, "dialogue_model", lambda: "fake-model")
    monkeypatch.setattr(
        npc_intent_agent,
        "generate_text",
        lambda **kwargs: (
            '{"intent_id":"alice_invites_reading",'
            '"response_id":"accept_reading_note",'
            '"confidence":0.91,"reason":"当前事件与书库线索直接相关。"}'
        ),
        raising=False,
    )

    result = npc_intent_agent.propose_npc_intent(
        state=sess.state,
        npc_id="alice",
        project_root=sess.root,
        memory_context={},
    )

    assert result["source"] == "agent"
    assert result["ok"] is True
    assert result["decision"]["accepted"] is True
    assert result["provider"]["provider"] == "fake"


def test_invalid_provider_candidate_falls_back_without_world_mutation(monkeypatch):
    sess = Session(run_id="intent-agent-invalid-test")
    monkeypatch.setattr(npc_intent_agent, "adapter_enabled", lambda: True)
    monkeypatch.setattr(
        npc_intent_agent,
        "provider_meta",
        lambda: {"provider": "fake", "configured": True},
    )
    monkeypatch.setattr(npc_intent_agent, "dialogue_model", lambda: "fake-model")
    monkeypatch.setattr(
        npc_intent_agent,
        "generate_text",
        lambda **kwargs: '{"intent_id":"not-authored","response_id":"nope","confidence":1,"reason":"bad"}',
        raising=False,
    )

    result = npc_intent_agent.propose_npc_intent(
        state=sess.state,
        npc_id="alice",
        project_root=sess.root,
        memory_context={},
    )

    assert result["source"] == "agent"
    assert result["ok"] is False
    assert result["decision"]["reason"] == "intent_not_in_current_catalog"
    assert sess.state.day == 1
