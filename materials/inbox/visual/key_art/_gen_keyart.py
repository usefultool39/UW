"""
VIS-KA-002 UW-UPGRADE-1.0 Endpoint Key Art Processor
Processes AI-generated base images into final key art deliverables.
"""
import os, json, hashlib, csv
from pathlib import Path
from PIL import Image

BASE = Path(r"C:\Users\liang\Desktop\UW\materials\inbox\visual\key_art")
PREFIX = "VIS-KA-002"
BATCH = "UW-UPGRADE-1.0"
CREATOR = "WorkBuddy AI Asset Agent"
TOOL = "ImageGen (Hunyuan) + Python PIL LANCZOS"
CREATED_AT = "2026-08-07T18:40:00+08:00"

# Source images from ImageGen
LANDSCAPE_SRC = BASE / "Storybook_illustration_style_k_2026-08-07T10-13-29.png"
PORTRAIT_SRC = BASE / "Storybook_illustration_style_v_2026-08-07T10-13-58.png"

# Target specifications
DESKTOP_SIZE = (2560, 1440)   # 16:9 landscape
MOBILE_SIZE = (1440, 1920)    # 3:4 portrait
THUMB_SIZE = (640, 360)       # Desktop thumbnail
MOBILE_THUMB = (360, 480)     # Mobile thumbnail

