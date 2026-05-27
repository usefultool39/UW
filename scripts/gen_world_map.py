"""Regenerate data/world/world_map.json for the Luin novice open map."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


W, H = 108, 64


def tile_hash(x: int, y: int, salt: int = 0) -> float:
    n = (x * 374761393 + y * 668265263 + salt * 1442695041) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) & 0xFFFFFFFF
    return (n & 0x0FFFFFFF) / 0x0FFFFFFF


def build_grid() -> tuple[list[str], int, int]:
    g = [["0"] * W for _ in range(H)]

    def setc(x: int, y: int, c: str, *, overwrite: Iterable[str] | None = None) -> None:
        if not (0 <= x < W and 0 <= y < H):
            return
        if overwrite is not None and g[y][x] not in set(overwrite):
            return
        g[y][x] = c

    def rect(x1: int, y1: int, x2: int, y2: int, c: str, *, overwrite: Iterable[str] | None = None) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                setc(x, y, c, overwrite=overwrite)

    def ellipse(cx: float, cy: float, rx: float, ry: float, c: str, *, overwrite: Iterable[str] | None = None) -> None:
        for y in range(max(0, int(cy - ry - 2)), min(H, int(cy + ry + 3))):
            for x in range(max(0, int(cx - rx - 2)), min(W, int(cx + rx + 3))):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                    setc(x, y, c, overwrite=overwrite)

    def hroad(y: int, x1: int, x2: int, *, width: int = 1) -> None:
        half = width // 2
        for yy in range(y - half, y + half + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                setc(x, yy, "3")

    def vroad(x: int, y1: int, y2: int, *, width: int = 1) -> None:
        half = width // 2
        for xx in range(x - half, x + half + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                setc(xx, y, "3")

    def scatter_forest(x1: int, y1: int, x2: int, y2: int, threshold: float, salt: int) -> None:
        for y in range(max(1, y1), min(H - 1, y2 + 1)):
            for x in range(max(1, x1), min(W - 1, x2 + 1)):
                if g[y][x] != "0":
                    continue
                coarse = tile_hash(x // 3, y // 3, salt)
                fine = tile_hash(x, y, salt + 31)
                if coarse * 0.72 + fine * 0.28 > threshold:
                    setc(x, y, "1")

    def smooth_forest() -> None:
        old = [row[:] for row in g]
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if old[y][x] not in ("0", "1"):
                    continue
                count = 0
                for yy in range(y - 1, y + 2):
                    for xx in range(x - 1, x + 2):
                        if xx == x and yy == y:
                            continue
                        if old[yy][xx] == "1":
                            count += 1
                if old[y][x] == "1" and count <= 1:
                    g[y][x] = "0"
                elif old[y][x] == "0" and count >= 6:
                    g[y][x] = "1"

    # Natural outer limits. The map is bigger now, but the edge still reads as
    # wilderness rather than a hard rectangular demo boundary.
    rect(0, 0, W - 1, 1, "1")
    rect(0, H - 2, W - 1, H - 1, "1")
    rect(0, 0, 1, H - 1, "1")
    rect(W - 2, 0, W - 1, H - 1, "1")
    ellipse(18, 55, 17, 7, "2")
    ellipse(56, 54, 24, 8, "2")
    ellipse(94, 9, 10, 5, "2")
    ellipse(6, 21, 4, 16, "2")

    # Woodland masses and mountain edges.
    scatter_forest(3, 3, 26, 21, 0.47, 2)
    scatter_forest(34, 4, 80, 17, 0.58, 4)
    scatter_forest(34, 8, 43, 41, 0.36, 5)
    scatter_forest(66, 10, 79, 39, 0.38, 6)
    scatter_forest(82, 2, 105, 36, 0.52, 7)
    scatter_forest(3, 35, 23, 58, 0.72, 8)
    scatter_forest(71, 40, 104, 58, 0.56, 9)
    smooth_forest()

    # The old coordinates stay intact, but the roads now continue outward.
    hroad(24, 4, 96)
    hroad(12, 22, 76)
    hroad(27, 9, 26)
    hroad(49, 23, 39)
    vroad(23, 3, 55)
    vroad(28, 12, 24)
    vroad(54, 12, 25)
    vroad(67, 18, 30)

    # Village square and teleport plaza have room to breathe.
    rect(20, 21, 31, 27, "0", overwrite=("0", "1"))
    hroad(24, 18, 33)
    vroad(24, 20, 28)
    rect(33, 19, 38, 25, "0", overwrite=("0", "1"))
    hroad(22, 28, 39)
    vroad(35, 20, 25)

    # Library / home spaces are kept walkable around their original anchors.
    rect(10, 10, 18, 18, "0", overwrite=("0", "1"))
    hroad(14, 13, 24)
    vroad(13, 14, 24)
    rect(8, 25, 15, 31, "0", overwrite=("0", "1"))
    rect(6, 26, 17, 32, "0", overwrite=("0", "1"))
    hroad(27, 11, 24)

    # The ancient tree clearing is a broad playable glade inside dense forest.
    ellipse(54, 23, 16, 10, "0", overwrite=("0", "1"))
    ellipse(55, 22, 8, 5, "0", overwrite=("0", "1"))
    hroad(24, 39, 68)
    vroad(54, 18, 26)
    for x, y in ((46, 19), (63, 21), (40, 35), (72, 18), (15, 27), (67, 23)):
        setc(x, y, "4", overwrite=("0", "3"))

    # Future roads are visible but blocked by locked scene zones.
    hroad(24, 82, 102)
    vroad(90, 18, 31)
    hroad(49, 31, 64)
    vroad(60, 4, 12)
    hroad(9, 52, 70)

    # Add a few field paths in the open novice region.
    hroad(38, 5, 22)
    hroad(44, 5, 21)
    vroad(11, 33, 50)
    vroad(18, 34, 51)

    rows = ["".join(r) for r in g]
    return rows, W, H


def main() -> None:
    rows, width, height = build_grid()
    root = Path(__file__).resolve().parents[1]
    out = root / "data" / "world" / "world_map.json"
    data = {
        "v": 1,
        "id": "novice_open",
        "width": width,
        "height": height,
        "tile_size": 28,
        "visual": {
            "style": "fine_tilemap_v2_open_novice",
            "background": False,
            "tileset_manifest": "/assets/game/tilesets/luin_village_v1.json",
            "scale": {
                "profile": "open_world_readable_demo",
                "character_height_tiles": 1.85,
                "marker_density": "roomy",
            },
            "camera": {
                "default_zoom": 1.06,
                "background_zoom": 1.02,
                "min_zoom": 0.34,
                "max_zoom": 2.2,
                "wheel_step": 0.06,
                "follow_lerp": 0.16,
            },
            "movement": {
                "walk_speed": 760,
                "min_walk_ms": 105,
                "max_walk_ms": 2600,
                "left_drag_pan": True,
            },
            "performance": {
                "bake_static_layers": True,
                "guide_interval_ms": 200,
                "water_interval_ms": 220,
                "weather_interval_ms": 90,
            },
        },
        "spawn": {"x": 24, "y": 24},
        "walkable": [0, 3],
        "legend": {
            "0": "草地",
            "1": "森林/山壁（不可走）",
            "2": "水域",
            "3": "道路",
            "4": "障碍",
        },
        "scene_zones": [
            {
                "scene_id": "church_library",
                "label": "村西书库",
                "regionType": "interact",
                "x1": 9,
                "y1": 8,
                "x2": 19,
                "y2": 18,
                "entry_points": [{"id": "front_desk", "x": 13, "y": 14}],
                "transfers": [{"to_scene_id": "reading_hall", "kind": "same_map", "label": "返回村西书道"}],
                "requirements": {},
            },
            {
                "scene_id": "home_hearth",
                "label": "家中炉火",
                "regionType": "rest",
                "x1": 7,
                "y1": 25,
                "x2": 16,
                "y2": 31,
                "entry_points": [{"id": "door", "x": 11, "y": 27}],
                "transfers": [{"to_scene_id": "village_square", "kind": "same_map", "label": "回到村道广场"}],
                "requirements": {},
            },
            {
                "scene_id": "village_square",
                "label": "村道广场",
                "regionType": "interact",
                "x1": 19,
                "y1": 21,
                "x2": 31,
                "y2": 28,
                "entry_points": [{"id": "crossroad", "x": 24, "y": 24}],
                "transfers": [
                    {"to_scene_id": "church_library", "kind": "same_map", "label": "去村西书库"},
                    {"to_scene_id": "gigas_clearing", "kind": "same_map", "label": "去古誓树清场"},
                    {"to_scene_id": "teleport_plaza", "kind": "same_map", "label": "去传送阵广场"},
                ],
                "requirements": {},
            },
            {
                "scene_id": "reading_hall",
                "label": "村西书道",
                "regionType": "interact",
                "x1": 20,
                "y1": 5,
                "x2": 25,
                "y2": 20,
                "entry_points": [{"id": "west_path", "x": 14, "y": 14}],
                "transfers": [{"to_scene_id": "church_library", "kind": "same_map", "label": "进入村西书库"}],
                "requirements": {},
            },
            {
                "scene_id": "teleport_plaza",
                "label": "传送阵广场",
                "regionType": "travel",
                "x1": 33,
                "y1": 18,
                "x2": 37,
                "y2": 26,
                "entry_points": [{"id": "gate_ring", "x": 35, "y": 22}],
                "transfers": [
                    {
                        "to_scene_id": "east_highroad_gate",
                        "kind": "future_gate",
                        "label": "东侧高路（未开放）",
                    }
                ],
                "requirements": {"planned_unlock": "chapter_02"},
            },
            {
                "scene_id": "west_fields",
                "label": "西侧田野",
                "regionType": "explore",
                "x1": 4,
                "y1": 32,
                "x2": 22,
                "y2": 55,
                "entry_points": [{"id": "field_path", "x": 11, "y": 38}],
                "transfers": [{"to_scene_id": "village_square", "kind": "same_map", "label": "回到村道广场"}],
                "requirements": {},
            },
            {
                "scene_id": "north_gate",
                "label": "北境边门",
                "regionType": "boundary",
                "x1": 64,
                "y1": 20,
                "x2": 76,
                "y2": 29,
                "entry_points": [{"id": "gate", "x": 67, "y": 24}],
                "transfers": [
                    {
                        "to_map_id": "north_boundary_stub",
                        "to_scene_id": "north_boundary",
                        "kind": "map_gate",
                        "label": "调查北境边界",
                    }
                ],
                "requirements": {"recommended_flags": ["surveyed_north_gate"]},
            },
            {
                "scene_id": "gigas_clearing",
                "label": "古誓树清场",
                "regionType": "work",
                "x1": 38,
                "y1": 11,
                "x2": 63,
                "y2": 41,
                "entry_points": [{"id": "tree_line", "x": 54, "y": 22}],
                "transfers": [
                    {"to_scene_id": "village_square", "kind": "same_map", "label": "回村道广场"},
                    {"to_scene_id": "north_gate", "kind": "same_map", "label": "去北境边门"},
                ],
                "requirements": {},
            },
            {
                "scene_id": "north_ridge_gate",
                "label": "北境山道 未开放",
                "regionType": "locked",
                "x1": 42,
                "y1": 2,
                "x2": 78,
                "y2": 10,
                "entry_points": [{"id": "ridge_airwall", "x": 60, "y": 9}],
                "transfers": [{"to_map_id": "north_boundary_stub", "kind": "planned", "label": "第二月开放"}],
                "requirements": {"planned_unlock": "chapter_02"},
            },
            {
                "scene_id": "east_highroad_gate",
                "label": "东侧高路 未开放",
                "regionType": "locked",
                "x1": 84,
                "y1": 17,
                "x2": 103,
                "y2": 32,
                "entry_points": [{"id": "east_airwall", "x": 90, "y": 24}],
                "transfers": [{"kind": "planned", "label": "传送阵激活后开放"}],
                "requirements": {"planned_unlock": "chapter_02"},
            },
            {
                "scene_id": "south_lake_gate",
                "label": "南湖旧渡 未开放",
                "regionType": "locked",
                "x1": 32,
                "y1": 45,
                "x2": 68,
                "y2": 58,
                "entry_points": [{"id": "lake_airwall", "x": 35, "y": 49}],
                "transfers": [{"kind": "planned", "label": "渡口修复后开放"}],
                "requirements": {"planned_unlock": "chapter_03"},
            },
        ],
        "pois": [
            {
                "id": "poi_reading_quest",
                "kind": "quest",
                "scene_id": "church_library",
                "active_story_nodes": ["mq00_tutorial"],
                "tile_x": 14,
                "tile_y": 14,
                "label": "书库·剧情",
                "hint": "书库里藏着关于北方边界的旧记录。靠近后可以阅读，也可以触发金色章节事件。",
            },
            {
                "id": "ix_reading_desk",
                "kind": "interact",
                "scene_id": "church_library",
                "tile_x": 13,
                "tile_y": 14,
                "radius": 2,
                "label": "村西书库",
                "title": "书库阅览台",
                "body": "尘光落在纸页上。静下心来读几章，像是穿过了一整天。",
                "actions": [
                    {
                        "id": "read",
                        "label": "翻阅旧记录（标记读完书）",
                        "type": "set_flag",
                        "flag_key": "prologue_reading_done",
                        "flag_value": 1,
                        "toast": "书页里的边界记录被你记下了。留意地图上的金色章节事件。",
                    },
                    {
                        "id": "church_read_sacred_arts",
                        "label": "进入读书玩法：拼接刻印术线索",
                        "type": "scene_activity",
                        "activity_id": "church_read_sacred_arts",
                    },
                    {
                        "id": "church_ask_alice_lunch",
                        "label": "决定午餐篮怎么准备",
                        "type": "scene_activity",
                        "activity_id": "church_ask_alice_lunch",
                    },
                ],
            },
            {
                "id": "ix_gigas_tree",
                "kind": "interact",
                "scene_id": "gigas_clearing",
                "tile_x": 54,
                "tile_y": 22,
                "radius": 2,
                "label": "古誓树",
                "title": "古誓树",
                "body": "树龄无可计量。训练不只是挥斧，也是确认世界每日仍按规则运转的方式。",
                "actions": [
                    {
                        "id": "chop_train",
                        "label": "试挥斧（1 tick）",
                        "type": "daily_tick",
                        "n": 1,
                        "toast": "你试着挥斧，节奏被古誓树沉默地接住了。",
                    },
                    {
                        "id": "gigas_chop_rhythm",
                        "label": "进入训练玩法：按节奏砍树",
                        "type": "scene_activity",
                        "activity_id": "gigas_chop_rhythm",
                    },
                    {
                        "id": "gigas_listen_to_forest",
                        "label": "停下来听北边的风",
                        "type": "scene_activity",
                        "activity_id": "gigas_listen_to_forest",
                    },
                    {
                        "id": "chop_work",
                        "label": "认真砍树（5 tick）",
                        "type": "daily_tick",
                        "n": 5,
                        "requires_story": "mq01_tree_arc",
                        "toast": "训练持续了一阵。悠吉欧会记得你今天没有逃开日常。",
                    },
                ],
            },
            {
                "id": "ix_home_bed",
                "kind": "interact",
                "scene_id": "home_hearth",
                "tile_x": 11,
                "tile_y": 27,
                "radius": 2,
                "label": "家中炉火",
                "title": "小屋床铺",
                "body": "夜风在外，炉火尚温。躺下会快进到下一段时间，并记住你回到家中。",
                "actions": [
                    {
                        "id": "rest",
                        "label": "休息（回家 + 1 tick）",
                        "type": "compound_sleep",
                        "daily_n": 1,
                        "toast": "已回家并休息 1 tick。",
                    },
                    {
                        "id": "home_evening_meal",
                        "label": "进入家中场景：围炉晚餐",
                        "type": "scene_activity",
                        "activity_id": "home_evening_meal",
                    },
                    {
                        "id": "home_sleep_until_morning",
                        "label": "睡到第二天清晨",
                        "type": "scene_activity",
                        "activity_id": "home_sleep_until_morning",
                    },
                ],
            },
            {
                "id": "ix_village_square",
                "kind": "interact",
                "scene_id": "village_square",
                "tile_x": 24,
                "tile_y": 24,
                "radius": 3,
                "label": "村道广场",
                "title": "村道广场",
                "body": "水渠、村道和田地在这里交汇。这里适合听传闻、确认日程，也让世界不只是一张背景图。",
                "actions": [
                    {
                        "id": "village_square_listen",
                        "label": "听村民谈北方山脉",
                        "type": "scene_activity",
                        "activity_id": "village_square_listen",
                    }
                ],
            },
            {
                "id": "ix_teleport_gate",
                "kind": "interact",
                "scene_id": "teleport_plaza",
                "tile_x": 35,
                "tile_y": 22,
                "radius": 2,
                "label": "传送阵",
                "title": "传送阵广场",
                "body": "石环里的蓝光还没有完全醒来。以后这里会承担跨地图移动，现在可以先作为村内地标和未来入口。",
                "actions": [
                    {
                        "id": "inspect_transfer_gate",
                        "label": "检查传送阵刻印",
                        "type": "set_flag",
                        "flag_key": "transfer_gate_seen",
                        "flag_value": 1,
                        "toast": "你记下了传送阵刻印。它还缺少可前往的目的地。",
                    }
                ],
            },
            {
                "id": "ix_north_gate",
                "kind": "interact",
                "scene_id": "north_gate",
                "tile_x": 67,
                "tile_y": 24,
                "approach_tile_x": 63,
                "approach_tile_y": 24,
                "radius": 3,
                "label": "北境边门",
                "title": "北境边门",
                "body": "再往北就是山脉与北境律令共同构成的边界。现在它仍是未开放边界，但你可以先远望和记录。",
                "actions": [
                    {
                        "id": "north_gate_survey",
                        "label": "远望边界线",
                        "type": "scene_activity",
                        "activity_id": "north_gate_survey",
                    }
                ],
            },
            {
                "id": "ix_east_highroad_gate",
                "kind": "interact",
                "scene_id": "east_highroad_gate",
                "regionType": "locked",
                "tile_x": 86,
                "tile_y": 24,
                "approach_tile_x": 82,
                "approach_tile_y": 24,
                "radius": 3,
                "label": "东侧高路",
                "title": "东侧高路",
                "body": "道路已经铺到空气墙之后。它会作为后续章节的新地图入口，现在只能调查边界标记。",
                "actions": [
                    {
                        "id": "inspect_east_highroad",
                        "label": "记录东侧空气墙",
                        "type": "set_flag",
                        "flag_key": "east_highroad_seen",
                        "flag_value": 1,
                        "toast": "东侧高路被记录到地图上。传送阵激活后这里会重新检查。",
                    }
                ],
            },
            {
                "id": "ix_south_lake_gate",
                "kind": "interact",
                "scene_id": "south_lake_gate",
                "regionType": "locked",
                "tile_x": 34,
                "tile_y": 49,
                "approach_tile_x": 31,
                "approach_tile_y": 49,
                "radius": 3,
                "label": "南湖旧渡",
                "title": "南湖旧渡",
                "body": "旧渡口被临时封住，湖对岸已经画在地图上，但还不能探索。",
                "actions": [
                    {
                        "id": "inspect_south_lake",
                        "label": "确认旧渡口封锁",
                        "type": "set_flag",
                        "flag_key": "south_lake_seen",
                        "flag_value": 1,
                        "toast": "南湖旧渡被记在地图上。以后这里适合做跨区域入口。",
                    }
                ],
            },
        ],
        "rows": rows,
    }
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    for x, y in [(24, 24), (11, 27), (54, 22), (67, 24), (35, 22), (82, 24), (31, 49)]:
        assert rows[y][x] in ("0", "3"), (x, y, rows[y][x])
    print(f"wrote {out} ({width}x{height}) spawn={rows[24][24]} tree={rows[22][54]}")


if __name__ == "__main__":
    main()
