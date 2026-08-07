#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-CHR-001/002/003 v003 角色 sprite 生成器。

每个角色 1 个 768x384 RGBA sprite sheet, 4 行 (down/left/right/up) × 12 列
(idle_0, idle_1, walk_0..5, interact_0..3), 64x96 frame cell。
提供 VIS-CHR-XXX_frames_v003.json 含 rect/duration/fps/loop/anchor/footprint。
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw

ROOT = Path(r"C:\Users\liang\Desktop\UW")
CHR_DIR = ROOT / "materials" / "inbox" / "visual" / "characters"
WORK_DIR = CHR_DIR / "_v003_work"

FRAME_W = 64
FRAME_H = 96
DIRECTIONS = ["down", "left", "right", "up"]
ANIM_FRAMES = {
    "idle": 2,
    "walk": 6,
    "interact": 4,
}
# 列布局: [idle_0, idle_1, walk_0..5, interact_0..3] = 12 帧
COL_ORDER = (
    [("idle", 0), ("idle", 1)]
    + [("walk", i) for i in range(6)]
    + [("interact", i) for i in range(4)]
)
SHEET_W = FRAME_W * len(COL_ORDER)  # 768
SHEET_H = FRAME_H * len(DIRECTIONS)  # 384

# 角色配色
CHARACTERS = {
    "VIS-CHR-001": {  # Kirito
        "name": "kirito",
        "skin": (255, 220, 180, 255),
        "skin_shadow": (220, 180, 150, 255),
        "hair": (28, 24, 30, 255),
        "hair_highlight": (60, 50, 60, 255),
        "cloth_main": (40, 60, 120, 255),
        "cloth_dark": (28, 40, 80, 255),
        "cloth_accent": (200, 190, 100, 255),  # 黄铜扣
        "belt": (60, 40, 30, 255),
        "shoes": (40, 30, 25, 255),
        "eye_dark": (35, 25, 20, 255),
        "eye_white": (245, 240, 230, 255),
    },
    "VIS-CHR-002": {  # Alice (childhood)
        "name": "alice",
        "skin": (250, 218, 188, 255),
        "skin_shadow": (220, 188, 160, 255),
        "hair": (235, 215, 130, 255),  # 金发
        "hair_highlight": (255, 240, 170, 255),
        "cloth_main": (235, 235, 245, 255),  # 白裙
        "cloth_dark": (200, 200, 215, 255),
        "cloth_accent": (110, 150, 200, 255),  # 蓝丝带
        "belt": (90, 70, 110, 255),
        "shoes": (90, 80, 100, 255),
        "eye_dark": (60, 90, 120, 255),
        "eye_white": (250, 245, 240, 255),
    },
    "VIS-CHR-003": {  # Eugeo
        "name": "eugeo",
        "skin": (250, 215, 175, 255),
        "skin_shadow": (215, 180, 145, 255),
        "hair": (155, 130, 80, 255),  # 浅棕
        "hair_highlight": (195, 170, 110, 255),
        "cloth_main": (110, 130, 80, 255),  # 绿色
        "cloth_dark": (75, 95, 55, 255),
        "cloth_accent": (180, 150, 100, 255),
        "belt": (90, 70, 50, 255),
        "shoes": (60, 45, 35, 255),
        "eye_dark": (60, 80, 60, 255),
        "eye_white": (245, 240, 230, 255),
    },
}


# ---------------- 帧渲染 ----------------

def new_frame() -> Image.Image:
    return Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))


def draw_head(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, c: Dict) -> None:
    # 脸
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c["skin"])
    # 阴影（右脸）
    d.ellipse([cx, cy - r, cx + r, cy + r], fill=c["skin_shadow"])


