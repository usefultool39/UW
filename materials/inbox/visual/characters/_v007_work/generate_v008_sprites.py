#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UW《边境回声》v008 Sprite 生成器
- 提升版：用圆润有机剪影替换矩形躯干
- 4 帧行走相位、4 帧 idle 呼吸、4 帧 interact 动作
- 真实身体比例（儿童，约3.5头高），非 chibi
- 64x96 RGBA, bottom-center foot anchor
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os
import json
import hashlib
from datetime import datetime

# === 角色设计参数 ===
CHARACTERS = {
    "kirito": {
        "name": "kirito",
        "palette": {
            "hair": (28, 28, 42),
            "hair_light": (50, 52, 72),
            "hair_dark": (18, 18, 30),
            "skin": (232, 200, 168),
            "skin_shade": (210, 178, 148),
            "skin_dark": (175, 145, 115),
            "eye_white": (248, 242, 232),
            "eye_dark": (32, 48, 75),
            "coat": (38, 44, 62),
            "coat_light": (58, 66, 88),
            "coat_dark": (26, 30, 46),
            "accent": (78, 175, 180),
            "accent_light": (130, 215, 220),
            "trousers": (32, 36, 50),
            "trousers_light": (48, 54, 72),
            "boots": (32, 24, 18),
            "boots_light": (50, 40, 30),
            "tool_book": (110, 90, 65),
            "tool_page": (220, 210, 180),
            "tool_pen": (90, 95, 105),
        },
        "hair_style": "medium_messy",
        "build": "slim",
        "equipment": "notebook",
    },
    "alice": {
        "name": "alice",
        "palette": {
            "hair": (215, 170, 85),
            "hair_light": (240, 205, 135),
            "hair_dark": (180, 135, 55),
            "skin": (245, 215, 185),
            "skin_shade": (225, 192, 162),
            "skin_dark": (190, 155, 125),
            "eye_white": (250, 245, 235),
            "eye_dark": (140, 95, 45),
            "coat": (238, 222, 195),
            "coat_light": (250, 240, 220),
            "coat_dark": (200, 180, 150),
            "vest": (168, 138, 100),
            "vest_light": (195, 168, 130),
            "accent": (91, 158, 170),
            "accent_light": (140, 200, 210),
            "trousers": (175, 150, 115),
            "trousers_light": (200, 178, 142),
            "boots": (85, 65, 45),
            "boots_light": (115, 92, 70),
            "tool_page": (225, 220, 200),
            "tool_mark": (91, 158, 170),
        },
        "hair_style": "tied_back",
        "build": "balanced",
        "equipment": "record_page",
    },
    "eugeo": {
        "name": "eugeo",
        "palette": {
            "hair": (160, 180, 200),
            "hair_light": (195, 215, 230),
            "hair_dark": (120, 140, 165),
            "skin": (230, 200, 170),
            "skin_shade": (208, 178, 148),
            "skin_dark": (175, 145, 115),
            "eye_white": (245, 240, 232),
            "eye_dark": (85, 115, 150),
            "coat": (115, 145, 178),
            "coat_light": (145, 178, 210),
            "coat_dark": (80, 108, 140),
            "vest": (155, 135, 100),
            "vest_light": (185, 165, 130),
            "accent": (90, 130, 165),
            "accent_light": (130, 170, 200),
            "trousers": (145, 118, 88),
            "trousers_light": (175, 148, 115),
            "boots": (70, 55, 38),
            "boots_light": (95, 78, 58),
            "tool_wood": (95, 80, 60),
            "tool_wood_light": (130, 112, 85),
        },
        "hair_style": "neat_short",
        "build": "sturdy",
        "equipment": "labor_tool",
    },
}

CELL_W = 64
CELL_H = 96
SHEET_COLS = 12
SHEET_ROWS = 4
SHEET_W = CELL_W * SHEET_COLS  # 768
SHEET_H = CELL_H * SHEET_ROWS  # 384

# 关键锚点
HEAD_CX = CELL_W // 2  # 32
HEAD_CY = 20           # 头部中心
NECK_Y = 32            # 颈部
SHOULDER_Y = 34        # 肩部
HIP_Y = 52             # 髋部（腰带）
KNEE_Y = 72            # 膝盖
FOOT_Y = CELL_H - 2    # 脚底锚点
FOOT_CX = CELL_W // 2  # 脚底 X


def rgba(c, a=255):
    if len(c) == 3:
        return (c[0], c[1], c[2], a)
    return c


def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def draw_ellipse_aa(draw, bbox, fill, outline=None, width=0):
    draw.ellipse(bbox, fill=fill, outline=outline, width=width)


def draw_polygon_aa(draw, points, fill, outline=None):
    draw.polygon(points, fill=fill, outline=outline)


