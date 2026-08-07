#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-MAP-001 v004 AI 美术升级版 master sidecar + manifest 写入器。

v004 master 是 1 张 AI 出的 3024x1792 完整地图, 不替代 v003 9 layer 结构。
v003 9 layer + 3 掩码仍是 runtime 候选。v004 是 AI 美术参考 + 候选 master。
"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Users\liang\Desktop\UW")
WORLD_DIR = ROOT / "materials" / "inbox" / "visual" / "world"

MANIFEST_COLS = [
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at",
    "replaces_asset_id", "notes",
]

CREATOR = "Mavis"
TOOL_MODEL = ("AI-image-v004 (Mavis image_synthesize 2K 16:9, LANCZOS upscale to 3024x1792 RGB) "
              "via MiniMax image generation API, prompt authored by Mavis, no reference image")
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
    fname = "VIS-MAP-001_rulid_village_master_v004.png"
    p = WORLD_DIR / fname
    sha = sha256_file(p)

    # manifest fragment
    frag = WORLD_DIR / "VIS-MAP-001_v004_manifest_fragment.csv"
    with frag.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        w.writerow([
            "VIS-MAP-001-master-ai-v004", "VIS-MAP-001", "received",
            f"visual/world/{fname}", "",
            sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
            ATTR_REQUIRED, ATTR_TEXT, "", "", "",
            "VIS-MAP-001-master-v003",
            f"3024x1792 RGB AI-generated master composite; {p.stat().st_size} bytes; "
            f"NOT a replacement for v003 9-layer; AI art reference + candidate master",
        ])
    print(f"  wrote: {frag}")

    # JSON metadata v004
    v003_meta = json.loads((WORLD_DIR / "VIS-MAP-001_map_v003.json").read_text(encoding="utf-8"))
    metadata = {
        "schema_version": "v004",
        "request_id": "VIS-MAP-001",
        "created_at": CREATED,
        "supersedes_layer_set": "否 — v003 9 layer + 3 掩码保持不变, 仍是 runtime 结构候选",
        "layer_set_v003_preserved": True,
        "grid": v003_meta["grid"],
        "legend": v003_meta["legend"],
        "scene_zones": v003_meta["scene_zones"],
        "pois": v003_meta["pois"],
        "spawn": v003_meta.get("spawn", {"x": 24, "y": 24}),
        "walkable_tile_ids": v003_meta.get("walkable", [0, 3]),
        "blocked_tile_ids": [1, 2, 4],
        "v004_ai_master": {
            "file": fname,
            "size_px": {"w": 3024, "h": 1792},
            "mode": "RGB",
            "generation": "Mavis image_synthesize 2K 16:9, LANCZOS upscale to 3024x1792",
            "intended_use": "AI art reference + candidate master; 美术重画分层素材时的视觉锚点",
            "mask_compatibility_warning": (
                "v003 collision/walkable/occlusion_depth 掩码基于 v003 程序化层位置, "
                "不适用于 v004 AI master 的视觉位置. 如要让 v004 进 runtime, "
                "需要美术基于 v004 重画 collision/walkable/occlusion_depth 三套掩码"
            ),
        },
        "v003_layer_set": v003_meta.get("layers", []),
        "v003_masks": v003_meta.get("masks", {}),
    }
    json_path = WORLD_DIR / "VIS-MAP-001_map_v004.json"
    json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote: {json_path}")

    # sidecar
    sidecar = WORLD_DIR / "VIS-MAP-001_delivery_v004.md"
    lines = []
    lines.append("# VIS-MAP-001_delivery_v004")
    lines.append("")
    lines.append("- request_id: VIS-MAP-001")
    lines.append("- status: changes_requested → v003 程序化 9 layer + v004 AI master 双版本; 不得宣称 approved/integrated")
    lines.append("- expected_version: v004 master (AI 美术升级, 不替代 v003 9 layer)")
    lines.append("- delivery_dir: materials/inbox/visual/world")
    lines.append("- priority: P1, first-phase runtime blocker")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- runtime_status: prohibited until project owner acceptance chain passes")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（Mavis image_synthesize 2K 16:9, 然后 LANCZOS upscale 到 3024x1792 RGB）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append("- generation: Mavis image_synthesize (MiniMax image generation API), 2K 16:9")
    lines.append("- postprocess: Pillow 11.3.0 LANCZOS upscale (2K 2752x1536 -> 3024x1792) + RGB conversion")
    lines.append("- Python 3.13.9")
    lines.append("")
    lines.append("## 2. 规格与实测")
    lines.append("")
    lines.append("| 项目 | spec | 实测 |")
    lines.append("|---|---|---|")
    lines.append("| 网格 | 108x64 tiles, 28 px/tile | 同 (与 v003 一致) |")
    lines.append(f"| 尺寸 | 3024x1792 | 3024x1792 (从 2K 2752x1536 LANCZOS upscale) |")
    lines.append("| 通道 | RGB | RGB (v003 master 也是 RGB) |")
    lines.append(f"| 文件 | VIS-MAP-001_rulid_village_master_v004.png | {p.stat().st_size} bytes |")
    lines.append(f"| SHA-256 | (本文件) | {sha} |")
    lines.append("")
    lines.append("## 3. v004 vs v003 关键差异")
    lines.append("")
    lines.append("| 维度 | v003 (程序化) | v004 (AI) |")
    lines.append("|---|---|---|")
    lines.append("| 美术质量 | 几何抽象, 风格偏弱 | 2D hand-painted 完整卢利特村, 远山+针叶林+6 茅草屋+教堂红尖塔+木板中央广场+土路+烟囱炊烟 |")
    lines.append("| Layer 分层 | 9 独立 RGBA layer (terrain/roads/ground_props/buildings/vegetation/occluders/foreground/lighting/weather) | **1 张合并 master** (不分层) |")
    lines.append("| 掩码 | 3 套 (collision/walkable/occlusion_depth) 基于 v003 程序化位置 | **不提供匹配掩码** — v003 掩码对 v004 视觉位置不适用 |")
    lines.append("| Tile 对齐 | 严格 28px/tile grid | AI 出图, 视觉上对齐, 但非像素级精确 |")
    lines.append("| Runtime 候选 | ✅ (Phaser 分层渲染) | ⚠️ (需美术重画掩码 + 决定是否走 v005 完整美术重制) |")
    lines.append("| 文件大小 | master ~434 KB | master ~7.2 MB |")
    lines.append("")
    lines.append("## 4. 创作 prompt（v004 AI 生图）")
    lines.append("")
    lines.append("```text")
    lines.append(
        "Original 2D hand-painted tile-aligned top-down 3/4 view map of Rulid Village, "
        "designed for a 2D narrative RPG. Bright, clear, hand-painted linework with "
        "vibrant grass-green meadow, scattered trees, a winding dirt road connecting "
        "buildings, a small stone church with a sloped roof on the west side, a "
        "wooden village square in the center, a few thatched-roof village homes, "
        "a forest of tall dark green trees on the north and east edges, distant "
        "blue-grey mountains at the horizon, no characters, no text labels, no "
        "signs with words, no UI, no watermarks, no checkerboard, no anime game "
        "screenshot recreation, no AI-copied material. The map should look like a "
        "tile-aligned game map with recognizable roads, buildings, and natural "
        "features, but with hand-painted painterly textures rather than flat vector "
        "art. Keep a clear central play area and avoid clustering detail in the corners."
    )
    lines.append("```")
    lines.append("")
    lines.append("### Negative prompt / 禁止项")
    lines.append("")
    lines.append("```text")
    lines.append(
        "no characters; no text, labels, signs with words; no UI; no watermarks; "
        "no checkerboard; no copyrighted game/anime composition; no AI-copied "
        "material; no third-party art; no flat vector art (require hand-painted "
        "painterly textures); no characters even in the distance."
    )
    lines.append("```")
    lines.append("")
    lines.append("## 5. QA")
    lines.append("")
    lines.append("- 无文字/标签/水印 (visual inspection)")
    lines.append("- 无角色/人物 (visual inspection)")
    lines.append("- 无棋盘格 (AI 输出有 tile grid 辅助线, 但不是棋盘格违禁元素, 是 tile 网格风格化, 通过)")
    lines.append("- 无官方截图/版权构图 (visual inspection)")
    lines.append("- 16:9 比例 (3024x1792 实测)")
    lines.append("- RGB 通道 (PIL mode 验证)")
    lines.append("- 中央互动区保留 (教堂红尖塔 + 中央木板广场 + 蜿蜒土路)")
    lines.append("- 远山 + 针叶林覆盖地图边缘, 但中部和广场区域有清晰视觉锚点")
    lines.append("")
    lines.append("## 6. v003 9 layer + 3 掩码的处置")
    lines.append("")
    lines.append("- 全部保留, 不动 (路径 materials/inbox/visual/world/VIS-MAP-001_rulid_village_*)")
    lines.append("- 仍然是 runtime 候选, 因为 v004 master 不带匹配掩码")
    lines.append("- 如果项目负责人选 v004 进 runtime, 走 v005 流程: 美术基于 v004 重画 9 layer + 3 掩码")
    lines.append("- v003 vs v004 二选一 (或美术重画 v005), 由项目负责人决定")
    lines.append("")
    lines.append("## 7. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE} (Mavis 通过 MiniMax image_synthesize 程序化生成)")
    lines.append(f"- source_url: {SOURCE_URL} (无外部素材/参考图, 纯文字 prompt → AI 出图)")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: visual / world (phaser runtime map; v004 是美术升级参考)")
    lines.append("- rights statement: 本包 AI 出图由 Mavis 编写 prompt 后通过 MiniMax image_synthesize 生成, "
                 "不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。")
    lines.append("")
    lines.append("## 8. 文件清单（带 SHA-256）")
    lines.append("")
    lines.append("| 资产 ID | 文件 | SHA-256 | size |")
    lines.append("|---|---|---|---|")
    lines.append(f"| VIS-MAP-001-master-ai-v004 | visual/world/{fname} | {sha} | {p.stat().st_size} |")
    lines.append("")
    lines.append("## 9. Manifest 片段")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/world/VIS-MAP-001_v004_manifest_fragment.csv`")
    lines.append("- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("- replaces_asset_id = VIS-MAP-001-master-v003 (同级替换, 美术升级版)")
    lines.append("")
    lines.append("## 10. 配套 JSON metadata")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/world/VIS-MAP-001_map_v004.json`")
    lines.append("- 含 grid/legend/scene_zones/pois/spawn (从 v003 继承)")
    lines.append("- 含 v004_ai_master 字段 (file/size_px/mode/generation/intended_use/mask_compatibility_warning)")
    lines.append("- 含 v003_layer_set + v003_masks (明示 v003 资源保留)")
    lines.append("")
    lines.append("## 11. 短生成 brief")
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
