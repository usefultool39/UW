#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-MAP-001 v003 地图生成器。

读 world_map.json (108x64 字符网格, 28px/tile, 3024x1792) 生成 9 个注册对齐 PNG 图层 +
atlas + collision/walkable/occlusion/depth 掩码 + VIS-MAP-001_map_v003.json。
每个 layer 用 RGBA，背景透明；terrain_water 层为不透明基底层。
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(r"C:\Users\liang\Desktop\UW")
WORLD_JSON = ROOT / "data" / "world" / "world_map.json"
OUT_DIR = ROOT / "materials" / "inbox" / "visual" / "world"
WORK_DIR = OUT_DIR / "_v003_work"

GRID_W = 108
GRID_H = 64
TILE = 28
LAYER_W = GRID_W * TILE  # 3024
LAYER_H = GRID_H * TILE  # 1792

# legend: 0 grass, 1 forest, 2 water, 3 road, 4 obstacle
COLOR_GRASS = (130, 200, 110, 255)        # 草地
COLOR_GRASS_VARIANT = (118, 188, 100, 255)
COLOR_FOREST = (60, 130, 70, 255)         # 森林
COLOR_FOREST_DARK = (40, 100, 55, 255)
COLOR_WATER = (90, 150, 220, 255)
COLOR_WATER_DEEP = (60, 120, 200, 255)
COLOR_ROAD = (200, 175, 130, 255)         # 道路
COLOR_ROAD_VARIANT = (190, 165, 120, 255)
COLOR_OBSTACLE = (110, 90, 70, 255)


def load_grid() -> List[str]:
    data = json.loads(WORLD_JSON.read_text(encoding="utf-8"))
    rows = data["rows"]
    assert len(rows) == GRID_H, f"expected {GRID_H} rows, got {len(rows)}"
    for r in rows:
        assert len(r) == GRID_W, f"row length {len(r)} != {GRID_W}"
    return rows


def new_layer(rgba_bg=(0, 0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", (LAYER_W, LAYER_H), rgba_bg)


def tile_pixels(layer: Image.Image, x: int, y: int, w: int = 1, h: int = 1,
                color: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> None:
    """填充 (x, y) 起的 w×h 瓦片区域。"""
    px0 = x * TILE
    py0 = y * TILE
    px1 = (x + w) * TILE
    py1 = (y + h) * TILE
    ImageDraw.Draw(layer).rectangle([px0, py0, px1 - 1, py1 - 1], fill=color)


# ---------------- 图层 1: terrain/water ----------------

def draw_terrain_water(grid: List[str]) -> Image.Image:
    """基底层：RGBA, 整层不透明, 草地 + 水体。"""
    layer = new_layer(rgba_bg=(0, 0, 0, 255))
    draw = ImageDraw.Draw(layer)
    # 草地底色
    draw.rectangle([0, 0, LAYER_W - 1, LAYER_H - 1], fill=COLOR_GRASS)
    # 加点状色块做草地变化
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            cx, cy = x * TILE + TILE // 2, y * TILE + TILE // 2
            if t == "2":
                # 水体
                draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                               fill=COLOR_WATER)
            elif t == "1":
                # 森林底色（深绿）
                draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                               fill=COLOR_FOREST_DARK)
            else:
                # 草地变体 - 小色斑
                if (x + y) % 3 == 0:
                    draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                                   fill=COLOR_GRASS_VARIANT)
            # 草地纹理 - 每 2-3 像素一个小色点
            if t in ("0", "3"):
                # 道路/草地上的小细节
                for dx in (4, 12, 20):
                    for dy in (4, 14, 22):
                        if (x + y + dx + dy) % 5 == 0:
                            pcx, pcy = x * TILE + dx, y * TILE + dy
                            r, g, b, _ = COLOR_GRASS
                            draw.point((pcx, pcy),
                                       fill=(max(0, r - 20), max(0, g - 20), b, 255))
    # 高斯模糊让色块更柔和（更接近手绘风）
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.7))
    return layer


# ---------------- 图层 2: roads ----------------

