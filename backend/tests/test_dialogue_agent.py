from __future__ import annotations

from pathlib import Path

from app.dialogue_agent import fallback_dialogue_reply
from app.models import RelationshipState
from app.world import initial_world


ROOT = Path(__file__).resolve().parents[2]


def test_fallback_dialogue_tone_changes_with_relationship_values():
    state = initial_world(seed=123)

    trusted = fallback_dialogue_reply(
        state=state,
        npc_id="alice",
        message="今天怎么样？",
        project_root=ROOT,
        relationship=RelationshipState(trust=8, tension=0),
    )
    tense = fallback_dialogue_reply(
        state=state,
        npc_id="alice",
        message="今天怎么样？",
        project_root=ROOT,
        relationship=RelationshipState(trust=0, tension=8),
    )

    assert trusted["reply"] != tense["reply"]
    assert "相信" in trusted["reply"]
    assert "担心" in tense["reply"]
