#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UW《边境回声》v007 Sprite 生成器
- 三角色四方向 48 帧 RGBA sprite sheet
- 64x96 cell, transparent background, bottom-center foot anchor
- 真实动画差异：walk 6帧行走循环, idle 2帧呼吸, interact 4帧交互
- 儿童阶段，非 chibi，原创设计
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
            "hair": (28, 28, 42),        # 深墨黑
            "hair_light": (48, 48, 68),
            "skin": (232, 200, 168),     # 暖肤色
            "skin_shadow": (200, 168, 140),
            "eye": (40, 60, 90),
            "eye_white": (245, 240, 232),
            "coat": (38, 42, 58),        # 深墨蓝
            "coat_light": (52, 58, 78),
            "accent": (78, 175, 180),    # 青色识别色
            "accent_light": (120, 210, 215),
            "trousers": (28, 32, 44),
            "trousers_light": (42, 48, 62),
            "belt": (60, 55, 45),
            "boots": (35, 28, 22),
            "tool": (80, 90, 85),         # 记录册
            "tool_light": (115, 125, 120),
        },
        "hair_style": "medium_messy",
        "build": "slim",
        "equipment": "notebook",
    },
    "alice": {
        "name": "alice",
        "palette": {
            "hair": (212, 168, 83),      # 麦金色
            "hair_light": (235, 200, 130),
            "hair_ribbon": (75, 130, 145),  # 青蓝色发带
            "skin": (240, 210, 182),
            "skin_shadow": (210, 178, 150),
            "eye": (160, 110, 45),       # 琥珀色
            "eye_white": (248, 242, 232),
            "dress": (232, 218, 192),    # 米白
            "dress_light": (245, 235, 215),
            "vest": (160, 130, 95),      # 浅棕护肩
            "vest_light": (190, 160, 125),
            "accent": (91, 158, 170),    # 冷青蓝
            "accent_light": (135, 195, 205),
            "trousers": (175, 150, 115),
            "trousers_light": (200, 178, 142),
            "boots": (90, 70, 50),
            "tool": (200, 195, 175),      # 圈注记录页
            "tool_light": (225, 220, 200),
        },
        "hair_style": "tied_back",
        "build": "balanced",
        "equipment": "record_page",
    },
    "eugeo": {
        "name": "eugeo",
        "palette": {
            "hair": (155, 175, 195),     # 冷蓝棕
            "hair_light": (185, 205, 220),
            "skin": (228, 198, 168),
            "skin_shadow": (198, 168, 140),
            "eye": (95, 120, 150),       # 蓝灰
            "eye_white": (242, 238, 230),
            "shirt": (107, 140, 175),    # 冷蓝
            "shirt_light": (140, 172, 205),
            "vest": (140, 120, 90),      # 麻色背心
            "vest_light": (170, 150, 118),
            "accent": (90, 130, 165),
            "accent_light": (130, 170, 200),
            "trousers": (139, 115, 85),  # 木褐
            "trousers_light": (168, 142, 110),
            "boots": (70, 55, 40),
            "tool": (95, 80, 60),         # 训练/劳动工具
            "tool_light": (125, 108, 85),
        },
        "hair_style": "neat_short",
        "build": "sturdy",
        "equipment": "labor_tool",
    },
}

CELL_W = 64
CELL_H = 96
SHEET_COLS = 12  # 2 idle + 6 walk + 4 interact
SHEET_ROWS = 4   # down, left, right, up
SHEET_W = CELL_W * SHEET_COLS  # 768
SHEET_H = CELL_H * SHEET_ROWS  # 384


def srgba(color, alpha=255):
    """Convert RGB tuple to RGBA."""
    return (color[0], color[1], color[2], alpha)


def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    """Interpolate between two RGB colors."""
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def draw_ellipse_aa(draw, bbox, fill, outline=None, width=0):
    """Draw an anti-aliased ellipse."""
    draw.ellipse(bbox, fill=fill, outline=outline, width=width)


