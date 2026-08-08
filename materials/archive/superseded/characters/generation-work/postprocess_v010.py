#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIS-CHR-001/002/003 v010 sprite post-processor.

Pipeline per frame:
  1. Load raw ImageGen RGB output (typically 832x1216).
  2. Detect the light/dark gray checker background and convert to alpha=0.
  3. Find the character's bounding box using the alpha mask.
  4. Crop to character with a small bottom margin.
  5. Pad / position into a 64x96 cell with the foot anchored at (32, 94).
  6. LANCZOS resize preserving aspect.
  7. Stack into a 768x96 RGBA sprite sheet.

Also emits:
  - frame_metadata.json for the three characters.
  - 1440x900 desktop preview and 390x844 mobile preview showing all three
    characters lined up on a neutral dark backdrop.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np

CELL_W, CELL_H = 64, 96
SHEET_W = CELL_W * 12
SHEET_H = CELL_H
ANCHOR_X, ANCHOR_Y = 32, 94  # bottom-center for 64x96 cell

BASE_DIR = Path("/Users/lzm/Desktop/UW/materials/inbox/visual/characters/v010")
FRAMES_DIR = BASE_DIR / "_frames"


def rgba_from_rgb_checker(rgb_img: Image.Image) -> Image.Image:
    """Convert RGB checker background to RGBA transparent."""
    arr = np.array(rgb_img.convert("RGB")).astype(np.int16)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # How "gray" is the pixel? (low spread = gray)
    spread = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)
    brightness = (r + g + b) // 3

    # alpha = 255 if clearly non-gray
    # alpha = 0 if clearly the light/dark gray checker background
    # alpha = partial for the small gradient at the edge between checker and character
    alpha = np.full_like(r, 255, dtype=np.uint8)

    # Light checker background (252/255): definitely transparent
    light_mask = (spread <= 6) & (brightness >= 235)
    # Dark checker background (~199): definitely transparent
    dark_mask = (spread <= 6) & (brightness >= 188) & (brightness <= 215)
    bg_mask = light_mask | dark_mask

    # For pixels that are partially gray (edge between bg and character),
    # alpha = clamp((spread / 6) * 255, 0..255). That way edge pixels
    # gain real alpha only if they actually pick up character color.
    edge_mask = (spread > 6) & (spread <= 22) & (brightness >= 160)
    # Anything that strongly looks like skin shadow inside the character
    # (low brightness AND very neutral) might still be unwanted shadow.
    # We do NOT kill it here to preserve shading; let post-validate flag it.

    # Final alpha
    alpha[bg_mask] = 0
    # For edge pixels, scale alpha by how non-gray they are
    alpha[edge_mask] = np.clip(((spread[edge_mask] - 6) / 16.0) * 255, 0, 255).astype(np.uint8)

    rgba = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(rgba, mode="RGBA")


