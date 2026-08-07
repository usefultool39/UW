#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UW 预览合成图生成器
- 组合三个角色 sprite + tile atlas 预览
- 输出到 /tmp/preview.png
"""
from PIL import Image, ImageDraw, ImageFilter
import os
import math

CHAR_DIR = r"C:\Users\liang\Desktop\uw\materials\inbox\visual\characters"
WORLD_DIR = r"C:\Users\liang\Desktop\uw\materials\inbox\visual\world"
OUTPUT = r"C:\Users\liang\Desktop\uw\preview_composite.png"


def main():
    # Load sprite sheets
    sheets = {}
    for name in ["kirito", "alice", "eugeo"]:
        idx = {"kirito": 1, "alice": 2, "eugeo": 3}[name]
        path = os.path.join(CHAR_DIR, f"VIS-CHR-{idx:03d}_{name}_sprite_sheet_v008.png")
        sheets[name] = Image.open(path).convert("RGBA")

    # Load tile atlases
    tile_terrain = Image.open(os.path.join(WORLD_DIR, "VIS-MAP-001_terrain_tile_atlas_v006.png")).convert("RGBA")
    tile_water = Image.open(os.path.join(WORLD_DIR, "VIS-MAP-001_water_tile_atlas_v006.png")).convert("RGBA")
    tile_road = Image.open(os.path.join(WORLD_DIR, "VIS-MAP-001_road_tile_atlas_v006.png")).convert("RGBA")
    tile_veg = Image.open(os.path.join(WORLD_DIR, "VIS-MAP-001_vegetation_props_atlas_v006.png")).convert("RGBA")
    tile_bld = Image.open(os.path.join(WORLD_DIR, "VIS-MAP-001_buildings_props_atlas_v006.png")).convert("RGBA")

    # 输出尺寸
    W, H = 1600, 1000
    canvas = Image.new("RGBA", (W, H), (40, 55, 40, 255))  # 深绿底

    # === 1. 顶部：标题区 ===
    draw = ImageDraw.Draw(canvas)
    # 标题
    draw.rectangle([0, 0, W, 60], fill=(20, 30, 40, 255))
    draw.text((20, 18), "UW《边境回声》v008 Sprite + Tile/Prop Atlas Preview",
              fill=(255, 230, 180, 255))
    draw.text((20, 38), "0.5.0-pre-capture | Kirito / Alice / Eugeo + Rulid Village Tiles",
              fill=(180, 200, 220, 255))

    # === 2. 左侧：三个角色 down_walk 第 1 帧展示 ===
    char_x_start = 30
    char_y_start = 100
    char_scale = 2.5

    for i, name in enumerate(["kirito", "alice", "eugeo"]):
        sheet = sheets[name]
        # down_walk 帧 2（中间帧，最明显的走路姿态）
        # column_order: idle[0,1] + walk[0..5]，walk frame 2 = col 4
        walk_frame_col = 4  # walk[2]
        # row 0 = down
        frame = sheet.crop((walk_frame_col * 64, 0,
                            (walk_frame_col + 1) * 64, 96))
        frame_scaled = frame.resize((int(64 * char_scale), int(96 * char_scale)),
                                    Image.NEAREST)
        # 居中放置
        x = char_x_start + i * 200
        y = char_y_start
        # 角色名标签
        draw.rectangle([x, y + int(96 * char_scale) + 4,
                        x + int(64 * char_scale), y + int(96 * char_scale) + 24],
                       fill=(30, 40, 55, 220))
        labels = {"kirito": "kirito (深墨黑+冷蓝)", "alice": "alice (麦金+青蓝)",
                  "eugeo": "eugeo (冷蓝+木褐)"}
        draw.text((x + 6, y + int(96 * char_scale) + 8), labels[name],
                  fill=(220, 220, 200, 255))
        canvas.paste(frame_scaled, (x, y), frame_scaled)

    # === 3. 中部：角色 walk 6 帧序列展示 ===
    walk_y = 400
    draw.rectangle([0, walk_y - 30, W, walk_y - 10], fill=(30, 40, 55, 200))
    draw.text((20, walk_y - 22), "Walk 6-frame animation sequences (down direction)",
              fill=(200, 220, 240, 255))

    walk_frame_scale = 1.8
    walk_x = 30
    for char_i, name in enumerate(["kirito", "alice", "eugeo"]):
        sheet = sheets[name]
        # 角色标签
        draw.text((walk_x, walk_y + 130), name.capitalize(),
                  fill=(220, 200, 160, 255))
        for fi in range(6):  # walk frames 0..5 = col 2..7
            col = 2 + fi
            frame = sheet.crop((col * 64, 0, (col + 1) * 64, 96))
            frame_scaled = frame.resize((int(64 * walk_frame_scale),
                                         int(96 * walk_frame_scale)),
                                        Image.NEAREST)
            x = walk_x + fi * int(64 * walk_frame_scale)
            y = walk_y
            canvas.paste(frame_scaled, (x, y), frame_scaled)
        walk_x += int(64 * walk_frame_scale * 6) + 30

    # === 4. 右侧：tile atlas 缩略展示 ===
    tile_x = 1100
    tile_y = 100
    draw.text((tile_x, tile_y - 20), "Tile & Prop Atlases",
              fill=(200, 220, 240, 255))

    tile_items = [
        ("Terrain (4x4)", tile_terrain, 4),
        ("Water (4x2)", tile_water, 2),
        ("Roads (4x2)", tile_road, 2),
        ("Vegetation (4x4)", tile_veg, 4),
        ("Buildings (3x3)", tile_bld, 3),
    ]

    ty = tile_y
    for label, img, grid_cols in tile_items:
        # 缩略图尺寸
        scale = 0.7
        thumb_w = int(img.width * scale)
        thumb_h = int(img.height * scale)
        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        draw.text((tile_x, ty + thumb_h + 2), label,
                  fill=(180, 200, 220, 255))
        canvas.paste(thumb, (tile_x, ty), thumb)
        ty += thumb_h + 22

    # === 5. 底部：交付概要 ===
    footer_y = 750
    draw.rectangle([0, footer_y, W, H], fill=(15, 25, 35, 255))
    draw.text((20, footer_y + 10),
              "Delivery Summary (received only, NOT approved/integrated)",
              fill=(255, 220, 150, 255))
    summary = [
        "VIS-CHR-001/002/003 v008 — 3 sprite sheets (768x384 RGBA), 3 frames JSON (18001 B each), 3 sidecars, 3 manifests",
        "VIS-MAP-001 v006 tiles — terrain/water/roads/vegetation/buildings atlases + occlusion/foreground/lighting/weather + collision/walkable",
        "All files in materials/inbox/visual/{characters,world}/ with proper naming and SHA-256",
        "Tools: Python 3.13.12 + Pillow 12.3.0 procedural painterly generation; no external AI art; no franchise clones",
    ]
    for i, line in enumerate(summary):
        draw.text((20, footer_y + 40 + i * 22), "  " + line,
                  fill=(200, 210, 220, 255))

    # 保存
    canvas = canvas.convert("RGB")
    canvas.save(OUTPUT, "PNG")
    print(f"Preview saved to: {OUTPUT}")
    print(f"Size: {os.path.getsize(OUTPUT)} bytes")


if __name__ == "__main__":
    main()