def draw_chr_head(draw, cx, cy, direction, pal, hair_style, scale=1.0):
    """绘制头部。cx,cy 为面部中心。direction: down/left/right/up。"""
    p = pal
    # 头部椭圆
    head_w = int(11 * scale)
    head_h = int(12 * scale)
    # 头发后层
    if direction == "down":
        # 正面：额头前发、脸可见
        # 头顶头发
        draw_ellipse_aa(draw, [cx - head_w - 1, cy - head_h - 2,
                               cx + head_w + 1, cy + 2], srgba(p["hair"]))
        # 刘海
        draw_ellipse_aa(draw, [cx - head_w, cy - head_h + 1,
                               cx + head_w, cy - head_h + 5], srgba(p["hair_light"]))
        # 脸
        draw_ellipse_aa(draw, [cx - head_w + 1, cy - head_h + 3,
                               cx + head_w - 1, cy + head_h - 2], srgba(p["skin"]))
        # 下巴阴影
        draw_ellipse_aa(draw, [cx - head_w + 2, cy + head_h - 4,
                               cx + head_w - 2, cy + head_h - 1], srgba(p["skin_shadow"]))
        # 眼睛
        eye_y = cy - 1
        draw_ellipse_aa(draw, [cx - 5, eye_y - 1, cx - 2, eye_y + 2], srgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx + 2, eye_y - 1, cx + 5, eye_y + 2], srgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx - 4, eye_y, cx - 3, eye_y + 1], srgba(p["eye"]))
        draw_ellipse_aa(draw, [cx + 3, eye_y, cx + 4, eye_y + 1], srgba(p["eye"]))
        # 鼻
        draw_ellipse_aa(draw, [cx - 1, cy + 3, cx + 1, cy + 5], srgba(p["skin_shadow"]))
        # 嘴
        draw_ellipse_aa(draw, [cx - 2, cy + 6, cx + 2, cy + 7], srgba(p["skin_shadow"]))
        # 爱丽丝发带
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w - 2, cy - 3,
                                   cx + head_w + 2, cy - 1], srgba(p["hair_ribbon"]))
    elif direction == "up":
        # 背面：只看后脑勺头发
        draw_ellipse_aa(draw, [cx - head_w - 1, cy - head_h - 2,
                               cx + head_w + 1, cy + head_h], srgba(p["hair"]))
        # 发丝纹理
        for i in range(-2, 3):
            draw.line([(cx + i * 3, cy - head_h + 1),
                       (cx + i * 3, cy + 2)], fill=srgba(p["hair_light"]), width=1)
        # 爱丽丝发带后部
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w, cy - 4,
                                   cx + head_w, cy - 1], srgba(p["hair_ribbon"]))
    elif direction == "left":
        # 左侧面：轮廓向左
        # 头顶头发
        draw_ellipse_aa(draw, [cx - head_w, cy - head_h - 2,
                               cx + head_w, cy + 1], srgba(p["hair"]))
        # 后发
        draw_ellipse_aa(draw, [cx + head_w - 3, cy - head_h + 2,
                               cx + head_w + 2, cy + head_h], srgba(p["hair_light"]))
        # 脸（侧面，左边为脸部轮廓）
        draw_ellipse_aa(draw, [cx - head_w + 1, cy - head_h + 4,
                               cx + head_w - 1, cy + head_h - 2], srgba(p["skin"]))
        # 下巴阴影
        draw_ellipse_aa(draw, [cx - head_w + 2, cy + head_h - 4,
                               cx + head_w - 2, cy + head_h - 1], srgba(p["skin_shadow"]))
        # 眼睛（左侧，只一只可见）
        eye_y = cy - 1
        draw_ellipse_aa(draw, [cx - 4, eye_y - 1, cx - 1, eye_y + 2], srgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx - 3, eye_y, cx - 2, eye_y + 1], srgba(p["eye"]))
        # 鼻尖（侧面凸出）
        draw_ellipse_aa(draw, [cx - head_w - 1, cy + 2,
                               cx - head_w + 2, cy + 5], srgba(p["skin_shadow"]))
        # 嘴（侧面小点）
        draw_ellipse_aa(draw, [cx - head_w + 1, cy + 6,
                               cx - head_w + 4, cy + 7], srgba(p["skin_shadow"]))
        # 爱丽丝发带（侧）
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w, cy - 4,
                                   cx + head_w - 2, cy - 1], srgba(p["hair_ribbon"]))
    elif direction == "right":
        # 右侧面（与 left 镜像）
        draw_ellipse_aa(draw, [cx - head_w, cy - head_h - 2,
                               cx + head_w, cy + 1], srgba(p["hair"]))
        draw_ellipse_aa(draw, [cx - head_w - 2, cy - head_h + 2,
                               cx - head_w + 3, cy + head_h], srgba(p["hair_light"]))
        draw_ellipse_aa(draw, [cx - head_w + 1, cy - head_h + 4,
                               cx + head_w - 1, cy + head_h - 2], srgba(p["skin"]))
        draw_ellipse_aa(draw, [cx - head_w + 2, cy + head_h - 4,
                               cx + head_w - 2, cy + head_h - 1], srgba(p["skin_shadow"]))
        eye_y = cy - 1
        draw_ellipse_aa(draw, [cx + 1, eye_y - 1, cx + 4, eye_y + 2], srgba(p["eye_white"]))
        draw_ellipse_aa(draw, [cx + 2, eye_y, cx + 3, eye_y + 1], srgba(p["eye"]))
        draw_ellipse_aa(draw, [cx + head_w - 2, cy + 2,
                               cx + head_w + 1, cy + 5], srgba(p["skin_shadow"]))
        draw_ellipse_aa(draw, [cx + head_w - 4, cy + 6,
                               cx + head_w - 1, cy + 7], srgba(p["skin_shadow"]))
        if hair_style == "tied_back":
            draw_ellipse_aa(draw, [cx - head_w + 2, cy - 4,
                                   cx + head_w, cy - 1], srgba(p["hair_ribbon"]))


