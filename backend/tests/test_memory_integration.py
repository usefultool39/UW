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
