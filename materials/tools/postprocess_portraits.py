#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-POR-001 肖像后处理：去背景（渐变背景模型）+ 256px 缩略图 + 规范命名。

背景模型：用四角颜色做双线性插值估计每个像素的背景色，
alpha = 1 - smoothstep(dist, t0, t1)；随后轻微羽化。
"""

import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

SRC = Path("/Users/lzm/Desktop/UW/materials/inbox/visual/portraits")
T0, T1 = 18, 60  # 距离阈值（欧氏距离，0-255 空间）


def remove_bg(im):
    rgb = np.asarray(im.convert("RGB")).astype(np.float64)
    h, w, _ = rgb.shape
    # 四角背景色
    c = {
        "tl": rgb[2, 2], "tr": rgb[2, w - 3],
        "bl": rgb[h - 3, 2], "br": rgb[h - 3, w - 3],
    }
    ys, xs = np.mgrid[0:h, 0:w]
    ty = ys / max(1, h - 1)
    tx = xs / max(1, w - 1)
    # 双线性插值
    top = c["tl"][None, None, :] * (1 - tx[..., None]) + c["tr"][None, None, :] * tx[..., None]
    bot = c["bl"][None, None, :] * (1 - tx[..., None]) + c["br"][None, None, :] * tx[..., None]
    bg = top * (1 - ty[..., None]) + bot * ty[..., None]
    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    # smoothstep 过渡
    t = np.clip((dist - T0) / max(1, T1 - T0), 0, 1)
    alpha = t * t * (3 - 2 * t)
    a8 = (alpha * 255).astype(np.uint8)
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray(a8, "L").filter(ImageFilter.GaussianBlur(0.8)))
    return out


def main():
    # 规范命名
    mapping = {
        "Portrait_of_a_young_man_with_s_2026-08-04T14-48-03.png": "VIS-POR-001_kirito_resolved_v001",
        "Portrait_of_a_young_woman_with_2026-08-04T14-48-04.png": "VIS-POR-001_alice_neutral_v001",
        "calm_neutral_portrait__a_teena_2026-08-04T14-48-49.png": "VIS-POR-001_kirito_neutral_v001",
        "warm_gentle_smile_portrait__a__2026-08-04T14-49-18.png": "VIS-POR-001_alice_warm_v001",
        "gentle_neutral_portrait__a_tee_2026-08-04T14-49-18.png": "VIS-POR-001_eugeo_neutral_v001",
        "concerned_worried_portrait__a__2026-08-04T14-49-18.png": "VIS-POR-001_eugeo_concerned_v001",
    }
    for src, stem in mapping.items():
        p = SRC / src
        if not p.exists():
            print("MISSING:", src)
            continue
        im = Image.open(p)
        out = remove_bg(im)
        # 透明版本
        out.save(SRC / f"{stem}.png")
        # 256 缩略图（透明+半透明棋盘底可另存，这里只存透明版）
        thumb = out.resize((256, 256), Image.LANCZOS)
        thumb.save(SRC / f"{stem}_256.png")
        print("OK", stem)
        p.unlink()  # 删除自动命名原文件


if __name__ == "__main__":
    main()