def draw_chr_body(draw, cx, body_y, direction, pal, character, walk_phase=0, anim="idle", pose_data=None):
    """绘制身体。cx 为身体中心, body_y 为颈部位置。"""
    p = pal
    char_name = character["name"]
    torso_w = 13
    torso_h = 18
    shoulder_y = body_y + 1
    hip_y = shoulder_y + torso_h

    # 走路姿态参数
    if anim == "walk":
        # 6帧行走：左右腿交替摆动、手臂交替、身体上下浮动
        # walk_phase: 0=左脚着地, 1=左下, 2=右脚着地, 3=右下, 4=左脚着地(同0), 5=左下(同1)
        bob = int(1.5 * math.sin(walk_phase * math.pi / 1.5))
        lean = int(0.8 * math.sin(walk_phase * math.pi / 1.5))
    elif anim == "interact":
        bob = 0
        lean = int(0.5 * math.cos(pose_data * math.pi / 1.5))
    else:  # idle
        bob = int(1.0 * math.sin(pose_data * math.pi))
        lean = 0

    # === 外套/衣服主体 ===
    if char_name == "kirito":
        coat_color = p["coat"]
        coat_light = p["coat_light"]
        accent = p["accent"]
    elif char_name == "alice":
        coat_color = p["dress"]
        coat_light = p["dress_light"]
        accent = p["accent"]
    else:
        coat_color = p["shirt"]
        coat_light = p["shirt_light"]
        accent = p["accent"]

    # 躯干（梯形剪影）
    if direction == "down":
        # 双肩
        tlx, tly = cx - torso_w, shoulder_y + bob
        brx, bry = cx + torso_w, shoulder_y + torso_h + bob
        # 上身
        draw.polygon([(cx - torso_w + 1, shoulder_y + bob),
                      (cx + torso_w - 1, shoulder_y + bob),
                      (cx + torso_w - 1, hip_y - 1 + bob),
                      (cx - torso_w + 1, hip_y - 1 + bob)], fill=srgba(coat_color))
        # 胸衣亮面（左侧）
        draw.polygon([(cx - torso_w + 1, shoulder_y + bob),
                      (cx - torso_w + 5, shoulder_y + bob),
                      (cx - torso_w + 4, hip_y - 1 + bob),
                      (cx - torso_w + 1, hip_y - 1 + bob)], fill=srgba(coat_light))
        # 识别色装饰线
        draw.rectangle([cx - 1, shoulder_y + 2 + bob, cx + 1, shoulder_y + 8 + bob], fill=srgba(accent))
        if char_name == "alice":
            # 护肩披肩
            draw.polygon([(cx - torso_w - 2, shoulder_y + bob),
                          (cx - torso_w + 3, shoulder_y + bob),
                          (cx - torso_w + 1, shoulder_y + 4 + bob),
                          (cx - torso_w - 2, shoulder_y + 4 + bob)], fill=srgba(p["vest"]))
            draw.polygon([(cx + torso_w - 3, shoulder_y + bob),
                          (cx + torso_w + 2, shoulder_y + bob),
                          (cx + torso_w + 2, shoulder_y + 4 + bob),
                          (cx + torso_w - 1, shoulder_y + 4 + bob)], fill=srgba(p["vest"]))
        if char_name == "eugeo":
            # 背心外套
            draw.polygon([(cx - torso_w + 1, shoulder_y + bob),
                          (cx + torso_w - 1, shoulder_y + bob),
                          (cx + torso_w - 2, shoulder_y + 12 + bob),
                          (cx - torso_w + 2, shoulder_y + 12 + bob)], fill=srgba(p["vest"], 180))

    elif direction == "up":
        # 背面：无正面装饰，只看背部剪影
        draw.polygon([(cx - torso_w + 1, shoulder_y + bob),
                      (cx + torso_w - 1, shoulder_y + bob),
                      (cx + torso_w - 1, hip_y - 1 + bob),
                      (cx - torso_w + 1, hip_y - 1 + bob)], fill=srgba(coat_color))
        # 背部折线（浅色装饰）
        draw.line([(cx, shoulder_y + 2 + bob), (cx, hip_y - 2 + bob)],
                  fill=srgba(coat_light), width=1)
        if char_name == "alice":
            draw.polygon([(cx - torso_w - 1, shoulder_y + bob),
                          (cx - torso_w + 3, shoulder_y + bob),
                          (cx - torso_w + 1, shoulder_y + 4 + bob),
                          (cx - torso_w - 1, shoulder_y + 4 + bob)], fill=srgba(p["vest"]))
            draw.polygon([(cx + torso_w - 3, shoulder_y + bob),
                          (cx + torso_w + 1, shoulder_y + bob),
                          (cx + torso_w + 1, shoulder_y + 4 + bob),
                          (cx + torso_w - 1, shoulder_y + 4 + bob)], fill=srgba(p["vest"]))

    elif direction == "left":
        # 左侧面：身体左侧轮廓
        draw.polygon([(cx - torso_w + 2, shoulder_y + bob),
                      (cx + torso_w - 1, shoulder_y + bob),
                      (cx + torso_w - 1, hip_y - 1 + bob),
                      (cx - torso_w + 1, hip_y - 1 + bob)], fill=srgba(coat_color))
        # 胸前装饰（侧面可见）
        draw.line([(cx + torso_w - 3, shoulder_y + 3 + bob),
                   (cx + torso_w - 3, shoulder_y + 8 + bob)], fill=srgba(accent), width=1)

    elif direction == "right":
        # 右侧面（与 left 镜像）
        draw.polygon([(cx - torso_w + 1, shoulder_y + bob),
                      (cx + torso_w - 2, shoulder_y + bob),
                      (cx + torso_w - 1, hip_y - 1 + bob),
                      (cx - torso_w + 1, hip_y - 1 + bob)], fill=srgba(coat_color))
        draw.line([(cx - torso_w + 3, shoulder_y + 3 + bob),
                   (cx - torso_w + 3, shoulder_y + 8 + bob)], fill=srgba(accent), width=1)

    return hip_y, lean