def smooth_path(points, tension=0.3):
    """生成平滑路径点。"""
    if len(points) < 3:
        return points
    result = []
    for i in range(-1, len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        p2 = points[(i + 2) % len(points)]
        for t in [j / 6 for j in range(7)]:
            t2 = t * t
            t3 = t2 * t
            x = (2 * t3 - 3 * t2 + 1) * p1[0] + (-2 * t3 + 3 * t2) * p2[0] + \
                (t3 - 2 * t2 + t) * tension * (p2[0] - p0[0]) + \
                (t3 - t2) * tension * (p2[0] - p1[0])
            y = (2 * t3 - 3 * t2 + 1) * p1[1] + (-2 * t3 + 3 * t2) * p2[1] + \
                (t3 - 2 * t2 + t) * tension * (p2[1] - p0[1]) + \
                (t3 - t2) * tension * (p2[1] - p1[1])
            if i == -1 and t == 0:
                continue
            result.append((x, y))
    return result


def draw_rounded_rect(draw, bbox, fill, radius=3):
    """圆角矩形。"""
    x1, y1, x2, y2 = bbox
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    draw.rounded_rectangle(bbox, radius=r, fill=fill)


def draw_torso(draw, cx, top_y, bot_y, direction, p, char_name, anim="idle", frame=0):
    """绘制躯干（圆形剪影，非矩形）。"""
    w_top = 10  # 肩宽
    w_bot = 12  # 腰宽

    # walk 摆动
    if anim == "walk":
        bob = int(1.0 * math.sin(frame * math.pi / 1.5))
        lean = int(1.2 * math.sin(frame * math.pi / 1.5))
    elif anim == "interact":
        bob = 0
        lean = int(0.5 * math.cos(frame * math.pi / 1.5))
    else:
        bob = int(1.2 * math.sin(frame * math.pi / 2))
        lean = 0

    if char_name == "kirito":
        coat = p["coat"]
        coat_light = p["coat_light"]
        coat_dark = p["coat_dark"]
        accent = p["accent"]
    elif char_name == "alice":
        coat = p["coat"]
        coat_light = p["coat_light"]
        coat_dark = p["coat_dark"]
        accent = p["accent"]
    else:
        coat = p["coat"]
        coat_light = p["coat_light"]
        coat_dark = p["coat_dark"]
        accent = p["accent"]

    top_y_adj = top_y + bob + lean
    bot_y_adj = bot_y + bob

    if direction == "down":
        # 正面：圆润肩→腰曲线
        # 外轮廓（从左肩到右肩，经过腰部）
        pts = [
            (cx - w_top - 2, top_y_adj),       # 左肩外
            (cx - w_top - 1, top_y_adj + 2),
            (cx - w_bot - 1, bot_y_adj - 2),   # 左腰外
            (cx - w_bot, bot_y_adj),            # 左腰底
            (cx + w_bot, bot_y_adj),
            (cx + w_bot + 1, bot_y_adj - 2),
            (cx + w_top + 1, top_y_adj + 2),
            (cx + w_top + 2, top_y_adj),
        ]
        draw.polygon(pts, fill=rgba(coat))
        # 亮面（左侧受光）
        light_pts = [
            (cx - w_top - 2, top_y_adj),
            (cx - w_top + 1, top_y_adj + 2),
            (cx - w_bot + 2, bot_y_adj - 2),
            (cx - w_bot + 1, bot_y_adj),
            (cx - w_top + 1, top_y_adj + 4),
            (cx - w_top + 1, top_y_adj + 6),
            (cx - w_top + 2, top_y_adj + 8),
            (cx - w_bot + 4, bot_y_adj - 2),
        ]
        # 简化亮面
        draw.polygon([
            (cx - w_top, top_y_adj + 2),
            (cx - w_top + 3, top_y_adj + 4),
            (cx - w_bot + 3, bot_y_adj - 1),
            (cx - w_bot + 1, bot_y_adj),
            (cx - w_top, bot_y_adj - 2),
        ], fill=rgba(coat_light))
        # 暗面（右侧阴影）
        draw.polygon([
            (cx + w_top - 2, top_y_adj + 3),
            (cx + w_top, top_y_adj + 2),
            (cx + w_bot, bot_y_adj),
            (cx + w_bot - 2, bot_y_adj - 1),
        ], fill=rgba(coat_dark))
        # 识别色装饰线（中央）
        draw.line([(cx, top_y_adj + 4), (cx, top_y_adj + 12)],
                  fill=rgba(accent), width=1)
        if char_name == "alice":
            # 护肩披肩
            draw.polygon([
                (cx - w_top - 4, top_y_adj - 1),
                (cx - w_top + 1, top_y_adj - 1),
                (cx - w_top - 1, top_y_adj + 5),
                (cx - w_top - 3, top_y_adj + 4),
            ], fill=rgba(p["vest"]))
            draw.polygon([
                (cx + w_top - 1, top_y_adj - 1),
                (cx + w_top + 4, top_y_adj - 1),
                (cx + w_top + 3, top_y_adj + 4),
                (cx + w_top + 1, top_y_adj + 5),
            ], fill=rgba(p["vest_light"]))
        if char_name == "eugeo":
            # 背心
            draw.polygon([
                (cx - w_top + 2, top_y_adj),
                (cx + w_top - 2, top_y_adj),
                (cx + w_top - 3, bot_y_adj - 2),
                (cx - w_top + 3, bot_y_adj - 2),
            ], fill=rgba(p["vest"], 200))

    elif direction == "up":
        # 背面：圆润背剪影
        pts = [
            (cx - w_top - 2, top_y_adj),
            (cx - w_top - 1, top_y_adj + 2),
            (cx - w_bot - 1, bot_y_adj - 2),
            (cx - w_bot, bot_y_adj),
            (cx + w_bot, bot_y_adj),
            (cx + w_bot + 1, bot_y_adj - 2),
            (cx + w_top + 1, top_y_adj + 2),
            (cx + w_top + 2, top_y_adj),
        ]
        draw.polygon(pts, fill=rgba(coat))
        # 背部折线
        draw.line([(cx, top_y_adj + 3), (cx, bot_y_adj - 2)],
                  fill=rgba(coat_light), width=1)
        # 后发下端
        draw.line([(cx - w_top + 1, top_y_adj + 1),
                   (cx + w_top - 1, top_y_adj + 1)],
                  fill=rgba(coat_dark), width=1)

    elif direction == "left":
        # 左侧面：身体左侧轮廓
        pts = [
            (cx - w_top, top_y_adj),
            (cx - w_top - 1, top_y_adj + 2),
            (cx - w_bot - 1, bot_y_adj - 2),
            (cx - w_bot, bot_y_adj),
            (cx + w_bot - 2, bot_y_adj),
            (cx + w_top - 2, top_y_adj + 2),
            (cx + w_top, top_y_adj),
        ]
        draw.polygon(pts, fill=rgba(coat))
        # 胸前亮面
        draw.polygon([
            (cx + w_top - 3, top_y_adj + 2),
            (cx + w_top - 1, top_y_adj + 2),
            (cx + w_bot - 2, bot_y_adj),
            (cx + w_bot - 4, bot_y_adj),
        ], fill=rgba(coat_light))
        # 识别色装饰（侧面可见）
        if char_name == "alice":
            draw_ellipse_aa(draw, [cx + w_top - 6, top_y_adj + 3,
                                   cx + w_top - 4, top_y_adj + 5],
                           rgba(p["vest"]))

    elif direction == "right":
        # 右侧面（与 left 镜像）
        pts = [
            (cx + w_top, top_y_adj),
            (cx + w_top + 1, top_y_adj + 2),
            (cx + w_bot + 1, bot_y_adj - 2),
            (cx + w_bot, bot_y_adj),
            (cx - w_bot + 2, bot_y_adj),
            (cx - w_top + 2, top_y_adj + 2),
            (cx - w_top, top_y_adj),
        ]
        draw.polygon(pts, fill=rgba(coat))
        draw.polygon([
            (cx - w_top + 3, top_y_adj + 2),
            (cx - w_top + 1, top_y_adj + 2),
            (cx - w_bot + 2, bot_y_adj),
            (cx - w_bot + 4, bot_y_adj),
        ], fill=rgba(coat_light))
        if char_name == "alice":
            draw_ellipse_aa(draw, [cx - w_top + 4, top_y_adj + 3,
                                   cx - w_top + 6, top_y_adj + 5],
                           rgba(p["vest"]))


def draw_head(draw, cx, cy, direction, p, hair_style, anim="idle", frame=0):
    """绘制头部。"""
    head_w = 11
    head_h = 12

    # walk 摆动
    if anim == "walk":
        bob = int(1.2 * math.sin(frame * math.pi / 1.5))
    elif anim == "interact":
        bob = int(1.0 * math.cos(frame * math.pi / 1.5))
    else:
        bob = int(1.0 * math.sin(frame * math.pi / 2))

    cy_adj = cy + bob

    if direction == "down":
        # === 正面 ===
        # 头发后层（大椭圆）
        draw_ellipse_aa(draw, [cx - head_w - 2, cy_adj - head_h - 1,
                               cx + head_w + 2, cy_adj + head_h - 3],
                       rgba(p["hair"]))
        # 脸椭圆
        draw_ellipse_aa(draw, [cx - head_w, cy_adj - head_h + 3,
                               cx + head_w, cy_adj + head_h - 2],
                       rgba(p["skin"]))
        # 下巴阴影
        draw_ellipse_aa(draw, [cx - head_w + 2, cy_adj + head_h - 5,
                               cx + head_w - 2, cy_adj + head_h - 1],
                       rgba(p["skin_shade"]))
        # 刘海（覆盖额头）
        if hair_style == "medium_messy":
            # 不规则刘海
            draw_ellipse_aa(draw, [cx - head_w - 1, cy_adj - head_h + 1,
                                   cx + head_w + 1, cy_adj - head_h + 4],
                           rgba(p["hair"]))
            # 几缕发丝
            for i, dx in enumerate([-5, -2, 1, 4]):
                draw.line([(cx + dx, cy_adj - head_h + 1),
                           (cx + dx - 1, cy_adj - head_h + 5)],
                          fill=rgba(p["hair_dark"]), width=1)
        elif hair_style == "tied_back":
            # 爱丽丝：头发向后绑，前面露出额头和脸
            # 头顶头发
            draw_ellipse_aa(draw, [cx - head_w - 1, cy_adj - head_h - 1,
                                   cx + head_w + 1, cy_adj - head_h + 1],
                           rgba(p["hair"]))
            # 发带（青蓝色，横在头顶）
            draw.rectangle([cx - head_w - 1, cy_adj - head_h + 2,
                            cx + head_w + 1, cy_adj - head_h + 4],
                           fill=rgba(p["accent"]))
            draw.rectangle([cx - head_w - 1, cy_adj - head_h + 2,
                            cx + head_w + 1, cy_adj - head_h + 3],
                           fill=rgba(p["accent_light"]))
        else:  # neat_short
            # 尤吉欧：整齐短发，刘海齐整
            draw_ellipse_aa(draw, [cx - head_w - 1, cy_adj - head_h + 1,
                                   cx + head_w + 1, cy_adj - head_h + 4],
                           rgba(p["hair"]))
            draw_ellipse_aa(draw, [cx - head_w, cy_adj - head_h + 2,
                                   cx + head_w, cy_adj - head_h + 5],
                           rgba(p["hair_light"]))

        # 眼睛
        eye_y = cy_adj
        if anim == "interact" and frame == 1:
            # 检查时眼睛下移看下方物体
            eye_y = cy_adj + 2
        # 左眼
        draw_ellipse_aa(draw, [cx - 5, eye_y - 1, cx - 2, eye_y + 2],
                       rgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx - 4, eye_y, cx - 3, eye_y + 1],
                       rgba(p["eye_dark"]))
        # 右眼
        draw_ellipse_aa(draw, [cx + 2, eye_y - 1, cx + 5, eye_y + 2],
                       rgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx + 3, eye_y, cx + 4, eye_y + 1],
                       rgba(p["eye_dark"]))
        # 鼻（小点）
        draw_ellipse_aa(draw, [cx - 1, cy_adj + 3, cx + 1, cy_adj + 5],
                       rgba(p["skin_dark"]))
        # 嘴
        if anim == "interact" and frame == 1:
            # 检查时微张嘴
            draw_ellipse_aa(draw, [cx - 2, cy_adj + 6, cx + 2, cy_adj + 7],
                           rgba(p["skin_dark"]))
        else:
            draw.line([(cx - 2, cy_adj + 6), (cx + 2, cy_adj + 6)],
                      fill=rgba(p["skin_dark"]), width=1)

        # 耳朵
        draw_ellipse_aa(draw, [cx - head_w - 2, cy_adj + 2, cx - head_w, cy_adj + 6],
                       rgba(p["skin_shade"]))
        draw_ellipse_aa(draw, [cx + head_w, cy_adj + 2, cx + head_w + 2, cy_adj + 6],
                       rgba(p["skin_shade"]))

    elif direction == "up":
        # === 背面 ===
        # 整个头部被头发覆盖
        draw_ellipse_aa(draw, [cx - head_w - 2, cy_adj - head_h - 1,
                               cx + head_w + 2, cy_adj + head_h],
                       rgba(p["hair"]))
        # 头发纹理
        for i in range(-3, 4):
            dx = i * 2
            shade = p["hair_light"] if i % 2 == 0 else p["hair_dark"]
            draw.line([(cx + dx, cy_adj - head_h + 1),
                       (cx + dx, cy_adj + head_h - 3)],
                      fill=rgba(shade), width=1)
        # 后颈
        draw_ellipse_aa(draw, [cx - 4, cy_adj + head_h - 3, cx + 4, cy_adj + head_h + 2],
                       rgba(p["skin_shade"]))
        # 爱丽丝发带背面
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w, cy_adj - head_h + 1,
                                   cx + head_w, cy_adj - head_h + 4],
                           rgba(p["accent"]))

    elif direction == "left":
        # === 左侧面 ===
        # 头顶头发
        draw_ellipse_aa(draw, [cx - head_w, cy_adj - head_h - 1,
                               cx + head_w, cy_adj + 1],
                       rgba(p["hair"]))
        # 后发
        draw_ellipse_aa(draw, [cx + head_w - 3, cy_adj - head_h + 3,
                               cx + head_w + 2, cy_adj + head_h - 1],
                       rgba(p["hair_light"]))
        # 脸（侧面）
        draw_ellipse_aa(draw, [cx - head_w + 1, cy_adj - head_h + 4,
                               cx + head_w - 1, cy_adj + head_h - 2],
                       rgba(p["skin"]))
        # 下巴阴影
        draw_ellipse_aa(draw, [cx - head_w + 2, cy_adj + head_h - 5,
                               cx + head_w - 2, cy_adj + head_h - 1],
                       rgba(p["skin_shade"]))
        # 鼻尖（侧面凸出）
        draw_ellipse_aa(draw, [cx - head_w - 1, cy_adj + 2,
                               cx - head_w + 2, cy_adj + 5],
                       rgba(p["skin_shade"]))
        # 嘴（侧面小条）
        draw.line([(cx - head_w + 1, cy_adj + 6), (cx - head_w + 4, cy_adj + 6)],
                  fill=rgba(p["skin_dark"]), width=1)
        # 眼睛（侧面，只一只可见）
        eye_y = cy_adj
        draw_ellipse_aa(draw, [cx - 4, eye_y - 1, cx - 1, eye_y + 2],
                       rgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx - 3, eye_y, cx - 2, eye_y + 1],
                       rgba(p["eye_dark"]))
        # 爱丽丝发带（侧）
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w, cy_adj - head_h + 2,
                                   cx + head_w - 2, cy_adj - head_h + 4],
                           rgba(p["accent"]))

    elif direction == "right":
        # === 右侧面（与 left 镜像）===
        draw_ellipse_aa(draw, [cx - head_w, cy_adj - head_h - 1,
                               cx + head_w, cy_adj + 1],
                       rgba(p["hair"]))
        draw_ellipse_aa(draw, [cx - head_w - 2, cy_adj - head_h + 3,
                               cx - head_w + 3, cy_adj + head_h - 1],
                       rgba(p["hair_light"]))
        draw_ellipse_aa(draw, [cx - head_w + 1, cy_adj - head_h + 4,
                               cx + head_w - 1, cy_adj + head_h - 2],
                       rgba(p["skin"]))
        draw_ellipse_aa(draw, [cx - head_w + 2, cy_adj + head_h - 5,
                               cx + head_w - 2, cy_adj + head_h - 1],
                       rgba(p["skin_shade"]))
        draw_ellipse_aa(draw, [cx + head_w - 2, cy_adj + 2,
                               cx + head_w + 1, cy_adj + 5],
                       rgba(p["skin_shade"]))
        draw.line([(cx + head_w - 4, cy_adj + 6), (cx + head_w - 1, cy_adj + 6)],
                  fill=rgba(p["skin_dark"]), width=1)
        eye_y = cy_adj
        draw_ellipse_aa(draw, [cx + 1, eye_y - 1, cx + 4, eye_y + 2],
                       rgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx + 2, eye_y, cx + 3, eye_y + 1],
                       rgba(p["eye_dark"]))
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w + 2, cy_adj - head_h + 2,
                                   cx + head_w, cy_adj - head_h + 4],
                           rgba(p["accent"]))


