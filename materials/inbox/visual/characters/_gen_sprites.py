"""
VIS-CHR-001/002/003 UW-UPGRADE-1.0 Character Sprite Sheet Generator
Creates 48-frame sprite sheets (4 directions x 12 frames) for each character.
Cell: 64x96, RGBA, bottom-center anchor.
"""
import hashlib, json, os, csv, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageOps

random.seed(42)

CELL_W, CELL_H = 64, 96
DIRS = ["down", "left", "right", "up"]
ANIMS = {"idle": 2, "walk": 6, "interact": 4}
FRAMES_PER_DIR = sum(ANIMS.values())  # 12
TOTAL_FRAMES = FRAMES_PER_DIR * len(DIRS)  # 48

# Sheet layout: 12 columns x 4 rows
SHEET_COLS = FRAMES_PER_DIR  # 12
SHEET_ROWS = len(DIRS)       # 4

CHARACTERS = [
    {
        "request_id": "VIS-CHR-001",
        "name": "kirito",
        "src": "Pixel_art_RPG_character_sprite_2026-08-07T09-59-52.png",
        "desc": "Kirito - young boy, black hair, dark navy village worker outfit",
        "interact_desc": "record, point, crouch_observe, reach_stop"
    },
    {
        "request_id": "VIS-CHR-002",
        "name": "alice",
        "src": "Pixel_art_RPG_character_sprite_2026-08-07T10-00-20.png",
        "desc": "Alice - young girl, wheat-golden hair, cream village dress",
        "interact_desc": "hand_item, basic_aid, check_record, farewell_look"
    },
    {
        "request_id": "VIS-CHR-003",
        "name": "eugeo",
        "src": "Pixel_art_RPG_character_sprite_2026-08-07T10-00-47.png",
        "desc": "Eugeo - young boy, light brown hair, cold blue-grey worker outfit",
        "interact_desc": "axe_ready,协作_hand_item, check_route, protective_stance"
    }
]

def load_and_fit_character(src_path):
    """Load character image, crop to content, fit into 64x96 cell"""
    img = Image.open(src_path).convert("RGBA")

    # Find bounding box of non-transparent content
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # Resize to fit within cell while maintaining aspect ratio
    w, h = img.size
    scale = min(CELL_W / w, CELL_H / h, 1.0)
    # Don't upscale too much; aim for character to be about 80% of cell height
    target_h = int(CELL_H * 0.82)
    target_w = int(w * (target_h / h))
    if target_w > CELL_W:
        target_w = CELL_W
        target_h = int(h * (target_w / w))
    img = img.resize((target_w, target_h), Image.LANCZOS)

    # Create cell with bottom-center alignment
    cell = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    x = (CELL_W - target_w) // 2
    y = CELL_H - target_h
    cell.paste(img, (x, y), img)

    return cell

def create_back_view(cell):
    """Create a back view by flipping vertically and covering face with hair color"""
    back = cell.copy()
    # Flip vertically for approximate back view
    back = ImageOps.flip(back)
    # Actually, for a proper back view, we should just use the original
    # but cover the face area. Let's use a different approach:
    # Keep the body, replace the head area with a solid color
    back = cell.copy()
    # Cover face area (top ~25% of character) with a darkened version
    overlay = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # Cover face region
    head_h = int(CELL_H * 0.22)
    draw.rectangle([8, 4, CELL_W-8, head_h], fill=(0, 0, 0, 0))
    # Blend - actually just darken the top portion
    darkened = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
    top_part = cell.crop((0, 0, CELL_W, head_h + 5))
    # Darken it
    darker = ImageOps.colorize(top_part.convert("L"), (30, 25, 20), (200, 180, 150))
    darker = darker.convert("RGBA")
    # Copy alpha from original
    for y in range(head_h + 5):
        for x in range(CELL_W):
            a = top_part.getpixel((x, y))[3]
            if a > 0:
                darker.putpixel((x, y), darker.getpixel((x, y))[:3] + (a,))
    darkened.paste(darker, (0, 0))
    # Combine: darkened head + original body
    back = cell.copy()
    back.paste(darkened, (0, 0), darkened)
    return back