def draw_roads(grid: List[str]) -> Image.Image:
    """道路层，RGBA 透明底。仅 id=3 瓦片有内容。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t == "3":
                px, py = x * TILE, y * TILE
                # 道路基底
                draw.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=COLOR_ROAD)
                # 道路纹理 - 水平小石块
                for i in range(0, TILE, 4):
                    color = COLOR_ROAD_VARIANT if (i // 4 + x + y) % 2 == 0 else COLOR_ROAD
                    draw.line([(px + i, py + 6), (px + i + 2, py + 6)], fill=color)
                    draw.line([(px + i, py + 18), (px + i + 2, py + 18)], fill=color)
                # 边缘暗色
                draw.line([(px, py), (px + TILE - 1, py)], fill=(150, 125, 90, 180))
                draw.line([(px, py + TILE - 1), (px + TILE - 1, py + TILE - 1)],
                          fill=(150, 125, 90, 180))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.5))
    return layer


# ---------------- 图层 3: ground props ----------------

def draw_ground_props(grid: List[str]) -> Image.Image:
    """地面小道具：草簇、石头、蘑菇。仅在草地/道路瓦片上。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    # 在草地上散布小道具
    import random
    rng = random.Random(7001)
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t in ("0", "3"):
                # 50% 概率有草簇
                if rng.random() < 0.4:
                    px = x * TILE + rng.randint(2, TILE - 4)
                    py = y * TILE + rng.randint(2, TILE - 4)
                    sz = rng.randint(2, 4)
                    draw.ellipse([px, py, px + sz, py + sz], fill=(100, 170, 80, 220))
                # 8% 概率有石头
                if rng.random() < 0.06:
                    px = x * TILE + rng.randint(3, TILE - 6)
                    py = y * TILE + rng.randint(3, TILE - 6)
                    sz = rng.randint(3, 5)
                    draw.ellipse([px, py, px + sz, py + sz], fill=(140, 130, 120, 200))
            elif t == "2":
                # 水面小波纹
                if rng.random() < 0.3:
                    px = x * TILE + rng.randint(2, TILE - 6)
                    py = y * TILE + rng.randint(2, TILE - 6)
                    draw.line([(px, py), (px + 4, py)], fill=(255, 255, 255, 100))
    return layer


# ---------------- 图层 4: buildings ----------------

def draw_buildings(grid: List[str]) -> Image.Image:
    """建筑/大型设施。森林视为植被+建筑混合层。
    本层只画明显的人工建筑（教堂、家、广场、传送阵、北门等 POI 位置）。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    # 从 world_map.json 读 scene zones
    wm = json.loads(WORLD_JSON.read_text(encoding="utf-8"))
    zones = wm["scene_zones"]

    # 用更深的绿色块/棕色块表示大型设施
    for z in zones:
        x1, y1, x2, y2 = z["x1"], z["y1"], z["x2"], z["y2"]
        sid = z.get("scene_id", "")
        if sid == "church_library":
            # 教堂书库
            draw.rectangle([x1 * TILE, y1 * TILE, (x2 + 1) * TILE - 1, (y2 + 1) * TILE - 1],
                           fill=(180, 160, 110, 255))
            # 屋顶
            draw.polygon([
                (x1 * TILE, y1 * TILE),
                ((x1 + x2 + 1) // 2 * TILE, y1 * TILE - 8),
                ((x2 + 1) * TILE - 1, y1 * TILE),
            ], fill=(140, 80, 60, 255))
        elif sid == "home_hearth":
            draw.rectangle([x1 * TILE, y1 * TILE, (x2 + 1) * TILE - 1, (y2 + 1) * TILE - 1],
                           fill=(200, 170, 120, 255))
            # 屋顶
            draw.polygon([
                (x1 * TILE, y1 * TILE),
                ((x1 + x2 + 1) // 2 * TILE, y1 * TILE - 6),
                ((x2 + 1) * TILE - 1, y1 * TILE),
            ], fill=(170, 100, 70, 255))
        elif sid == "teleport_plaza":
            # 传送阵 - 蓝紫光环
            cx, cy = (x1 + x2 + 1) // 2 * TILE, (y1 + y2 + 1) // 2 * TILE
            r = ((x2 - x1) // 2 + 1) * TILE
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(140, 110, 200, 200))
        elif sid == "north_gate":
            # 北境边门
            draw.rectangle([x1 * TILE, y1 * TILE, (x2 + 1) * TILE - 1, (y2 + 1) * TILE - 1],
                           fill=(120, 110, 95, 255))
            # 城门框
            draw.rectangle([(x1 + 1) * TILE, (y1 + 1) * TILE,
                            (x1 + 3) * TILE, (y2) * TILE], fill=(70, 60, 50, 255))
        elif sid == "gigas_clearing":
            # 古誓树 - 中心一棵树
            cx = 54 * TILE + TILE // 2
            cy = 22 * TILE + TILE // 2
            # 树冠
            draw.ellipse([cx - 30, cy - 40, cx + 30, cy + 10], fill=(50, 130, 60, 255))
            # 树干
            draw.rectangle([cx - 4, cy + 5, cx + 4, cy + 30], fill=(110, 75, 50, 255))
    return layer


# ---------------- 图层 5: vegetation ----------------

def draw_vegetation(grid: List[str]) -> Image.Image:
    """植被层：森林树冠 + 灌木 + 路旁小树。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    import random
    rng = random.Random(7002)
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t == "1":
                # 森林瓦片 - 大树冠
                cx = x * TILE + TILE // 2
                cy = y * TILE + TILE // 2
                r = 9 + rng.randint(0, 3)
                # 多层树冠
                color = rng.choice([(45, 115, 60, 255), (60, 130, 70, 255), (35, 100, 50, 255)])
                draw.ellipse([cx - r, cy - r + 2, cx + r, cy + r + 2], fill=color)
                # 高光
                draw.ellipse([cx - r + 2, cy - r + 2, cx - r + 6, cy - r + 6],
                             fill=(min(255, color[0] + 30), min(255, color[1] + 30),
                                   min(255, color[2] + 20), 255))
            elif t == "0":
                # 草地瓦片 - 偶尔小树
                if rng.random() < 0.10:
                    cx = x * TILE + rng.randint(4, TILE - 4)
                    cy = y * TILE + rng.randint(4, TILE - 4)
                    r = rng.randint(3, 5)
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 145, 80, 255))
    return layer