def draw_arms(draw, cx, shoulder_y, hip_y, direction, p, char_name,
              anim="idle", frame=0):
    """绘制手臂。"""
    if char_name == "kirito":
        coat = p["coat"]
        skin = p["skin"]
        skin_shade = p["skin_shade"]
    elif char_name == "alice":
        coat = p["coat"]
        skin = p["skin"]
        skin_shade = p["skin_shade"]
    else:
        coat = p["coat"]
        skin = p["skin"]
        skin_shade = p["skin_shade"]

    # 计算手臂摆动
    if anim == "walk":
        swing = math.sin(frame * math.pi / 1.5)
        l_swing_x = -swing * 4
        r_swing_x = swing * 4
        bob = int(1.0 * math.sin(frame * math.pi / 1.5))
    elif anim == "interact":
        # 4 帧：伸出 → 检查 → 持物 → 放手
        if frame == 0:  # 伸出右手
            l_swing_x = -1
            r_swing_x = -10
        elif frame == 1:  # 检查（手收回胸前看）
            l_swing_x = -3
            r_swing_x = -6
        elif frame == 2:  # 持物（双手胸前合拢）
            l_swing_x = -5
            r_swing_x = -5
        else:  # 放手
            l_swing_x = -2
            r_swing_x = -3
        bob = 0
    else:  # idle
        swing = math.sin(frame * math.pi / 2)
        l_swing_x = int(0.5 * swing)
        r_swing_x = -l_swing_x
        bob = int(1.2 * math.sin(frame * math.pi / 2))

    shoulder_y_adj = shoulder_y + bob

    if direction == "down":
        # === 正面：双臂 ===
        # 左臂
        l_sx = cx - 11
        l_ex = l_sx + l_swing_x
        l_ey = shoulder_y_adj + 14
        draw.line([(l_sx, shoulder_y_adj + 2), (l_ex, l_ey - 2)],
                  fill=rgba(coat), width=3)
        draw_ellipse_aa(draw, [l_ex - 2, l_ey - 3, l_ex + 2, l_ey + 1],
                       rgba(skin))
        # 左手指（简化）
        draw.line([(l_ex - 1, l_ey), (l_ex - 1, l_ey + 1)],
                  fill=rgba(skin_shade), width=1)

        # 右臂
        r_sx = cx + 11
        r_ex = r_sx + r_swing_x
        r_ey = shoulder_y_adj + 14
        draw.line([(r_sx, shoulder_y_adj + 2), (r_ex, r_ey - 2)],
                  fill=rgba(coat), width=3)
        draw_ellipse_aa(draw, [r_ex - 2, r_ey - 3, r_ex + 2, r_ey + 1],
                       rgba(skin))
        draw.line([(r_ex + 1, r_ey), (r_ex + 1, r_ey + 1)],
                  fill=rgba(skin_shade), width=1)

        # 交互时持物
        if anim == "interact" and frame == 2:
            tool_x = cx - 4
            tool_y = shoulder_y_adj + 10
            if char_name == "kirito":
                # 记录册
                draw_rounded_rect(draw, [tool_x, tool_y, tool_x + 8, tool_y + 5],
                                  fill=rgba(p["tool_book"]), radius=1)
                draw_rounded_rect(draw, [tool_x + 1, tool_y + 1, tool_x + 7, tool_y + 4],
                                  fill=rgba(p["tool_page"]), radius=1)
                draw.line([(tool_x + 2, tool_y + 2), (tool_x + 6, tool_y + 2)],
                          fill=rgba(p["tool_pen"]), width=1)
            elif char_name == "alice":
                # 圈注过的记录页
                draw_rounded_rect(draw, [tool_x, tool_y, tool_x + 8, tool_y + 5],
                                  fill=rgba(p["tool_page"]), radius=1)
                draw.line([(tool_x + 1, tool_y + 1), (tool_x + 7, tool_y + 1)],
                          fill=rgba(p["tool_mark"]), width=1)
                draw_ellipse_aa(draw, [tool_x + 3, tool_y + 2, tool_x + 5, tool_y + 4],
                                rgba(p["tool_mark"]))
            else:
                # 劳动工具（小木棒）
                draw.line([(tool_x, tool_y + 2), (tool_x + 8, tool_y + 4)],
                          fill=rgba(p["tool_wood"]), width=2)
                draw.line([(tool_x + 1, tool_y + 2), (tool_x + 7, tool_y + 4)],
                          fill=rgba(p["tool_wood_light"]), width=1)

    elif direction == "left":
        # === 左侧面：近侧完整，远侧简化 ===
        # 近侧（左手）
        n_sx = cx - 8
        n_ex = n_sx + l_swing_x
        n_ey = shoulder_y_adj + 14
        draw.line([(n_sx, shoulder_y_adj + 2), (n_ex, n_ey - 2)],
                  fill=rgba(coat), width=3)
        draw_ellipse_aa(draw, [n_ex - 2, n_ey - 3, n_ex + 2, n_ey + 1],
                       rgba(skin))

        # 远侧（右手，部分遮挡）
        f_sx = cx + 5
        f_ex = f_sx + r_swing_x
        f_ey = shoulder_y_adj + 14
        draw.line([(f_sx, shoulder_y_adj + 2), (f_ex, f_ey - 2)],
                  fill=rgba(coat, 180), width=2)
        draw_ellipse_aa(draw, [f_ex - 1, f_ey - 2, f_ex + 2, f_ey + 1],
                       rgba(skin, 200))

    elif direction == "right":
        # === 右侧面（与 left 镜像）===
        n_sx = cx + 8
        n_ex = n_sx - l_swing_x  # 镜像反向
        n_ey = shoulder_y_adj + 14
        draw.line([(n_sx, shoulder_y_adj + 2), (n_ex, n_ey - 2)],
                  fill=rgba(coat), width=3)
        draw_ellipse_aa(draw, [n_ex - 2, n_ey - 3, n_ex + 2, n_ey + 1],
                       rgba(skin))

        f_sx = cx - 5
        f_ex = f_sx - r_swing_x
        f_ey = shoulder_y_adj + 14
        draw.line([(f_sx, shoulder_y_adj + 2), (f_ex, f_ey - 2)],
                  fill=rgba(coat, 180), width=2)
        draw_ellipse_aa(draw, [f_ex - 2, f_ey - 2, f_ex + 1, f_ey + 1],
                       rgba(skin, 200))

    elif direction == "up":
        # === 背面：双臂对称 ===
        for sign in [-1, 1]:
            s_x = cx + sign * 11
            e_x = s_x + l_swing_x * sign
            e_y = shoulder_y_adj + 14
            draw.line([(s_x, shoulder_y_adj + 2), (e_x, e_y - 2)],
                      fill=rgba(coat), width=3)
            draw_ellipse_aa(draw, [e_x - 2, e_y - 3, e_x + 2, e_y + 1],
                           rgba(skin))


