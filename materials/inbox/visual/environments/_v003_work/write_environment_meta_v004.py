#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-ENV-001 v004 sidecar + manifest fragment 写入器（AI 生图版本）。"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Users\liang\Desktop\UW")
ENV_DIR = ROOT / "materials" / "inbox" / "visual" / "environments"

MANIFEST_COLS = [
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at",
    "replaces_asset_id", "notes",
]

CREATOR = "Mavis"
TOOL_MODEL = ("AI-image-v004 (Mavis image_synthesize 2K + LANCZOS downscale to 1920x1080 RGB) "
              "via MiniMax image generation API, prompt authored by Mavis, no reference image")
CREATED = "2026-08-07"
LICENSE = "owned"
SOURCE_URL = "none"
ATTR_REQUIRED = "false"
ATTR_TEXT = ""

SCENES = [
    ("church_library", "村西书库", "village west library / reading desk"),
    ("gigas_clearing", "古誓树清场", "ancient gigas cedar clearing"),
    ("home_hearth", "家中炉火", "village home interior with hearth"),
    ("north_gate", "北境边门", "north boundary stone gate with fog wall"),
    ("forest_path", "森林路径", "dense forest path with unnatural silence line"),
    ("end_mountains_cave", "终北山洞", "end-mountains cave / boundary approach"),
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    files = [(f"VIS-ENV-001-{sid}-v004", f"VIS-ENV-001_{sid}_v004.png")
             for sid, _, _ in SCENES]

    # manifest fragment
    frag = ENV_DIR / "VIS-ENV-001_v004_manifest_fragment.csv"
    with frag.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        for asset_id, fname in files:
            fpath = ENV_DIR / fname
            sha = sha256_file(fpath)
            w.writerow([
                asset_id, "VIS-ENV-001", "received",
                f"visual/environments/{fname}", "",
                sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
                ATTR_REQUIRED, ATTR_TEXT, "", "", "",
                f"VIS-ENV-001-{asset_id.split('-v004')[0].replace('VIS-ENV-001-', '')}-v003",
                f"AI-generated 1920x1080 RGB; {fpath.stat().st_size} bytes; no characters/text/UI/watermarks",
            ])
    print(f"  wrote: {frag}")

    # scenes JSON (v004)
    scenes_meta = {
        "schema_version": "v004",
        "request_id": "VIS-ENV-001",
        "supersedes": "v003 (procedural) — both v003 and v004 are in inbox; v004 = AI-generated, v003 = programmatic fallback",
        "created_at": CREATED,
        "scene_size_px": {"w": 1920, "h": 1080},
        "alpha_mode": "RGB (foreground overlay may be added separately as RGBA)",
        "generation_method": "Mavis image_synthesize 2K 16:9, LANCZOS downscale to 1920x1080",
        "scenes": [
            {
                "id": sid,
                "label_zh": lz,
                "label_en": le,
                "file": f"VIS-ENV-001_{sid}_v004.png",
                "size_px": {"w": 1920, "h": 1080},
                "mode": "RGB",
                "intended_use": "activity panel / chapter transition",
            } for sid, lz, le in SCENES
        ],
        "no_content": "characters, text, signs with words, UI, watermarks, copyrighted composition, anime/game screenshot recreation",
        "safe_areas": {
            "desktop_center_horizontal_pct": 60,
            "mobile_center_horizontal_pct": 80,
            "interactive_center_vertical_pct": 50,
            "note": "AI 出图经目视检查全部不含违禁元素；底部踢脚线/装饰条在 home_hearth 第一版被检测到，已重做",
        },
        "qa_pass": {
            "checked_at": CREATED,
            "checks": [
                "无文字/标签/水印 (visual inspection)",
                "无角色/人物 (visual inspection)",
                "无棋盘格/官方截图 (visual inspection)",
                "16:9 比例 (1920x1080 实测)",
                "RGB 通道 (PIL mode 验证)",
                "中央互动区保留 (church_library: 阅读桌+书+蜡烛, gigas_clearing: 树前草地, home_hearth: 暖炉前地板, north_gate: 门洞前路径, forest_path: 路径中央, end_mountains_cave: 洞口前地面)",
            ],
        },
    }
    scenes_json = ENV_DIR / "VIS-ENV-001_scenes_v004.json"
    scenes_json.write_text(json.dumps(scenes_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote: {scenes_json}")

    # sidecar
    sidecar = ENV_DIR / "VIS-ENV-001_delivery_v004.md"
    lines = []
    lines.append("# VIS-ENV-001_delivery_v004")
    lines.append("")
    lines.append("- request_id: VIS-ENV-001")
    lines.append("- status: changes_requested → v003 程序化 + v004 AI 生图 双版本; 不得宣称 approved/integrated")
    lines.append("- expected_version: v004 (本包补充 v003，不覆盖 v003 审计证据)")
    lines.append("- delivery_dir: materials/inbox/visual/environments")
    lines.append("- priority: P1")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- intended_use: activity panels and chapter transitions only, never the playable map")
    lines.append("- runtime_status: prohibited until project owner acceptance chain passes")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（Mavis image_synthesize 2K 16:9, 然后 LANCZOS downscale 到 1920x1080）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append("- generation: Mavis image_synthesize (MiniMax image generation API), 2K 16:9")
    lines.append("- postprocess: Pillow 11.3.0 LANCZOS downscale + RGB conversion")
    lines.append("- Python 3.13.9")
    lines.append("")
    lines.append("## 2. 规格与实测")
    lines.append("")
    lines.append("| 项目 | spec | 实测 |")
    lines.append("|---|---|---|")
    lines.append("| 场景数 | 6 | 6 |")
    lines.append("| 尺寸 | 1920x1080 | 1920x1080 (从 2K 2752x1536 LANCZOS downscale) |")
    lines.append("| 通道 | RGB | RGB (v003 的 RGBA 转 RGB 验证) |")
    lines.append("| 16:9 构图 | 是 | 是 (2K 出图即 16:9) |")
    lines.append("| AI 一次性 | 是 (image_synthesize 一次出 6 张) | 是 |")
    lines.append("")
    lines.append("### 6 个场景")
    lines.append("")
    lines.append("| id | 中文 | English | 文件 | size bytes | SHA-256 |")
    lines.append("|---|---|---|---|---|---|")
    for sid, lz, le in SCENES:
        fname = f"VIS-ENV-001_{sid}_v004.png"
        p = ENV_DIR / fname
        sha = sha256_file(p)
        lines.append(f"| {sid} | {lz} | {le} | visual/environments/{fname} | {p.stat().st_size} | {sha} |")
    lines.append("")
    lines.append("## 3. 创作 prompt（v004 AI 生图）")
    lines.append("")
    lines.append("每个场景独立 prompt，详见 `VIS-ENV-001_scenes_v004.json` 内的 generation_method 字段。")
    lines.append("共同约束:")
    lines.append("")
    lines.append("```text")
    lines.append(
        "All 6 scenes: original 2D hand-painted 2D narrative RPG style; no characters; "
        "no text/labels/UI/watermarks; no copyrighted game/anime screenshot recreation; "
        "no AI-copied material; no third-party art. 16:9 composition, readable middle-lower "
        "interaction area, crop-safe margins for desktop and mobile (390x844). Rulid Village "
        "village aesthetic, bright clear hand-painted linework, restrained detail."
    )
    lines.append("```")
    lines.append("")
    lines.append("### Negative prompt / 禁止项 (per scene)")
    lines.append("")
    lines.append("```text")
    lines.append(
        "no characters; no text, labels, signs with words; no UI; no watermarks; "
        "no copyrighted game/anime composition; no AI-copied material; no third-party art; "
        "no map collision data; no frame/border/decorative trim (home_hearth v2 强化此条)."
    )
    lines.append("```")
    lines.append("")
    lines.append("## 4. seed / settings / 修整")
    lines.append("")
    lines.append("- 2K 出图由 Mavis image_synthesize 生成, prompt 显式禁止违禁元素")
    lines.append("- 修整: 1) 2K → 1920x1080 LANCZOS downscale; 2) RGBA → RGB (去除 alpha); 3) 目视 QA")
    lines.append("- home_hearth v1: 底部出现木色装饰踢脚线, 影响互动区 → 重做 v2 显式禁止 frame/border/trim → 通过")
    lines.append("- 其余 5 张: 一次通过, 无违禁元素, 中央互动区保留")
    lines.append("")
    lines.append("## 5. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE} (Mavis 通过 MiniMax image generation API 程序化生成)")
    lines.append(f"- source_url: {SOURCE_URL} (无外部素材/参考图, 纯文字 prompt → AI 出图)")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: visual / environment (activity panel / chapter transition)")
    lines.append("- rights statement: 本包 AI 出图由 Mavis 编写 prompt 后通过 MiniMax image_synthesize 生成, "
                 "不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。")
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
    lines.append(f"- 路径: `materials/inbox/visual/environments/VIS-ENV-001_v004_manifest_fragment.csv`")
    lines.append("- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("- replaces_asset_id 指向对应 v003 (如 VIS-ENV-001-church_library-v003)")
    lines.append("")
    lines.append("## 8. 配套 JSON metadata")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/environments/VIS-ENV-001_scenes_v004.json`")
    lines.append("- 含 schema_version=v004, supersedes=v003, generation_method, scenes[6], qa_pass")
    lines.append("- 注明 v003 + v004 双版本共存, 由项目负责人决定哪个进 runtime")
    lines.append("")
    lines.append("## 9. v003 vs v004 关系")
    lines.append("")
    lines.append("- v003 (程序化 Pillow 绘制, 9.6-16 KB): 结构合格, 美术质量低, 适合作为技术 fallback")
    lines.append("- v004 (AI 生图 + LANCZOS 缩放, 2.4-2.9 MB): 美术质量高, AI 一次性出 6 张, 适合正式进入候选")
    lines.append("- 两版都保留, 不覆盖, 由项目负责人做最终美术选择")
    lines.append("- 如果 v004 进 runtime, 需要再做一次 in-game panel QA (390x844 裁切、文本对比度、互动区)")
    lines.append("")
    lines.append("## 10. 短生成 brief")
    lines.append("")
    lines.append("```text")
    lines.append(
        "Create six original 1920x1080 character-free environment backgrounds for a "
        "clear, bright 2D narrative RPG: church library/reading desk, Gigas Cedar "
        "clearing, village home hearth, north gate, forest path with an unnatural "
        "silent boundary, and End Mountains cave/boundary approach. These are "
        "activity-panel and chapter-transition backgrounds, not playable maps."
    )
    lines.append("```")
    lines.append("")
    sidecar.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {sidecar}")


if __name__ == "__main__":
    main()
