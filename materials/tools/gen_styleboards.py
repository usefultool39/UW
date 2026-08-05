#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REF-STYLE-001 三套视觉方向板生成器。

每套输出 1920×1080 PNG：
  - 方向标题 + 一句话定义
  - 主色板（6 个色块 + HEX）
  - 三种光线缩略图（用于比较同一景在不同天气/时间下的读法）
  - 三人剪影/色块占位（仅色块比例，不画具体五官）
  - 六类材质示意（木纹/石/纸/水/金/天空）
  - 一个微型 UI 样张（按钮 + 文字）

全部程序化绘制，无外部图库；所见即可用作方向板/评审。"""

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path("/Users/lzm/Desktop/UW/materials")
OUT_DIR = ROOT / "inbox" / "visual" / "styleboards"
RSVG = "/opt/miniconda3/bin/rsvg-convert"
CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"

W, H = 1920, 1080


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def blend(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def gradient(im, y0, y1, c_top, c_bot, alpha=255):
    """从 y0 到 y1 绘制线性渐变（包含 alpha）。"""
    base = im.convert("RGBA")
    grad = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        col = (*blend(c_top, c_bot, t), alpha)
        for x in range(base.width):
            grad.putpixel((x, y), col)
    return Image.alpha_composite(base, grad)


def overlay(im, color, alpha):
    """整张图叠一层纯色。"""
    layer = Image.new("RGBA", im.size, (*hex_to_rgb(color), int(alpha * 255)))
    return Image.alpha_composite(im.convert("RGBA"), layer)


def noise_layer(size, color, density=0.06):
    """纸张颗粒/胶片颗粒层。"""
    import random
    n = Image.new("RGBA", size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(n)
    c = hex_to_rgb(color)
    for _ in range(int(size[0] * size[1] * density)):
        x, y = random.randint(0, size[0] - 1), random.randint(0, size[1] - 1)
        a = random.randint(8, 35)
        nd.point((x, y), fill=(*c, a))
    return n


def rounded_panel(d, bbox, radius, fill, outline=None, width=1):
    d.rounded_rectangle(bbox, radius=radius, fill=fill)
    if outline:
        d.rounded_rectangle(bbox, radius=radius, outline=outline, width=width)


# ============================================================ 三套方向定义
DIRECTIONS = {
    "A": {
        "name": "雨后初晴的北境秩序",
        "subtitle": "冷湿空气、清晰轮廓、旧纸张暖边。秩序感强，静默线是远处的低饱和边界。",
        "bg": ["#0A1822", "#132F40"],
        "palette": [
            ("ink-950", "#071018", "主背景"),
            ("paper-100", "#FFF7DF", "主文字/高光"),
            ("cyan-400", "#7DD3FC", "线索/地点"),
            ("slate-wet", "#5C7185", "湿润阴影"),
            ("drizzle", "#8FA3B2", "细雨天色"),
            ("gold-400", "#F6D36E", "目标/术式"),
        ],
        "thumb_theme": [
            ("晨雾广场", "#8FA3B2", "#C8D8E0", "#132F40"),
            ("雨后石板", "#5C7185", "#7DD3FC", "#071018"),
            ("黄昏溪边", "#F6D36E", "#A07C3C", "#102331"),
        ],
        "mats": [
            ("湿润石板", "#6B7D8C", "#3E4C58"),
            ("老木屋墙", "#6E5238", "#3B2B1E"),
            ("羊皮纸", "#E8DCC0", "#C4B492"),
            ("麦田", "#B89F56", "#7A652E"),
            ("溪水", "#7DD3FC", "#3E7A99"),
            ("雾空", "#8FA3B2", "#4A5C6A"),
        ],
    },
    "B": {
        "name": "旧书库与烛光律法",
        "subtitle": "暖纸、墨渍、烛光金黄、深影。权威来自记录本身，光是稀缺资源。",
        "bg": ["#180E08", "#2A1D12"],
        "palette": [
            ("archive-950", "#180E08", "最深背景"),
            ("paper-200", "#F2E6C7", "羊皮纸"),
            ("candle-400", "#F6C06E", "烛光"),
            ("ink-600", "#4A3726", "墨渍/阴影"),
            ("gold-500", "#C99A36", "金箔标题"),
            ("rose-700", "#7A2E2E", "警示/涂改"),
        ],
        "thumb_theme": [
            ("高窗烛光", "#F6C06E", "#4A3726", "#180E08"),
            ("堆叠卷轴", "#F2E6C7", "#C4B492", "#2A1D12"),
            ("墨渍旁注", "#7A2E2E", "#4A3726", "#180E08"),
        ],
        "mats": [
            ("旧羊皮纸", "#F2E6C7", "#C4B492"),
            ("蜂蜡封口", "#D4A55D", "#8C6A2F"),
            ("墨渍", "#4A3726", "#2A1D12"),
            ("烛光晕", "#F6C06E", "#A07226"),
            ("书架木", "#5A3E27", "#2E1E10"),
            ("金箔纹", "#C99A36", "#7A5318"),
        ],
    },
    "C": {
        "name": "静默线边界",
        "subtitle": "蓝紫夜色、金质异常、边界两侧的可见差异。情绪更冷，未知侵入已知。",
        "bg": ["#0B0A1A", "#1A1530"],
        "palette": [
            ("void-950", "#0B0A1A", "最深空"),
            ("violet-500", "#8B5CF6", "静默线"),
            ("paper-100", "#FFF7DF", "可读文字"),
            ("cyan-500", "#38BDF8", "正常侧"),
            ("gold-400", "#F6D36E", "异常节点"),
            ("teal-600", "#0F766E", "湿润暗部"),
        ],
        "thumb_theme": [
            ("边界树列", "#8B5CF6", "#0B0A1A", "#1A1530"),
            ("异常辉光", "#F6D36E", "#8B5CF6", "#0B0A1A"),
            ("溪水分界", "#38BDF8", "#8B5CF6", "#0B0A1A"),
        ],
        "mats": [
            ("暗水", "#1A2F45", "#0B1722"),
            ("蓝晶体", "#38BDF8", "#0F4C75"),
            ("金脉", "#F6D36E", "#9E731D"),
            ("紫雾", "#8B5CF6", "#3B257A"),
            ("冻土", "#3E4C5E", "#1F2832"),
            ("星光", "#E0E7FF", "#6366F1"),
        ],
    },
}


# ============================================================ 绘图函数
def draw_thumb(draw, bbox, title, c1, c2, c3, theme_type="village"):
    x0, y0, x1, y1 = bbox
    w, h = x1 - x0, y1 - y0
    # 背景渐变
    for y in range(y0, y1):
        t = (y - y0) / max(1, h)
        col = blend(hex_to_rgb(c2), hex_to_rgb(c3), t)
        draw.line([(x0, y), (x1 - 1, y)], fill=col, width=1)
    # 主题图形：简化的地面线 + 远景块
    ground = y0 + int(h * 0.72)
    draw.polygon([
        (x0, ground), (x0 + int(w * .18), ground - int(h * .22)),
        (x0 + int(w * .45), ground - int(h * .12)), (x1, ground - int(h * .28)),
        (x1, y1), (x0, y1)
    ], fill=c3)
    # 竖条树/书架/晶簇
    n_bars = 5
    for i in range(n_bars):
        bx = x0 + int(w * (0.12 + i * 0.16))
        bw = int(w * 0.06)
        bh = int(h * (0.25 + (i % 3) * 0.12))
        draw.rectangle([bx, ground - bh, bx + bw, ground], fill=c1)
    # 主体光/雾
    draw.ellipse([x0 + w * 0.55, y0 + h * 0.15, x0 + w * 0.85, y0 + h * 0.45],
                 fill=c1)


def draw_mat(draw, bbox, name, c1, c2):
    x0, y0, x1, y1 = bbox
    # 横纹/颗粒
    for y in range(y0, y1, 2):
        t = (y - y0) / max(1, y1 - y0)
        col = blend(hex_to_rgb(c1), hex_to_rgb(c2), t)
        draw.line([(x0, y), (x1, y)], fill=col, width=2)
    # 边框
    draw.rectangle([x0, y0, x1, y1], outline="#FFFFFF20", width=1)


def draw_silhouette(draw, cx, cy, h, color, shape="hood"):
    """三人占位剪影：仅头肩色块，无五官。"""
    rgb = hex_to_rgb(color)
    # 肩
    draw.polygon([
        (cx - h * .32, cy + h * .55), (cx + h * .32, cy + h * .55),
        (cx + h * .22, cy - h * .15), (cx - h * .22, cy - h * .15)
    ], fill=color)
    # 头
    r = h * .22
    draw.ellipse([cx - r, cy - h * .45 - r, cx + r, cy - h * .45 + r], fill=color)
    # 发型/兜帽差异：仅在边缘加高光提示
    if shape == "long":
        draw.polygon([
            (cx - r * .5, cy - h * .45 - r), (cx, cy - h * .9), (cx + r * .5, cy - h * .45 - r)
        ], fill=color)
    elif shape == "hood":
        draw.arc([cx - r * 1.2, cy - h * .7, cx + r * 1.2, cy - h * .1], start=180, end=360,
                 fill=color, width=int(r * .3))


def draw_ui_mockup(draw, bbox, theme):
    x0, y0, x1, y1 = bbox
    bg, accent, text = theme["bg"], theme["accent"], theme["text"]
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=bg, outline=accent, width=2)
    # 标题条
    draw.rounded_rectangle([x0 + 16, y0 + 16, x1 - 16, y0 + 44], radius=6,
                           fill=accent, outline=None)
    # 三行文本
    f = font(CJK, 16, 1)
    draw.text((x0 + 20, y0 + 54), "调查基加斯西达", font=f, fill=text)
    draw.line([(x0 + 20, y0 + 78), (x1 - 20, y0 + 78)], fill=accent, width=1)
    draw.text((x0 + 20, y0 + 86), "—— 体力 -1 · 时间 晨", font=f, fill=text)
    # 按钮
    draw.rounded_rectangle([x0 + 16, y1 - 42, x0 + 76, y1 - 14], radius=6, fill=accent)
    draw.text((x0 + 46, y1 - 28), "确认", font=f, fill=bg, anchor="mm")


def build_board(letter, D):
    im = Image.new("RGB", (W, H), D["bg"][0])
    draw = ImageDraw.Draw(im)

    # 背景渐变
    c0, c1 = hex_to_rgb(D["bg"][0]), hex_to_rgb(D["bg"][1])
    for y in range(H):
        col = blend(c0, c1, y / H)
        draw.line([(0, y), (W, y)], fill=col, width=1)

    # 整体纹理
    im = im.convert("RGBA")
    if letter == "B":
        im = Image.alpha_composite(im, noise_layer((W, H), "#F6C06E", 0.12))
    else:
        im = Image.alpha_composite(im, noise_layer((W, H), "#FFFFFF", 0.05))
    draw = ImageDraw.Draw(im)

    # 标题区
    f_letter = font(MONO, 120)
    f_title = font(CJK, 46, 1)
    f_sub = font(CJK, 20, 1)
    f_label = font(CJK, 16, 1)

    draw.text((64, 56), f"方向 {letter}", font=f_title, fill="#FFF7DF")
    draw.text((64, 110), D["name"], font=f_title, fill=D["palette"][2][1])
    draw.text((64, 168), D["subtitle"], font=f_sub, fill="#D9E3E8")

    # 色板
    px, py = 64, 248
    sw, sh = 104, 76
    gap = 24
    for i, (name, hexv, desc) in enumerate(D["palette"]):
        x = px + i * (sw + gap)
        draw.rounded_rectangle([x, py, x + sw, py + sh], radius=8, fill=hexv,
                               outline="#FFFFFF40", width=1)
        draw.text((x + 8, py + 84), name, font=f_label, fill="#D9E3E8")
        draw.text((x + 8, py + 104), hexv, font=f_label, fill="#8FA3B2")
        draw.text((x + 8, py + 122), desc, font=f_label, fill="#8FA3B2")

    # 三种光线缩略图
    tx, ty = 64, 420
    tw, th = 304, 180
    for i, (title, c1, c2, c3) in enumerate(D["thumb_theme"]):
        x = tx + i * (tw + 24)
        draw_thumb(draw, (x, ty, x + tw, ty + th), title, c1, c2, c3)
        draw.rounded_rectangle([x, ty, x + tw, ty + th], radius=10, outline="#FFFFFF30", width=1)
        draw.text((x + 12, ty + th + 12), title, font=f_label, fill="#D9E3E8")

    # 三人占位剪影
    sx, sy = 64, 660
    sil_h = 120
    roles = [
        ("桐人", "hood", D["palette"][3][1]),   # 中灰/中棕色，避免与背景融合
        ("爱丽丝", "long", D["palette"][2][1]), # 主题强调色
        ("尤吉欧", "hood", D["palette"][4][1]), # 暖金/次强调色
    ]
    for i, (label, shape, col) in enumerate(roles):
        cx = sx + i * 160 + 60
        draw_silhouette(draw, cx, sy, sil_h, col, shape)
        draw.text((cx, sy + sil_h * .7 + 16), label, font=f_label, fill="#D9E3E8", anchor="ma")

    # 材质
    mx, my = sx + 520, 660
    mw, mh = 118, 78
    for i, (mname, c1, c2) in enumerate(D["mats"]):
        row, col = divmod(i, 3)
        x = mx + col * (mw + 18)
        y = my + row * (mh + 46)
        draw_mat(draw, (x, y, x + mw, y + mh), mname, c1, c2)
        draw.text((x, y + mh + 8), mname, font=f_label, fill="#D9E3E8")

    # 微型 UI 样张
    ux, uy = W - 420, 660
    ui_theme = {
        "bg": D["palette"][0][1],
        "accent": D["palette"][2][1],
        "text": D["palette"][1][1],
    }
    draw_ui_mockup(draw, (ux, uy, ux + 356, uy + 196), ui_theme)

    # 页脚
    draw.text((W - 64, H - 40),
              "REF-STYLE-001 视觉方向板 v001 · 2026-08-04 · 程序化绘制",
              font=f_label, fill="#5C7185", anchor="rs")

    return im.convert("RGB")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for letter, D in DIRECTIONS.items():
        im = build_board(letter, D)
        out = OUT_DIR / f"REF-STYLE-001_direction_{letter}_v001.png"
        im.save(out, quality=95)
        print("saved", out)


if __name__ == "__main__":
    main()
