#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-ENV-001 v003 场景背景生成器。

6 张 1920x1080 RGB PNG (无角色/无文字/无水印), 保留中下部互动区
+ 桌面/移动 crop-safe margins. 附 VIS-ENV-001_scenes_v003.json。
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(r"C:\Users\liang\Desktop\UW")
ENV_DIR = ROOT / "materials" / "inbox" / "visual" / "environments"
WORK_DIR = ENV_DIR / "_v003_work"

W, H = 1920, 1080


def vgrad(top: Tuple[int, int, int], bottom: Tuple[int, int, int], size=(W, H)) -> Image.Image:
    """垂直渐变 RGB 图。"""
    import numpy as np
    arr = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        arr[y, :, 0] = int(top[0] * (1 - t) + bottom[0] * t)
        arr[y, :, 1] = int(top[1] * (1 - t) + bottom[1] * t)
        arr[y, :, 2] = int(top[2] * (1 - t) + bottom[2] * t)
    return Image.fromarray(arr)


def new_image() -> Image.Image:
    return Image.new("RGB", (W, H), (0, 0, 0))


# ---------- 6 个场景 ----------

def env_church_library() -> Image.Image:
    """教堂书库/阅览室：木书架、暖色灯光、阅读桌。"""
    im = vgrad((195, 175, 150), (90, 70, 60))  # 暖色
    d = ImageDraw.Draw(im)
    # 远墙书架
    for x in range(0, W, 90):
        d.rectangle([x, 200, x + 80, 450], fill=(120, 80, 50))  # 书架
        for row in range(5):
            for col in range(4):
                bx = x + 6 + col * 18
                by = 210 + row * 50
                # 书本
                color = (200 - col * 10, 150 - row * 8, 80 + (col + row) * 5)
                d.rectangle([bx, by, bx + 14, by + 40], fill=color)
    # 拱形窗户在中央
    cx = W // 2
    d.polygon([
        (cx - 80, 100), (cx + 80, 100), (cx + 80, 220), (cx - 80, 220),
    ], fill=(200, 180, 100))
    d.line([(cx - 80, 220), (cx, 130), (cx + 80, 220)], fill=(160, 130, 80), width=2)
    # 桌椅
    d.rectangle([cx - 200, 650, cx + 200, 700], fill=(140, 95, 60))  # 桌面
    d.rectangle([cx - 195, 700, cx - 180, 850], fill=(100, 65, 40))  # 桌腿
    d.rectangle([cx + 180, 700, cx + 195, 850], fill=(100, 65, 40))
    # 桌面上的书
    d.rectangle([cx - 80, 640, cx + 80, 660], fill=(220, 210, 180))
    d.rectangle([cx - 60, 625, cx + 60, 640], fill=(200, 180, 140))
    # 蜡烛
    d.rectangle([cx - 8, 590, cx + 8, 640], fill=(245, 230, 200))
    # 火焰（暖色光）
    d.polygon([(cx - 6, 590), (cx + 6, 590), (cx, 560)], fill=(255, 200, 80))
    d.polygon([(cx - 4, 590), (cx + 4, 590), (cx, 570)], fill=(255, 240, 160))
    # 地面
    d.rectangle([0, 850, W, H], fill=(110, 80, 60))
    # 暖光
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - 350, 480, cx + 350, 800], fill=(255, 220, 120, 50))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    return im


def env_gigas_clearing() -> Image.Image:
    """古誓树清场：巨大的古树 + 草地 + 远山。"""
    im = vgrad((180, 210, 240), (160, 200, 150))  # 蓝天到草地
    d = ImageDraw.Draw(im)
    # 远山
    for i, off in enumerate([(-30, 80), (60, 100), (200, 90), (350, 110)]):
        d.polygon([
            (off[0], 350), (off[0] + 350, 200 + off[1]),
            (off[0] + 700, 350),
        ], fill=(120, 140, 130))
    # 远树
    for x in range(0, W, 60):
        h = 60 + (x * 7) % 30
        d.ellipse([x, 380 - h, x + 50, 380], fill=(60, 130, 80))
    # 草地
    d.rectangle([0, 500, W, H], fill=(110, 170, 90))
    # 古誓树（中央偏左）
    cx = W // 2
    base_y = 900
    # 树干
    d.rectangle([cx - 40, 500, cx + 40, base_y], fill=(110, 75, 50))
    # 树纹
    for y in range(500, base_y, 30):
        d.line([(cx - 40, y), (cx - 35, y + 15)], fill=(80, 50, 30), width=2)
    # 树冠
    d.ellipse([cx - 240, 220, cx + 240, 600], fill=(50, 130, 60))
    d.ellipse([cx - 200, 200, cx + 60, 380], fill=(70, 145, 75))
    d.ellipse([cx - 60, 180, cx + 200, 380], fill=(40, 120, 55))
    # 高光
    d.ellipse([cx - 100, 250, cx - 20, 290], fill=(120, 200, 130))
    # 树下散落木屑
    import random
    rng = random.Random(8001)
    for _ in range(30):
        sx = cx + rng.randint(-200, 200)
        sy = base_y - rng.randint(0, 30)
        d.ellipse([sx, sy, sx + 4, sy + 2], fill=(140, 100, 70))
    return im


