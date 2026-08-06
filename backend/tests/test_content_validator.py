from __future__ import annotations

import json
from pathlib import Path

from app.content_validator import validate_project


ROOT = Path(__file__).resolve().parents[2]


def test_validate_current_project_content_has_no_errors():
    out = validate_project(ROOT)

    assert out["ok"] is True, out["errors"]
    assert out["warnings"] == []
    assert out["summary"]["agents"] >= 2
    assert out["summary"]["story_events"] >= 4
    assert out["summary"]["scene_activities"] >= 4
    assert out["summary"]["schedule_entries"] >= 8


def test_validate_project_reports_bad_story_references(tmp_path: Path):
    def write_json(rel: str, payload: dict) -> None:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    write_json(
        "characters/meta.json",
        {
            "v": 1,
            "agents": [
                {
                    "id": "alice",
                    "display": "Alice",
                    "role": "Tester",
                    "behavior_role": "logistics",
                    "initial_location": "home",
                    "enabled": True,
                }
            ],
        },
    )
    write_json(
        "data/story/main_nodes.json",
        {"nodes": {"mq00_tutorial": {"requires": {}}}},
    )
    write_json(
        "data/world/world_map.json",
        {
            "v": 1,
            "id": "novice_open",
            "width": 3,
            "height": 3,
            "spawn": {"x": 1, "y": 1},
            "walkable": [0],
            "scene_zones": [
                {
                    "scene_id": "home_hearth",
                    "x1": 0,
                    "y1": 0,
                    "x2": 2,
                    "y2": 2,
                    "entry_points": [{"id": "door", "x": 1, "y": 1}],
                    "transfers": [],
                }
            ],
            "pois": [],
            "rows": ["000", "000", "000"],
        },
    )
    write_json("data/world/scene_activities.json", {"v": 1, "activities": []})
    write_json(
        "data/story/events_chapter_01.json",
        {
            "v": 1,
            "events": [
                {
                    "id": "bad_event",
                    "chapter": "chapter_01",
                    "trigger": {"day_min": 1},
                    "location": {"scene_id": "missing_scene", "tile_x": 1, "tile_y": 1},
                    "participants": ["missing_agent"],
                    "choices": [
                        {
                            "id": "bad_choice",
                            "effects": {
                                "relationship": {"missing_agent.trust": 1},
                                "story_node_id": "missing_node",
                            },
                        }
                    ],
                }
            ],
        },
    )

    out = validate_project(tmp_path)
    codes = {issue["code"] for issue in out["errors"]}

    assert out["ok"] is False
    assert "unknown_scene" in codes
    assert "unknown_participant" in codes
    assert "unknown_relationship_agent" in codes
    assert "unknown_story_node" in codes


def test_validate_project_reports_bad_visual_tileset_manifest(tmp_path: Path):
    def write_json(rel: str, payload: dict) -> None:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    write_json(
        "characters/meta.json",
        {
            "v": 1,
            "agents": [
                {
                    "id": "alice",
                    "display": "Alice",
                    "role": "Tester",
                    "behavior_role": "logistics",
                    "initial_location": "home",
                    "enabled": True,
                }
            ],
        },
    )
    write_json("data/story/main_nodes.json", {"nodes": {}})
    write_json("data/story/events_chapter_01.json", {"v": 1, "events": []})
    write_json("data/world/scene_activities.json", {"v": 1, "activities": []})
    write_json(
        "data/world/world_map.json",
        {
            "v": 1,
            "id": "novice_open",
            "width": 3,
            "height": 3,
            "tile_size": 28,
            "visual": {"tileset_manifest": {"bad": True}},
            "spawn": {"x": 1, "y": 1},
            "walkable": [0],
            "scene_zones": [],
            "pois": [],
            "rows": ["000", "000", "000"],
        },
    )

    out = validate_project(tmp_path)
    codes = {issue["code"] for issue in out["errors"]}

    assert out["ok"] is False
    assert "invalid_visual_tileset_manifest" in codes


def test_validate_project_reports_unproducible_day_gate_flag(tmp_path: Path):
    def write_json(rel: str, payload: dict) -> None:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    write_json("characters/meta.json", {"v": 1, "agents": []})
    write_json(
        "data/story/main_nodes.json",
        {
            "nodes": {},
            "day_gates": {
                "4": {
                    "required_flags": {"never_written": 1},
                    "advance_to": 5,
                }
            },
        },
    )
    write_json("data/story/events_chapter_01.json", {"v": 1, "events": []})
    write_json("data/world/scene_activities.json", {"v": 1, "activities": []})
    write_json(
        "data/world/world_map.json",
        {
            "v": 1,
            "id": "novice_open",
            "width": 1,
            "height": 1,
            "spawn": {"x": 0, "y": 0},
            "walkable": [0],
            "scene_zones": [],
            "pois": [],
            "rows": ["0"],
        },
    )

    out = validate_project(tmp_path)
    assert out["ok"] is False
    assert "unproducible_day_gate_flag" in {issue["code"] for issue in out["errors"]}


def test_validate_project_reports_unproducible_required_any_day_gate_flag(tmp_path: Path):
    def write_json(rel: str, payload: dict) -> None:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    write_json("characters/meta.json", {"v": 1, "agents": []})
    write_json(
        "data/story/main_nodes.json",
        {
            "nodes": {},
            "day_gates": {
                "32": {
                    "required_any_flags": [
                        {"written_route": 1, "never_written_route": 1}
                    ],
                    "advance_to": 33,
                }
            },
        },
    )
    write_json("data/story/events_chapter_01.json", {"v": 1, "events": []})
    write_json(
        "data/world/scene_activities.json",
        {
            "v": 1,
            "activities": [
                {
                    "id": "route_activity",
                    "effects": {"flags": {"written_route": 1}},
                }
            ],
        },
    )
    write_json(
        "data/world/world_map.json",
        {
            "v": 1,
            "id": "novice_open",
            "width": 1,
            "height": 1,
            "spawn": {"x": 0, "y": 0},
            "walkable": [0],
            "scene_zones": [],
            "pois": [],
            "rows": ["0"],
        },
    )

    out = validate_project(tmp_path)
    issues = [issue for issue in out["errors"] if issue["code"] == "unproducible_day_gate_flag"]

    assert out["ok"] is False
    assert any("never_written_route" in issue["path"] for issue in issues)
    assert not any(issue["path"].endswith(".written_route") for issue in issues)
