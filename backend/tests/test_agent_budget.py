from app.agent_budget import AgentBudget


def test_budget_enforces_total_and_purpose_limits(monkeypatch):
    monkeypatch.setenv("AI_MAX_CALLS_PER_RUN", "2")
    monkeypatch.setenv("AI_MAX_DIALOGUE_CALLS_PER_RUN", "1")
    budget = AgentBudget()

    first = budget.reserve("dialogue")
    second = budget.reserve("dialogue")
    third = budget.reserve("action")

    assert first["allowed"] is True
    assert second["allowed"] is False
    assert second["reason"] == "purpose_budget_exhausted"
    assert third["allowed"] is True
    assert budget.snapshot()["total_used"] == 2


def test_disabled_budget_does_not_consume_a_call():
    budget = AgentBudget()
    decision = budget.reserve("intent", enabled=False)

    assert decision["allowed"] is False
    assert decision["reason"] == "not_requested"
    assert budget.snapshot()["total_used"] == 0