def draw_legs(draw, cx, hip_y, direction, p, char_name, anim="idle", frame=0):
    """绘制腿部。"""
    if char_name == "kirito":
        trousers = p["trousers"]
        trousers_light = p["trousers_light"]
        boots = p["boots"]
        boots_light = p["boots_light"]
    elif char_name == "alice":
        trousers = p["trousers"]
        trousers_light = p["trousers_light"]
        boots = p["boots"]
        boots_light = p["boots_light"]
    else:
        trousers = p["trousers"]
        trousers_light = p["trousers_light"]
        boots = p["boots"]
        boots_light = p["boots_light"]

    # walk 6 帧行走
    if anim == "walk":
        # 行走循环：左脚相位=frame, 右脚相位=frame+3
        l_phase = frame
        r_phase = (frame + 3) % 6
        l_swing = math.sin(l_phase * math.pi / 1.5) * 3
        r_swing = math.sin(r_phase * math.pi / 1.5) * 3
        # 上下浮动（脚落地时低，抬脚时高）
        bob_l = -abs(math.sin(l_phase * math.pi / 1.5)) * 1.5
        bob_r = -abs(math.sin(r_phase * math.pi / 1.5)) * 1.5
        # 平均身高下移（行走时身高降低）
        hip_drop = int(1.0 * (abs(math.sin(l_phase * math.pi / 1.5)) +
                              abs(math.sin(r_phase * math.pi / 1.5))) / 2)
        hip_y_adj = hip_y + hip_drop
    elif anim == "interact":
        l_swing = 0
        r_swing = 0
        hip_y_adj = hip_y
        bob_l = 0
        bob_r = 0
    else:
        l_swing = int(1.2 * math.sin(frame * math.pi / 2))
        r_swing = -l_swing
        bob_l = 0
        bob_r = 0
        hip_y_adj = hip_y + int(1.2 * math.sin(frame * math.pi / 2))

    if direction == "down":
        # === 正面：双腿 ===
        # 左腿
        l_thigh_x = cx - 3
        l_foot_x = cx - 5 + int(l_swing)
        l_foot_y = FOOT_Y
        # 大腿
        draw.line([(l_thigh_x, hip_y_adj + 1), (l_foot_x + 1, l_foot_y - 6)],
                  fill=rgba(trousers), width=4)
        # 小腿（亮面）
        draw.line([(l_thigh_x - 1, hip_y_adj + 5), (l_foot_x, l_foot_y - 7)],
                  fill=rgba(trousers_light), width=1)
        # 鞋
        draw_ellipse_aa(draw, [l_foot_x - 3, l_foot_y - 3,
                               l_foot_x + 3, l_foot_y + 1],
                       rgba(boots))
        draw_ellipse_aa(draw, [l_foot_x - 3, l_foot_y - 3,
                               l_foot_x + 1, l_foot_y - 1],
                       rgba(boots_light))

        # 右腿
        r_thigh_x = cx + 3
        r_foot_x = cx + 5 + int(r_swing)
        r_foot_y = FOOT_Y
        draw.line([(r_thigh_x, hip_y_adj + 1), (r_foot_x - 1, r_foot_y - 6)],
                  fill=rgba(trousers), width=4)
        draw.line([(r_thigh_x + 1, hip_y_adj + 5), (r_foot_x, r_foot_y - 7)],
                  fill=rgba(trousers_light), width=1)
        draw_ellipse_aa(draw, [r_foot_x - 3, r_foot_y - 3,
                               r_foot_x + 3, r_foot_y + 1],
                       rgba(boots))
        draw_ellipse_aa(draw, [r_foot_x + 1, r_foot_y - 3,
                               r_foot_x + 3, r_foot_y - 1],
                       rgba(boots_light))

    elif direction == "left":
        # === 左侧面：近侧完整，远侧简化 ===
        # 近侧
        n_thigh_x = cx - 1
        n_foot_x = cx - 3 + int(l_swing)
        n_foot_y = FOOT_Y
        draw.line([(n_thigh_x, hip_y_adj + 1), (n_foot_x + 1, n_foot_y - 6)],
                  fill=rgba(trousers), width=4)
        draw_ellipse_aa(draw, [n_foot_x - 3, n_foot_y - 3,
                               n_foot_x + 3, n_foot_y + 1],
                       rgba(boots))
        draw_ellipse_aa(draw, [n_foot_x - 3, n_foot_y - 3,
                               n_foot_x + 1, n_foot_y - 1],
                       rgba(boots_light))
        # 远侧
        f_thigh_x = cx + 3
        f_foot_x = cx + 5 + int(r_swing)
        f_foot_y = FOOT_Y
        draw.line([(f_thigh_x, hip_y_adj + 1), (f_foot_x - 1, f_foot_y - 6)],
                  fill=rgba(trousers, 200), width=3)
        draw_ellipse_aa(draw, [f_foot_x - 2, f_foot_y - 3,
                               f_foot_x + 2, f_foot_y + 1],
                       rgba(boots, 200))

    elif direction == "right":
        # === 右侧面（与 left 镜像）===
        n_thigh_x = cx + 1
        n_foot_x = cx + 3 - int(l_swing)
        n_foot_y = FOOT_Y
        draw.line([(n_thigh_x, hip_y_adj + 1), (n_foot_x - 1, n_foot_y - 6)],
                  fill=rgba(trousers), width=4)
        draw_ellipse_aa(draw, [n_foot_x - 3, n_foot_y - 3,
                               n_foot_x + 3, n_foot_y + 1],
                       rgba(boots))
        draw_ellipse_aa(draw, [n_foot_x + 1, n_foot_y - 3,
                               n_foot_x + 3, n_foot_y - 1],
                       rgba(boots_light))

        f_thigh_x = cx - 3
        f_foot_x = cx - 5 - int(r_swing)
        f_foot_y = FOOT_Y
        draw.line([(f_thigh_x, hip_y_adj + 1), (f_foot_x + 1, f_foot_y - 6)],
                  fill=rgba(trousers, 200), width=3)
        draw_ellipse_aa(draw, [f_foot_x - 2, f_foot_y - 3,
                               f_foot_x + 2, f_foot_y + 1],
                       rgba(boots, 200))

    elif direction == "up":
        # === 背面：双腿对称 ===
        l_thigh_x = cx - 3
        l_foot_x = cx - 5 + int(l_swing)
        l_foot_y = FOOT_Y
        draw.line([(l_thigh_x, hip_y_adj + 1), (l_foot_x + 1, l_foot_y - 6)],
                  fill=rgba(trousers), width=4)
        draw_ellipse_aa(draw, [l_foot_x - 3, l_foot_y - 3,
                               l_foot_x + 3, l_foot_y + 1],
                       rgba(boots))

        r_thigh_x = cx + 3
        r_foot_x = cx + 5 + int(r_swing)
        r_foot_y = FOOT_Y
        draw.line([(r_thigh_x, hip_y_adj + 1), (r_foot_x - 1, r_foot_y - 6)],
                  fill=rgba(trousers), width=4)
        draw_ellipse_aa(draw, [r_foot_x - 3, r_foot_y - 3,
                               r_foot_x + 3, r_foot_y + 1],
                       rgba(boots))


