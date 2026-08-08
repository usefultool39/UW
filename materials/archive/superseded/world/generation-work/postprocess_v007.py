#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIS-MAP-001 v007 map post-processor.

- Takes the raw 1280x720 ImageGen output.
- Stamps out the system watermark in the bottom-right with synthesized forest tone.
- Upscales to the runtime master size 3024x1792 using LANCZOS.
- Emits 1440x900 desktop and 390x844 mobile previews.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = Path("/Users/lzm/Desktop/UW/materials/inbox/visual/world/v007")
SRC = BASE_DIR / "Original_hand_painted_2D_game__2026-08-07T17-44-18.png"
MASTER_OUT = BASE_DIR / "VIS-MAP-001_rulid_village_master_v007_sample.png"
PREVIEW_DESKTOP_OUT = BASE_DIR / "VIS-MAP-001_rulid_village_master_v007_preview_1440x900.png"
PREVIEW_MOBILE_OUT = BASE_DIR / "VIS-MAP-001_rulid_village_master_v007_preview_390x844.png"


def sample_forest_tone(img: Image.Image, sample_box: tuple) -> tuple:
    """Return average RGB of the source sample box."""
    region = img.crop(sample_box).convert("RGB")
    pixels = list(region.getdata())
    n = len(pixels)
    r = sum(p[0] for p in pixels) // n
    g = sum(p[1] for p in pixels) // n
    b = sum(p[2] for p in pixels) // n
    return r, g, b


def stamp_watermark(img: Image.Image) -> Image.Image:
    """
    Cover the system watermark (lower-right) by averaging four forest patches
    onto the watermark box with a radial alpha falloff. The result reads as
    a soft painterly forest fade rather than a hard rectangle.
    """
    w, h = img.size
    wm_box = (int(w * 0.795), int(h * 0.905), int(w * 0.985), int(h * 0.985))
    bw = wm_box[2] - wm_box[0]
    bh = wm_box[3] - wm_box[1]

    # Sample four forest patches
    patches = [
        img.crop((int(w * 0.05), int(h * 0.05), int(w * 0.40), int(h * 0.40))),
        img.crop((int(w * 0.60), int(h * 0.05), int(w * 0.95), int(h * 0.40))),
        img.crop((int(w * 0.05), int(h * 0.45), int(w * 0.40), int(h * 0.85))),
        img.crop((int(w * 0.60), int(h * 0.45), int(w * 0.95), int(h * 0.85))),
    ]

    import random
    rnd = random.Random(7001)
    pieces = []
    for patch in patches:
        resized = patch.convert("RGB").resize((bw, bh), Image.LANCZOS)
        px = resized.load()
        for y in range(bh):
            for x in range(bw):
                r, g, b = px[x, y]
                j = rnd.randint(-10, 10)
                px[x, y] = (
                    max(0, min(255, r + j)),
                    max(0, min(255, g + j)),
                    max(0, min(255, b + j)),
                )
        pieces.append(resized)

    avg = Image.new("RGB", (bw, bh))
    avg_px = avg.load()
    for y in range(bh):
        for x in range(bw):
            rs = gs = bs = 0
            for p in pieces:
                pr, pg, pb = p.getpixel((x, y))
                rs += pr
                gs += pg
                bs += pb
            n = len(pieces)
            avg_px[x, y] = (rs // n, gs // n, bs // n)

    # Build a radial alpha mask so the stamp fades smoothly into the surroundings
    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    cx, cy = bw // 2, bh // 2
    maxr = int((bw + bh) * 0.45)
    for r in range(maxr, 0, -1):
        t = 1 - (r / maxr)
        alpha = int(220 * (t ** 1.6))
        md.ellipse((cx - r, cy - r, cx + r, cy + r), outline=alpha, width=1)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=4))

    img = img.convert("RGB")
    img.paste(avg, (wm_box[0], wm_box[1]), mask)

    # Wide feather over the entire right-lower edge so the stamp boundary
    # dissolves into the surrounding forest.
    seam_mask = Image.new("L", img.size, 0)
    sd = ImageDraw.Draw(seam_mask)
    sd.rectangle((wm_box[0] - 32, wm_box[1] - 32, wm_box[2] + 32, wm_box[3] + 32), fill=180)
    seam_mask = seam_mask.filter(ImageFilter.GaussianBlur(radius=10))
    blurred = img.filter(ImageFilter.GaussianBlur(radius=3.5))
    img.paste(blurred, (0, 0), seam_mask)
    return img


def upscale_to_master(src_img: Image.Image, target=(3024, 1792)) -> Image.Image:
    return src_img.resize(target, Image.LANCZOS)


def make_desktop_preview(master: Image.Image, target=(1440, 900)) -> Image.Image:
    """Letterbox-fit master into a 1440x900 canvas without cropping the map."""
    mw, mh = master.size
    tw, th = target
    scale = min(tw / mw, th / mh)
    nw, nh = int(mw * scale), int(mh * scale)
    fit = master.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", target, (24, 32, 40))
    canvas.paste(fit, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def make_mobile_preview(master: Image.Image, target=(390, 844)) -> Image.Image:
    """
    For a 390x844 mobile preview we need a vertical slice. We crop the
    central vertical strip (north gate -> south bridge) and resize to fit.
    """
    mw, mh = master.size
    # Vertical strip ~50% width centered
    strip_w = int(mw * 0.50)
    strip_x = (mw - strip_w) // 2
    strip = master.crop((strip_x, 0, strip_x + strip_w, mh))
    sw, sh = strip.size
    tw, th = target
    scale = min(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    fit = strip.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", target, (24, 32, 40))
    canvas.paste(fit, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    if not SRC.exists():
        print(f"missing source: {SRC}", file=sys.stderr)
        return 1

    raw = Image.open(SRC)
    print(f"source: {SRC.name} {raw.size}")

    cleaned = stamp_watermark(raw)

    # Save intermediate cleaned version for trace
    cleaned_path = BASE_DIR / "_intermediate_cleaned_1280x720.png"
    cleaned.save(cleaned_path, format="PNG")

    master = upscale_to_master(cleaned, (3024, 1792))
    master.save(MASTER_OUT, format="PNG", optimize=False)
    print(f"master: {MASTER_OUT.name} {master.size}")

    desktop = make_desktop_preview(master, (1440, 900))
    desktop.save(PREVIEW_DESKTOP_OUT, format="PNG", optimize=False)
    print(f"desktop preview: {PREVIEW_DESKTOP_OUT.name} {desktop.size}")

    mobile = make_mobile_preview(master, (390, 844))
    mobile.save(PREVIEW_MOBILE_OUT, format="PNG", optimize=False)
    print(f"mobile preview: {PREVIEW_MOBILE_OUT.name} {mobile.size}")

    summary = {
        "source": SRC.name,
        "intermediate_cleaned": cleaned_path.name,
        "master": {
            "path": MASTER_OUT.name,
            "size": list(master.size),
            "sha256": sha256(MASTER_OUT),
        },
        "desktop_preview": {
            "path": PREVIEW_DESKTOP_OUT.name,
            "size": list(desktop.size),
            "sha256": sha256(PREVIEW_DESKTOP_OUT),
        },
        "mobile_preview": {
            "path": PREVIEW_MOBILE_OUT.name,
            "size": list(mobile.size),
            "sha256": sha256(PREVIEW_MOBILE_OUT),
        },
    }
    (BASE_DIR / "VIS-MAP-001_v007_postprocess_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())