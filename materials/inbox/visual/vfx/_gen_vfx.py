"""
VIS-VFX-001 UW-UPGRADE-1.0 VFX Generator
Generates 6 VFX types as transparent PNG frame sheets.
"""
import os, json, hashlib, csv, math, random
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)

# Colors
CLUE_CYAN = (114, 184, 196)
INDIGO = (60, 70, 104)
GOLD = (246, 211, 110)
WARM = (255, 200, 130)
WHITE = (255, 255, 255)

FRAME_W, FRAME_H = 128, 128

VFX_TYPES = [
    {
        "id": "clue-pulse",
        "name": "Clue Pulse",
        "description": "Target/clue arrival pulse, cold cyan, radius <= 1.4 character height",
        "duration_s": 0.7,
        "fps": 15,
        "frame_count": 10,
        "color": CLUE_CYAN,
        "trigger_id": "clue_found",
        "sfx_id": "clue_select",
        "blend": "screen",
        "radius": 60,
        "anchor": [64, 64]
    },
    {
        "id": "sacred-ink",
        "name": "Sacred Ink",
        "description": "Sacred arts/record lines, thin gold lines, low flicker",
        "duration_s": 1.1,
        "fps": 12,
        "frame_count": 13,
        "color": GOLD,
        "trigger_id": "sacred_ink",
        "sfx_id": "sacred_ink",
        "blend": "add",
        "radius": 50,
        "anchor": [64, 64]
    },
    {
        "id": "boundary-ripple",
        "name": "Boundary Ripple",
        "description": "Boundary disturbance, indigo/cyan, local refraction",
        "duration_s": 1.4,
        "fps": 12,
        "frame_count": 17,
        "color": INDIGO,
        "trigger_id": "boundary_ripple",
        "sfx_id": "boundary_ripple",
        "blend": "screen",
        "radius": 70,
        "anchor": [64, 64]
    },
    {
        "id": "relationship-warmth",
        "name": "Relationship Warmth",
        "description": "Relationship echo, warm light/small particles, no large orbs",
        "duration_s": 0.8,
        "fps": 15,
        "frame_count": 12,
        "color": WARM,
        "trigger_id": "relationship_up",
        "sfx_id": "relationship_up",
        "blend": "add",
        "radius": 45,
        "anchor": [64, 64]
    },
    {
        "id": "reward-spark",
        "name": "Reward Spark",
        "description": "Reward confirmation, wheat gold particles",
        "duration_s": 0.6,
        "fps": 15,
        "frame_count": 9,
        "color": GOLD,
        "trigger_id": "reward",
        "sfx_id": "reward",
        "blend": "add",
        "radius": 40,
        "anchor": [64, 64]
    },
    {
        "id": "capture-silence",
        "name": "Capture Silence",
        "description": "Capture moment motion/color convergence, no white flash",
        "duration_s": 2.0,
        "fps": 10,
        "frame_count": 20,
        "color": INDIGO,
        "trigger_id": "capture_silence",
        "sfx_id": "capture_silence",
        "blend": "screen",
        "radius": 80,
        "anchor": [64, 64]
    }
]