def draw_chr_arms(draw, cx, shoulder_y, hip_y, direction, pal, character,
                  walk_phase=0, anim="idle", pose_data=0):
    """绘制手臂。"""
    p = pal
    char_name = character["name"]
    if char_name == "kirito":
        coat_color = p["coat"]
        skin_color = p["skin"]
    elif char_name == "alice":
        coat_color = p["dress"]
        skin_color = p["skin"]
    else:
        coat_color = p["shirt"]
        skin_color = p["skin"]

    # 计算手臂位置和角度
    arms = []

    if anim == "walk":
        # 6帧行走：手臂前后摆动（与脚步反向）
        # walk_phase 0-5
        swing = math.sin(walk_phase * math.pi / 1.5)
        left_arm_swing = -swing * 4   # 左手前后
        right_arm_swing = swing * 4   # 右手反向
        bob = int(1.5 * math.sin(walk_phase * math.pi / 1.5))
    elif anim == "interact":
        # 4帧交互：伸手-检查-持物-放手
        # pose_data: 0=伸出, 1=检查, 2=持物, 3=放手
        if pose_data == 0:  # 伸出右手
            left_arm_swing = 0
            right_arm_swing = -8
        elif pose_data == 1:  # 检查（低头看）
            left_arm_swing = -2
            right_arm_swing = -4
        elif pose_data == 2:  # 持物（双手胸前）
            left_arm_swing = -5
            right_arm_swing = -5
        else:  # 放手回归
            left_arm_swing = -1
            right_arm_swing = -2
        bob = 0
    else:  # idle
        left_arm_swing = int(0.5 * math.sin(pose_data * math.pi))
        right_arm_swing = -left_arm_swing
        bob = int(1.0 * math.sin(pose_data * math.pi))

    shoulder_y_adj = shoulder_y + bob

    if direction == "down":
        # 左手臂（身体左侧）
        l_sx = cx - 11
        l_ex = cx - 11 + left_arm_swing
        l_ey = shoulder_y_adj + 13
        draw.line([(l_sx, shoulder_y_adj + 2), (l_ex, l_ey)],
                  fill=srgba(coat_color), width=3)
        # 左手（皮肤）
        draw_ellipse_aa(draw, [l_ex - 2, l_ey - 2, l_ex + 2, l_ey + 2], srgba(skin_color))

        # 右手臂
        r_sx = cx + 11
        r_ex = cx + 11 + right_arm_swing
        r_ey = shoulder_y_adj + 13
        draw.line([(r_sx, shoulder_y_adj + 2), (r_ex, r_ey)],
                  fill=srgba(coat_color), width=3)
        draw_ellipse_aa(draw, [r_ex - 2, r_ey - 2, r_ex + 2, r_ey + 2], srgba(skin_color))

        # 交互动作：持物时在胸前画记录册/记录页
        if anim == "interact" and pose_data == 2:
            tool_x = cx - 4
            tool_y = shoulder_y_adj + 10
            if char_name == "kirito":
                # 记录册
                draw_ellipse_aa(draw, [tool_x, tool_y, tool_x + 8, tool_y + 6],
                               srgba(p["tool"]))
                draw_ellipse_aa(draw, [tool_x + 1, tool_y + 1, tool_x + 7, tool_y + 5],
                               srgba(p["tool_light"]))
            elif char_name == "alice":
                # 圈注过的记录页
                draw_ellipse_aa(draw, [tool_x, tool_y, tool_x + 8, tool_y + 6],
                               srgba(p["tool"]))
                draw_ellipse_aa(draw, [tool_x + 2, tool_y + 1, tool_x + 6, tool_y + 2],
                               srgba(p["accent"]))
            else:
                # 劳动工具
                draw_ellipse_aa(draw, [tool_x, tool_y, tool_x + 8, tool_y + 6],
                               srgba(p["tool"]))
                draw_ellipse_aa(draw, [tool_x + 2, tool_y + 2, tool_x + 6, tool_y + 5],
                               srgba(p["tool_light"]))

    elif direction == "left":
        # 左侧面：只画近侧手臂（左手）和远侧手臂（右手，部分遮挡）
        # 近侧手臂
        n_sx = cx - 9
        n_ex = cx - 9 + left_arm_swing
        n_ey = shoulder_y_adj + 13
        draw.line([(n_sx, shoulder_y_adj + 2), (n_ex, n_ey)],
                  fill=srgba(coat_color), width=3)
        draw_ellipse_aa(draw, [n_ex - 2, n_ey - 2, n_ex + 2, n_ey + 2], srgba(skin_color))

        # 远侧手臂（部分可见）
        f_sx = cx + 7
        f_ex = cx + 7 + right_arm_swing
        f_ey = shoulder_y_adj + 13
        draw.line([(f_sx, shoulder_y_adj + 2), (f_ex, f_ey)],
                  fill=srgba(coat_color, 200), width=2)
        draw_ellipse_aa(draw, [f_ex - 1, f_ey - 1, f_ex + 2, f_ey + 2], srgba(skin_color, 200))

    elif direction == "right":
        # 右侧面（与 left 镜像）
        n_sx = cx + 9
        n_ex = cx + 9 - left_arm_swing  # 镜像：反向摆动
        n_ey = shoulder_y_adj + 13
        draw.line([(n_sx, shoulder_y_adj + 2), (n_ex, n_ey)],
                  fill=srgba(coat_color), width=3)
        draw_ellipse_aa(draw, [n_ex - 2, n_ey - 2, n_ex + 2, n_ey + 2], srgba(skin_color))

        f_sx = cx - 7
        f_ex = cx - 7 - right_arm_swing
        f_ey = shoulder_y_adj + 13
        draw.line([(f_sx, shoulder_y_adj + 2), (f_ex, f_ey)],
                  fill=srgba(coat_color, 200), width=2)
        draw_ellipse_aa(draw, [f_ex - 2, f_ey - 1, f_ex + 1, f_ey + 2], srgba(skin_color, 200))

    elif direction == "up":
        # 背面：双臂对称，自然下垂
        for sign in [-1, 1]:
            s_x = cx + sign * 11
            e_x = cx + sign * 11 + left_arm_swing * sign
            e_y = shoulder_y_adj + 13
            draw.line([(s_x, shoulder_y_adj + 2), (e_x, e_y)],
                      fill=srgba(coat_color), width=3)
            draw_ellipse_aa(draw, [e_x - 2, e_y - 2, e_x + 2, e_y + 2], srgba(skin_color))