def create_idle_frames(base_cell, count=2):
    """Create idle frames with subtle breathing"""
    frames = []
    for i in range(count):
        frame = base_cell.copy()
        if i == 1:
            # Slight vertical compression for breathing
            w, h = frame.size
            compressed = frame.resize((w, h-1), Image.LANCZOS)
            new_frame = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
            new_frame.paste(compressed, (0, 1), compressed)
            frame = new_frame
        frames.append(frame)
    return frames

def create_walk_frames(base_cell, count=6):
    """Create walk cycle frames with leg and arm movement"""
    frames = []
    w, h = CELL_W, CELL_H

    # Walk cycle phases
    # Frame 0: right foot forward, left arm forward
    # Frame 1: mid-step (feet together)
    # Frame 2: left foot forward, right arm forward
    # Frame 3: mid-step (feet together, opposite)
    # Frame 4: right foot forward (more extreme)
    # Frame 5: neutral

    for i in range(count):
        frame = base_cell.copy()

        # Calculate phase
        phase = (i / count) * 2 * math.pi

        # Leg shift: shift bottom portion left/right
        leg_shift = int(math.sin(phase) * 3)
        # Arm shift: opposite direction
        arm_shift = -int(math.sin(phase) * 2)
        # Vertical bob
        bob = int(abs(math.sin(phase * 2)) * 2)

        # Create shifted version
        shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        # Split character into upper and lower body
        body_split = int(h * 0.55)

        # Upper body (slight arm movement + bob)
        upper = base_cell.crop((0, 0, w, body_split))
        upper_shifted = Image.new("RGBA", (w, body_split), (0, 0, 0, 0))
        upper_shifted.paste(upper, (arm_shift, -bob), upper)
        shifted.paste(upper_shifted, (0, 0), upper_shifted)

        # Lower body (leg movement)
        lower = base_cell.crop((0, body_split, w, h))
        lower_shifted = Image.new("RGBA", (w, h - body_split), (0, 0, 0, 0))
        lower_shifted.paste(lower, (leg_shift, bob), lower)
        shifted.paste(lower_shifted, (0, body_split), lower_shifted)

        # Slight horizontal lean
        lean = int(math.sin(phase) * 1)
        final = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        final.paste(shifted, (lean, 0), shifted)

        frames.append(final)

    return frames

def create_interact_frames(base_cell, count=4, char_name="kirito"):
    """Create interaction frames"""
    frames = []
    w, h = CELL_W, CELL_H

    for i in range(count):
        frame = base_cell.copy()
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        if i == 0:
            # Frame 1: Lean forward slightly (reach/record)
            shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            upper = base_cell.crop((0, 0, w, int(h*0.6)))
            shifted.paste(upper, (2, -2), upper)
            lower = base_cell.crop((0, int(h*0.6), w, h))
            shifted.paste(lower, (0, int(h*0.6)), lower)
            frame = shifted

        elif i == 1:
            # Frame 2: Raise right arm (point/action)
            shifted = base_cell.copy()
            # Brighten right side slightly to suggest arm movement
            bright = Image.new("RGBA", (w, h), (30, 25, 15, 0))
            frame = Image.alpha_composite(shifted, bright)

        elif i == 2:
            # Frame 3: Crouch/squat (observe)
            compressed = base_cell.resize((w, h-6), Image.LANCZOS)
            new_frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            new_frame.paste(compressed, (0, 6), compressed)
            frame = new_frame

        elif i == 3:
            # Frame 4: Extended reach (stop/give item)
            shifted = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            upper = base_cell.crop((0, 0, w, int(h*0.5)))
            shifted.paste(upper, (3, -1), upper)
            lower = base_cell.crop((0, int(h*0.5), w, h))
            shifted.paste(lower, (1, int(h*0.5)), lower)
            frame = shifted

        frames.append(frame)

    return frames

def create_direction(base_cell, direction):
    """Create a directional view from the base (down-facing) cell"""
    if direction == "down":
        return base_cell.copy()
    elif direction == "left":
        return ImageOps.mirror(base_cell)
    elif direction == "right":
        return ImageOps.mirror(base_cell)
    elif direction == "up":
        return create_back_view(base_cell)
    return base_cell.copy()

