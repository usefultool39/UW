#!/usr/bin/env python3
"""
vfx v001 assembler: 拼合 4 帧到 1024x256 sheet (1x4 grid)，并做白底 knockout。
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

CELL = 256
WHITE_SUM_MAX = 700

HERE = Path(__file__).parent


def _strip_white(img):
    src = img.convert("RGBA").copy()
    px = src.load()
    w, h = src.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r + g + b > WHITE_SUM_MAX:
                px[x, y] = (r, g, b, 0)
    return src


def build_sheet(prefix: str, out_name: str) -> dict:
    sheet = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
    stats = []
    for i in range(4):
        src = Image.open(HERE / f"{prefix}_{i}.png").convert("RGBA")
        cut = _strip_white(src)
        cell = cut.resize((CELL, CELL), Image.LANCZOS)
        sheet.alpha_composite(cell, dest=(i * CELL, 0))
        stats.append({"frame": i, "src": f"{prefix}_{i}.png", "size": list(src.size)})
    out = HERE / out_name
    sheet.save(out, optimize=True)
    out_json = HERE / out_name.replace(".png", ".assemble.json")
    out_json.write_text(json.dumps({"sheet": out_name, "size": list(sheet.size), "frames": stats}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"sheet": str(out), "json": str(out_json), "stats": stats}


for prefix, out_name in [
    ("holy_arts", "VIS-VFX-001_holy_arts_v001.png"),
    ("silence_line", "VIS-VFX-001_silence_line_v001.png"),
]:
    info = build_sheet(prefix, out_name)
    print(f"built {info['sheet']} ({info['stats']})")