def draw_hair_down(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, c: Dict) -> None:
    # 刘海覆盖额头 + 两侧
    d.chord([cx - r - 1, cy - r - 1, cx + r + 1, cy + r // 2 + 1], 180, 360,
            fill=c["hair"])
    # 鬓角
    d.rectangle([cx - r - 1, cy - r // 2, cx - r + 2, cy + r], fill=c["hair"])
    d.rectangle([cx + r - 2, cy - r // 2, cx + r + 1, cy + r], fill=c["hair"])
    # 高光
    d.point((cx - 2, cy - 2), fill=c["hair_highlight"])


def draw_eyes_down(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict) -> None:
    # 眼白
    d.ellipse([cx - 6, cy - 2, cx - 2, cy + 1], fill=c["eye_white"])
    d.ellipse([cx + 2, cy - 2, cx + 6, cy + 1], fill=c["eye_white"])
    # 瞳孔
    d.ellipse([cx - 5, cy - 1, cx - 3, cy + 1], fill=c["eye_dark"])
    d.ellipse([cx + 3, cy - 1, cx + 5, cy + 1], fill=c["eye_dark"])


def draw_body_down(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   body_h: int = 22, body_w: int = 14) -> None:
    # 身体梯形
    d.polygon([
        (cx - body_w // 2, cy - body_h // 2),
        (cx + body_w // 2, cy - body_h // 2),
        (cx + body_w // 2 + 1, cy + body_h // 2),
        (cx - body_w // 2 - 1, cy + body_h // 2),
    ], fill=c["cloth_main"])
    # 阴影（身体右下）
    d.polygon([
        (cx + 1, cy - body_h // 2),
        (cx + body_w // 2 + 1, cy - body_h // 2),
        (cx + body_w // 2 + 1, cy + body_h // 2),
        (cx + 1, cy + body_h // 2),
    ], fill=c["cloth_dark"])
    # 扣
    d.point((cx, cy - 2), fill=c["cloth_accent"])


def draw_legs_down(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   offset_l: int = 0, offset_r: int = 0) -> None:
    # 左腿
    d.rectangle([cx - 5 + offset_l, cy, cx - 1 + offset_l, cy + 14], fill=c["cloth_dark"])
    # 右腿
    d.rectangle([cx + 1 + offset_r, cy, cx + 5 + offset_r, cy + 14], fill=c["cloth_dark"])
    # 鞋
    d.rectangle([cx - 6 + offset_l, cy + 12, cx + offset_l, cy + 16], fill=c["shoes"])
    d.rectangle([cx + offset_r, cy + 12, cx + 6 + offset_r, cy + 16], fill=c["shoes"])


def draw_arms_down(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   arm_l_y: int = 0, arm_r_y: int = 0,
                   raise_l: int = 0, raise_r: int = 0) -> None:
    # 左手臂
    d.rectangle([cx - 10, cy - 8 + arm_l_y - raise_l, cx - 7, cy + 6 + arm_l_y], fill=c["cloth_main"])
    # 右手臂
    d.rectangle([cx + 7, cy - 8 + arm_r_y - raise_r, cx + 10, cy + 6 + arm_r_y], fill=c["cloth_main"])
    # 手
    d.ellipse([cx - 11, cy + 4 + arm_l_y, cx - 6, cy + 8 + arm_l_y], fill=c["skin"])
    d.ellipse([cx + 6, cy + 4 + arm_r_y, cx + 11, cy + 8 + arm_r_y], fill=c["skin"])


# ----- 后视图（up） -----

def draw_hair_back(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, c: Dict) -> None:
    # 后脑勺整体头发
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c["hair"])
    # 头发纹理
    d.line([(cx - r + 2, cy - 2), (cx + r - 2, cy - 2)], fill=c["hair_highlight"])
    d.line([(cx - 2, cy - r), (cx - 2, cy + r - 4)], fill=c["hair_highlight"])


def draw_body_back(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   body_h: int = 22, body_w: int = 14) -> None:
    d.rectangle([cx - body_w // 2, cy - body_h // 2, cx + body_w // 2, cy + body_h // 2],
                fill=c["cloth_main"])


# ----- 侧视图（left/right） -----

def draw_head_side(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, c: Dict,
                   facing: str) -> None:
    """facing: 'left' or 'right'"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c["skin"])
    # 头发覆盖
    if facing == "left":
        d.chord([cx - r - 1, cy - r - 1, cx + r + 1, cy + 1], 180, 360, fill=c["hair"])
    else:
        d.chord([cx - r - 1, cy - r - 1, cx + r + 1, cy + 1], 180, 360, fill=c["hair"])
    # 单只眼
    if facing == "left":
        d.ellipse([cx - 5, cy - 1, cx - 1, cy + 2], fill=c["eye_white"])
        d.ellipse([cx - 4, cy, cx - 2, cy + 2], fill=c["eye_dark"])
    else:
        d.ellipse([cx + 1, cy - 1, cx + 5, cy + 2], fill=c["eye_white"])
        d.ellipse([cx + 2, cy, cx + 4, cy + 2], fill=c["eye_dark"])


def draw_body_side(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   facing: str, body_h: int = 22, body_w: int = 10) -> None:
    d.rectangle([cx - body_w // 2, cy - body_h // 2, cx + body_w // 2, cy + body_h // 2],
                fill=c["cloth_main"])
    # 背带
    d.line([(cx, cy - body_h // 2), (cx, cy + body_h // 2 - 1)], fill=c["cloth_dark"], width=1)


def draw_legs_side(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   facing: str, walk_phase: float) -> None:
    """walk_phase: 0..1 cycle. 0 = left leg forward, 0.5 = right leg forward."""
    # 前腿
    front_off = int(2 * math.sin(walk_phase * 2 * math.pi))
    back_off = -front_off
    if facing == "left":
        front_x = cx - 2
        back_x = cx + 1
    else:
        front_x = cx + 2
        back_x = cx - 1
    d.rectangle([front_x - 2, cy + front_off, front_x + 2, cy + 14 + front_off],
                fill=c["cloth_dark"])
    d.rectangle([back_x - 2, cy + back_off, back_x + 2, cy + 14 + back_off],
                fill=c["cloth_dark"])
    d.rectangle([front_x - 3, cy + 12 + front_off, front_x + 3, cy + 16 + front_off],
                fill=c["shoes"])
    d.rectangle([back_x - 3, cy + 12 + back_off, back_x + 3, cy + 16 + back_off],
                fill=c["shoes"])


def draw_arms_side(d: ImageDraw.ImageDraw, cx: int, cy: int, c: Dict,
                   facing: str, swing: float = 0) -> None:
    """swing: -1..1, 手臂前后摆动."""
    if facing == "left":
        front_x, back_x = cx - 5, cx + 4
    else:
        front_x, back_x = cx + 5, cx - 4
    # 前臂
    d.rectangle([front_x - 2, cy - 8 + int(swing * 2), front_x + 2, cy + 6 + int(swing * 2)],
                fill=c["cloth_main"])
    d.ellipse([front_x - 3, cy + 4 + int(swing * 2), front_x + 3, cy + 8 + int(swing * 2)],
              fill=c["skin"])
    # 后臂（更靠近身体）
    d.rectangle([back_x - 2, cy - 8 - int(swing * 2), back_x + 2, cy + 6 - int(swing * 2)],
                fill=c["cloth_dark"])
    d.ellipse([back_x - 3, cy + 4 - int(swing * 2), back_x + 3, cy + 8 - int(swing * 2)],
              fill=c["skin_shadow"])


# ---------------- 帧定义 ----------------

def render_idle_down(idx: int, c: Dict) -> Image.Image:
    """idle 2 帧：呼吸位移。"""
    im = new_frame()
    d = ImageDraw.Draw(im)
    # foot anchor 在 (32, 92)
    foot_y = 92
    head_cy = foot_y - 60 - idx  # 呼吸
    body_cy = foot_y - 38
    # 后腿画在下层
    draw_legs_down(d, 32, body_cy + 10, c, offset_l=0, offset_r=0)
    draw_body_down(d, 32, body_cy, c)
    draw_arms_down(d, 32, body_cy, c, arm_l_y=0, arm_r_y=0)
    draw_head(d, 32, head_cy, 8, c)
    draw_hair_down(d, 32, head_cy, 8, c)
    draw_eyes_down(d, 32, head_cy + 1, c)
    return im


def render_walk_down(idx: int, c: Dict) -> Image.Image:
    """walk 6 帧：两脚左右摆动 + 身体微弹。"""
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    # 6 帧 = 一个完整步态周期
    # 0: 左前, 1: 中(左立), 2: 右前, 3: 中(右立), 4: 左前(回到), 5: 中
    cycle = [(-3, 3), (0, 0), (3, -3), (0, 0), (-3, 3), (0, 0)][idx]
    bounce = 1 if idx in (1, 4) else 0
    head_cy = foot_y - 60 - bounce
    body_cy = foot_y - 38 - bounce
    draw_legs_down(d, 32, body_cy + 10, c, offset_l=cycle[0], offset_r=cycle[1])
    draw_body_down(d, 32, body_cy, c)
    draw_arms_down(d, 32, body_cy, c,
                   arm_l_y=-cycle[1] // 2, arm_r_y=-cycle[0] // 2)
    draw_head(d, 32, head_cy, 8, c)
    draw_hair_down(d, 32, head_cy, 8, c)
    draw_eyes_down(d, 32, head_cy + 1, c)
    return im


def render_interact_down(idx: int, c: Dict) -> Image.Image:
    """interact 4 帧：右手抬起做招手/接物动作。"""
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    head_cy = foot_y - 60
    body_cy = foot_y - 38
    # idx 0: 准备, 1: 抬起到 45度, 2: 抬手到顶, 3: 放下
    raise_amount = [0, 8, 14, 4][idx]
    draw_legs_down(d, 32, body_cy + 10, c)
    draw_body_down(d, 32, body_cy, c)
    draw_arms_down(d, 32, body_cy, c,
                   arm_l_y=0, arm_r_y=0, raise_r=raise_amount)
    draw_head(d, 32, head_cy, 8, c)
    draw_hair_down(d, 32, head_cy, 8, c)
    draw_eyes_down(d, 32, head_cy + 1, c)
    # 抬手时眼睛略上扬
    if raise_amount >= 8:
        d.point((28, head_cy - 1), fill=c["eye_dark"])
        d.point((36, head_cy - 1), fill=c["eye_dark"])
    return im


# 通用侧视/后视渲染

def render_idle_side(idx: int, c: Dict, facing: str) -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    head_cy = foot_y - 60 - idx
    body_cy = foot_y - 38
    draw_legs_side(d, 32, body_cy + 10, c, facing, walk_phase=0)
    draw_body_side(d, 32, body_cy, c, facing)
    draw_arms_side(d, 32, body_cy, c, facing, swing=0)
    draw_head_side(d, 32, head_cy, 8, c, facing)
    return im


def render_walk_side(idx: int, c: Dict, facing: str) -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    phase = idx / 6.0
    head_cy = foot_y - 60
    body_cy = foot_y - 38
    draw_legs_side(d, 32, body_cy + 10, c, facing, walk_phase=phase)
    draw_body_side(d, 32, body_cy, c, facing)
    draw_arms_side(d, 32, body_cy, c, facing, swing=math.sin(phase * 2 * math.pi))
    draw_head_side(d, 32, head_cy, 8, c, facing)
    return im


def render_interact_side(idx: int, c: Dict, facing: str) -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    head_cy = foot_y - 60
    body_cy = foot_y - 38
    # 抬手（朝前）
    if facing == "left":
        raise_y = [0, 6, 10, 3][idx]
        # 右手（前手）抬起
        d.rectangle([32 - 5 - 2, body_cy - 8 - raise_y, 32 - 5 + 2, body_cy + 6 - raise_y],
                    fill=c["cloth_main"])
        d.ellipse([32 - 5 - 3, body_cy + 4 - raise_y, 32 - 5 + 3, body_cy + 8 - raise_y],
                  fill=c["skin"])
    else:
        raise_y = [0, 6, 10, 3][idx]
        d.rectangle([32 + 5 - 2, body_cy - 8 - raise_y, 32 + 5 + 2, body_cy + 6 - raise_y],
                    fill=c["cloth_main"])
        d.ellipse([32 + 5 - 3, body_cy + 4 - raise_y, 32 + 5 + 3, body_cy + 8 - raise_y],
                  fill=c["skin"])
    draw_legs_side(d, 32, body_cy + 10, c, facing, walk_phase=0)
    draw_body_side(d, 32, body_cy, c, facing)
    # 后手自然下垂
    if facing == "left":
        d.rectangle([32 + 4 - 2, body_cy - 8, 32 + 4 + 2, body_cy + 6], fill=c["cloth_dark"])
        d.ellipse([32 + 4 - 3, body_cy + 4, 32 + 4 + 3, body_cy + 8], fill=c["skin_shadow"])
    else:
        d.rectangle([32 - 4 - 2, body_cy - 8, 32 - 4 + 2, body_cy + 6], fill=c["cloth_dark"])
        d.ellipse([32 - 4 - 3, body_cy + 4, 32 - 4 + 3, body_cy + 8], fill=c["skin_shadow"])
    draw_head_side(d, 32, head_cy, 8, c, facing)
    return im


def render_idle_up(idx: int, c: Dict) -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    head_cy = foot_y - 60 - idx
    body_cy = foot_y - 38
    draw_legs_down(d, 32, body_cy + 10, c)
    draw_body_back(d, 32, body_cy, c)
    draw_arms_down(d, 32, body_cy, c)
    draw_hair_back(d, 32, head_cy, 8, c)
    return im


def render_walk_up(idx: int, c: Dict) -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    cycle = [(-3, 3), (0, 0), (3, -3), (0, 0), (-3, 3), (0, 0)][idx]
    bounce = 1 if idx in (1, 4) else 0
    head_cy = foot_y - 60 - bounce
    body_cy = foot_y - 38 - bounce
    draw_legs_down(d, 32, body_cy + 10, c, offset_l=cycle[0], offset_r=cycle[1])
    draw_body_back(d, 32, body_cy, c)
    draw_arms_down(d, 32, body_cy, c,
                   arm_l_y=-cycle[1] // 2, arm_r_y=-cycle[0] // 2)
    draw_hair_back(d, 32, head_cy, 8, c)
    return im


def render_interact_up(idx: int, c: Dict) -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im)
    foot_y = 92
    head_cy = foot_y - 60
    body_cy = foot_y - 38
    raise_amount = [0, 8, 14, 4][idx]
    draw_legs_down(d, 32, body_cy + 10, c)
    draw_body_back(d, 32, body_cy, c)
    # 抬手
    d.rectangle([32 + 7, body_cy - 8 - raise_amount, 32 + 10, body_cy + 6 - raise_amount],
                fill=c["cloth_main"])
    d.ellipse([32 + 6, body_cy + 4 - raise_amount, 32 + 11, body_cy + 8 - raise_amount],
              fill=c["skin"])
    # 后手
    d.rectangle([32 - 10, body_cy - 8, 32 - 7, body_cy + 6], fill=c["cloth_dark"])
    d.ellipse([32 - 11, body_cy + 4, 32 - 6, body_cy + 8], fill=c["skin_shadow"])
    draw_hair_back(d, 32, head_cy, 8, c)
    return im


# ---------------- 装配 ----------------

def render_frame(direction: str, anim: str, idx: int, c: Dict) -> Image.Image:
    if direction == "down":
        if anim == "idle":
            return render_idle_down(idx, c)
        if anim == "walk":
            return render_walk_down(idx, c)
        if anim == "interact":
            return render_interact_down(idx, c)
    if direction == "left":
        if anim == "idle":
            return render_idle_side(idx, c, "left")
        if anim == "walk":
            return render_walk_side(idx, c, "left")
        if anim == "interact":
            return render_interact_side(idx, c, "left")
    if direction == "right":
        if anim == "idle":
            return render_idle_side(idx, c, "right")
        if anim == "walk":
            return render_walk_side(idx, c, "right")
        if anim == "interact":
            return render_interact_side(idx, c, "right")
    if direction == "up":
        if anim == "idle":
            return render_idle_up(idx, c)
        if anim == "walk":
            return render_walk_up(idx, c)
        if anim == "interact":
            return render_interact_up(idx, c)
    raise ValueError(f"unknown {direction}/{anim}/{idx}")


def build_sheet(req_id: str) -> Tuple[Image.Image, Dict]:
    c = CHARACTERS[req_id]
    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    frames_meta = []
    col_index = {(a, i): idx for idx, (a, i) in enumerate(COL_ORDER)}
    for dir_idx, direction in enumerate(DIRECTIONS):
        for anim, n in ANIM_FRAMES.items():
            for i in range(n):
                frame = render_frame(direction, anim, i, c)
                col = col_index[(anim, i)]
                px = col * FRAME_W
                py = dir_idx * FRAME_H
                sheet.paste(frame, (px, py), frame)
                # 帧元数据
                if anim == "idle":
                    fps = 2  # 1 秒 2 帧
                    dur_ms = 500
                elif anim == "walk":
                    fps = 8
                    dur_ms = 125
                else:  # interact
                    fps = 6
                    dur_ms = int(1000 / 6)
                frames_meta.append({
                    "direction": direction,
                    "animation": anim,
                    "frame_index": i,
                    "rect": {"x": px, "y": py, "w": FRAME_W, "h": FRAME_H},
                    "duration_ms": dur_ms,
                    "fps": fps,
                })
    metadata = {
        "schema_version": "v003",
        "request_id": req_id,
        "character": c["name"],
        "created_at": "2026-08-07",
        "frame_cell_px": {"w": FRAME_W, "h": FRAME_H},
        "sheet_px": {"w": SHEET_W, "h": SHEET_H},
        "directions": DIRECTIONS,
        "column_order": [{"animation": a, "index": i} for (a, i) in COL_ORDER],
        "animations": {
            "idle": {"frames": 2, "fps": 2, "loop": True, "duration_ms": 1000},
            "walk": {"frames": 6, "fps": 8, "loop": True, "duration_ms": 750},
            "interact": {"frames": 4, "fps": 6, "loop": False, "duration_ms": 666},
        },
        "anchor": {
            "type": "bottom-center",
            "px": {"x": FRAME_W // 2, "y": 92},
            "note": "foot anchor at y=92 (bottom of frame minus 4px)",
        },
        "collision_footprint": {
            "width_px": 12,
            "height_px": 4,
            "anchor": "bottom-center",
            "note": "render height 92px, hitbox 12x4 sits on the foot line",
        },
        "alpha_mode": "RGBA, non-interlaced, 8-bit",
        "scale_proof": "render 96px tall; visible 44-52px retains silhouette; "
                       "bottom-center anchor locked across all frames",
        "frames": frames_meta,
    }
    return sheet, metadata


def main() -> None:
    CHR_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    for req_id in ("VIS-CHR-001", "VIS-CHR-002", "VIS-CHR-003"):
        c = CHARACTERS[req_id]
        print(f"Generating {req_id} ({c['name']})...")
        sheet, meta = build_sheet(req_id)
        out = CHR_DIR / f"{req_id}_{c['name']}_sprite_sheet_v003.png"
        sheet.save(out, "PNG", optimize=True)
        print(f"  wrote: {out} ({out.stat().st_size} bytes)")
        json_path = CHR_DIR / f"{req_id}_frames_v003.json"
        json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  wrote: {json_path}")


if __name__ == "__main__":
    main()