# ---------------- 图层 6: occluders ----------------

def draw_occluders(grid: List[str]) -> Image.Image:
    """遮挡层：黑色 alpha 标记。森林=高 alpha，建筑=中 alpha。供 Phaser 深度排序用。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t == "1":
                # 森林 occluder
                draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                               fill=(0, 0, 0, 200))
    # 大建筑 occluder
    wm = json.loads(WORLD_JSON.read_text(encoding="utf-8"))
    for z in wm["scene_zones"]:
        sid = z.get("scene_id", "")
        if sid in ("church_library", "home_hearth", "north_gate"):
            x1, y1, x2, y2 = z["x1"], z["y1"], z["x2"], z["y2"]
            draw.rectangle([x1 * TILE, y1 * TILE, (x2 + 1) * TILE - 1, (y2 + 1) * TILE - 1],
                           fill=(0, 0, 0, 160))
    return layer


# ---------------- 图层 7: foreground ----------------

def draw_foreground(grid: List[str]) -> Image.Image:
    """前景深度层：路径附近低植被、围栏、装饰物。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    import random
    rng = random.Random(7003)
    # 道路两侧的草叶
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] == "3":
                # 道路四边随机小草
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_W and 0 <= ny < GRID_H and grid[ny][nx] == "0":
                        if rng.random() < 0.3:
                            px = nx * TILE + rng.randint(2, TILE - 4)
                            py = ny * TILE + rng.randint(2, TILE - 4)
                            draw.line([(px, py + 2), (px, py - 2)], fill=(110, 170, 90, 220))
    return layer


# ---------------- 图层 8: lighting ----------------

def draw_lighting(grid: List[str]) -> Image.Image:
    """光照层：暖色阳光 + 阴影。半透明叠加。"""
    layer = new_layer()
    # 用 numpy 渐变生成柔和阳光
    import numpy as np
    arr = np.zeros((LAYER_H, LAYER_W, 4), dtype=np.uint8)
    # 中心暖光
    cx, cy = LAYER_W * 0.35, LAYER_H * 0.25
    yy, xx = np.mgrid[0:LAYER_H, 0:LAYER_W]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    max_dist = np.sqrt(LAYER_W ** 2 + LAYER_H ** 2) * 0.7
    warmth = np.clip(1.0 - dist / max_dist, 0, 1) * 80
    arr[..., 0] = warmth.astype(np.uint8)  # R
    arr[..., 1] = (warmth * 0.85).astype(np.uint8)  # G
    arr[..., 2] = (warmth * 0.6).astype(np.uint8)  # B
    arr[..., 3] = (warmth * 0.5).astype(np.uint8)  # A
    layer = Image.fromarray(arr)

    # 森林阴影
    sh = Image.new("RGBA", (LAYER_W, LAYER_H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sh)
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] == "1":
                sdraw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                                fill=(0, 0, 0, 60))
    return Image.alpha_composite(layer, sh)


