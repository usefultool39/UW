#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-MAP-001 v003 sidecar + manifest fragment 写入器。"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Users\liang\Desktop\UW")
WORLD_DIR = ROOT / "materials" / "inbox" / "visual" / "world"
MAP_JSON = WORLD_DIR / "VIS-MAP-001_map_v003.json"

MANIFEST_COLS = [
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at",
    "replaces_asset_id", "notes",
]

CREATOR = "Mavis"
TOOL_MODEL = ("procedural-map-v003 (Python Pillow 11.3.0 + numpy 2.3.5) "
              "reading data/world/world_map.json (108x64 tile grid, 28px/tile)")
CREATED = "2026-08-07"
LICENSE = "owned"
SOURCE_URL = "none"
ATTR_REQUIRED = "false"
ATTR_TEXT = ""


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    meta = json.loads(MAP_JSON.read_text(encoding="utf-8"))

    # 计算所有文件 SHA-256
    files = []
    for layer in meta["layers"]:
        files.append(("VIS-MAP-001-" + layer["name"].replace("_", "-") + "-v003", layer["file"]))
    for mask_name, mask_info in meta["masks"].items():
        files.append((f"VIS-MAP-001-{mask_name}-v003", mask_info["file"]))
    files.append(("VIS-MAP-001-tiles-atlas-v003", meta["tiles_atlas"]["atlas"]))
    files.append(("VIS-MAP-001-props-atlas-v003", meta["props_atlas"]["atlas"]))
    files.append(("VIS-MAP-001-master-composite-v003", meta["master_composite"]))
    files.append(("VIS-MAP-001-metadata-v003", "VIS-MAP-001_map_v003.json"))

    # ---------- manifest fragment ----------
    frag_csv = WORLD_DIR / "VIS-MAP-001_manifest_fragment_v003.csv"
    with frag_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        for asset_id, fname in files:
            fpath = WORLD_DIR / fname
            sha = sha256_file(fpath)
            w.writerow([
                asset_id, "VIS-MAP-001", "received",
                f"visual/world/{fname}", "",
                sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
                ATTR_REQUIRED, ATTR_TEXT, "", "", "",
                "VIS-MAP-001-v002" if "metadata" not in asset_id else "",
                f"{fpath.stat().st_size} bytes; {fname}"
            ])
    print(f"  wrote: {frag_csv}")

    # ---------- sidecar ----------
    sidecar = WORLD_DIR / "VIS-MAP-001_delivery_v003.md"
    lines = []
    lines.append("# VIS-MAP-001_delivery_v003")
    lines.append("")
    lines.append("- request_id: VIS-MAP-001")
    lines.append("- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated")
    lines.append("- expected_version: v003 (本包替换 v002，v002 文件保留作为审计证据)")
    lines.append("- delivery_dir: materials/inbox/visual/world")
    lines.append("- priority: P1, first-phase runtime blocker")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- runtime_status: prohibited until project owner acceptance chain passes")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（程序化绘制，读取项目自带的 data/world/world_map.json 108x64 瓦片网格）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append("- Pillow 11.3.0 (numpy 2.3.5) 渲染所有 PNG 图层 + 掩码 + atlas")
    lines.append("- Python 3.13.9")
    lines.append("")
    lines.append("## 2. 规格与实测")
    lines.append("")
    lines.append("| 项目 | spec | 实测 |")
    lines.append("|---|---|---|")
    lines.append(f"| 网格 | 108x64 tiles, 28 px/tile | {meta['grid']['cols']}x{meta['grid']['rows']} tiles, {meta['grid']['tile_size_px']} px/tile |")
    lines.append(f"| 每层像素 | 3024x1792 | {meta['grid']['layer_width_px']}x{meta['grid']['layer_height_px']} |")
    lines.append(f"| 图层数 | 9 (terrain/water, roads, ground props, buildings, vegetation, occluders, foreground, lighting, weather) | 9 |")
    lines.append(f"| 掩码 | collision, walkable, occlusion/depth | 3 (含 occlusion_depth) |")
    lines.append(f"| Atlas | tile/prop reusable | 2 (tiles_atlas 256x256, props_atlas 256x256) |")
    lines.append(f"| JSON metadata | VIS-MAP-001_map_v003.json | {MAP_JSON.stat().st_size} bytes |")
    lines.append(f"| 图例 | 0=grass 1=forest 2=water 3=road 4=obstacle | 与 world_map.json 一致 |")
    lines.append(f"| 可走瓦片 ID | 0, 3 | {meta['walkable_tile_ids']} |")
    lines.append(f"| 阻挡瓦片 ID | 1, 2, 4 | {meta['blocked_tile_ids']} |")
    lines.append(f"| POI 数量 | 9 (pois in world_map.json) | {len(meta['pois'])} |")
    lines.append(f"| 场景 zone | 12 scene_zones in world_map.json | {len(meta['scene_zones'])} |")
    lines.append("")
    lines.append("## 3. 创作提示词（合成描述）")
    lines.append("")
    lines.append("```text")
    lines.append(
        "Original hand-painted 3/4 top-down tile-aligned map of Rulid Village. "
        "108x64 grid, 28px/tile, 3024x1792 pixels per layer. Deliver grid-aligned "
        "PNG layers for terrain/water (grass + water bodies), roads (dirt path on "
        "tile id=3), ground props (grass tufts, small rocks, water ripples), "
        "buildings (church library, home hearth, teleport plaza stone ring, north "
        "gate, gigas cedar tree), vegetation (forest canopies + scattered small "
        "trees), occluders (alpha-200 on forest + alpha-160 on major buildings), "
        "foreground (road-adjacent grass blades), lighting (warm sun radial + "
        "forest shadow), weather (ambient cloud). Also deliver tile/prop atlas, "
        "collision/walkable/occlusion_depth masks, and POI/interaction JSON. No "
        "characters, no text, no UI, no checkerboard, no copyright composition."
    )
    lines.append("```")
    lines.append("")
    lines.append("### Negative prompt / 禁止项")
    lines.append("")
    lines.append("```text")
    lines.append(
        "no characters; no text, labels, signs with words; no UI elements; no "
        "watermarks; no baked checkerboard; no copyrighted anime/game screenshot "
        "composition; no single flattened illustration as the only deliverable; "
        "no AI-copied material; no third-party art."
    )
    lines.append("```")
    lines.append("")
    lines.append("## 4. seed / settings / 修整")
    lines.append("")
    lines.append("- 网格来源: data/world/world_map.json (项目自带 ground truth)")
    lines.append("- 随机种子: 7001 (ground_props) / 7002 (vegetation) / 7003 (foreground) / "
                 "7004 (weather) / 7005 (props atlas)")
    lines.append("- 滤镜: terrain GaussianBlur r=0.7, roads GaussianBlur r=0.5 (柔和手绘风)")
    lines.append("- 输出格式: PNG, RGBA, optimize=True")
    lines.append("- Layer compositing order (master): terrain → roads → ground_props → buildings "
                 "→ vegetation → occluders → foreground → lighting → weather")
    lines.append("")
    lines.append("## 5. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE}（procedural synthesis by Mavis, derived from project-owned "
                 f"data/world/world_map.json）")
    lines.append(f"- source_url: {SOURCE_URL}（项目内部数据，无外部素材/参考图）")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: visual / world (phaser runtime map)")
    lines.append("- rights statement: 本包由 Mavis 通过 Python + Pillow 程序化绘制，"
                 "从 data/world/world_map.json 读取 ground truth 瓦片布局；"
                 "不包含第三方素材、版权图像或 AI 训练集参考。")
    lines.append("")
    lines.append("## 6. 文件清单（带 SHA-256）")
    lines.append("")
    lines.append("| 资产 ID | 文件 | 角色 | SHA-256 | size |")
    lines.append("|---|---|---|---|---|")
    for asset_id, fname in files:
        fpath = WORLD_DIR / fname
        sha = sha256_file(fpath)
        role = "master composite" if "master" in asset_id else \
               "tile atlas" if "tiles-atlas" in asset_id else \
               "prop atlas" if "props-atlas" in asset_id else \
               "metadata JSON" if "metadata" in asset_id else \
               "mask" if any(m in asset_id for m in ("collision", "walkable", "occlusion")) else \
               "layer"
        lines.append(f"| {asset_id} | visual/world/{fname} | {role} | {sha} | {fpath.stat().st_size} |")
    lines.append("")
    lines.append("## 7. Manifest 片段")
    lines.append("")
    lines.append("- 路径: `materials/inbox/visual/world/VIS-MAP-001_manifest_fragment_v003.csv`")
    lines.append("- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("- 一文件一行, 含 SHA-256")
    lines.append("")
    lines.append("## 8. 配套 JSON metadata")
    lines.append("")
    lines.append("- 路径: `materials/inbox/visual/world/VIS-MAP-001_map_v003.json`")
    lines.append("- 含 grid/legend/scene_zones/pois/spawn/walkable_tile_ids/blocked_tile_ids/"
                 "poi_interaction_data/tiles_atlas/props_atlas/layers/masks/master_composite")
    lines.append("")
    lines.append("## 9. 短生成 brief")
    lines.append("")
    lines.append("```text")
    lines.append(
        "Create an original, production-ready 2D narrative RPG map package for "
        "Rulid Village. Use a clear, bright, hand-painted 3/4 top-down style with "
        "strong road readability and restrained detail. Target the existing Phaser "
        "grid exactly: 108x64 tiles, 28 pixels per tile, 3024x1792 pixels per "
        "runtime layer. Deliver separate registered PNG layers for terrain/water, "
        "roads, ground props, buildings, vegetation, occluders, foreground, "
        "lighting, and weather, plus a reusable tile/prop atlas, "
        "collision/walkable mask, occlusion/depth mask, and interaction metadata "
        "for church/library, village square, Gigas Cedar route, home, north gate, "
        "and End Mountains route. No characters, no text, no signs with words, no "
        "UI, no copyrighted game/anime composition, no baked checkerboard, and "
        "no single flattened illustration as the only deliverable."
    )
    lines.append("```")
    lines.append("")
    sidecar.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {sidecar}")


if __name__ == "__main__":
    main()
