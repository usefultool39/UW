#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-UI-001 总览 sheet（2048x1024）。

包含四块验收证据：
  A 96px 语义色主展示（12 枚）
  B 24px 原尺寸实测行（暗底，游戏真实使用场景）
  C 24px 黑白反相行（打印/无彩条件下的轮廓可区分性验收）
  D 同一枚图标 24/48/96 三尺寸对比（抽样验证无糊线）
"""

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/lzm/Desktop/UW/materials")
SET = ROOT / "inbox" / "visual" / "ui_icons" / "VIS-UI-001_core_icons_v001"
OUT = ROOT / "inbox" / "visual" / "ui_icons" / "VIS-UI-001_core_icons_v001_sheet.png"
RSVG = "/opt/miniconda3/bin/rsvg-convert"

W, H = 2048, 1024
BG = "#071018"      # ink-950
PANEL = "#102331"   # ink-800
PAPER = "#FFF7DF"   # paper-100
SUB = "#D9E3E8"     # paper-300
MUTED = "#5C7185"

CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def render_mono(name, size, color):
    """把 SVG 以指定单色渲染成 PIL 图（用于黑白验收行）。"""
    svg = (SET / "svg" / f"{name}.svg").read_text(encoding="utf-8")
    svg = svg.replace("currentColor", color)
    tmp = SET / f".__sheet_{name}.svg"
    tmp.write_text(svg, encoding="utf-8")
    png = SET / f".__sheet_{name}.png"
    subprocess.run([RSVG, "-w", str(size), "-h", str(size), "-o", str(png), str(tmp)],
                   check=True)
    img = Image.open(png).convert("RGBA")
    tmp.unlink()
    png.unlink()
    return img


def main():
    meta = json.loads((SET / "icons.meta.json").read_text(encoding="utf-8"))
    names = list(meta.keys())

    f_title = font(CJK, 40, 1)
    f_sub = font(CJK, 20, 1)
    f_name = font(MONO, 19)
    f_cn = font(CJK, 22, 1)
    f_hex = font(MONO, 15)
    f_lbl = font(CJK, 18, 1)
    f_tiny = font(CJK, 15, 1)

    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    M = 56
    # ---------------------------------------------------------- 标题
    d.text((M, 38), "VIS-UI-001  核心 UI 图标样张 v001", font=f_title, fill=PAPER)
    d.text((M, 92),
           "24×24 设计栅格 · 统一笔宽 1.5 · round cap/join · stroke=currentColor · 无文字无商标",
           font=f_sub, fill=MUTED)
    d.line([(M, 128), (W - M, 128)], fill="#1E3A4C", width=2)

    # ---------------------------------------------------------- A 主展示 6x2
    cols, rows = 6, 2
    gw = W - 2 * M
    cw = gw // cols
    ch = 232
    top = 152
    for i, n in enumerate(names):
        r, c = divmod(i, cols)
        x0 = M + c * cw
        y0 = top + r * ch
        d.rounded_rectangle([x0 + 6, y0, x0 + cw - 10, y0 + ch - 18],
                            radius=12, fill=PANEL)
        ic = Image.open(SET / "png" / "96" / f"{n}.png").convert("RGBA")
        im.paste(ic, (x0 + (cw - 16) // 2 - 48 + 6, y0 + 26), ic)
        cx = x0 + (cw - 4) // 2
        d.text((cx, y0 + 136), meta[n]["cn"], font=f_cn, fill=PAPER, anchor="ma")
        d.text((cx, y0 + 166), n, font=f_name, fill=SUB, anchor="ma")
        d.text((cx, y0 + 190), f'{meta[n]["color"]}  {meta[n]["hex"]}',
               font=f_hex, fill=MUTED, anchor="ma")

    # ---------------------------------------------------------- B/C/D 验收带
    band_y = top + rows * ch + 16
    d.line([(M, band_y), (W - M, band_y)], fill="#1E3A4C", width=2)

    # B：24px 暗底原尺寸
    by = band_y + 26
    d.text((M, by), "B  24px 原尺寸 · 暗底（游戏内真实尺寸）", font=f_lbl, fill=SUB)
    sx = M + 400
    for i, n in enumerate(names):
        ic = Image.open(SET / "png" / "24" / f"{n}.png").convert("RGBA")
        im.paste(ic, (sx + i * 52, by - 2), ic)

    # C：24px 黑白（打印验收）
    cy = by + 52
    d.text((M, cy + 4), "C  24px 纯黑白 · 亮底（打印/无彩验收）", font=f_lbl, fill=SUB)
    strip_x = sx - 14
    d.rounded_rectangle([strip_x, cy - 6, strip_x + 12 * 52 + 12, cy + 46],
                        radius=8, fill=PAPER)
    for i, n in enumerate(names):
        ic = render_mono(n, 24, "#071018")
        im.paste(ic, (sx + i * 52, cy + 8), ic)

    # D：三尺寸对比
    dy = cy + 78
    d.text((M, dy + 30), "D  24 / 48 / 96 三尺寸缩放实测（抽样 4 枚）", font=f_lbl, fill=SUB)
    dx = sx
    for n in ["clue", "memory", "schedule", "locked"]:
        base = dx
        for s in (24, 48, 96):
            ic = Image.open(SET / "png" / str(s) / f"{n}.png").convert("RGBA")
            im.paste(ic, (dx, dy + 96 - s), ic)
            dx += s + 14
        d.text((base, dy + 104), n, font=f_tiny, fill=MUTED)
        dx += 46

    # 右下角签名
    d.text((W - M, H - 34),
           "《边境回声》素材工作区 · 生成于 2026-08-04 · tools/gen_ui_icons.py",
           font=f_tiny, fill="#3D5468", anchor="rs")

    im.save(OUT)
    print("sheet ->", OUT, im.size)


if __name__ == "__main__":
    main()