# ---------------- 图层 9: weather ----------------

def draw_weather(grid: List[str]) -> Image.Image:
    """天气层：远处云/薄雾，透明叠加。"""
    layer = new_layer()
    draw = ImageDraw.Draw(layer)
    import random
    rng = random.Random(7004)
    # 散布白色云朵
    for _ in range(18):
        cx = rng.randint(0, LAYER_W)
        cy = rng.randint(0, LAYER_H // 2)
        r = rng.randint(60, 140)
        # 用 3-4 个圆叠出云
        for ox, oy, rr in [(0, 0, r), (-r // 2, 5, r * 0.8), (r // 2, 5, r * 0.8),
                           (-r // 4, -r // 4, r * 0.7)]:
            draw.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr],
                         fill=(255, 255, 255, 35))
    return layer


# ---------------- collision / walkable / occlusion / depth 掩码 ----------------

def draw_collision(grid: List[str]) -> Image.Image:
    """collision: RGBA, R=255 表示阻挡, A=255.
    1=森林, 2=水, 4=障碍, 3=道路(部分碰撞见 walkable)"""
    layer = Image.new("RGBA", (LAYER_W, LAYER_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t in ("1", "2", "4"):
                draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                               fill=(255, 0, 0, 255))
    # 大建筑 = 阻挡
    wm = json.loads(WORLD_JSON.read_text(encoding="utf-8"))
    for z in wm["scene_zones"]:
        sid = z.get("scene_id", "")
        if sid in ("church_library", "home_hearth", "north_gate", "teleport_plaza"):
            x1, y1, x2, y2 = z["x1"], z["y1"], z["x2"], z["y2"]
            draw.rectangle([x1 * TILE, y1 * TILE, (x2 + 1) * TILE - 1, (y2 + 1) * TILE - 1],
                           fill=(255, 0, 0, 255))
    return layer


def draw_walkable(grid: List[str]) -> Image.Image:
    """walkable: RGBA, G=255 表示可走, A=255. 仅 0 草地和 3 道路"""
    layer = Image.new("RGBA", (LAYER_W, LAYER_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t in ("0", "3"):
                draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                               fill=(0, 255, 0, 255))
    return layer


def draw_occlusion_depth(grid: List[str]) -> Image.Image:
    """occlusion_depth: RGBA, 灰度图表示深度排序权重。数值越大越靠前。"""
    layer = Image.new("RGBA", (LAYER_W, LAYER_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    # 0=草 -> 0
    # 1=森林 -> 80
    # 2=水 -> 0
    # 3=道路 -> 0
    # 4=障碍 -> 100
    for y in range(GRID_H):
        for x in range(GRID_W):
            t = grid[y][x]
            if t == "1":
                v = 80
            elif t == "4":
                v = 100
            else:
                continue
            draw.rectangle([x * TILE, y * TILE, (x + 1) * TILE - 1, (y + 1) * TILE - 1],
                           fill=(v, v, v, 255))
    return layer


# ---------------- atlas ----------------

def draw_tile_atlas() -> Tuple[Image.Image, Dict[str, Dict]]:
    """tile atlas: 64x64 per tile, 4x4 grid, RGBA。包含 0 草地/1 森林/2 水/3 道路/4 障碍 5 种 + 道路变体."""
    atlas_w, atlas_h = 256, 256
    tile_size = 64
    cols = atlas_w // tile_size
    rows = atlas_h // tile_size
    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    names = ["grass", "grass_variant", "forest", "forest_dark", "water", "water_deep",
             "road", "road_variant", "road_edge", "obstacle", "occluder_walkable",
             "occluder_blocked", "shadow", "highlight", "placeholder", "reserved"]
    palette = [
        COLOR_GRASS, COLOR_GRASS_VARIANT, COLOR_FOREST, COLOR_FOREST_DARK,
        COLOR_WATER, COLOR_WATER_DEEP, COLOR_ROAD, COLOR_ROAD_VARIANT,
        (150, 125, 90, 255), COLOR_OBSTACLE, (0, 0, 0, 0), (255, 0, 0, 255),
        (0, 0, 0, 80), (255, 255, 255, 100), (0, 0, 0, 0), (0, 0, 0, 0),
    ]
    for i, (name, color) in enumerate(zip(names, palette)):
        col = i % cols
        row = i // cols
        x0 = col * tile_size
        y0 = row * tile_size
        if name in ("placeholder", "reserved", "occluder_walkable"):
            # 透明或留白
            continue
        draw.rectangle([x0, y0, x0 + tile_size - 1, y0 + tile_size - 1], fill=color)
        # 加网格
        draw.rectangle([x0, y0, x0 + tile_size - 1, y0 + tile_size - 1],
                       outline=(0, 0, 0, 100))

    manifest: Dict[str, Dict] = {
        "atlas": "tiles_atlas_v003.png",
        "tile_size_px": tile_size,
        "cols": cols,
        "rows": rows,
        "tiles": {},
    }
    for i, name in enumerate(names):
        if name in ("placeholder", "reserved", "occluder_walkable"):
            continue
        col = i % cols
        row = i // cols
        manifest["tiles"][name] = {
            "col": col,
            "row": row,
            "x": col * tile_size,
            "y": row * tile_size,
            "w": tile_size,
            "h": tile_size,
        }
    return atlas, manifest


def draw_prop_atlas() -> Tuple[Image.Image, Dict[str, Dict]]:
    """prop atlas: 32x32 per prop, 8x8 grid, RGBA。"""
    atlas_w, atlas_h = 256, 256
    prop_size = 32
    cols = atlas_w // prop_size
    rows = atlas_h // prop_size
    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    import random
    rng = random.Random(7005)
    names = ["grass_tuft", "small_rock", "mushroom", "small_tree", "bush",
             "tree_top", "tree_trunk", "lamp_post", "fence_post", "well",
             "barrel", "stump", "log", "path_stone", "moss", "flower_red",
             "flower_yellow", "leaf_pile", "twig", "bird_feather", "small_mound",
             "dirt_patch", "wood_chip", "feather_white", "berry_red", "berry_blue",
             "mushroom_red", "mushroom_brown", "moss_dark", "stone_path",
             "rope", "wooden_box"]
    for i, name in enumerate(names):
        col = i % cols
        row = i // cols
        x0 = col * prop_size
        y0 = row * prop_size
        cx, cy = x0 + prop_size // 2, y0 + prop_size // 2
        if name == "grass_tuft":
            for dx, dy in [(-4, 0), (0, -2), (4, 0), (0, 2)]:
                draw.line([(cx + dx, cy + dy), (cx + dx, cy + dy - 6)], fill=(100, 170, 80, 255))
        elif name == "small_rock":
            draw.ellipse([cx - 5, cy - 3, cx + 5, cy + 3], fill=(140, 130, 120, 255))
            draw.ellipse([cx - 3, cy - 5, cx - 1, cy - 3], fill=(170, 160, 150, 255))
        elif name == "mushroom":
            draw.rectangle([cx - 1, cy - 1, cx + 1, cy + 5], fill=(220, 200, 180, 255))
            draw.ellipse([cx - 4, cy - 5, cx + 4, cy - 1], fill=(180, 60, 60, 255))
        elif name == "small_tree":
            draw.rectangle([cx - 1, cy, cx + 1, cy + 6], fill=(110, 75, 50, 255))
            draw.ellipse([cx - 5, cy - 9, cx + 5, cy + 1], fill=(70, 145, 80, 255))
        elif name == "bush":
            draw.ellipse([cx - 7, cy - 4, cx + 7, cy + 4], fill=(80, 150, 90, 255))
        elif name == "tree_top":
            draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 6], fill=(45, 115, 60, 255))
        elif name == "tree_trunk":
            draw.rectangle([cx - 2, cy - 4, cx + 2, cy + 10], fill=(110, 75, 50, 255))
        elif name in ("lamp_post", "fence_post", "well", "barrel", "stump", "log",
                      "path_stone", "moss", "flower_red", "flower_yellow", "leaf_pile",
                      "twig", "bird_feather", "small_mound", "dirt_patch", "wood_chip",
                      "feather_white", "berry_red", "berry_blue", "mushroom_red",
                      "mushroom_brown", "moss_dark", "stone_path", "rope", "wooden_box"):
            # 简单占位：圆形/方形彩色
            color_pool = {
                "lamp_post": (50, 50, 60, 255),
                "fence_post": (140, 110, 80, 255),
                "well": (90, 90, 100, 255),
                "barrel": (140, 90, 50, 255),
                "stump": (110, 75, 50, 255),
                "log": (130, 90, 60, 255),
                "path_stone": (160, 150, 140, 255),
                "moss": (60, 140, 80, 255),
                "flower_red": (220, 60, 60, 255),
                "flower_yellow": (220, 200, 60, 255),
                "leaf_pile": (110, 160, 70, 255),
                "twig": (130, 95, 70, 255),
                "bird_feather": (200, 200, 210, 255),
                "small_mound": (150, 130, 100, 255),
                "dirt_patch": (130, 100, 70, 255),
                "wood_chip": (160, 130, 90, 255),
                "feather_white": (240, 240, 240, 255),
                "berry_red": (200, 40, 40, 255),
                "berry_blue": (60, 60, 200, 255),
                "mushroom_red": (200, 70, 50, 255),
                "mushroom_brown": (130, 80, 50, 255),
                "moss_dark": (40, 110, 60, 255),
                "stone_path": (170, 160, 150, 255),
                "rope": (180, 160, 110, 255),
                "wooden_box": (140, 100, 60, 255),
            }
            color = color_pool.get(name, (200, 200, 200, 255))
            if name in ("flower_red", "flower_yellow", "berry_red", "berry_blue",
                        "mushroom_red", "feather_white", "bird_feather"):
                draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=color)
            else:
                draw.rectangle([cx - 5, cy - 4, cx + 5, cy + 4], fill=color)
    manifest: Dict[str, Dict] = {
        "atlas": "props_atlas_v003.png",
        "prop_size_px": prop_size,
        "cols": cols,
        "rows": rows,
        "props": {},
    }
    for i, name in enumerate(names):
        col = i % cols
        row = i // cols
        manifest["props"][name] = {
            "col": col, "row": row,
            "x": col * prop_size, "y": row * prop_size,
            "w": prop_size, "h": prop_size,
        }
    return atlas, manifest


# ---------------- 主流程 ----------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    grid = load_grid()

    print("Drawing terrain_water...")
    terrain = draw_terrain_water(grid)
    terrain.save(OUT_DIR / "VIS-MAP-001_rulid_village_terrain_v003.png", "PNG", optimize=True)

    print("Drawing roads...")
    roads = draw_roads(grid)
    roads.save(OUT_DIR / "VIS-MAP-001_rulid_village_roads_v003.png", "PNG", optimize=True)

    print("Drawing ground_props...")
    ground = draw_ground_props(grid)
    ground.save(OUT_DIR / "VIS-MAP-001_rulid_village_ground_props_v003.png", "PNG", optimize=True)

    print("Drawing buildings...")
    buildings = draw_buildings(grid)
    buildings.save(OUT_DIR / "VIS-MAP-001_rulid_village_buildings_v003.png", "PNG", optimize=True)

    print("Drawing vegetation...")
    veg = draw_vegetation(grid)
    veg.save(OUT_DIR / "VIS-MAP-001_rulid_village_vegetation_v003.png", "PNG", optimize=True)

    print("Drawing occluders...")
    occ = draw_occluders(grid)
    occ.save(OUT_DIR / "VIS-MAP-001_rulid_village_occluders_v003.png", "PNG", optimize=True)

    print("Drawing foreground...")
    fg = draw_foreground(grid)
    fg.save(OUT_DIR / "VIS-MAP-001_rulid_village_foreground_v003.png", "PNG", optimize=True)

    print("Drawing lighting...")
    light = draw_lighting(grid)
    light.save(OUT_DIR / "VIS-MAP-001_rulid_village_lighting_v003.png", "PNG", optimize=True)

    print("Drawing weather...")
    weather = draw_weather(grid)
    weather.save(OUT_DIR / "VIS-MAP-001_rulid_village_weather_v003.png", "PNG", optimize=True)

    print("Drawing collision/walkable/occlusion_depth...")
    coll = draw_collision(grid)
    coll.save(OUT_DIR / "VIS-MAP-001_rulid_village_collision_v003.png", "PNG", optimize=True)
    walk = draw_walkable(grid)
    walk.save(OUT_DIR / "VIS-MAP-001_rulid_village_walkable_v003.png", "PNG", optimize=True)
    depth = draw_occlusion_depth(grid)
    depth.save(OUT_DIR / "VIS-MAP-001_rulid_village_occlusion_depth_v003.png", "PNG", optimize=True)

    print("Drawing atlases...")
    tiles_atlas, tiles_manifest = draw_tile_atlas()
    tiles_atlas.save(OUT_DIR / "tiles_atlas_v003.png", "PNG", optimize=True)
    props_atlas, props_manifest = draw_prop_atlas()
    props_atlas.save(OUT_DIR / "props_atlas_v003.png", "PNG", optimize=True)

    # Master composite (terrain + roads + buildings + veg + occluders + lighting + weather)
    print("Drawing master composite...")
    master = terrain.copy()
    for layer in (roads, buildings, veg, occ, fg, light, weather):
        master = Image.alpha_composite(master, layer)
    master.save(OUT_DIR / "VIS-MAP-001_rulid_village_master_v003.png", "PNG", optimize=True)

    # JSON metadata
    print("Writing map JSON...")
    wm = json.loads(WORLD_JSON.read_text(encoding="utf-8"))
    metadata: Dict = {
        "schema_version": "v003",
        "request_id": "VIS-MAP-001",
        "created_at": "2026-08-07",
        "grid": {
            "cols": GRID_W,
            "rows": GRID_H,
            "tile_size_px": TILE,
            "layer_width_px": LAYER_W,
            "layer_height_px": LAYER_H,
        },
        "legend": wm["legend"],
        "scene_zones": wm["scene_zones"],
        "pois": wm["pois"],
        "spawn": wm.get("spawn", {"x": 24, "y": 24}),
        "walkable_tile_ids": wm.get("walkable", [0, 3]),
        "blocked_tile_ids": [1, 2, 4],
        "poi_interaction_data": {
            z["scene_id"]: {
                "id": z["scene_id"],
                "label": z.get("label"),
                "regionType": z.get("regionType"),
                "tile_bounds": [z["x1"], z["y1"], z["x2"], z["y2"]],
                "entry_points": z.get("entry_points", []),
                "transfers": z.get("transfers", []),
                "requirements": z.get("requirements", {}),
            }
            for z in wm["scene_zones"]
        },
        "tiles_atlas": tiles_manifest,
        "props_atlas": props_manifest,
        "layers": [
            {"name": "terrain_water", "file": "VIS-MAP-001_rulid_village_terrain_v003.png",
             "alpha": "RGBA", "description": "base grass + water bodies, full opacity"},
            {"name": "roads", "file": "VIS-MAP-001_rulid_village_roads_v003.png",
             "alpha": "RGBA", "description": "dirt path tile id=3"},
            {"name": "ground_props", "file": "VIS-MAP-001_rulid_village_ground_props_v003.png",
             "alpha": "RGBA", "description": "grass tufts, small rocks, water ripples"},
            {"name": "buildings", "file": "VIS-MAP-001_rulid_village_buildings_v003.png",
             "alpha": "RGBA", "description": "church library, home hearth, north gate, "
                                                "teleport plaza, gigas tree"},
            {"name": "vegetation", "file": "VIS-MAP-001_rulid_village_vegetation_v003.png",
             "alpha": "RGBA", "description": "forest canopies + scattered small trees"},
            {"name": "occluders", "file": "VIS-MAP-001_rulid_village_occluders_v003.png",
             "alpha": "RGBA", "description": "high-alpha occluders for depth sort"},
            {"name": "foreground", "file": "VIS-MAP-001_rulid_village_foreground_v003.png",
             "alpha": "RGBA", "description": "road-adjacent grass blades, decorative props"},
            {"name": "lighting", "file": "VIS-MAP-001_rulid_village_lighting_v003.png",
             "alpha": "RGBA", "description": "warm sunlight + forest shadows"},
            {"name": "weather", "file": "VIS-MAP-001_rulid_village_weather_v003.png",
             "alpha": "RGBA", "description": "ambient cloud/fog layer"},
        ],
        "masks": {
            "collision": {
                "file": "VIS-MAP-001_rulid_village_collision_v003.png",
                "encoding": "R=255 means blocked, A=255",
            },
            "walkable": {
                "file": "VIS-MAP-001_rulid_village_walkable_v003.png",
                "encoding": "G=255 means walkable, A=255",
            },
            "occlusion_depth": {
                "file": "VIS-MAP-001_rulid_village_occlusion_depth_v003.png",
                "encoding": "grayscale 0..255, higher = closer to camera",
            },
        },
        "master_composite": "VIS-MAP-001_rulid_village_master_v003.png",
    }
    json_path = OUT_DIR / "VIS-MAP-001_map_v003.json"
    json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {json_path}")


if __name__ == "__main__":
    main()
