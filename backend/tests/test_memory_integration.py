from fastapi.testclient import TestClient

from app.main import app, SESSION
from app.memory_store import MemoryStore
from app.session import Session


def test_session_step_writes_per_npc_memory(tmp_path):
    s = Session(run_id="memtest")
    s.memory_store = MemoryStore(tmp_path / "memory")

    events = s.step(mode="heuristic")
    assert len(events) == len(s.state.agents)

    for npc_id in [agent.id for agent in s.state.agents]:
        summary = s.memory_store.load_summary(npc_id)
        assert summary["npc_id"] == npc_id
        assert summary["total_events"] == 1
        assert isinstance(summary["action_stats"], dict)


def test_memory_api_returns_summary_and_recent_events(tmp_path):
    original_store = SESSION.memory_store
    try:
        SESSION.memory_store = MemoryStore(tmp_path / "memory")
        SESSION.step(mode="heuristic")

        client = TestClient(app)
        response = client.get("/api/memory/alice?limit=5")
        assert response.status_code == 200
        payload = response.json()
        assert payload["npc_id"] == "alice"
        assert "summary" in payload
        assert "recent_events" in payload
        assert isinstance(payload["recent_events"], list)
    finally:
        SESSION.memory_store = original_store


def test_session_memory_is_scoped_per_run():
    first = Session(run_id="memory-scope-first")
    second = Session(run_id="memory-scope-second")
    assert first.memory_store.root_dir != second.memory_store.root_dir

    first.memory_store.append_important_memory(
        "alice",
        {"day": 3, "type": "choice", "summary": "只属于第一局的边界记忆", "weight": 5},
        first.run_id,
    )
    context = second.memory_store.read_important_context("alice")
    assert context["important_memories"] == []


def test_dialogue_fallback_candidate_is_committed_only_when_marked_important(tmp_path, monkeypatch):
    from app import session as session_module

    s = Session(run_id="dialogue-fallback-memory")
    s.memory_store = MemoryStore(tmp_path / "memory")
    monkeypatch.setattr(session_module, "npc_runtime_for", lambda npc_id: "agent")
    monkeypatch.setattr(session_module, "llm_is_configured", lambda: True)
    monkeypatch.setattr(
        session_module,
        "dialogue_reply",
        lambda **kwargs: {
            "ok": True,
            "reply": "我听见了。",
            "emotion": "focused",
            "intent": "respond",
            "source": "fallback",
            "memory_candidate": {
                "type": "dialogue",
                "summary": "玩家问起村口的风声",
                "weight": 2,
            },
        },
    )

    result = s.dialogue(npc_id="alice", message="你听见风声了吗？")

    assert result["memory_committed"] is False
    assert result["memory_decision"]["reason"] == "scripted_candidate_below_threshold"
    context = s.memory_store.read_important_context("alice")
    assert context["important_memories"] == []


def test_dialogue_ai_low_confidence_candidate_is_not_committed(tmp_path, monkeypatch):
    from app import session as session_module

    s = Session(run_id="dialogue-ai-low-memory")
    s.memory_store = MemoryStore(tmp_path / "memory")
    monkeypatch.setattr(session_module, "npc_runtime_for", lambda npc_id: "agent")
    monkeypatch.setattr(session_module, "llm_is_configured", lambda: True)
    monkeypatch.setattr(
        session_module,
        "dialogue_reply",
        lambda **kwargs: {
            "ok": True,
            "reply": "我会记住你说的事。",
            "emotion": "warm",
            "intent": "respond",
            "source": "llm",
            "memory_candidate": {
                "type": "dialogue",
                "summary": "玩家说起了需要关注的风声",
                "weight": 3,
            },
        },
    )

    result = s.dialogue(npc_id="alice", message="记住今天的风声。")

    assert result["memory_committed"] is False
    assert result["memory_decision"]["reason"] == "ai_candidate_held_low_confidence"
    assert s.memory_store.read_important_context("alice")["important_memories"] == []
    event = s.memory_store.read_recent_events("alice", limit=1)[-1]
    assert event["memory_committed"] is False
    assert event["memory_decision"]["accepted"] is False


def test_dialogue_ai_high_confidence_candidate_is_committed_and_audited(tmp_path, monkeypatch):
    from app import session as session_module

    s = Session(run_id="dialogue-ai-high-memory")
    s.memory_store = MemoryStore(tmp_path / "memory")
    monkeypatch.setattr(session_module, "npc_runtime_for", lambda npc_id: "agent")
    monkeypatch.setattr(session_module, "llm_is_configured", lambda: True)
    monkeypatch.setattr(
        session_module,
        "dialogue_reply",
        lambda **kwargs: {
            "ok": True,
            "reply": "这件事值得记下来。",
            "emotion": "focused",
            "intent": "respond",
            "source": "llm",
            "memory_candidate": {
                "type": "observation",
                "summary": "玩家观察到村口的风声异常",
                "weight": 4,
            },
        },
    )

    result = s.dialogue(npc_id="alice", message="村口的风声很异常。")

    assert result["memory_committed"] is True
    memories = s.memory_store.read_important_context("alice")["important_memories"]
    assert memories[0]["summary"] == "玩家观察到村口的风声异常"
    event = s.memory_store.read_recent_events("alice", limit=1)[-1]
    assert event["memory_decision"]["accepted"] is True