def env_home_hearth() -> Image.Image:
    """家中炉火：木屋内部 + 炉火 + 木桌。"""
    im = vgrad((60, 45, 35), (100, 70, 50))  # 暗棕
    d = ImageDraw.Draw(im)
    # 木梁
    for x in range(0, W, 200):
        d.rectangle([x, 0, x + 30, 150], fill=(60, 40, 25))
    # 炉火在左
    fx, fy = 280, 700
    d.rectangle([fx - 100, fy, fx + 100, fy + 250], fill=(80, 50, 35))  # 壁炉框
    d.rectangle([fx - 80, fy + 20, fx + 80, fy + 220], fill=(30, 20, 15))  # 炉膛
    # 火焰
    for h in range(3):
        d.polygon([
            (fx - 40 + h * 5, fy + 200), (fx + 40 - h * 5, fy + 200),
            (fx + h * 3, fy + 80 + h * 10),
        ], fill=(255, 100 + h * 30, 30))
    d.polygon([
        (fx - 20, fy + 200), (fx + 20, fy + 200), (fx, fy + 130),
    ], fill=(255, 200, 100))
    # 木桌
    tx, ty = 1200, 750
    d.rectangle([tx - 200, ty, tx + 200, ty + 30], fill=(130, 85, 50))
    d.rectangle([tx - 180, ty + 30, tx - 160, ty + 200], fill=(90, 60, 35))
    d.rectangle([tx + 160, ty + 30, tx + 180, ty + 200], fill=(90, 60, 35))
    # 桌上面包
    d.ellipse([tx - 80, ty - 40, tx + 80, ty], fill=(200, 170, 120))
    d.ellipse([tx - 60, ty - 50, tx + 60, ty - 10], fill=(220, 190, 140))
    # 地面
    d.rectangle([0, 950, W, H], fill=(80, 55, 40))
    # 暖光
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([fx - 400, fy - 100, fx + 400, fy + 500], fill=(255, 130, 50, 70))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    return im


def env_north_gate() -> Image.Image:
    """北境边门：石门框 + 远山脉 + 雾墙。"""
    im = vgrad((100, 120, 140), (160, 175, 180))  # 灰冷调
    d = ImageDraw.Draw(im)
    # 远山脉（高耸）
    for i in range(5):
        x0 = i * 380 - 100
        d.polygon([
            (x0, 500), (x0 + 200, 200 - i * 10), (x0 + 400, 500),
        ], fill=(80, 90, 110))
    # 雾墙
    for x in range(0, W, 80):
        d.rectangle([x, 200, x + 80, 500], fill=(180, 190, 200))
    # 门框（中央）
    cx = W // 2
    d.rectangle([cx - 150, 350, cx + 150, 900], fill=(110, 105, 95))  # 门框
    d.rectangle([cx - 120, 380, cx + 120, 870], fill=(50, 45, 40))  # 门洞
    # 门洞内的雾
    d.rectangle([cx - 120, 380, cx + 120, 870], fill=(170, 180, 195))
    # 顶部装饰
    d.polygon([
        (cx - 150, 350), (cx + 150, 350), (cx, 280),
    ], fill=(130, 125, 110))
    d.line([(cx - 150, 350), (cx, 280), (cx + 150, 350)], fill=(80, 75, 65), width=3)
    # 边柱
    d.rectangle([cx - 180, 380, cx - 150, 900], fill=(90, 85, 75))
    d.rectangle([cx + 150, 380, cx + 180, 900], fill=(90, 85, 75))
    # 地面
    d.rectangle([0, 900, W, H], fill=(90, 90, 85))
    # 路径
    d.polygon([
        (cx - 80, 900), (cx + 80, 900), (cx + 250, H), (cx - 250, H),
    ], fill=(130, 130, 120))
    # 顶部天空飞过的鸟（极小）
    for x, y in [(400, 200), (600, 180), (1300, 200), (1500, 220)]:
        d.line([(x, y), (x + 4, y - 2), (x + 8, y)], fill=(60, 60, 70), width=1)
    return im


