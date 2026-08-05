from app.intent_policy import screen_intent_candidate
from app.models import NpcIntent


def _intent():
    return NpcIntent(
        id="alice_invites_reading",
        npc_id="alice",
        kind="npc_invite",
        title="去查旧记录",
        scene_id="church_library",
        tile_x=1,
        tile_y=1,
        response_options=[
            {"id": "accept_reading_note", "label": "我会去查"},
        ],
    )


def test_accepts_only_current_catalog_intent_and_response():
    normalized, decision = screen_intent_candidate(
        {
            "intent_id": "alice_invites_reading",
            "response_id": "accept_reading_note",
            "confidence": 0.82,
            "reason": "当前事件优先级高，且回应选项与线索一致。",
        },
        npc_id="alice",
        intents=[_intent()],
        source="agent",
    )

    assert normalized["intent_id"] == "alice_invites_reading"
    assert decision["accepted"] is True


def test_rejects_unknown_response_and_cross_npc_intent():
    candidate = {
        "intent_id": "alice_invites_reading",
        "response_id": "invented_effect",
        "confidence": 1,
        "reason": "尝试修改关系。",
    }
    normalized, decision = screen_intent_candidate(
        candidate,
        npc_id="alice",
        intents=[_intent()],
        source="agent",
    )
    assert normalized is None
    assert decision["reason"] == "response_not_in_current_intent"

    normalized, decision = screen_intent_candidate(
        {
            **candidate,
            "response_id": "accept_reading_note",
            "reason": "当前选项合理。",
        },
        npc_id="eugeo",
        intents=[_intent()],
        source="agent",
    )
    assert normalized is None
    assert decision["reason"] == "intent_npc_mismatch"


def test_holds_low_confidence_agent_candidate():
    normalized, decision = screen_intent_candidate(
        {
            "intent_id": "alice_invites_reading",
            "response_id": "accept_reading_note",
            "confidence": 0.4,
            "reason": "不太确定，但可以先看看。",
        },
        npc_id="alice",
        intents=[_intent()],
        source="agent",
    )
    assert normalized is None
    assert decision["reason"] == "ai_candidate_held_low_confidence"