def render_frame(character, direction, anim, frame_index):
    """渲染单帧 64x96 RGBA。"""
    img = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    p = character["palette"]
    char_name = character["name"]
    hair_style = character["hair_style"]

    cx = HEAD_CX

    # 1. 腿（先画，在身体后面）
    draw_legs(draw, cx, HIP_Y, direction, p, char_name,
              anim=anim, frame=frame_index)

    # 2. 身体
    draw_torso(draw, cx, SHOULDER_Y, HIP_Y, direction, p, char_name,
               anim=anim, frame=frame_index)

    # 3. 手臂（在身体之后）
    draw_arms(draw, cx, SHOULDER_Y, HIP_Y, direction, p, char_name,
              anim=anim, frame=frame_index)

    # 4. 头（最后画，最前面）
    draw_head(draw, cx, HEAD_CY, direction, p, hair_style,
              anim=anim, frame=frame_index)

    return img


def compose_sheet(frames_grid):
    """合成 sprite sheet。"""
    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    for row_idx, row in enumerate(frames_grid):
        for col_idx, frame in enumerate(row):
            sheet.paste(frame, (col_idx * CELL_W, row_idx * CELL_H))
    return sheet


def smooth_frame(img, radius=0.4):
    """轻量平滑。"""
    if radius > 0:
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    return img


