"""One-off / regen helper: build data/world/world_map.json (larger open map)."""
from __future__ import annotations

import json
from pathlib import Path


def build_grid() -> tuple[list[str], int, int]:
    w, h = 76, 44
    g = [["0"] * w for _ in range(h)]

    def setc(x: int, y: int, c: str) -> None:
        if 0 <= x < w and 0 <= y < h:
            g[y][x] = c

    for x in range(w):
        setc(x, 0, "2")
        setc(x, h - 1, "2")
    for y in range(h):
        setc(0, y, "2")
        setc(w - 1, y, "2")

    for x in range(2, w - 2):
        setc(x, 24, "3")
    for y in range(2, h - 2):
        setc(22, y, "3")
    for x in range(28, w - 3):
        setc(x, 12, "3")
    for y in range(12, 25):
        setc(28, y, "3")

    for y in range(30, h - 2):
        for x in range(8, 34):
            if (x - 20) ** 2 * 2 + (y - 36) ** 2 < 180:
                setc(x, y, "2")
    for y in range(3, 10):
        for x in range(56, 72):
            if (x - 64) ** 2 + (y - 6) ** 2 < 55:
                setc(x, y, "2")

    for y in range(4, 26):
        for x in range(4, 26):
            if g[y][x] in ("2", "3"):
                continue
            if x <= 7 or y <= 7 or (x >= 20 and y <= 12) or (y >= 20 and x <= 10):
                setc(x, y, "1")
            elif (x + y) % 3 == 0 and x < 18 and y < 22:
                setc(x, y, "1")
    for y in range(10, 20):
        for x in range(10, 19):
            if g[y][x] == "1":
                setc(x, y, "0")

    for y in range(7, 39):
        for x in range(34, 73):
            if g[y][x] in ("2", "3"):
                continue
            if 34 <= x <= 40 and 8 <= y <= 36:
                setc(x, y, "1")
            elif 66 <= x <= 71 and 10 <= y <= 34:
                setc(x, y, "1")
            elif 48 <= x <= 62 and 10 <= y <= 16:
                setc(x, y, "1")
            elif 52 <= x <= 60 and 28 <= y <= 36:
                setc(x, y, "1")

    for y in range(17, 33):
        for x in range(42, 65):
            if g[y][x] not in ("2", "3"):
                setc(x, y, "0")

    for rx, ry in ((46, 19), (63, 21), (15, 27), (70, 15)):
        setc(rx, ry, "4")
    for tx, ty in ((18, 30), (25, 32), (32, 28), (40, 35), (6, 28)):
        if g[ty][tx] == "0":
            setc(tx, ty, "1")

    rows = ["".join(r) for r in g]
    return rows, w, h


def main() -> None:
    rows, width, height = build_grid()
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / "world" / "world_map.json"
    data = {
        "v": 1,
        "id": "novice_open",
        "width": width,
        "height": height,
        "tile_size": 34,
        "spawn": {"x": 24, "y": 24},
        "walkable": [0, 3],
        "legend": {
            "0": "草地",
            "1": "树林（不可走，深绿为树冠）",
            "2": "水域",
            "3": "路",
            "4": "障碍",
        },
        "scene_zones": [
            {"scene_id": "reading_hall", "x1": 5, "y1": 5, "x2": 23, "y2": 21},
            {"scene_id": "gigas_clearing", "x1": 38, "y1": 7, "x2": 72, "y2": 39},
        ],
        "pois": [
            {
                "id": "poi_reading_quest",
                "kind": "quest",
                "active_story_nodes": ["mq00_tutorial"],
                "tile_x": 14,
                "tile_y": 14,
                "label": "书库·剧情",
                "hint": "先到书库附近；再点上方「标记读完书」，最后点「推进→mq01」解锁巨树线。",
            },
            {
                "id": "ix_reading_desk",
                "kind": "interact",
                "tile_x": 13,
                "tile_y": 14,
                "radius": 2,
                "title": "书库阅览台",
                "body": "尘光落在纸页上。静下心来读几章，仿佛过了一整天。",
                "actions": [
                    {
                        "id": "read",
                        "label": "翻阅典籍（标记读完书）",
                        "type": "set_flag",
                        "flag_key": "prologue_reading_done",
                        "flag_value": 1,
                        "toast": "已记录：读完书。可回工具栏推进 mq01。",
                    }
                ],
            },
            {
                "id": "ix_gigas_tree",
                "kind": "interact",
                "tile_x": 54,
                "tile_y": 22,
                "radius": 2,
                "title": "巨树",
                "body": "树龄无可计量。若要挥斧，将与「日常模拟」同步：由 AI 同伴在控制台里行动；此处可快进若干 tick 模拟砍树节奏。",
                "actions": [
                    {
                        "id": "chop_train",
                        "label": "试讲斧（1 tick）",
                        "type": "daily_tick",
                        "n": 1,
                        "toast": "已快进 1 tick（试讲）。完整砍树请在「模拟控制台」操作优吉欧。",
                    },
                    {
                        "id": "chop_work",
                        "label": "认真砍树（5 tick）",
                        "type": "daily_tick",
                        "n": 5,
                        "requires_story": "mq01_tree_arc",
                        "toast": "已快进 5 tick。",
                    },
                ],
            },
            {
                "id": "ix_home_bed",
                "kind": "interact",
                "tile_x": 11,
                "tile_y": 27,
                "radius": 2,
                "title": "小屋床铺",
                "body": "夜风在外，炉火尚温。躺下会快进到下一段时间流逝，并记你回到家中。",
                "actions": [
                    {
                        "id": "rest",
                        "label": "休息（回家 + 1 tick）",
                        "type": "compound_sleep",
                        "daily_n": 1,
                        "toast": "已回家并休息 1 tick。",
                    }
                ],
            },
        ],
        "rows": rows,
    }
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    sx, sy = data["spawn"]["x"], data["spawn"]["y"]
    assert rows[sy][sx] in ("0", "3"), rows[sy][sx]
    print("wrote", out, "spawn", rows[sy][sx], "tree cell", rows[22][54])


if __name__ == "__main__":
    main()
