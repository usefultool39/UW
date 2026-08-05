#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-POR-001 水印与孤立斑点移除。

策略：基于去背后的 alpha 做连通域分析，保留与最大主体相连的所有分量；
右下角远离主体的孤立分量（典型为水印文字）置 alpha=0。
"""

import numpy as np
from pathlib import Path
from PIL import Image
from scipy.ndimage import label

SRC = Path("/Users/lzm/Desktop/UW/materials/inbox/visual/portraits")


def clean(im):
    arr = np.asarray(im).copy()
    if arr.shape[2] == 3:
        return im
    rgb = arr[..., :3]
    alpha = arr[..., 3].copy()
    # 二值化：alpha > 200 视为前景
    binary = alpha > 180
    labels, n = label(binary)
    if n == 0:
        return im
    # 每个分量的像素数
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0  # 背景
    if len(sizes) <= 1:
        return im
    main_label = int(np.argmax(sizes))
    main_size = sizes[main_label]
    # 主体分量太小的兜底（理论上不会发生）
    if main_size < 100:
        return im
    # 选保留集合：主体 + 任何与主体 8 邻接的同连通分量（实际连通域本身已连通）
    # 这里再追加一个准则：分量质心与主体质心距离在合理范围，或者像素数 > 阈值
    main_pts = np.argwhere(labels == main_label)
    cy_main, cx_main = main_pts.mean(axis=0)
    new_alpha = np.where(labels == main_label, alpha, 0).astype(np.uint8)
    # 附加：分量像素数 < main_size * 0.15 且位于底部 25% 行内，置 0
    h, w = alpha.shape
    bottom_y = int(h * 0.75)
    right_x = int(w * 0.5)
    for lbl in range(1, n):
        if lbl == main_label:
            continue
        if sizes[lbl] < main_size * 0.15:
            pts = np.argwhere(labels == lbl)
            py = pts[:, 0].mean()
            px = pts[:, 1].mean()
            if py > bottom_y or px > right_x:
                new_alpha[labels == lbl] = 0
    out = Image.fromarray(np.concatenate([rgb, new_alpha[..., None]], axis=2), "RGBA")
    return out


def main():
    for p in sorted(SRC.glob("VIS-POR-001_*_v001.png")):
        im = Image.open(p).convert("RGBA")
        out = clean(im)
        # 比较移除前后
        before = np.asarray(im)[..., 3].sum()
        after = np.asarray(out)[..., 3].sum()
        removed = int((before - after) / 255)
        out.save(p)
        # 重生 256 缩略图
        thumb = out.resize((256, 256), Image.LANCZOS)
        thumb.save(SRC / f"{p.stem}_256.png")
        print(f"{p.name}: removed {removed} px")


if __name__ == "__main__":
    main()