def find_character_bbox(rgba: Image.Image) -> tuple:
    """Return (x0, y0, x1, y1) of non-transparent pixels with margin."""
    arr = np.array(rgba)
    alpha = arr[..., 3]
    ys, xs = np.where(alpha > 0)
    if len(xs) == 0:
        # No character found - return center crop as fallback
        w, h = rgba.size
        return (w // 2 - 1, h // 2 - 1, w // 2 + 1, h // 2 + 1)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    # Add a 2px margin
    x0 = max(0, x0 - 2)
    y0 = max(0, y0 - 2)
    x1 = min(rgba.size[0] - 1, x1 + 2)
    y1 = min(rgba.size[1] - 1, y1 + 2)
    return (x0, y0, x1, y1)


def fit_into_cell(crop: Image.Image, cell_size=(CELL_W, CELL_H)) -> Image.Image:
    """
    Fit the cropped character into a 64x96 cell, anchoring the bottom-center
    of the character bounding box to (32, 94).
    """
    cw, ch = cell_size
    crop = crop.convert("RGBA")

    src_w, src_h = crop.size
    # We want character bottom (y = src_h - 1) to land on y = ANCHOR_Y in the cell.
    # Scale so that the character height fills ~88 of 96 vertical pixels (leave
    # a small headroom + foot margin).
    target_h = 88  # pixels of the cell the body occupies
    scale = target_h / src_h
    nw = max(1, int(round(src_w * scale)))
    nh = max(1, int(round(src_h * scale)))
    resized = crop.resize((nw, nh), Image.LANCZOS)

    # Compose into cell with alpha
    cell = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # x: center
    px = (cw - nw) // 2
    # y: anchor the resized character's bottom edge at ANCHOR_Y (94)
    py = ANCHOR_Y + 1 - nh
    # Clip top if necessary
    if py < 0:
        # Bottom clip, but we never want to clip the feet; if the head is too
        # tall, we accept some head clipping at the top.
        py = 0
    cell.alpha_composite(resized, (px, py))
    return cell


def assemble_sheet(cells: list) -> Image.Image:
    """Stack 12 cells horizontally into a 768x96 sheet."""
    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    for i, cell in enumerate(cells):
        sheet.alpha_composite(cell, (i * CELL_W, 0))
    return sheet


def process_frame(raw_path: Path) -> Image.Image:
    """Full pipeline: load → alpha → crop → fit to cell."""
    raw = Image.open(raw_path)
    rgba = rgba_from_rgb_checker(raw)
    bbox = find_character_bbox(rgba)
    cropped = rgba.crop(bbox)
    cell = fit_into_cell(cropped)
    return cell


def validate_alpha(cell: Image.Image, name: str) -> list:
    """Return a list of issues detected for a single cell."""
    issues = []
    arr = np.array(cell)
    h, w = arr.shape[:2]

    # Check corners
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for cx, cy in corners:
        if arr[cy, cx, 3] != 0:
            issues.append(f"{name}: corner ({cx},{cy}) alpha={arr[cy, cx, 3]} != 0")

    # Check anchor point is transparent (foot area)
    if arr[ANCHOR_Y, ANCHOR_X, 3] != 0:
        issues.append(f"{name}: anchor ({ANCHOR_X},{ANCHOR_Y}) alpha={arr[ANCHOR_Y, ANCHOR_X, 3]} != 0")

    # Check there is at least some character content
    total_alpha = int(arr[..., 3].sum())
    if total_alpha < 1000:
        issues.append(f"{name}: total_alpha={total_alpha}, character may be empty")

    return issues


def character_frames(character: str) -> list:
    """Return the 12 raw frame paths for a character in order: idle0, idle1,
    walk0..walk5, interact0..interact3."""
    frames = []
    fdir = FRAMES_DIR / character
    names = (
        [f"idle_{i}" for i in range(2)]
        + [f"walk_{i}" for i in range(6)]
        + [f"interact_{i}" for i in range(4)]
    )
    for name in names:
        # The actual filenames are tool-named; we look up the most recent
        # file matching the prompt slug.
        matches = sorted(fdir.glob(f"*{name}*.png"))
        if not matches:
            # Fallback: pick the n-th file by prompt order
            pngs = sorted(fdir.glob("*.png"))
            if len(pngs) >= 12:
                idx = names.index(name)
                frames.append(pngs[idx])
            else:
                frames.append(None)
        else:
            frames.append(matches[-1])
    return frames


def process_character(character: str, request_id: str) -> dict:
    raw_frames = character_frames(character)
    cells = []
    issues_all = []
    frame_meta = []
    for i, raw_path in enumerate(raw_frames):
        if raw_path is None:
            issues_all.append(f"frame {i}: missing raw source")
            cells.append(Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0)))
            frame_meta.append({"index": i, "source": None, "status": "missing"})
            continue
        try:
            cell = process_frame(raw_path)
        except Exception as exc:
            issues_all.append(f"frame {i} ({raw_path.name}): {exc}")
            cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
            frame_meta.append({"index": i, "source": raw_path.name, "status": "error"})
            continue
        issues = validate_alpha(cell, f"frame{i}")
        if issues:
            issues_all.extend(issues)
        cells.append(cell)
        frame_meta.append({
            "index": i,
            "source": raw_path.name,
            "status": "ok" if not issues else "issues",
            "issues": issues,
        })

    sheet = assemble_sheet(cells)

    out_dir = BASE_DIR
    sheet_path = out_dir / f"VIS-CHR-{request_id[-3:]}_sprite_sheet_v010_down_sample.png"
    sheet.save(sheet_path, format="PNG", optimize=False)

    # Compose preview at 1440x900 (3 rows: kirito / alice / eugeo)
    preview_desktop = make_desktop_preview_single(sheet, (1440, 900), label=character)
    preview_desktop_path = out_dir / f"VIS-CHR-{request_id[-3:]}_v010_sample_1440x900.png"
    preview_desktop.save(preview_desktop_path, format="PNG", optimize=False)

    preview_mobile = make_mobile_preview_single(sheet, (390, 844))
    preview_mobile_path = out_dir / f"VIS-CHR-{request_id[-3:]}_v010_sample_mobile_390x844.png"
    preview_mobile.save(preview_mobile_path, format="PNG", optimize=False)

    metadata = {
        "request_id": request_id,
        "character": character,
        "sheet_path": sheet_path.name,
        "sheet_size": list(sheet.size),
        "cell_size": [CELL_W, CELL_H],
        "anchor": [ANCHOR_X, ANCHOR_Y],
        "frames": frame_meta,
        "issues": issues_all,
        "color_mode": "RGBA",
        "alpha": True,
        "frame_count": len(cells),
        "preview_desktop": preview_desktop_path.name,
        "preview_mobile": preview_mobile_path.name,
    }
    return metadata


def make_desktop_preview_single(sheet: Image.Image, target=(1440, 900), label: str = "") -> Image.Image:
    """Render the sheet at scale 6x on a neutral dark backdrop, with caption."""
    sw, sh = sheet.size
    scale = 6
    nw, nh = sw * scale, sh * scale
    big = sheet.resize((nw, nh), Image.NEAREST)
    canvas = Image.new("RGB", target, (24, 32, 40))
    canvas.paste(big, ((target[0] - nw) // 2, (target[1] - nh) // 2 // 2))
    return canvas


def make_mobile_preview_single(sheet: Image.Image, target=(390, 844)) -> Image.Image:
    """Render the sheet at scale 4x vertically scrollable on mobile."""
    sw, sh = sheet.size
    scale = 4
    nw, nh = sw * scale, sh * scale
    big = sheet.resize((nw, nh), Image.NEAREST)
    canvas = Image.new("RGB", target, (24, 32, 40))
    canvas.paste(big, ((target[0] - nw) // 2, (target[1] - nh) // 2))
    return canvas


def main() -> int:
    results = {}
    chars = [
        ("kirito", "VIS-CHR-001"),
        ("alice", "VIS-CHR-002"),
        ("eugeo", "VIS-CHR-003"),
    ]
    for character, request_id in chars:
        print(f"\n=== processing {character} ({request_id}) ===")
        meta = process_character(character, request_id)
        results[request_id] = meta
        print(f"  sheet: {meta['sheet_path']}")
        print(f"  frames: {meta['frame_count']}")
        if meta["issues"]:
            print(f"  ISSUES ({len(meta['issues'])}):")
            for iss in meta["issues"][:10]:
                print(f"    - {iss}")

    out_path = BASE_DIR / "VIS-CHR-001_002_003_v010_frame_metadata.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nmetadata written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())