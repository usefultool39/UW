from pathlib import Path

from app.story_catalog import can_enter_node, load_main_nodes, requirements_met


def test_requirements_met_empty():
    assert requirements_met({}, {}) is True


def test_requirements_met_int():
    assert requirements_met({"a": 1}, {"a": 1}) is True
    assert requirements_met({"a": 0}, {"a": 1}) is False


def test_can_enter_mq01_requires_reading(tmp_path):
    p = tmp_path / "main_nodes.json"
    p.write_text(
        '{"nodes": {'
        '"mq00_tutorial": {"requires": {}},'
        '"mq01_tree_arc": {"requires": {"prologue_reading_done": 1}, "from": ["mq00_tutorial"]}'
        "}}",
        encoding="utf-8",
    )
    data = load_main_nodes(p)
    nodes = data.get("nodes") or {}
    ok, _ = can_enter_node(nodes, "mq00_tutorial", "mq01_tree_arc", {})
    assert ok is False
    ok2, _ = can_enter_node(
        nodes, "mq00_tutorial", "mq01_tree_arc", {"prologue_reading_done": 1}
    )
    assert ok2 is True
