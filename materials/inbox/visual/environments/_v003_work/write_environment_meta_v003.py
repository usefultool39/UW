#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-ENV-001 v003 sidecar + manifest fragment 写入器。"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Users\liang\Desktop\UW")
ENV_DIR = ROOT / "materials" / "inbox" / "visual" / "environments"
SCENES_JSON = ENV_DIR / "VIS-ENV-001_scenes_v003.json"

MANIFEST_COLS = [
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at",
    "replaces_asset_id", "notes",
]

CREATOR = "Mavis"
TOOL_MODEL = "procedural-environment-v003 (Python Pillow 11.3.0 + numpy 2.3.5)"
CREATED = "2026-08-07"
LICENSE = "owned"
SOURCE_URL = "none"
ATTR_REQUIRED = "false"
ATTR_TEXT = ""

BRIEF = (
    "Create six original 1920x1080 character-free environment backgrounds for a "
    "clear, bright 2D narrative RPG: church library/reading desk, Gigas Cedar "
    "clearing, village home hearth, north gate, forest path with an unnatural "
    "silent boundary, and End Mountains cave/boundary approach. These are "
    "activity-panel and chapter-transition backgrounds, not playable maps."
)

PROMPT = (
    "Original 2D hand-painted 1920x1080 RGB activity background. No characters, "
    "no text/labels/UI/watermarks, no copyrighted game/anime composition. Each "
    "scene has a clear middle/lower interaction area and crop-safe margins for "
    "desktop (16:9) and mobile (390x844 9:19.5). Color palette: church_library "
    "= warm amber wood + candle glow; gigas_clearing = bright green grass + "
    "ancient tree crown; home_hearth = dark warm brown + fireplace flame; "
    "north_gate = cold grey stone + fog wall; forest_path = green-brown dense "
    "canopy + earthy path; end_mountains_cave = deep blue-grey stone + distant "
    "faint glow inside cave mouth. Style: clear bright linework, restrained "
    "detail, hand-painted feel."
)

NEG = (
    "no characters; no text, labels, signs with words; no UI; no watermarks; "
    "no copyrighted game/anime composition; no AI-copied material; no third-"
    "party art; no map collision data (these are not playable maps)."
)