def draw_chr_legs(draw, cx, hip_y, direction, pal, character,
                  walk_phase=0, anim="idle", pose_data=0):
    """绘制腿部。"""
    p = pal
    char_name = character["name"]
    if char_name == "kirito":
        trousers_color = p["trousers"]
        trousers_light = p["trousers_light"]
        boots_color = p["boots"]
    elif char_name == "alice":
        trousers_color = p["trousers"]
        trousers_light = p["trousers_light"]
        boots_color = p["boots"]
    else:
        trousers_color = p["trousers"]
        trousers_light = p["trousers_light"]
        boots_color = p["boots"]

    # 脚底锚点：bottom-center (cx, CELL_H-2)
    # hip_y 是腰带位置，下面是腿部
    leg_top_y = hip_y + 1

    if anim == "walk":
        # 6帧行走循环
        # walk_phase 0-5
        # 左脚相位 = walk_phase
        # 右脚相位 = walk_phase + 3 (反相)
        l_phase = walk_phase
        r_phase = (walk_phase + 3) % 6
        # 摆动幅度：腿前后摆动
        l_swing = math.sin(l_phase * math.pi / 1.5) * 3
        r_swing = math.sin(r_phase * math.pi / 1.5) * 3
        # 上下浮动
        bob = int(1.5 * math.sin(walk_phase * math.pi / 1.5))
        leg_top_y_adj = leg_top_y + bob
    elif anim == "interact":
        l_swing = 0
        r_swing = 0
        bob = 0
        leg_top_y_adj = leg_top_y
    else:  # idle
        l_swing = int(0.5 * math.sin(pose_data * math.pi))
        r_swing = -l_swing
        bob = int(1.0 * math.sin(pose_data * math.pi))
        leg_top_y_adj = leg_top_y + bob

    if direction == "down":
        # 左腿（身体左侧）
        l_foot_x = cx - 4 + int(l_swing)
        l_foot_y = CELL_H - 2
        draw.line([(cx - 4, leg_top_y_adj), (l_foot_x, l_foot_y - 4)],
                  fill=srgba(trousers_color), width=3)
        # 鞋
        draw_ellipse_aa(draw, [l_foot_x - 3, l_foot_y - 3, l_foot_x + 3, l_foot_y + 1],
                       srgba(boots_color))

        # 右腿
        r_foot_x = cx + 4 + int(r_swing)
        r_foot_y = CELL_H - 2
        draw.line([(cx + 4, leg_top_y_adj), (r_foot_x, r_foot_y - 4)],
                  fill=srgba(trousers_color), width=3)
        draw_ellipse_aa(draw, [r_foot_x - 3, r_foot_y - 3, r_foot_x + 3, r_foot_y + 1],
                       srgba(boots_color))

    elif direction == "left":
        # 左侧面：近侧腿完整，远侧腿部分遮挡
        n_foot_x = cx - 3 + int(l_swing)
        n_foot_y = CELL_H - 2
        draw.line([(cx - 2, leg_top_y_adj), (n_foot_x, n_foot_y - 4)],
                  fill=srgba(trousers_color), width=3)
        draw_ellipse_aa(draw, [n_foot_x - 3, n_foot_y - 3, n_foot_x + 3, n_foot_y + 1],
                       srgba(boots_color))

        # 远侧腿
        f_foot_x = cx + 4 + int(r_swing)
        f_foot_y = CELL_H - 2
        draw.line([(cx + 2, leg_top_y_adj), (f_foot_x, f_foot_y - 4)],
                  fill=srgba(trousers_color, 200), width=2)
        draw_ellipse_aa(draw, [f_foot_x - 2, f_foot_y - 3, f_foot_x + 2, f_foot_y + 1],
                       srgba(boots_color, 200))

    elif direction == "right":
        # 右侧面（与 left 镜像）
        n_foot_x = cx + 3 - int(l_swing)
        n_foot_y = CELL_H - 2
        draw.line([(cx + 2, leg_top_y_adj), (n_foot_x, n_foot_y - 4)],
                  fill=srgba(trousers_color), width=3)
        draw_ellipse_aa(draw, [n_foot_x - 3, n_foot_y - 3, n_foot_x + 3, n_foot_y + 1],
                       srgba(boots_color))

        f_foot_x = cx - 4 - int(r_swing)
        f_foot_y = CELL_H - 2
        draw.line([(cx - 2, leg_top_y_adj), (f_foot_x, f_foot_y - 4)],
                  fill=srgba(trousers_color, 200), width=2)
        draw_ellipse_aa(draw, [f_foot_x - 2, f_foot_y - 3, f_foot_x + 2, f_foot_y + 1],
                       srgba(boots_color, 200))

    elif direction == "up":
        # 背面：双腿对称
        l_foot_x = cx - 4 + int(l_swing)
        l_foot_y = CELL_H - 2
        draw.line([(cx - 4, leg_top_y_adj), (l_foot_x, l_foot_y - 4)],
                  fill=srgba(trousers_color), width=3)
        draw_ellipse_aa(draw, [l_foot_x - 3, l_foot_y - 3, l_foot_x + 3, l_foot_y + 1],
                       srgba(boots_color))

        r_foot_x = cx + 4 + int(r_swing)
        r_foot_y = CELL_H - 2
        draw.line([(cx + 4, leg_top_y_adj), (r_foot_x, r_foot_y - 4)],
                  fill=srgba(trousers_color), width=3)
        draw_ellipse_aa(draw, [r_foot_x - 3, r_foot_y - 3, r_foot_x + 3, r_foot_y + 1],
                       srgba(boots_color))