def generate_character_sprites(char_key, version="v008"):
    """为单个角色生成完整 48 帧 sprite sheet + frames JSON。"""
    character = CHARACTERS[char_key]
    name = character["name"]

    # 动画顺序
    column_order = []
    for i in range(2):
        column_order.append(("idle", i))
    for i in range(6):
        column_order.append(("walk", i))
    for i in range(4):
        column_order.append(("interact", i))

    directions = ["down", "left", "right", "up"]
    frames_grid = []
    frames_meta = []

    for row_idx, direction in enumerate(directions):
        row = []
        for col_idx, (anim, frame_idx) in enumerate(column_order):
            frame_img = render_frame(character, direction, anim, frame_idx)
            frame_img = smooth_frame(frame_img, radius=0.4)
            row.append(frame_img)

            x = col_idx * CELL_W
            y = row_idx * CELL_H
            frames_meta.append({
                "direction": direction,
                "animation": anim,
                "frame_index": frame_idx,
                "rect": [x, y, CELL_W, CELL_H],
            })
        frames_grid.append(row)

    sheet = compose_sheet(frames_grid)

    # 构建动画元数据
    animations_meta = {}
    for direction in directions:
        for anim in ["idle", "walk", "interact"]:
            key = f"{direction}_{anim}"
            anim_frames = []
            for col_idx, (a, fi) in enumerate(column_order):
                if a == anim:
                    row_idx = directions.index(direction)
                    x = col_idx * CELL_W
                    y = row_idx * CELL_H
                    anim_frames.append({
                        "frame_index": fi,
                        "source": f"materials/inbox/visual/characters/VIS-CHR-00{list(CHARACTERS.keys()).index(char_key)+1}_{name}_sprite_sheet_{version}.png",
                        "rect": [x, y, CELL_W, CELL_H],
                        "duration_ms": {"idle": 800, "walk": 140, "interact": 350}[anim],
                    })
            animations_meta[key] = {
                "loop": anim != "interact",
                "frames": anim_frames,
                "anchor": [CELL_W // 2, CELL_H - 2],
                "collision_footprint": [CELL_W // 2 - 6, CELL_H - 8, 12, 6],
            }

    json_data = {
        "schema_version": version,
        "request_id": f"VIS-CHR-00{list(CHARACTERS.keys()).index(char_key)+1}",
        "character": name,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "frame_width": CELL_W,
        "frame_height": CELL_H,
        "frame_cell_px": {"w": CELL_W, "h": CELL_H},
        "sheet_px": {"w": SHEET_W, "h": SHEET_H},
        "directions": directions,
        "column_order": [[a, fi] for a, fi in column_order],
        "anchor": [CELL_W // 2, CELL_H - 2],
        "anchor_convention": "bottom-center, foot-pivot at y=cell_height-2",
        "display_height_px_range": [44, 52],
        "animations": animations_meta,
        "format": "RGBA8888 non-interlaced, transparent background, no checkerboard, no text, no UI, no baked shadow",
        "alpha_check": "both transparent and visible character pixels present",
        "license": "owned",
        "source_url": "none; original project-owned procedural painterly sprite generation",
        "rights_statement": "Original generated sprite material. Does not copy existing animation, character likeness, costume, or third-party samples.",
        "supersedes": "v003 geometric puppets, v006 procedural painterly, v007 first pass; v008 refines silhouettes, walking gait, and interaction gestures with smoother organic shapes",
    }

    return sheet, json_data, frames_meta


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    output_dir = r"C:\Users\liang\Desktop\uw\materials\inbox\visual\characters"
    os.makedirs(output_dir, exist_ok=True)

    version = "v008"

    print(f"=== UW v008 Sprite Generator ===")
    print(f"Output: {output_dir}")
    print(f"Version: {version}")
    print()

    for idx, char_key in enumerate(CHARACTERS.keys(), 1):
        request_id = f"VIS-CHR-{idx:03d}"
        character = CHARACTERS[char_key]
        name = character["name"]

        print(f"Generating {request_id} ({name})...")

        sheet, json_data, frames_meta = generate_character_sprites(char_key, version)

        sheet_filename = f"{request_id}_{name}_sprite_sheet_{version}.png"
        sheet_path = os.path.join(output_dir, sheet_filename)
        sheet.save(sheet_path, "PNG")

        json_filename = f"{request_id}_frames_{version}.json"
        json_path = os.path.join(output_dir, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        sheet_sha = sha256_file(sheet_path)
        json_sha = sha256_file(json_path)

        print(f"  Sheet: {sheet_filename} ({os.path.getsize(sheet_path)} bytes)")
        print(f"  SHA-256: {sheet_sha}")
        print(f"  JSON: {json_filename} ({os.path.getsize(json_path)} bytes)")
        print(f"  SHA-256: {json_sha}")
        print()

    print("=== All characters generated successfully ===")


if __name__ == "__main__":
    main()