def gen_clue_pulse(frame_idx, total_frames, color):
    """Expanding cyan ring pulse"""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = FRAME_W // 2, FRAME_H // 2
    progress = frame_idx / total_frames
    radius = int(10 + progress * 55)
    alpha = int(255 * (1 - progress * 0.8))
    
    # Main ring
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                 outline=color + (alpha,), width=3)
    # Inner ring
    inner_r = max(0, radius - 8)
    if inner_r > 0:
        draw.ellipse([cx-inner_r, cy-inner_r, cx+inner_r, cy+inner_r],
                     outline=color + (alpha//2,), width=1)
    # Center dot
    dot_r = max(2, int(8 * (1 - progress)))
    draw.ellipse([cx-dot_r, cy-dot_r, cx+dot_r, cy+dot_r], fill=color + (alpha,))
    
    return img

def gen_sacred_ink(frame_idx, total_frames, color):
    """Golden geometric lines forming a circle"""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = FRAME_W // 2, FRAME_H // 2
    progress = frame_idx / total_frames
    
    # Draw forming circle
    radius = 45
    start_angle = 0
    end_angle = int(360 * min(progress * 1.5, 1.0))
    
    if end_angle > 0:
        # Draw arc
        bbox = [cx-radius, cy-radius, cx+radius, cy+radius]
        draw.arc(bbox, start_angle, start_angle + end_angle, fill=color + (200,), width=2)
    
    # Add geometric runes
    if progress > 0.5:
        num_runes = 6
        rune_progress = (progress - 0.5) * 2
        for i in range(num_runes):
            angle = math.radians(i * 60 + frame_idx * 2)
            rx = cx + int(math.cos(angle) * radius)
            ry = cy + int(math.sin(angle) * radius)
            r = int(3 * rune_progress)
            if r > 0:
                draw.ellipse([rx-r, ry-r, rx+r, ry+r], fill=color + (150,))
    
    # Center glow
    glow_r = int(5 + 3 * math.sin(frame_idx * 0.5))
    draw.ellipse([cx-glow_r, cy-glow_r, cx+glow_r, cy+glow_r], fill=color + (100,))
    
    return img

def gen_boundary_ripple(frame_idx, total_frames, color):
    """Indigo ripple distortion"""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = FRAME_W // 2, FRAME_H // 2
    progress = frame_idx / total_frames
    
    # Multiple expanding rings
    for ring in range(3):
        ring_progress = (progress + ring * 0.3) % 1.0
        radius = int(15 + ring_progress * 60)
        alpha = int(150 * (1 - ring_progress))
        if alpha > 0:
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                         outline=color + (alpha,), width=2)
    
    # Distortion lines
    for i in range(4):
        angle = math.radians(i * 90 + frame_idx * 5)
        x1 = cx + int(math.cos(angle) * 20)
        y1 = cy + int(math.sin(angle) * 20)
        x2 = cx + int(math.cos(angle) * 55)
        y2 = cy + int(math.sin(angle) * 55)
        draw.line([(x1, y1), (x2, y2)], fill=color + (100,), width=1)
    
    return img

def gen_relationship_warmth(frame_idx, total_frames, color):
    """Warm particles rising"""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = FRAME_W // 2, FRAME_H // 2
    progress = frame_idx / total_frames
    
    # Rising particles
    for i in range(12):
        seed = i * 7 + frame_idx
        random.seed(seed)
        px = cx + random.randint(-25, 25)
        py_offset = (progress + i * 0.1) % 1.0
        py = cy + 30 - int(py_offset * 60)
        r = random.randint(2, 5)
        alpha = int(200 * (1 - py_offset))
        draw.ellipse([px-r, py-r, px+r, py+r], fill=color + (alpha,))
    
    # Soft glow
    glow_r = int(20 + 5 * math.sin(frame_idx * 0.3))
    for r in range(glow_r, 0, -3):
        alpha = int(30 * (1 - r / glow_r))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color + (alpha,))
    
    return img

def gen_reward_spark(frame_idx, total_frames, color):
    """Gold spark burst"""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = FRAME_W // 2, FRAME_H // 2
    progress = frame_idx / total_frames
    
    # Spark particles radiating outward
    num_sparks = 8
    for i in range(num_sparks):
        angle = math.radians(i * (360 / num_sparks) + frame_idx * 3)
        dist = int(progress * 40)
        sx = cx + int(math.cos(angle) * dist)
        sy = cy + int(math.sin(angle) * dist)
        r = max(1, int(4 * (1 - progress)))
        alpha = int(255 * (1 - progress * 0.7))
        draw.ellipse([sx-r, sy-r, sx+r, sy+r], fill=color + (alpha,))
    
    # Center flash
    flash_r = max(0, int(10 * (1 - progress * 1.5)))
    if flash_r > 0:
        draw.ellipse([cx-flash_r, cy-flash_r, cx+flash_r, cy+flash_r],
                     fill=color + (200,))
    
    # Star shape
    if progress < 0.3:
        star_r = int(15 * (1 - progress / 0.3))
        for i in range(4):
            angle = math.radians(i * 90)
            x1 = cx + int(math.cos(angle) * 3)
            y1 = cy + int(math.sin(angle) * 3)
            x2 = cx + int(math.cos(angle) * star_r)
            y2 = cy + int(math.sin(angle) * star_r)
            draw.line([(x1, y1), (x2, y2)], fill=color + (200,), width=2)
    
    return img

def gen_capture_silence(frame_idx, total_frames, color):
    """Color convergence, no white flash"""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = FRAME_W // 2, FRAME_H // 2
    progress = frame_idx / total_frames
    
    if progress < 0.3:
        # Phase 1: convergence - rings closing in
        phase = progress / 0.3
        radius = int(70 - phase * 50)
        alpha = int(100 + phase * 100)
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                     outline=color + (alpha,), width=2)
        # Inner convergence
        inner_r = int(30 - phase * 20)
        if inner_r > 0:
            draw.ellipse([cx-inner_r, cy-inner_r, cx+inner_r, cy+inner_r],
                         outline=color + (alpha,), width=1)
    elif progress < 0.5:
        # Phase 2: impact - dark expansion
        phase = (progress - 0.3) / 0.2
        radius = int(20 + phase * 60)
        alpha = int(200 * (1 - phase * 0.5))
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                     fill=color + (alpha // 3,), outline=color + (alpha,), width=2)
    else:
        # Phase 3: fade - rings dissipating
        phase = (progress - 0.5) / 0.5
        for ring in range(3):
            ring_phase = (phase + ring * 0.2) % 1.0
            radius = int(40 + ring_phase * 50)
            alpha = int(100 * (1 - ring_phase))
            if alpha > 0:
                draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                             outline=color + (alpha,), width=1)
    
    return img

VFX_GENERATORS = {
    "clue-pulse": gen_clue_pulse,
    "sacred-ink": gen_sacred_ink,
    "boundary-ripple": gen_boundary_ripple,
    "relationship-warmth": gen_relationship_warmth,
    "reward-spark": gen_reward_spark,
    "capture-silence": gen_capture_silence,
}

