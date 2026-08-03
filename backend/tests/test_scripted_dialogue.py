from pathlib import Path

from app.scripted_dialogue import choose_scripted_line, relationship_variant


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_relationship_variant_priority():
    assert relationship_variant({"trust": 8, "affinity": 8, "tension": 0}) == "trusted"
    assert relationship_variant({"trust": 8, "affinity": 8, "tension": 7}) == "tense"
    assert relationship_variant({"trust": 0, "affinity": 6, "tension": 0}) == "warm"


def test_alice_boundary_dialogue_uses_topic_and_trust_variant():
    out = choose_scripted_line(
        project_root=_root(),
        npc_id="alice",
        message="北方边界为什么突然安静？",
        relationship={"trust": 8, "affinity": 2, "tension": 0},
    )
    assert out is not None
    assert out["topic"] == "boundary"
    assert out["variant"] == "trusted"
    assert "记录" in out["reply"]


def test_missing_dialogue_book_returns_none():
    assert choose_scripted_line(
        project_root=_root(),
        npc_id="missing",
        message="你好",
    ) is None
