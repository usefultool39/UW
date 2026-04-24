from fastapi.testclient import TestClient

from app.main import app
import app.main as main_mod


class _DummyTree:
    def __init__(self):
        self.hp = 1_000_000
        self.state = type("_S", (), {"value": "standing"})()


class _DummyState:
    def __init__(self):
        self.tree = _DummyTree()
        self.agents = []

    def model_dump(self, mode="json"):
        return {
            "tick": 0,
            "day": 1,
            "tree": {"hp": self.tree.hp, "state": self.tree.state.value},
            "agents": [],
        }


class _DummyEvent:
    def __init__(self, marker: str):
        self.marker = marker

    def model_dump(self, mode="json"):
        return {"marker": self.marker}


class _SessionA:
    def __init__(self):
        self.state = _DummyState()
        self.calls = 0

    def step(self, mode="heuristic"):
        self.calls += 1
        # 在第一次 step 内部切换全局 SESSION，模拟 reset 并发覆盖
        if self.calls == 1:
            main_mod.SESSION = _SessionB()
        return [_DummyEvent("A")]


class _SessionB:
    def __init__(self):
        self.state = _DummyState()

    def step(self, mode="heuristic"):
        return [_DummyEvent("B")]


def test_step_uses_single_session_snapshot(monkeypatch):
    monkeypatch.setattr(main_mod, "SESSION", _SessionA())

    client = TestClient(app)
    resp = client.post("/api/step", json={"n": 2, "mode": "heuristic"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    markers = [ev["marker"] for ev in body["events"]]
    assert markers == ["A", "A"]
