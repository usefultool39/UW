import hashlib, os, csv

base = r"C:\Users\liang\Desktop\UW\materials\inbox\visual\world"
prefix = "VIS-MAP-001_UW-UPGRADE-1.0"
created_at = "2026-08-07T17:56:00+08:00"

# Move terrain source to work dir
terrain_src = None
for f in os.listdir(base):
    if f.startswith("Top_down_2D_RPG") and f.endswith(".png"):
        terrain_src = os.path.join(base, f)
        break
if terrain_src:
    work_dir = os.path.join(base, "_v007_work")
    os.makedirs(work_dir, exist_ok=True)
    new_path = os.path.join(work_dir, os.path.basename(terrain_src))
    os.rename(terrain_src, new_path)
    print(f"Moved terrain source to {new_path}")

# List all formal files
formal_files = [
    f"{prefix}_terrain.png", f"{prefix}_water.png", f"{prefix}_roads.png",
    f"{prefix}_buildings.png", f"{prefix}_vegetation.png", f"{prefix}_occlusion.png",
    f"{prefix}_foreground.png", f"{prefix}_lighting.png", f"{prefix}_weather.png",
    f"{prefix}_tile_atlas.png", f"{prefix}_prop_atlas.png",
    f"{prefix}_composite_preview.png", f"{prefix}_collision_walkable_preview.png",
    f"{prefix}_map.json"
]

hashes = {}
for f in formal_files:
    p = os.path.join(base, f)
    with open(p, "rb") as fh:
        hashes[f] = hashlib.sha256(fh.read()).hexdigest()

header = ["asset_id","request_id","status","source_file","runtime_file","sha256","creator","tool_model","created_at","license","source_url","attribution_required","attribution_text","approved_by","approved_at","integrated_at","replaces_asset_id","notes"]

rows = []
layer_names = ["terrain","water","roads","buildings","vegetation","occlusion","foreground","lighting","weather"]
for ln in layer_names:
    fname = f"{prefix}_{ln}.png"
    rows.append({
        "asset_id": f"{prefix}_{ln}",
        "request_id": "VIS-MAP-001",
        "status": "received",
        "source_file": f"materials/inbox/visual/world/{fname}",
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
        "replaces_asset_id": "VIS-MAP-001_v005",
        "notes": f"Independent {ln} layer, 3024x1792, RGBA"
    })

for fname, desc in [
    (f"{prefix}_tile_atlas.png", "Tile atlas with terrain/water/road tiles"),
    (f"{prefix}_prop_atlas.png", "Prop atlas with trees/bushes/objects"),
    (f"{prefix}_composite_preview.png", "Composite preview (all layers combined)"),
    (f"{prefix}_collision_walkable_preview.png", "Collision/walkable/interaction visualization"),
    (f"{prefix}_map.json", "Map metadata with layers, collision, walkable, interaction data"),
]:
    rows.append({
        "asset_id": fname.replace(".png","").replace(".json",""),
        "request_id": "VIS-MAP-001",
        "status": "received",
        "source_file": f"materials/inbox/visual/world/{fname}",
        "runtime_file": "",
        "sha256": hashes[fname],
        "creator": "WorkBuddy AI Asset Agent",
        "tool_model": "Python PIL",
        "created_at": created_at,
        "license": "Project original - UW 0.5.0-pre-capture",
        "source_url": "AI generated, no external URL",
        "attribution_required": "false",
        "attribution_text": "",
        "approved_by": "",
        "approved_at": "",
        "integrated_at": "",
        "replaces_asset_id": "",
        "notes": desc
    })

csv_path = os.path.join(base, f"{prefix}_manifest_fragment.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)
print(f"Manifest fragment: {len(rows)} rows written")
for f in formal_files:
    print(f"  {f}: {hashes[f][:32]}...")
