from app.npc_runtime import default_npc_runtime, npc_runtime_for


def test_runtime_defaults_to_scripted(monkeypatch):
    monkeypatch.delenv("NPC_RUNTIME", raising=False)
    assert default_npc_runtime() == "scripted"


def test_runtime_rejects_unknown_value(monkeypatch):
    monkeypatch.setenv("NPC_RUNTIME", "anything")
    assert default_npc_runtime() == "scripted"


def test_per_npc_runtime_override(monkeypatch):
    monkeypatch.setenv("NPC_RUNTIME", "hybrid")
    monkeypatch.setenv("NPC_RUNTIME_ALICE", "agent")
    assert npc_runtime_for("alice") == "agent"
    assert npc_runtime_for("eugeo") == "hybrid"