def smart_crop_resize(img, target_size):
    """Crop to target aspect ratio then resize with LANCZOS."""
    target_w, target_h = target_size
    target_ratio = target_w / target_h
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    
    if src_ratio > target_ratio:
        # Source is wider, crop sides
        new_w = int(src_h * target_ratio)
        offset = (src_w - new_w) // 2
        img = img.crop((offset, 0, offset + new_w, src_h))
    elif src_ratio < target_ratio:
        # Source is taller, crop top/bottom
        new_h = int(src_w / target_ratio)
        offset = (src_h - new_h) // 2
        # Bias crop toward top for portrait, center for landscape
        if target_h > target_w:
            offset = int((src_h - new_h) * 0.35)  # Slight upper bias for character focus
        img = img.crop((0, offset, src_w, offset + new_h))
    
    return img.resize(target_size, Image.LANCZOS)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    os.makedirs(BASE, exist_ok=True)
    
    all_files = []
    metadata = {
        "request_id": "VIS-KA-002",
        "batch": "UW-UPGRADE-1.0",
        "title": "Endpoint Key Art - Boundary Capture Scene",
        "description": "Alice at the forest boundary, the pivotal capture moment. Storybook illustration style with indigo boundary ripples, warm village light, and cold forest atmosphere.",
        "variants": [],
        "source_images": [
            {"file": LANDSCAPE_SRC.name, "tool": "ImageGen Hunyuan", "prompt": "Landscape key art - Alice at forest boundary"},
            {"file": PORTRAIT_SRC.name, "tool": "ImageGen Hunyuan", "prompt": "Portrait key art - Alice at forest boundary (vertical)"}
        ]
    }
    
    # Process desktop (landscape)
    print("Processing desktop key art (2560x1440)...")
    src = Image.open(LANDSCAPE_SRC).convert("RGB")
    print(f"  Source: {src.size}")
    desktop = smart_crop_resize(src, DESKTOP_SIZE)
    desktop_path = BASE / f"{PREFIX}_{BATCH}_desktop_2560x1440.png"
    desktop.save(desktop_path, "PNG", optimize=True)
    all_files.append(desktop_path.name)
    print(f"  Output: {desktop.size} -> {desktop_path.name}")
    
    # Desktop thumbnail
    thumb = desktop.resize(THUMB_SIZE, Image.LANCZOS)
    thumb_path = BASE / f"{PREFIX}_{BATCH}_desktop_thumb_640x360.png"
    thumb.save(thumb_path, "PNG", optimize=True)
    all_files.append(thumb_path.name)
    
    # Desktop JPEG (for web)
    jpg_path = BASE / f"{PREFIX}_{BATCH}_desktop_2560x1440.jpg"
    desktop.save(jpg_path, "JPEG", quality=92, optimize=True)
    all_files.append(jpg_path.name)
    
    metadata["variants"].append({
        "variant": "desktop",
        "resolution": list(DESKTOP_SIZE),
        "aspect_ratio": "16:9",
        "files": [desktop_path.name, thumb_path.name, jpg_path.name],
        "intended_use": "Desktop loading screen, store page header, promotional banner"
    })
    
    # Process mobile (portrait)
    print("Processing mobile key art (1440x1920)...")
    src = Image.open(PORTRAIT_SRC).convert("RGB")
    print(f"  Source: {src.size}")
    mobile = smart_crop_resize(src, MOBILE_SIZE)
    mobile_path = BASE / f"{PREFIX}_{BATCH}_mobile_1440x1920.png"
    mobile.save(mobile_path, "PNG", optimize=True)
    all_files.append(mobile_path.name)
    print(f"  Output: {mobile.size} -> {mobile_path.name}")
    
    # Mobile thumbnail
    mthumb = mobile.resize(MOBILE_THUMB, Image.LANCZOS)
    mthumb_path = BASE / f"{PREFIX}_{BATCH}_mobile_thumb_360x480.png"
    mthumb.save(mthumb_path, "PNG", optimize=True)
    all_files.append(mthumb_path.name)
    
    # Mobile JPEG
    mjpg_path = BASE / f"{PREFIX}_{BATCH}_mobile_1440x1920.jpg"
    mobile.save(mjpg_path, "JPEG", quality=92, optimize=True)
    all_files.append(mjpg_path.name)
    
    metadata["variants"].append({
        "variant": "mobile",
        "resolution": list(MOBILE_SIZE),
        "aspect_ratio": "3:4",
        "files": [mobile_path.name, mthumb_path.name, mjpg_path.name],
        "intended_use": "Mobile loading screen, app store screenshot, social media card"
    })
    
    # Save metadata JSON
    meta_path = BASE / f"{PREFIX}_{BATCH}_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    all_files.append(meta_path.name)
    
    # Manifest fragment
    header = ["asset_id","request_id","status","source_file","runtime_file","sha256","creator","tool_model","created_at","license","source_url","attribution_required","attribution_text","approved_by","approved_at","integrated_at","replaces_asset_id","notes"]
    rows = []
    
    for fname in all_files:
        fpath = BASE / fname
        sha = sha256_file(fpath)
        size = os.path.getsize(fpath)
        asset_id = fname.replace(f"_{BATCH}", "").replace(".png", "").replace(".jpg", "").replace(".json", "").replace("__", "_")
        
        notes = f"Key art: {fname}"
        if "desktop" in fname:
            notes += f" (2560x1440, 16:9)"
        elif "mobile" in fname:
            notes += f" (1440x1920, 3:4)"
        elif "metadata" in fname:
            notes = "Key art metadata JSON"
        
        rows.append({
            "asset_id": f"{PREFIX}_{fname.replace('.', '_')}",
            "request_id": "VIS-KA-002",
            "status": "received",
            "source_file": f"materials/inbox/visual/key_art/{fname}",
            "runtime_file": "",
            "sha256": sha,
            "creator": CREATOR,
            "tool_model": TOOL,
            "created_at": CREATED_AT,
            "license": "Project original - UW 0.5.0-pre-capture",
            "source_url": "ImageGen (Hunyuan) AI generation",
            "attribution_required": "false",
            "attribution_text": "",
            "approved_by": "",
            "approved_at": "",
            "integrated_at": "",
            "replaces_asset_id": "",
            "notes": notes
        })
    
    csv_path = BASE / f"{PREFIX}_{BATCH}_manifest_fragment.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nTotal files: {len(all_files)}")
    print(f"Manifest: {len(rows)} rows")
    
    # Print file list with sizes and hashes
    print("\nFile list:")
    for fname in all_files:
        fpath = BASE / fname
        size = os.path.getsize(fpath)
        sha = sha256_file(fpath)
        print(f"  {fname}: {size} bytes, sha256={sha[:16]}...")
    
    print("\nVIS-KA-002 complete!")

if __name__ == "__main__":
    main()