def generate_sprite_sheet(char_info, base_dir):
    """Generate complete sprite sheet for one character"""
    prefix = f"{char_info['request_id']}_UW-UPGRADE-1.0"
    name = char_info['name']
    src_path = os.path.join(base_dir, char_info['src'])

    print(f"\nProcessing {name} ({char_info['request_id']})...")

    # Load and fit base character
    base_cell = load_and_fit_character(src_path)
    print(f"  Base cell: {base_cell.size}, mode={base_cell.mode}")

    # Create sprite sheet
    sheet = Image.new("RGBA", (CELL_W * SHEET_COLS, CELL_H * SHEET_ROWS), (0, 0, 0, 0))

    frames_data = {}
    frame_index = 0

    for dir_idx, direction in enumerate(DIRS):
        dir_cell = create_direction(base_cell, direction)

        # Generate animation frames for this direction
        idle_frames = create_idle_frames(dir_cell, ANIMS["idle"])
        walk_frames = create_walk_frames(dir_cell, ANIMS["walk"])
        interact_frames = create_interact_frames(dir_cell, ANIMS["interact"], name)

        all_frames = idle_frames + walk_frames + interact_frames

        for anim_idx, frame in enumerate(all_frames):
            col = anim_idx
            row = dir_idx
            x = col * CELL_W
            y = row * CELL_H
            sheet.paste(frame, (x, y), frame)

            # Record frame metadata
            anim_name = None
            anim_frame_idx = None
            if anim_idx < ANIMS["idle"]:
                anim_name = "idle"
                anim_frame_idx = anim_idx
            elif anim_idx < ANIMS["idle"] + ANIMS["walk"]:
                anim_name = "walk"
                anim_frame_idx = anim_idx - ANIMS["idle"]
            else:
                anim_name = "interact"
                anim_frame_idx = anim_idx - ANIMS["idle"] - ANIMS["walk"]

            key = f"{direction}_{anim_name}_{anim_frame_idx}"
            frames_data[key] = {
                "source": f"materials/inbox/visual/characters/{prefix}_{name}_sheet.png",
                "rect": [x, y, CELL_W, CELL_H],
                "anchor": [CELL_W // 2, CELL_H],
                "fps": 8 if anim_name == "walk" else 4,
                "loop": anim_name in ["idle", "walk"]
            }

            frame_index += 1

    # Save sprite sheet
    sheet_path = os.path.join(base_dir, f"{prefix}_{name}_sheet.png")
    sheet.save(sheet_path, "PNG")
    print(f"  Sprite sheet: {sheet.size} -> {sheet_path}")

    # Create frames JSON
    frames_json = {
        "request_id": char_info['request_id'],
        "batch": "UW-UPGRADE-1.0",
        "character": name,
        "description": char_info['desc'],
        "frame_width": CELL_W,
        "frame_height": CELL_H,
        "sheet_cols": SHEET_COLS,
        "sheet_rows": SHEET_ROWS,
        "total_frames": TOTAL_FRAMES,
        "directions": DIRS,
        "animations": ANIMS,
        "anchor": "bottom-center",
        "collision_footprint": [CELL_W // 2 - 8, CELL_H - 12, CELL_W // 2 + 8, CELL_H - 2],
        "display_height_px": 48,
        "frames": frames_data
    }

    json_path = os.path.join(base_dir, f"{prefix}_{name}_frames.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(frames_json, f, indent=2, ensure_ascii=False)
    print(f"  Frames JSON: {json_path}")

    # Create contact sheet (4x3 grid showing one frame per direction/anim)
    contact = Image.new("RGBA", (CELL_W * 4, CELL_H * 3), (40, 40, 50, 255))
    # Show: row 0 = idle frame 0 for each direction
    # row 1 = walk frame 0 for each direction
    # row 2 = interact frame 0 for each direction
    for d_idx, d in enumerate(DIRS):
        for a_idx, a in enumerate(["idle", "walk", "interact"]):
            key = f"{d}_{a}_0"
            if key in frames_data:
                rect = frames_data[key]["rect"]
                frame = sheet.crop((rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3]))
                # Scale up 2x for visibility
                frame = frame.resize((CELL_W*2, CELL_H*2), Image.NEAREST)
                contact.paste(frame, (d_idx * CELL_W * 2, a_idx * CELL_H * 2), frame)
    contact = contact.resize((CELL_W*4*2, CELL_H*3*2), Image.NEAREST)
    contact_path = os.path.join(base_dir, f"{prefix}_{name}_contact_sheet.png")
    contact.save(contact_path, "PNG")
    print(f"  Contact sheet: {contact.size}")

    # Create 48px display preview
    display_preview = sheet.crop((0, 0, CELL_W, CELL_H))  # down_idle_0
    display_preview = display_preview.resize((32, 48), Image.LANCZOS)
    display_path = os.path.join(base_dir, f"{prefix}_{name}_48px_preview.png")
    display_preview.save(display_path, "PNG")
    print(f"  48px preview: {display_preview.size}")

    return {
        "sheet": f"{prefix}_{name}_sheet.png",
        "frames_json": f"{prefix}_{name}_frames.json",
        "contact": f"{prefix}_{name}_contact_sheet.png",
        "preview": f"{prefix}_{name}_48px_preview.png"
    }

def main():
    base_dir = r"C:\Users\liang\Desktop\UW\materials\inbox\visual\characters"
    results = {}

    for char in CHARACTERS:
        results[char['request_id']] = generate_sprite_sheet(char, base_dir)

    # Move source images to work directory
    work_dir = os.path.join(base_dir, "_v007_work")
    os.makedirs(work_dir, exist_ok=True)
    for char in CHARACTERS:
        src = os.path.join(base_dir, char['src'])
        if os.path.exists(src):
            dst = os.path.join(work_dir, char['src'])
            os.rename(src, dst)
            print(f"  Moved {char['src']} to _v007_work/")

    # Generate manifest fragment
    all_files = []
    for char in CHARACTERS:
        for f in results[char['request_id']].values():
            all_files.append((char['request_id'], f))

    hashes = {}
    for req_id, fname in all_files:
        p = os.path.join(base_dir, fname)
        with open(p, "rb") as fh:
            hashes[fname] = hashlib.sha256(fh.read()).hexdigest()

    header = ["asset_id","request_id","status","source_file","runtime_file","sha256","creator","tool_model","created_at","license","source_url","attribution_required","attribution_text","approved_by","approved_at","integrated_at","replaces_asset_id","notes"]
    rows = []
    created_at = "2026-08-07T18:00:00+08:00"

    for char in CHARACTERS:
        req_id = char['request_id']
        name = char['name']
        for fname, ftype in [
            (results[req_id]['sheet'], f"{name} sprite sheet 48 frames"),
            (results[req_id]['frames_json'], f"{name} frames metadata"),
            (results[req_id]['contact'], f"{name} contact sheet"),
            (results[req_id]['preview'], f"{name} 48px display preview"),
        ]:
            rows.append({
                "asset_id": fname.replace(".png","").replace(".json",""),
                "request_id": req_id,
                "status": "received",
                "source_file": f"materials/inbox/visual/characters/{fname}",
                "runtime_file": "",
                "sha256": hashes[fname],
                "creator": "WorkBuddy AI Asset Agent",
                "tool_model": "Hunyuan+Python PIL",
                "created_at": created_at,
                "license": "Project original - UW 0.5.0-pre-capture",
                "source_url": "AI generated, no external URL",
                "attribution_required": "false",
                "attribution_text": "",
                "approved_by": "",
                "approved_at": "",
                "integrated_at": "",
                "replaces_asset_id": f"{req_id}_v008",
                "notes": ftype
            })

    csv_path = os.path.join(base_dir, "VIS-CHR_UW-UPGRADE-1.0_manifest_fragment.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nManifest fragment: {len(rows)} rows written")

    print("\nAll character sprite sheets generated!")
    for char in CHARACTERS:
        r = results[char['request_id']]
        print(f"  {char['name']}: sheet={r['sheet']}, frames_json={r['frames_json']}")

if __name__ == "__main__":
    main()