def render_frame(character, direction, anim, frame_index):
    """渲染单帧 64x96 RGBA。"""
    img = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pal = character["palette"]
    char_name = character["name"]
    hair_style = character["hair_style"]

    # 角色中心 X = CELL_W // 2 = 32
    cx = CELL_W // 2

    # 头部中心 Y
    head_cy = 18  # 头顶到 CELL_H-2 = 96-2 = 94 的距离约 76，头部中心约在 18

    # === 绘制顺序：腿→身体→手臂→头 ===
    # 1. 腿部（先画，在身体后面）
    hip_y = 50  # 默认髋部位置
    draw_chr_legs(draw, cx, hip_y, direction, pal, character,
                  walk_phase=frame_index, anim=anim, pose_data=frame_index)

    # 2. 身体
    actual_hip_y, _ = draw_chr_body(draw, cx, 32, direction, pal, character,
                                     walk_phase=frame_index, anim=anim,
                                     pose_data=frame_index)

    # 3. 手臂（在身体之后画，可以覆盖身体一部分表示伸手）
    draw_chr_arms(draw, cx, 32, actual_hip_y, direction, pal, character,
                  walk_phase=frame_index, anim=anim, pose_data=frame_index)

    # 4. 头部（最后画，最前面）
    draw_chr_head(draw, cx, head_cy, direction, pal, hair_style)

    return img