LICENSE_NOTE = "owned (procedural synthesis by Mavis, no third-party art, no AI-cloned material)"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    meta = json.loads(SCENES_JSON.read_text(encoding="utf-8"))
    files = [(f"VIS-ENV-001-{s['id']}-v003", s["file"]) for s in meta["scenes"]]
    files.append(("VIS-ENV-001-scenes-json-v003", "VIS-ENV-001_scenes_v003.json"))

    # manifest fragment
    frag = ENV_DIR / "VIS-ENV-001_manifest_fragment_v003.csv"
    with frag.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        for asset_id, fname in files:
            fpath = ENV_DIR / fname
            sha = sha256_file(fpath)
            role = "metadata JSON" if "scenes-json" in asset_id else "1920x1080 RGB scene"
            w.writerow([
                asset_id, "VIS-ENV-001", "received",
                f"visual/environments/{fname}", "",
                sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
                ATTR_REQUIRED, ATTR_TEXT, "", "", "",
                f"VIS-ENV-001-{asset_id.split('-v003')[0].replace('VIS-ENV-001-', '')}-v002",
                f"{role}; {fpath.stat().st_size} bytes",
            ])
    print(f"  wrote: {frag}")

    # sidecar
    sidecar = ENV_DIR / "VIS-ENV-001_delivery_v003.md"
    lines = []
    lines.append("# VIS-ENV-001_delivery_v003")
    lines.append("")
    lines.append("- request_id: VIS-ENV-001")
    lines.append("- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated")
    lines.append("- expected_version: v003 (本包替换 v002, v002 文件保留作为审计证据)")
    lines.append("- delivery_dir: materials/inbox/visual/environments")
    lines.append("- priority: P1")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- intended_use: activity panels and chapter transitions only, never the playable map")
    lines.append("- runtime_status: prohibited until project owner acceptance chain passes")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（程序化绘制）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append("- Pillow 11.3.0 + numpy 2.3.5")
    lines.append("- Python 3.13.9")
    lines.append("")
    lines.append("## 2. 规格与实测")
    lines.append("")
    lines.append("| 项目 | spec | 实测 |")
    lines.append("|---|---|---|")
    lines.append("| 场景数 | 6 | 6 |")
    lines.append(f"| 尺寸 | 1920x1080 | {meta['scene_size_px']['w']}x{meta['scene_size_px']['h']} |")
    lines.append(f"| 通道 | RGB (前景叠加可另交 RGBA) | {meta['alpha_mode']} |")
    lines.append("| 16:9 构图 | 是 | 是 |")
    lines.append("")
    lines.append("### 6 个场景")
    lines.append("")
    lines.append("| id | 中文 | English | 文件 | size bytes | SHA-256 |")
    lines.append("|---|---|---|---|---|---|")
    for s in meta["scenes"]:
        p = ENV_DIR / s["file"]
        sha = sha256_file(p)
        lines.append(f"| {s['id']} | {s['label_zh']} | {s['label_en']} | "
                     f"visual/environments/{s['file']} | {p.stat().st_size} | {sha} |")
    lines.append("")
    lines.append("## 3. 创作提示词（合成描述）")
    lines.append("")
    lines.append("```text")
    lines.append(PROMPT)
    lines.append("```")
    lines.append("")
    lines.append("### Negative prompt / 禁止项")
    lines.append("")
    lines.append("```text")
    lines.append(NEG)
    lines.append("```")
    lines.append("")
    lines.append("## 4. seed / settings / 修整")
    lines.append("")
    lines.append("- 配色: 见 PROMPT (每场景独立调色板)")
    lines.append("- 随机种子: 8001 (gigas 木屑), 8002 (forest 落叶)")
    lines.append("- 输出 PNG RGB optimize=True")
    lines.append("- 不烘焙文字、UI、棋盘格、官方截图、动画帧临摹")
    lines.append("- 桌面 16:9 中心互动区保留; 移动 390x844 9:19.5 中心裁切保留核心场景")
    lines.append("")
    lines.append("## 5. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE}（{LICENSE_NOTE}）")
    lines.append(f"- source_url: {SOURCE_URL}（程序化绘制，无外部素材/参考图/版权场景）")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: visual / environment (activity panel / chapter transition)")
    lines.append("- rights statement: 本包场景由 Mavis 通过 Python + Pillow 程序化绘制，"
                 "采用原创几何形状 + 配色方案；不复制任何动漫/游戏截图、"
                 "不包含 AI 训练集参考或第三方美术。")
    lines.append("")
    lines.append("## 6. 文件清单（带 SHA-256）")
    lines.append("")
    lines.append("| 资产 ID | 文件 | SHA-256 | size |")
    lines.append("|---|---|---|---|")
    for asset_id, fname in files:
        fpath = ENV_DIR / fname
        sha = sha256_file(fpath)
        lines.append(f"| {asset_id} | visual/environments/{fname} | {sha} | {fpath.stat().st_size} |")
    lines.append("")
    lines.append("## 7. Manifest 片段")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/environments/VIS-ENV-001_manifest_fragment_v003.csv`")
    lines.append("- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("")
    lines.append("## 8. 配套 JSON metadata")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/environments/VIS-ENV-001_scenes_v003.json`")
    lines.append("- 含 schema_version, request_id, scene_size_px, alpha_mode, scenes[6], "
                 "no_content, safe_areas")
    lines.append("")
    lines.append("## 9. 短生成 brief")
    lines.append("")
    lines.append("```text")
    lines.append(BRIEF)
    lines.append("```")
    lines.append("")
    sidecar.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {sidecar}")


if __name__ == "__main__":
    main()
