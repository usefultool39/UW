#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UW《边境回声》Tile/Prop Atlas 生成器
- 卢利特村 9 层地图可切片素材
- terrain / water / roads / buildings / vegetation / occlusion / foreground / lighting / weather
- 风格匹配现有 v005 map
- tile_size 28px, 兼容 108x64 grid, 3024x1792 合成
"""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math
import os
import json
import hashlib
import random
from datetime import datetime

random.seed(20260807)

OUTPUT_DIR = r"C:\Users\liang\Desktop\uw\materials\inbox\visual\world"
TILE_SIZE = 28

# === 调色板（匹配 v005 风格）===
PAL = {
    "grass_light": (135, 185, 95),
    "grass_mid": (105, 160, 75),
    "grass_dark": (78, 130, 58),
    "grass_shadow": (55, 95, 42),
    "dirt_light": (175, 140, 95),
    "dirt_mid": (150, 115, 75),
    "dirt_dark": (120, 85, 55),
    "stone_light": (185, 180, 165),
    "stone_mid": (155, 150, 138),
    "stone_dark": (120, 115, 105),
    "water_light": (115, 175, 195),
    "water_mid": (75, 140, 170),
    "water_dark": (45, 100, 135),
    "water_deep": (30, 75, 105),
    "wood_light": (185, 150, 95),
    "wood_mid": (155, 118, 65),
    "wood_dark": (115, 82, 42),
    "wood_darkest": (75, 52, 28),
    "leaf_light": (140, 180, 90),
    "leaf_mid": (100, 150, 65),
    "leaf_dark": (70, 110, 45),
    "roof_red": (170, 70, 50),
    "roof_brown": (140, 95, 60),
    "wall_light": (220, 200, 165),
    "wall_mid": (195, 175, 140),
    "wall_dark": (160, 138, 105),
    "warm_glow": (255, 220, 130),
    "warm_glow_outer": (255, 200, 100, 60),
    "rain": (180, 195, 210, 160),
    "fog": (220, 225, 230, 80),
}


def rgba(c, a=255):
    if len(c) == 3:
        return (c[0], c[1], c[2], a)
    return c


def smooth_noise(size, scale=4, octaves=3):
    """生成平滑噪声纹理。"""
    w, h = size
    img = Image.new("L", (w * scale // 4 + 1, h * scale // 4 + 1))
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            px[x, y] = random.randint(0, 255)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = img.resize((w, h), Image.LANCZOS)
    return img


def apply_texture(base_img, noise_scale=0.15):
    """为图片添加噪声纹理。"""
    w, h = base_img.size
    noise = smooth_noise((w, h), scale=4)
    result = Image.new("RGBA", (w, h))
    px_base = base_img.load()
    px_noise = noise.load()
    px_result = result.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px_base[x, y]
            n = px_noise[x, y] / 255.0
            factor = 1.0 + (n - 0.5) * noise_scale * 2
            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))
            px_result[x, y] = (r, g, b, a)
    return result


def gen_terrain_tile(variant="grass", seed=None):
    """生成单个 terrain tile（28x28）。"""
    if seed is not None:
        random.seed(seed)
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if variant == "grass":
        # 草地 tile：底色 + 草丛纹理
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                # 基础色微变
                t = (math.sin(x * 0.3) + math.cos(y * 0.4)) * 0.5
                if t > 0.3:
                    c = PAL["grass_light"]
                elif t > -0.3:
                    c = PAL["grass_mid"]
                else:
                    c = PAL["grass_dark"]
                # 噪声扰动
                n = random.uniform(-0.1, 0.1)
                c = tuple(max(0, min(255, int(v + n * 30))) for v in c)
                img.putpixel((x, y), rgba(c, 255))
        # 草丛细节
        for _ in range(8):
            gx = random.randint(0, TILE_SIZE - 1)
            gy = random.randint(0, TILE_SIZE - 1)
            gh = random.randint(2, 4)
            gc = random.choice([PAL["grass_light"], PAL["grass_dark"]])
            draw.line([(gx, gy), (gx + random.choice([-1, 0, 1]), gy - gh)],
                      fill=rgba(gc), width=1)

    elif variant == "dirt":
        # 泥土 tile
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                t = (math.sin(x * 0.4) + math.cos(y * 0.3)) * 0.5
                if t > 0.2:
                    c = PAL["dirt_light"]
                elif t > -0.2:
                    c = PAL["dirt_mid"]
                else:
                    c = PAL["dirt_dark"]
                n = random.uniform(-0.08, 0.08)
                c = tuple(max(0, min(255, int(v + n * 25))) for v in c)
                img.putpixel((x, y), rgba(c, 255))
        # 小石子
        for _ in range(3):
            sx = random.randint(2, TILE_SIZE - 3)
            sy = random.randint(2, TILE_SIZE - 3)
            sr = random.randint(1, 2)
            sc = random.choice([PAL["stone_light"], PAL["stone_dark"]])
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=rgba(sc))

    elif variant == "stone":
        # 石板 tile（路用）
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                t = (math.sin(x * 0.5) + math.cos(y * 0.5)) * 0.5
                if t > 0.2:
                    c = PAL["stone_light"]
                elif t > -0.2:
                    c = PAL["stone_mid"]
                else:
                    c = PAL["stone_dark"]
                n = random.uniform(-0.06, 0.06)
                c = tuple(max(0, min(255, int(v + n * 20))) for v in c)
                img.putpixel((x, y), rgba(c, 255))

    img = apply_texture(img, noise_scale=0.08)
    return img


def gen_water_tile(variant="river", seed=None):
    """生成水 tile。"""
    if seed is not None:
        random.seed(seed)
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if variant == "river":
        # 流动水面：横向波纹
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                t = math.sin((x + y * 0.5) * 0.6) * 0.5
                if t > 0.2:
                    c = PAL["water_light"]
                elif t > -0.2:
                    c = PAL["water_mid"]
                else:
                    c = PAL["water_dark"]
                n = random.uniform(-0.05, 0.05)
                c = tuple(max(0, min(255, int(v + n * 15))) for v in c)
                img.putpixel((x, y), rgba(c, 220))
        # 高光
        for _ in range(4):
            lx = random.randint(2, TILE_SIZE - 8)
            ly = random.randint(2, TILE_SIZE - 3)
            lw = random.randint(3, 6)
            draw.line([(lx, ly), (lx + lw, ly)],
                      fill=rgba((220, 230, 240), 180), width=1)

    elif variant == "deep":
        # 深水 tile
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                t = math.sin(x * 0.3 + y * 0.2) * 0.5
                if t > 0.1:
                    c = PAL["water_dark"]
                else:
                    c = PAL["water_deep"]
                img.putpixel((x, y), rgba(c, 230))

    img = apply_texture(img, noise_scale=0.05)
    return img


def gen_road_tile(variant="cobble", seed=None):
    """生成路面 tile。"""
    if seed is not None:
        random.seed(seed)
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if variant == "cobble":
        # 鹅卵石路面：基色 + 圆石
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                img.putpixel((x, y), rgba(PAL["stone_mid"], 255))
        # 大石块
        stones = [
            (3, 3, 5, PAL["stone_light"]),
            (14, 5, 4, PAL["stone_dark"]),
            (22, 2, 4, PAL["stone_light"]),
            (6, 14, 5, PAL["stone_dark"]),
            (17, 13, 4, PAL["stone_light"]),
            (24, 16, 4, PAL["stone_mid"]),
            (3, 22, 4, PAL["stone_light"]),
            (14, 22, 5, PAL["stone_dark"]),
            (23, 23, 4, PAL["stone_light"]),
        ]
        for sx, sy, sr, sc in stones:
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                         fill=rgba(sc))
            draw.ellipse([sx - sr + 1, sy - sr + 1, sx + sr - 1, sy + sr - 1],
                         fill=rgba(sc, 200))

    elif variant == "dirt":
        # 泥路
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                t = math.sin(x * 0.4) * 0.3 + math.cos(y * 0.5) * 0.2
                if t > 0.2:
                    c = PAL["dirt_light"]
                elif t > -0.2:
                    c = PAL["dirt_mid"]
                else:
                    c = PAL["dirt_dark"]
                img.putpixel((x, y), rgba(c, 255))
        # 车辙
        for y in [6, 20]:
            for x in range(TILE_SIZE):
                if x % 2 == 0:
                    img.putpixel((x, y), rgba(PAL["dirt_dark"], 255))

    img = apply_texture(img, noise_scale=0.06)
    return img


def gen_vegetation_prop(variant="tree", seed=None):
    """生成植被 prop（28x28+，透明背景）。"""
    if seed is not None:
        random.seed(seed)
    size = 56  # prop 大一点，2x2 tile
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if variant == "tree":
        # 树：树干 + 树冠
        # 树干
        draw.rectangle([size // 2 - 3, size - 18, size // 2 + 3, size - 2],
                       fill=rgba(PAL["wood_mid"]))
        draw.rectangle([size // 2 - 3, size - 18, size // 2 - 1, size - 2],
                       fill=rgba(PAL["wood_light"]))
        # 树冠（多层圆）
        cx, cy = size // 2, size // 2 - 4
        for r, c in [(22, PAL["leaf_mid"]), (18, PAL["leaf_dark"]),
                     (14, PAL["leaf_mid"]), (10, PAL["leaf_light"])]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(c))
        # 树叶纹理
        for _ in range(12):
            lx = random.randint(cx - 16, cx + 16)
            ly = random.randint(cy - 16, cy + 16)
            lc = random.choice([PAL["leaf_light"], PAL["leaf_dark"], PAL["leaf_mid"]])
            draw.ellipse([lx - 1, ly - 1, lx + 1, ly + 1], fill=rgba(lc))

    elif variant == "bush":
        # 灌木：椭圆形
        cx, cy = size // 2, size // 2 + 4
        for r, c in [(14, PAL["leaf_mid"]), (10, PAL["leaf_dark"]),
                     (7, PAL["leaf_mid"]), (4, PAL["leaf_light"])]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(c))

    elif variant == "grass_patch":
        # 草丛：多束细线
        for _ in range(15):
            gx = random.randint(2, size - 2)
            gy = random.randint(2, size - 2)
            gh = random.randint(3, 8)
            gc = random.choice([PAL["grass_light"], PAL["grass_mid"],
                                PAL["grass_dark"]])
            draw.line([(gx, gy), (gx + random.choice([-1, 0, 1]), gy - gh)],
                      fill=rgba(gc), width=1)

    elif variant == "flower":
        # 花：几朵小花
        for _ in range(3):
            fx = random.randint(6, size - 6)
            fy = random.randint(6, size - 6)
            fc = random.choice([(220, 180, 100), (200, 100, 140),
                                (240, 220, 140), (180, 140, 200)])
            draw.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=rgba(fc))
            draw.ellipse([fx - 1, fy - 1, fx + 1, fy + 1], fill=rgba((255, 240, 180)))
            draw.line([(fx, fy + 2), (fx, fy + 6)],
                      fill=rgba(PAL["grass_dark"]), width=1)

    img = apply_texture(img, noise_scale=0.05)
    return img


def gen_building_prop(variant="house", seed=None):
    """生成建筑 prop（多 tile 大小，透明背景）。"""
    if seed is not None:
        random.seed(seed)

    if variant == "house_small":
        size = 84  # 3x3 tile
    elif variant == "church":
        size = 112  # 4x4 tile
    elif variant == "house_large":
        size = 112
    elif variant == "well":
        size = 56  # 2x2 tile
    elif variant == "market":
        size = 84  # 3x3 tile
    elif variant == "shed":
        size = 56
    else:
        size = 56

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if variant == "house_small":
        # 小木屋：木墙 + 三角顶
        base_y = size - 16  # 地面
        wall_w = 60
        wall_h = 40
        wall_x = (size - wall_w) // 2
        # 墙
        draw.rectangle([wall_x, base_y - wall_h, wall_x + wall_w, base_y],
                       fill=rgba(PAL["wood_mid"]))
        # 墙板
        for i in range(3):
            y = base_y - wall_h + i * (wall_h // 3)
            draw.line([(wall_x, y), (wall_x + wall_w, y)],
                      fill=rgba(PAL["wood_dark"]), width=1)
        # 亮面
        draw.rectangle([wall_x, base_y - wall_h, wall_x + 6, base_y],
                       fill=rgba(PAL["wood_light"]))
        # 屋顶（三角）
        roof_top = (size // 2, base_y - wall_h - 30)
        roof_left = (wall_x - 5, base_y - wall_h)
        roof_right = (wall_x + wall_w + 5, base_y - wall_h)
        draw.polygon([roof_left, roof_top, roof_right],
                     fill=rgba(PAL["roof_brown"]))
        # 屋顶暗面
        draw.polygon([roof_top, roof_right, (size // 2, base_y - wall_h)],
                     fill=rgba(PAL["wood_darkest"], 180))
        # 屋顶亮面
        draw.polygon([roof_left, (size // 2, base_y - wall_h - 1), roof_top],
                     fill=rgba(PAL["wood_light"], 150))
        # 门
        door_w, door_h = 10, 18
        door_x = size // 2 - door_w // 2
        door_y = base_y - door_h
        draw.rectangle([door_x, door_y, door_x + door_w, base_y],
                       fill=rgba(PAL["wood_darkest"]))
        draw.rectangle([door_x + 1, door_y + 1, door_x + door_w - 1, base_y - 1],
                       fill=rgba(PAL["wood_dark"]))
        # 窗
        win_w, win_h = 6, 6
        win_x = wall_x + 8
        draw.rectangle([win_x, base_y - wall_h + 8, win_x + win_w, base_y - wall_h + 8 + win_h],
                       fill=rgba((60, 50, 35)))
        draw.rectangle([win_x + wall_w - 14, base_y - wall_h + 8,
                        win_x + wall_w - 14 + win_w, base_y - wall_h + 8 + win_h],
                       fill=rgba((60, 50, 35)))
        # 烟囱
        chim_x = wall_x + wall_w - 14
        chim_top = base_y - wall_h - 20
        draw.rectangle([chim_x, chim_top, chim_x + 6, base_y - wall_h - 5],
                       fill=rgba(PAL["stone_dark"]))
        # 烟
        for i in range(3):
            sx = chim_x + 3 + random.randint(-2, 2)
            sy = chim_top - i * 4 - random.randint(0, 2)
            sr = 3 + i
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                         fill=rgba((200, 200, 200, 100 - i * 30)))

    elif variant == "church":
        # 教会/书库：石墙 + 高顶 + 钟楼
        base_y = size - 16
        wall_w = 80
        wall_h = 55
        wall_x = (size - wall_w) // 2
        # 主墙
        draw.rectangle([wall_x, base_y - wall_h, wall_x + wall_w, base_y],
                       fill=rgba(PAL["wall_mid"]))
        # 石块纹理
        for row in range(5):
            y = base_y - wall_h + row * (wall_h // 5)
            offset = (row % 2) * 10
            for col in range(4):
                x = wall_x + offset + col * (wall_w // 4)
                draw.rectangle([x + 1, y + 1, x + (wall_w // 4) - 1, y + (wall_h // 5) - 1],
                               outline=rgba(PAL["wall_dark"]))
        # 屋顶（高顶）
        roof_top = (size // 2, base_y - wall_h - 35)
        roof_left = (wall_x - 4, base_y - wall_h)
        roof_right = (wall_x + wall_w + 4, base_y - wall_h)
        draw.polygon([roof_left, roof_top, roof_right],
                     fill=rgba(PAL["roof_red"]))
        # 屋顶亮面
        draw.polygon([roof_left, roof_top, (size // 2, base_y - wall_h)],
                     fill=rgba((200, 90, 70), 150))
        # 钟楼（小塔）
        tower_w = 18
        tower_h = 30
        tower_x = size // 2 - tower_w // 2
        tower_top = base_y - wall_h - 35 - tower_h
        draw.rectangle([tower_x, tower_top, tower_x + tower_w, base_y - wall_h - 35],
                       fill=rgba(PAL["wall_light"]))
        # 钟楼顶
        draw.polygon([(tower_x - 2, base_y - wall_h - 35),
                      (size // 2, tower_top - 10),
                      (tower_x + tower_w + 2, base_y - wall_h - 35)],
                     fill=rgba(PAL["roof_red"]))
        # 钟
        draw.ellipse([size // 2 - 3, base_y - wall_h - 50,
                      size // 2 + 3, base_y - wall_h - 44],
                     fill=rgba((255, 220, 100)))
        # 大门（拱形）
        door_w, door_h = 14, 25
        door_x = size // 2 - door_w // 2
        door_y = base_y - door_h
        draw.rectangle([door_x, door_y, door_x + door_w, base_y],
                       fill=rgba(PAL["wood_darkest"]))
        draw.pieslice([door_x - 2, door_y - door_w // 2,
                       door_x + door_w + 2, door_y + 2],
                      start=180, end=360, fill=rgba(PAL["wood_darkest"]))
        # 大窗（圆）
        win_r = 5
        win_cx = size // 2
        win_cy = base_y - wall_h + 18
        draw.ellipse([win_cx - win_r, win_cy - win_r, win_cx + win_r, win_cy + win_r],
                     fill=rgba((200, 180, 80)))
        draw.ellipse([win_cx - win_r, win_cy - win_r, win_cx + win_r, win_cy + win_r],
                     outline=rgba(PAL["wall_dark"]))
        # 窗十字
        draw.line([(win_cx, win_cy - win_r), (win_cx, win_cy + win_r)],
                  fill=rgba(PAL["wall_dark"]), width=1)
        draw.line([(win_cx - win_r, win_cy), (win_cx + win_r, win_cy)],
                  fill=rgba(PAL["wall_dark"]), width=1)

    elif variant == "well":
        # 水井：圆石堆 + 木架
        cx = size // 2
        base_y = size - 8
        # 圆石堆
        draw.ellipse([cx - 14, base_y - 18, cx + 14, base_y + 4],
                     fill=rgba(PAL["stone_mid"]))
        draw.ellipse([cx - 12, base_y - 16, cx + 12, base_y + 2],
                     fill=rgba(PAL["stone_dark"]))
        draw.ellipse([cx - 8, base_y - 14, cx + 8, base_y - 2],
                     fill=rgba(PAL["water_dark"]))
        # 木架
        draw.rectangle([cx - 16, base_y - 38, cx - 14, base_y - 18],
                       fill=rgba(PAL["wood_mid"]))
        draw.rectangle([cx + 14, base_y - 38, cx + 16, base_y - 18],
                       fill=rgba(PAL["wood_mid"]))
        # 横木
        draw.rectangle([cx - 16, base_y - 40, cx + 16, base_y - 36],
                       fill=rgba(PAL["wood_dark"]))
        # 顶
        draw.polygon([(cx - 18, base_y - 40), (cx, base_y - 46), (cx + 18, base_y - 40)],
                     fill=rgba(PAL["roof_brown"]))

    elif variant == "market":
        # 市场摊位：木架 + 棚顶
        base_y = size - 8
        # 摊位台
        draw.rectangle([12, base_y - 16, size - 12, base_y],
                       fill=rgba(PAL["wood_mid"]))
        draw.rectangle([12, base_y - 16, 16, base_y],
                       fill=rgba(PAL["wood_dark"]))
        # 棚顶（条纹）
        roof_top = (size // 2, base_y - 38)
        draw.polygon([(8, base_y - 16), roof_top, (size - 8, base_y - 16)],
                     fill=rgba((220, 80, 60)))
        # 条纹
        for i in range(5):
            sx = 10 + i * (size - 20) // 5
            draw.line([(sx, base_y - 16), (size // 2 + (i - 2) * 4, base_y - 32)],
                      fill=rgba((240, 240, 240)), width=1)
        # 货物（水果筐）
        for i in range(3):
            fx = 18 + i * 20
            fy = base_y - 8
            draw.ellipse([fx - 4, fy - 2, fx + 4, fy + 4],
                         fill=rgba(PAL["wood_dark"]))
            # 水果
            for _ in range(3):
                px = fx + random.randint(-3, 3)
                py = fy - 1 + random.randint(-2, 0)
                pc = random.choice([(200, 80, 50), (240, 180, 60), (180, 140, 80)])
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=rgba(pc))

    elif variant == "shed":
        # 小棚：单斜顶
        base_y = size - 6
        draw.rectangle([10, base_y - 20, size - 10, base_y],
                       fill=rgba(PAL["wood_dark"]))
        draw.polygon([(6, base_y - 20), (size - 6, base_y - 28),
                      (size - 6, base_y - 20)],
                     fill=rgba(PAL["wood_mid"]))
        draw.rectangle([size // 2 - 4, base_y - 14, size // 2 + 4, base_y - 2],
                       fill=rgba(PAL["wood_darkest"]))

    img = apply_texture(img, noise_scale=0.04)
    return img


def gen_overlay_layer(variant="occlusion", w=3024, h=1792):
    """生成全图叠加层（透明）。"""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if variant == "occlusion":
        # 遮挡层：树冠和屋檐（alpha）
        # 几个大椭圆形遮挡
        for _ in range(40):
            ox = random.randint(0, w)
            oy = random.randint(0, h)
            o_r = random.randint(80, 200)
            shade = random.uniform(0.15, 0.35)
            c = (int(40 * shade), int(60 * shade), int(35 * shade), random.randint(120, 200))
            draw.ellipse([ox - o_r, oy - o_r, ox + o_r, oy + o_r], fill=c)

    elif variant == "foreground":
        # 前景层：草叶和花朵点缀
        for _ in range(600):
            fx = random.randint(0, w)
            fy = random.randint(0, h)
            fc = random.choice([PAL["grass_light"], PAL["grass_mid"],
                                (220, 180, 100, 160), (200, 100, 140, 160)])
            draw.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=rgba(fc, 160))

    elif variant == "lighting":
        # 光照层：暖色光晕
        # 中央广场
        for cx, cy, r, alpha in [
            (1512, 896, 400, 80),
            (800, 500, 250, 100),
            (2200, 700, 300, 70),
            (1200, 1200, 350, 60),
            (500, 300, 200, 90),
        ]:
            for step in range(10, 0, -1):
                rr = r * step / 10
                a = alpha * step / 10
                draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                             fill=rgba((255, 220, 130), int(a)))

    elif variant == "weather":
        # 天气层：雨线
        for _ in range(300):
            rx = random.randint(0, w)
            ry = random.randint(0, h)
            draw.line([(rx, ry), (rx - 1, ry + 6)],
                      fill=rgba(PAL["rain"]), width=1)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    return img


def gen_walkable_data(w=3024, h=1792):
    """生成可走区数据（黑白图：白=可走，黑=障碍）。"""
    img = Image.new("L", (w // 4, h // 4), 255)  # 默认全可走
    draw = ImageDraw.Draw(img)

    # 简化：黑色矩形表示建筑占地（不可走）
    # 主建筑区
    buildings = [
        (180, 200, 320, 320),  # 教会
        (500, 300, 640, 420),  # 广场周围
        (300, 500, 440, 620),  # 房屋
        (800, 400, 920, 500),  # 房屋
        (600, 700, 740, 820),  # 房屋
        (1000, 200, 1140, 320),  # 房屋
        (200, 800, 340, 920),  # 房屋
        (1000, 900, 1140, 1020),  # 房屋
        (1200, 500, 1340, 620),  # 房屋
        (1500, 200, 1640, 320),  # 房屋
    ]
    for x1, y1, x2, y2 in buildings:
        draw.rectangle([x1 // 4, y1 // 4, x2 // 4, y2 // 4], fill=0)

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = img.resize((w, h), Image.NEAREST)
    return img


def gen_collision_data(w=3024, h=1792):
    """生成碰撞数据（黑白图：黑=碰撞，白=通行）。"""
    # 与 walkable 类似，但更严格
    img = Image.new("L", (w // 4, h // 4), 255)
    draw = ImageDraw.Draw(img)

    buildings = [
        (180, 200, 320, 320),
        (500, 300, 640, 420),
        (300, 500, 440, 620),
        (800, 400, 920, 500),
        (600, 700, 740, 820),
        (1000, 200, 1140, 320),
        (200, 800, 340, 920),
        (1000, 900, 1140, 1020),
        (1200, 500, 1340, 620),
        (1500, 200, 1640, 320),
    ]
    for x1, y1, x2, y2 in buildings:
        # 碰撞稍微大一些
        draw.rectangle([x1 // 4 - 2, y1 // 4 - 2, x2 // 4 + 2, y2 // 4 + 2], fill=0)

    # 水域（河）
    draw.rectangle([0, h // 8, w // 4, h // 8 + 30], fill=0)

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = img.resize((w, h), Image.NEAREST)
    return img


def main():
    print(f"=== UW Tile/Prop Atlas Generator ===")
    print(f"Output: {OUTPUT_DIR}")
    print()

    version = "v006"

    # === 1. Terrain tile atlas (4x4 grid) ===
    print("Generating terrain tile atlas...")
    terrain_grid = Image.new("RGBA", (4 * TILE_SIZE, 4 * TILE_SIZE), (0, 0, 0, 0))
    terrain_variants = [
        ("grass", "main_grass"),
        ("grass", "light_grass"),
        ("grass", "dark_grass"),
        ("dirt", "main_dirt"),
        ("dirt", "packed_dirt"),
        ("dirt", "wet_dirt"),
        ("stone", "smooth_stone"),
        ("stone", "rough_stone"),
        ("stone", "cobble"),
        ("grass", "edge_to_dirt"),
        ("dirt", "edge_to_grass"),
        ("grass", "riverbank"),
        ("dirt", "mud"),
        ("stone", "stepping_stone"),
        ("grass", "shadow_grass"),
        ("dirt", "shadow_dirt"),
    ]
    for idx, (variant, _) in enumerate(terrain_variants):
        row = idx // 4
        col = idx % 4
        tile = gen_terrain_tile(variant, seed=idx + 100)
        terrain_grid.paste(tile, (col * TILE_SIZE, row * TILE_SIZE))
    terrain_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_terrain_tile_atlas_{version}.png")
    terrain_grid.save(terrain_path, "PNG")
    print(f"  Saved: {os.path.basename(terrain_path)} ({os.path.getsize(terrain_path)} bytes)")

    # === 2. Water tile atlas (2x4 grid) ===
    print("Generating water tile atlas...")
    water_grid = Image.new("RGBA", (4 * TILE_SIZE, 2 * TILE_SIZE), (0, 0, 0, 0))
    water_variants = [
        ("river", "shallow"),
        ("river", "flow"),
        ("river", "calm"),
        ("river", "edge_to_grass"),
        ("deep", "deep_water"),
        ("deep", "deep_edge"),
        ("river", "wet_edge"),
        ("river", "foam"),
    ]
    for idx, (variant, _) in enumerate(water_variants):
        row = idx // 4
        col = idx % 4
        tile = gen_water_tile(variant, seed=idx + 200)
        water_grid.paste(tile, (col * TILE_SIZE, row * TILE_SIZE))
    water_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_water_tile_atlas_{version}.png")
    water_grid.save(water_path, "PNG")
    print(f"  Saved: {os.path.basename(water_path)} ({os.path.getsize(water_path)} bytes)")

    # === 3. Road tile atlas (2x4 grid) ===
    print("Generating road tile atlas...")
    road_grid = Image.new("RGBA", (4 * TILE_SIZE, 2 * TILE_SIZE), (0, 0, 0, 0))
    road_variants = [
        ("cobble", "main"),
        ("cobble", "center"),
        ("cobble", "edge"),
        ("cobble", "cross"),
        ("dirt", "main"),
        ("dirt", "worn"),
        ("dirt", "edge"),
        ("dirt", "junction"),
    ]
    for idx, (variant, _) in enumerate(road_variants):
        row = idx // 4
        col = idx % 4
        tile = gen_road_tile(variant, seed=idx + 300)
        road_grid.paste(tile, (col * TILE_SIZE, row * TILE_SIZE))
    road_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_road_tile_atlas_{version}.png")
    road_grid.save(road_path, "PNG")
    print(f"  Saved: {os.path.basename(road_path)} ({os.path.getsize(road_path)} bytes)")

    # === 4. Vegetation props atlas (4x4, 56x56 each) ===
    print("Generating vegetation props atlas...")
    veg_size = 56
    veg_grid = Image.new("RGBA", (4 * veg_size, 4 * veg_size), (0, 0, 0, 0))
    veg_variants = [
        ("tree", "tree_oak"),
        ("tree", "tree_birch"),
        ("tree", "tree_pine"),
        ("tree", "tree_young"),
        ("bush", "bush_round"),
        ("bush", "bush_long"),
        ("grass_patch", "grass_tall"),
        ("grass_patch", "grass_short"),
        ("flower", "flower_yellow"),
        ("flower", "flower_pink"),
        ("flower", "flower_white"),
        ("flower", "flower_mix"),
        ("grass_patch", "grass_wheat"),
        ("bush", "bush_berry"),
        ("grass_patch", "grass_wet"),
        ("grass_patch", "grass_dry"),
    ]
    for idx, (variant, _) in enumerate(veg_variants):
        row = idx // 4
        col = idx % 4
        prop = gen_vegetation_prop(variant, seed=idx + 400)
        veg_grid.paste(prop, (col * veg_size, row * veg_size))
    veg_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_vegetation_props_atlas_{version}.png")
    veg_grid.save(veg_path, "PNG")
    print(f"  Saved: {os.path.basename(veg_path)} ({os.path.getsize(veg_path)} bytes)")

    # === 5. Buildings props atlas (3x3, varying sizes, normalized to 112x112) ===
    print("Generating buildings props atlas...")
    bld_size = 112
    bld_grid = Image.new("RGBA", (3 * bld_size, 3 * bld_size), (0, 0, 0, 0))
    bld_variants = [
        ("house_small", "house_a"),
        ("house_small", "house_b"),
        ("house_large", "house_c"),
        ("church", "church_main"),
        ("market", "market_stall"),
        ("well", "well"),
        ("shed", "shed"),
        ("house_small", "house_cottage"),
        ("shed", "wood_pile"),
    ]
    for idx, (variant, _) in enumerate(bld_variants):
        row = idx // 3
        col = idx % 3
        prop = gen_building_prop(variant, seed=idx + 500)
        # 居中放置
        px = (bld_size - prop.width) // 2 + col * bld_size
        py = (bld_size - prop.height) + row * bld_size  # 底部对齐
        bld_grid.paste(prop, (px, py), prop)
    bld_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_buildings_props_atlas_{version}.png")
    bld_grid.save(bld_path, "PNG")
    print(f"  Saved: {os.path.basename(bld_path)} ({os.path.getsize(bld_path)} bytes)")

    # === 6. Overlay layers ===
    W, H = 3024, 1792
    print("Generating overlay layers (3024x1792)...")
    for variant in ["occlusion", "foreground", "lighting", "weather"]:
        overlay = gen_overlay_layer(variant, W, H)
        overlay_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_{variant}_layer_{version}.png")
        overlay.save(overlay_path, "PNG")
        print(f"  Saved: {os.path.basename(overlay_path)} ({os.path.getsize(overlay_path)} bytes)")

    # === 7. Collision & walkable ===
    print("Generating collision/walkable data...")
    collision = gen_collision_data(W, H)
    collision_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_collision_{version}.png")
    collision.save(collision_path, "PNG")
    print(f"  Saved: {os.path.basename(collision_path)} ({os.path.getsize(collision_path)} bytes)")

    walkable = gen_walkable_data(W, H)
    walkable_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_walkable_{version}.png")
    walkable.save(walkable_path, "PNG")
    print(f"  Saved: {os.path.basename(walkable_path)} ({os.path.getsize(walkable_path)} bytes)")

    # === 8. tiles.json (metadata) ===
    print("Generating tiles metadata JSON...")
    tiles_meta = {
        "schema_version": version,
        "request_id": "VIS-MAP-001",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "tile_size_px": TILE_SIZE,
        "grid": {"cols": 108, "rows": 64},
        "runtime_size": [W, H],
        "atlases": {
            "terrain": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_terrain_tile_atlas_{version}.png",
                "grid": [4, 4],
                "tile_count": 16,
                "tile_size_px": TILE_SIZE,
                "tile_ids": [v[1] for v in terrain_variants],
            },
            "water": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_water_tile_atlas_{version}.png",
                "grid": [4, 2],
                "tile_count": 8,
                "tile_size_px": TILE_SIZE,
                "tile_ids": [v[1] for v in water_variants],
            },
            "roads": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_road_tile_atlas_{version}.png",
                "grid": [4, 2],
                "tile_count": 8,
                "tile_size_px": TILE_SIZE,
                "tile_ids": [v[1] for v in road_variants],
            },
            "vegetation": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_vegetation_props_atlas_{version}.png",
                "grid": [4, 4],
                "tile_count": 16,
                "prop_size_px": 56,
                "prop_ids": [v[1] for v in veg_variants],
            },
            "buildings": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_buildings_props_atlas_{version}.png",
                "grid": [3, 3],
                "tile_count": 9,
                "prop_size_px": 112,
                "prop_ids": [v[1] for v in bld_variants],
            },
        },
        "overlay_layers": {
            "occlusion": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_occlusion_layer_{version}.png",
                "alpha": True,
                "blend": "normal",
            },
            "foreground": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_foreground_layer_{version}.png",
                "alpha": True,
                "blend": "normal",
            },
            "lighting": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_lighting_layer_{version}.png",
                "alpha": True,
                "blend": "screen",
            },
            "weather": {
                "source": f"materials/inbox/visual/world/VIS-MAP-001_weather_layer_{version}.png",
                "alpha": True,
                "blend": "normal",
            },
        },
        "data": {
            "collision": f"materials/inbox/visual/world/VIS-MAP-001_collision_{version}.png",
            "walkable": f"materials/inbox/visual/world/VIS-MAP-001_walkable_{version}.png",
        },
        "license": "owned",
        "source_url": "none; original project-owned procedural painterly tile generation",
        "rights_statement": "Original generated tile material. Does not copy existing game tile art.",
        "format": "RGBA8888 PNG; tile atlases use transparent background except terrain/roads where opacity is full",
    }

    tiles_json_path = os.path.join(OUTPUT_DIR, f"VIS-MAP-001_tiles_{version}.json")
    with open(tiles_json_path, "w", encoding="utf-8") as f:
        json.dump(tiles_meta, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {os.path.basename(tiles_json_path)} ({os.path.getsize(tiles_json_path)} bytes)")

    print()
    print("=== Tile/prop atlas generation complete ===")


if __name__ == "__main__":
    main()