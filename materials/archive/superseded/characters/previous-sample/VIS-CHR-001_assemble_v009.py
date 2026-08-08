#!/usr/bin/env python3
"""
v009 sprite sheet assembler v6.

差异 v5：
- 二次 knockout 灰色软边：sheet 输出后，对每个 cell 做 R+G+B in [200, 540] 范围 knockout。
- 这能去掉 AI 输出图角色剪影外的"灰色软渐变"和"脚下阴影"。
- 保留"明显角色颜色"（蓝色 12-60, 棕色 30-100, 黑色 <50, 浅肤色 >500）。
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

CELL_W, CELL_H = 64, 96
SHEET_W, SHEET_H = 768, 96
ANCHOR_X, ANCHOR_Y = 32, 94

FRAME_IDS = [
    "down_idle_0", "down_idle_1",
    "down_walk_0", "down_walk_1", "down_walk_2",
    "down_walk_3", "down_walk_4", "down_walk_5",
    "down_interact_0", "down_interact_1", "down_interact_2", "down_interact_3",
]

HARD_BBOX_FRAC = (0.18, 0.04, 0.82, 0.96)
WHITE_SUM_MAX = 700

# 灰色软边 knockout 范围（sheet 阶段用）
GRAY_SOFT_MIN = 200  # R+G+B < 此值认为是阴影/黑边
GRAY_SOFT_MAX = 540  # R+G+B > 此值认为是亮边/白边
GRAY_CHROMA_MAX = 18  # |R-G|+|G-B|+|R-B| < 此值认为是灰色（无色相）

TARGET_BODY_HEIGHTS = {
    "idle":     50,
    "walk":     48,
    "interact": 50,
}
TARGET_BODY_HEIGHT_FALLBACK = 50

HERE = Path(__file__).parent
SHEET = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))

stats = []


def _strip_white_bg(img: Image.Image) -> Image.Image:
    src = img.convert("RGBA").copy()
    px = src.load()
    w, h = src.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r + g + b > WHITE_SUM_MAX:
                px[x, y] = (r, g, b, 0)
    return src


def _strip_gray_soft_edge(img: Image.Image) -> Image.Image:
    """Knockout 灰色软边/阴影/亮边。"""
    src = img.convert("RGBA").copy()
    px = src.load()
    w, h = src.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            s = r + g + b
            c = abs(r - g) + abs(g - b) + abs(r - b)
            # 灰色软边：sum 在 [200, 540] 且 chroma < 18
            if GRAY_SOFT_MIN <= s <= GRAY_SOFT_MAX and c < GRAY_CHROMA_MAX:
                px[x, y] = (r, g, b, 0)
    return src


def _anim_from_id(frame_id: str) -> str:
    return frame_id.split("_", 1)[1].rsplit("_", 1)[0]


def _process_frame(frame_id: str, col: int) -> dict:
    src_path = HERE / f"{frame_id}.png"
    raw = Image.open(src_path).convert("RGBA")
    src_w, src_h = raw.size

    bl = int(src_w * HARD_BBOX_FRAC[0])
    bt = int(src_h * HARD_BBOX_FRAC[1])
    br = int(src_w * HARD_BBOX_FRAC[2])
    bb = int(src_h * HARD_BBOX_FRAC[3])
    body_w = br - bl
    body_h = bb - bt

    cropped = raw.crop((bl, bt, br, bb))
    cut = _strip_white_bg(cropped)

    target_h = TARGET_BODY_HEIGHTS.get(_anim_from_id(frame_id), TARGET_BODY_HEIGHT_FALLBACK)
    scale = target_h / body_h
    new_w = max(1, int(round(body_w * scale)))
    new_h = max(1, int(round(body_h * scale)))
    body_resized = cut.resize((new_w, new_h), Image.LANCZOS)

    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    paste_x = ANCHOR_X - new_w // 2
    paste_y = ANCHOR_Y - new_h + 1
    cell.alpha_composite(body_resized, dest=(paste_x, paste_y))
    SHEET.alpha_composite(cell, dest=(col * CELL_W, 0))

    return {
        "frame_id": frame_id,
        "col": col,
        "src": src_path.name,
        "src_size": [src_w, src_h],
        "hard_bbox": [bl, bt, br, bb],
        "target_h": target_h,
        "scale": round(scale, 4),
        "new_size": [new_w, new_h],
        "paste_xy": [paste_x, paste_y],
    }


for i, fid in enumerate(FRAME_IDS):
    stats.append(_process_frame(fid, i))

# Sheet 阶段：二次 knockout 灰色软边
SHEET = _strip_gray_soft_edge(SHEET)

out_png = HERE / "VIS-CHR-001_kirito_sprite_sheet_v009_down.png"
SHEET.save(out_png, format="PNG", optimize=True)
out_json = HERE / "VIS-CHR-001_kirito_sprite_sheet_v009_down.assemble.json"
out_json.write_text(json.dumps({
    "sheet": out_png.name,
    "sheet_size": list(SHEET.size),
    "cell_size": [CELL_W, CELL_H],
    "anchor_px": [ANCHOR_X, ANCHOR_Y],
    "hard_bbox_frac": list(HARD_BBOX_FRAC),
    "gray_soft_range": [GRAY_SOFT_MIN, GRAY_SOFT_MAX],
    "gray_chroma_max": GRAY_CHROMA_MAX,
    "frames": stats,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"sheet: {out_png}  ({SHEET.size[0]}x{SHEET.size[1]})")
print(f"stats: {out_json}")