def main():
    base_dir = r"C:\Users\liang\Desktop\UW\materials\inbox\visual\vfx"
    prefix = "VIS-VFX-001_UW-UPGRADE-1.0"
    
    all_files = []
    vfx_data = []
    
    for vfx in VFX_TYPES:
        vfx_id = vfx["id"]
        gen_func = VFX_GENERATORS[vfx_id]
        frame_count = vfx["frame_count"]
        
        print(f"Generating {vfx_id} ({frame_count} frames)...")
        
        # Create frame sheet
        sheet = Image.new("RGBA", (FRAME_W * frame_count, FRAME_H), (0, 0, 0, 0))
        frames_info = []
        
        for i in range(frame_count):
            frame = gen_func(i, frame_count, vfx["color"])
            sheet.paste(frame, (i * FRAME_W, 0), frame)
            frames_info.append({
                "frame": i,
                "rect": [i * FRAME_W, 0, FRAME_W, FRAME_H],
                "duration_ms": int(1000 / vfx["fps"])
            })
        
        sheet_path = os.path.join(base_dir, f"{prefix}_{vfx_id}_sheet.png")
        sheet.save(sheet_path, "PNG")
        all_files.append(f"{prefix}_{vfx_id}_sheet.png")
        print(f"  Sheet: {sheet.size}")
        
        # Static fallback (first frame)
        fallback = gen_func(0, frame_count, vfx["color"])
        fallback_path = os.path.join(base_dir, f"{prefix}_{vfx_id}_fallback.png")
        fallback.save(fallback_path, "PNG")
        all_files.append(f"{prefix}_{vfx_id}_fallback.png")
        
        # Reduced motion version (3 frames only)
        reduced = Image.new("RGBA", (FRAME_W * 3, FRAME_H), (0, 0, 0, 0))
        for j, fi in enumerate([0, frame_count // 2, frame_count - 1]):
            frame = gen_func(fi, frame_count, vfx["color"])
            reduced.paste(frame, (j * FRAME_W, 0), frame)
        reduced_path = os.path.join(base_dir, f"{prefix}_{vfx_id}_reduced.png")
        reduced.save(reduced_path, "PNG")
        all_files.append(f"{prefix}_{vfx_id}_reduced.png")
        
        vfx_data.append({
            "id": vfx_id,
            "name": vfx["name"],
            "description": vfx["description"],
            "sheet_source": f"materials/inbox/visual/vfx/{prefix}_{vfx_id}_sheet.png",
            "fallback_source": f"materials/inbox/visual/vfx/{prefix}_{vfx_id}_fallback.png",
            "reduced_motion_source": f"materials/inbox/visual/vfx/{prefix}_{vfx_id}_reduced.png",
            "frame_width": FRAME_W,
            "frame_height": FRAME_H,
            "frame_count": frame_count,
            "fps": vfx["fps"],
            "duration_s": vfx["duration_s"],
            "blend": vfx["blend"],
            "radius": vfx["radius"],
            "anchor": vfx["anchor"],
            "trigger_id": vfx["trigger_id"],
            "sfx_id": vfx["sfx_id"],
            "frames": frames_info
        })
    
    # Metadata JSON
    meta_path = os.path.join(base_dir, f"{prefix}_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "request_id": "VIS-VFX-001",
            "batch": "UW-UPGRADE-1.0",
            "vfx_count": len(VFX_TYPES),
            "frame_size": [FRAME_W, FRAME_H],
            "vfx": vfx_data
        }, f, indent=2, ensure_ascii=False)
    all_files.append(f"{prefix}_metadata.json")
    
    # Manifest fragment
    header = ["asset_id","request_id","status","source_file","runtime_file","sha256","creator","tool_model","created_at","license","source_url","attribution_required","attribution_text","approved_by","approved_at","integrated_at","replaces_asset_id","notes"]
    rows = []
    created_at = "2026-08-07T18:20:00+08:00"
    
    for fname in all_files:
        fpath = os.path.join(base_dir, fname)
        with open(fpath, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        rows.append({
            "asset_id": fname.replace(".png","").replace(".json",""),
            "request_id": "VIS-VFX-001",
            "status": "received",
            "source_file": f"materials/inbox/visual/vfx/{fname}",
            "runtime_file": "",
            "sha256": sha,
            "creator": "WorkBuddy AI Asset Agent",
            "tool_model": "Python PIL",
            "created_at": created_at,
            "license": "Project original - UW 0.5.0-pre-capture",
            "source_url": "Procedurally generated",
            "attribution_required": "false",
            "attribution_text": "",
            "approved_by": "",
            "approved_at": "",
            "integrated_at": "",
            "replaces_asset_id": "",
            "notes": f"VFX: {fname}"
        })
    
    csv_path = os.path.join(base_dir, f"{prefix}_manifest_fragment.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nManifest fragment: {len(rows)} rows")
    print("VIS-VFX-001 complete!")

if __name__ == "__main__":
    main()