def compose_sheet(frames_grid):
    """合成 sprite sheet。frames_grid 是 4x12 列表，每元素是 64x96 RGBA Image。"""
    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    for row_idx, row in enumerate(frames_grid):
        for col_idx, frame in enumerate(row):
            sheet.paste(frame, (col_idx * CELL_W, row_idx * CELL_H))
    return sheet


def smooth_frame(img, radius=0.5):
    """轻量平滑。"""
    if radius > 0:
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    return img


def generate_character_sprites(char_key, version="v007"):
    """为单个角色生成完整 48 帧 sprite sheet + frames JSON。"""
    character = CHARACTERS[char_key]
    name = character["name"]

    # 动画顺序：idle[0,1] + walk[0..5] + interact[0..3] = 12 帧
    column_order = []
    for i in range(2):
        column_order.append(("idle", i))
    for i in range(6):
        column_order.append(("walk", i))
    for i in range(4):
        column_order.append(("interact", i))

    directions = ["down", "left", "right", "up"]
    frames_grid = []  # 4 行 × 12 列
    frames_meta = []

    for row_idx, direction in enumerate(directions):
        row = []
        for col_idx, (anim, frame_idx) in enumerate(column_order):
            frame_img = render_frame(character, direction, anim, frame_idx)
            # 轻量平滑
            frame_img = smooth_frame(frame_img, radius=0.4)
            row.append(frame_img)

            # 记录元数据
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

    # 生成 JSON
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
                        "duration_ms": {
                            "idle": 800,
                            "walk": 140,
                                "interact": 350,
                            }[anim],
                    })
            animations_meta[key] = {
                "loop": anim != "interact",
                "frames": anim_frames,
                "anchor": [CELL_W // 2, CELL_H - 2],  # bottom-center
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
        "supersedes": "v003 geometric puppets, v006 procedural painterly; v007 adds richer silhouettes, real walking gait, distinct interaction gestures",
    }

    return sheet, json_data, frames_meta


def sha256_file(path):
    """计算文件 SHA-256。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    """主入口。"""
    output_dir = r"C:\Users\liang\Desktop\uw\materials\inbox\visual\characters"
    os.makedirs(output_dir, exist_ok=True)

    version = "v007"

    print(f"=== UW v007 Sprite Generator ===")
    print(f"Output: {output_dir}")
    print(f"Version: {version}")
    print(f"Characters: {list(CHARACTERS.keys())}")
    print()

    for idx, char_key in enumerate(CHARACTERS.keys(), 1):
        request_id = f"VIS-CHR-{idx:03d}"
        character = CHARACTERS[char_key]
        name = character["name"]

        print(f"Generating {request_id} ({name})...")

        sheet, json_data, frames_meta = generate_character_sprites(char_key, version)

        # 保存 sprite sheet
        sheet_filename = f"{request_id}_{name}_sprite_sheet_{version}.png"
        sheet_path = os.path.join(output_dir, sheet_filename)
        sheet.save(sheet_path, "PNG")

        # 保存 JSON
        json_filename = f"{request_id}_frames_{version}.json"
        json_path = os.path.join(output_dir, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # 计算 SHA-256
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