def env_forest_path() -> Image.Image:
    """森林路径：浓密树冠 + 远雾 + 细枝。"""
    im = vgrad((150, 165, 155), (90, 110, 80))  # 绿灰
    d = ImageDraw.Draw(im)
    # 远树
    for x in range(0, W, 40):
        h = 100 + (x * 13) % 80
        d.ellipse([x, 350 - h, x + 60, 380], fill=(40, 100, 50))
    # 树冠覆盖
    for x in range(0, W, 120):
        d.ellipse([x, 50, x + 200, 300], fill=(35, 90, 45))
    # 树干（前景）
    for x in [50, 250, 1700, 1880]:
        d.rectangle([x, 400, x + 30, 950], fill=(80, 50, 30))
    # 路径
    d.polygon([
        (W // 2 - 60, 950), (W // 2 + 60, 950),
        (W // 2 + 300, H), (W // 2 - 300, H),
    ], fill=(110, 95, 70))
    # 落叶
    import random
    rng = random.Random(8002)
    for _ in range(80):
        x = rng.randint(0, W)
        y = rng.randint(500, H)
        d.ellipse([x, y, x + 4, y + 2], fill=(120, 90, 50))
    # 远雾
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for x in range(0, W, 60):
        fd.ellipse([x, 250, x + 100, 400], fill=(180, 190, 170, 80))
    im = Image.alpha_composite(im.convert("RGBA"), fog).convert("RGB")
    return im


def env_end_mountains_cave() -> Image.Image:
    """终北山洞/边界入口：黑暗洞口 + 山石 + 远处微光。"""
    im = vgrad((60, 70, 80), (40, 50, 60))  # 深灰蓝
    d = ImageDraw.Draw(im)
    # 山石（两侧）
    for x in range(0, 400, 60):
        d.polygon([
            (x, 1000), (x + 60, 500 - (x * 5) % 200), (x + 120, 1000),
        ], fill=(70, 70, 75))
    for x in range(W - 400, W, 60):
        d.polygon([
            (x, 1000), (x + 60, 500 - ((x - W) * 5) % 200), (x + 120, 1000),
        ], fill=(70, 70, 75))
    # 洞口
    cx = W // 2
    d.polygon([
        (cx - 220, 950), (cx + 220, 950),
        (cx + 180, 350), (cx - 180, 350),
    ], fill=(20, 25, 30))
    # 洞内极深处微光
    d.ellipse([cx - 30, 700, cx + 30, 760], fill=(180, 200, 220))
    d.ellipse([cx - 50, 690, cx + 50, 770], fill=(60, 80, 100))
    # 洞口边框
    d.line([
        (cx - 220, 950), (cx - 180, 350),
        (cx + 180, 350), (cx + 220, 950),
    ], fill=(50, 50, 55), width=4)
    # 顶部远峰
    for i, off in enumerate([100, 600, 1100, 1600]):
        d.polygon([
            (off, 200), (off + 100, 100 - i * 5), (off + 200, 200),
        ], fill=(70, 75, 85))
    # 地面
    d.rectangle([0, 950, W, H], fill=(50, 55, 60))
    return im


# ---------- 主流程 ----------

SCENES = [
    ("church_library", "村西书库", "village west library / reading desk", env_church_library),
    ("gigas_clearing", "古誓树清场", "ancient gigas cedar clearing", env_gigas_clearing),
    ("home_hearth", "家中炉火", "village home interior with hearth", env_home_hearth),
    ("north_gate", "北境边门", "north boundary stone gate", env_north_gate),
    ("forest_path", "森林路径", "dense forest path with unnatural silence line",
     env_forest_path),
    ("end_mountains_cave", "终北山洞", "end-mountains cave / boundary approach",
     env_end_mountains_cave),
]


def main() -> None:
    ENV_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    scene_meta = []
    for sid, label_zh, label_en, fn in SCENES:
        print(f"Rendering {sid}...")
        im = fn()
        # save as RGB
        out = ENV_DIR / f"VIS-ENV-001_{sid}_v003.png"
        im.save(out, "PNG", optimize=True)
        print(f"  wrote: {out} ({out.stat().st_size} bytes)")
        scene_meta.append({
            "id": sid,
            "label_zh": label_zh,
            "label_en": label_en,
            "file": out.name,
            "size_px": {"w": W, "h": H},
            "mode": "RGB",
            "intended_use": "activity panel / chapter transition",
        })
    # 写 scenes JSON
    metadata = {
        "schema_version": "v003",
        "request_id": "VIS-ENV-001",
        "created_at": "2026-08-07",
        "scene_size_px": {"w": W, "h": H},
        "alpha_mode": "RGB (foreground overlay may be added separately as RGBA)",
        "scenes": scene_meta,
        "no_content": "characters, text, signs with words, UI, watermarks, copyrighted composition",
        "safe_areas": {
            "desktop_center_horizontal_pct": 60,
            "mobile_center_horizontal_pct": 80,
            "interactive_center_vertical_pct": 50,
            "note": "middle/lower interaction area preserved; desktop crop 16:9, mobile 390x844 9:19.5 retains center",
        },
    }
    json_path = ENV_DIR / "VIS-ENV-001_scenes_v003.json"
    json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {json_path}")


if __name__ == "__main__":
    main()
