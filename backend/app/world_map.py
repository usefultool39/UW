"""开放世界格子地图：加载、可走判定、BFS 寻路。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_MAP_ID = "novice_open"
MAP_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def default_map_path(project_root: Path) -> Path:
    return project_root / "data" / "world" / "world_map.json"


def map_path_for_id(project_root: Path, map_id: str | None) -> Path | None:
    mid = (map_id or DEFAULT_MAP_ID).strip()
    if not MAP_ID_RE.fullmatch(mid):
        return None
    if mid in {DEFAULT_MAP_ID, "world_map"}:
        return default_map_path(project_root)
    return project_root / "data" / "world" / "maps" / f"{mid}.json"


def load_world_map(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return _fallback_map()
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "rows" not in data:
        return _fallback_map()
    return data


def _fallback_map() -> dict[str, Any]:
    rows = ["0000", "0..0", "0000"]
    rows = [r.replace(".", "0") for r in rows]
    return {
        "v": 1,
        "id": "fallback",
        "width": 4,
        "height": 3,
        "tile_size": 32,
        "spawn": {"x": 1, "y": 1},
        "walkable": [0],
        "rows": rows,
    }


def cell(grid: list[str], x: int, y: int) -> int | None:
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
        return None
    ch = grid[y][x]
    if ch.isdigit():
        return int(ch)
    return 0


def is_walkable(data: dict[str, Any], x: int, y: int) -> bool:
    rows: list[str] = data.get("rows") or []
    if not rows:
        return False
    c = cell(rows, x, y)
    if c is None:
        return False
    walk = data.get("walkable")
    if isinstance(walk, list) and walk:
        return c in walk
    return c in (0, 3)


def scene_for_tile(data: dict[str, Any], tx: int, ty: int) -> str | None:
    for z in data.get("scene_zones") or []:
        if not isinstance(z, dict):
            continue
        try:
            x1, y1, x2, y2 = (
                int(z["x1"]),
                int(z["y1"]),
                int(z["x2"]),
                int(z["y2"]),
            )
        except (KeyError, TypeError, ValueError):
            continue
        lo_x, hi_x = (x1, x2) if x1 <= x2 else (x2, x1)
        lo_y, hi_y = (y1, y2) if y1 <= y2 else (y2, y1)
        if lo_x <= tx <= hi_x and lo_y <= ty <= hi_y:
            sid = z.get("scene_id")
            if isinstance(sid, str):
                return sid
    return None


def bfs_path(
    data: dict[str, Any], sx: int, sy: int, tx: int, ty: int
) -> list[tuple[int, int]] | None:
    if not is_walkable(data, sx, sy) or not is_walkable(data, tx, ty):
        return None
    if sx == tx and sy == ty:
        return [(sx, sy)]
    from collections import deque

    rows: list[str] = data.get("rows") or []
    h, w = len(rows), len(rows[0])
    prev: dict[tuple[int, int], tuple[int, int] | None] = {}
    q: deque[tuple[int, int]] = deque()
    q.append((sx, sy))
    prev[(sx, sy)] = None
    dirs = (
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
    )
    found = None
    while q:
        cx, cy = q.popleft()
        if cx == tx and cy == ty:
            found = (cx, cy)
            break
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if not is_walkable(data, nx, ny):
                continue
            if dx and dy:
                if not is_walkable(data, cx + dx, cy) or not is_walkable(data, cx, cy + dy):
                    continue
            if (nx, ny) in prev:
                continue
            prev[(nx, ny)] = (cx, cy)
            q.append((nx, ny))
    if found is None:
        return None
    path: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = found
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path
