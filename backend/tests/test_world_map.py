from pathlib import Path

import pytest

from app.world_map import bfs_path, is_walkable, load_world_map, scene_for_tile


@pytest.fixture
def tiny_map(tmp_path: Path) -> Path:
    p = tmp_path / "world_map.json"
    p.write_text(
        '{"v":1,"id":"t","width":5,"height":3,"tile_size":32,'
        '"spawn":{"x":1,"y":1},"walkable":[0],'
        '"rows":["00000","00000","00000"],"scene_zones":[]}',
        encoding="utf-8",
    )
    return p


def test_load_and_walkable(tiny_map: Path):
    data = load_world_map(tiny_map)
    assert is_walkable(data, 1, 1) is True
    assert is_walkable(data, 0, 0) is True


def test_bfs_adjacent(tiny_map: Path):
    data = load_world_map(tiny_map)
    path = bfs_path(data, 1, 1, 3, 1)
    assert path is not None
    assert path[-1] == (3, 1)


def test_bfs_blocked(tiny_map: Path):
    data = load_world_map(tiny_map)
    data["rows"] = ["00000", "01000", "00000"]
    assert bfs_path(data, 1, 1, 2, 1) is None


def test_scene_for_tile():
    data = {
        "rows": ["00"],
        "scene_zones": [
            {"scene_id": "reading_hall", "x1": 0, "y1": 0, "x2": 1, "y2": 1}
        ],
    }
    assert scene_for_tile(data, 0, 0) == "reading_hall"
