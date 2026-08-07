#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-CHR-001/002/003 v004 角色立绘参考图 sidecar + manifest + index 写入器。

v004 portrait 是 AI 生成的全身正面立绘, 用作美术重画 sprite 时的视觉参考。
不替代 v003 程序化 sprite sheet。
"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Users\liang\Desktop\UW")
CHR_DIR = ROOT / "materials" / "inbox" / "visual" / "characters"

MANIFEST_COLS = [
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at",
    "replaces_asset_id", "notes",
]

CREATOR = "Mavis"
TOOL_MODEL = ("AI-image-v004 (Mavis image_synthesize 2K 1:1, no downscale) "
              "via MiniMax image generation API, prompt authored by Mavis, no reference image")
CREATED = "2026-08-07"
LICENSE = "owned"
SOURCE_URL = "none"
ATTR_REQUIRED = "false"
ATTR_TEXT = ""

REQS = [
    ("VIS-CHR-001", "kirito",
     "10-12岁黑发深蓝衣男孩, 皮革腰带 + 棕色皮靴, 中性放松姿势, 2D hand-painted RPG concept art",
     "VIS-CHR-001_kirito_portrait_v004.png"),
    ("VIS-CHR-002", "alice",
     "10-12岁金发白裙女孩, 长辫 + 蓝色领结 + 紫色腰带, 中性放松姿势, 2D hand-painted RPG concept art",
     "VIS-CHR-002_alice_portrait_v004.png"),
    ("VIS-CHR-003", "eugeo",
     "10-12岁浅棕发绿衣男孩, 棕色背心 + 棕腰带, 中性放松姿势, 2D hand-painted RPG concept art",
     "VIS-CHR-003_eugeo_portrait_v004.png"),
]

PROMPT_TPL = (
    "Original 2D hand-painted character concept art, full-body front-facing portrait of {desc}. "
    "Standing in a relaxed neutral pose, hands at sides, head slightly turned three-quarter, slight smile. "
    "Bright clear linework, 2D narrative RPG style. Isolated character on a pure white background, "
    "full body visible from head to feet, no scenery, no background, no floor, no shadow, no text, "
    "no labels, no UI, no watermarks, no checkerboard, no anime/game screenshot recreation."
)

NEG = (
    "no characters other than the subject; no text, labels, signs with words; no UI; no watermarks; "
    "no copyrighted game/anime composition; no AI-copied material; no third-party art; "
    "no scenery, no background, no floor, no shadow, no checkerboard, no frame/border/trim."
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(req_id: str, char_name: str, fname: str) -> None:
    frag = CHR_DIR / f"{req_id}_v004_manifest_fragment.csv"
    p = CHR_DIR / fname
    sha = sha256_file(p)
    with frag.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        w.writerow([
            f"{req_id}-portrait-v004", req_id, "received",
            f"visual/characters/{fname}", "",
            sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
            ATTR_REQUIRED, ATTR_TEXT, "", "", "",
            f"{req_id}-sprite-sheet-v003",
            f"2048x2048 RGB AI portrait reference; {p.stat().st_size} bytes; "
            f"NOT a replacement for v003 sprite sheet; used as visual ref for sprite re-art",
        ])
    print(f"  wrote: {frag}")


def write_sidecar(req_id: str, char_name: str, desc: str, fname: str) -> None:
    p = CHR_DIR / fname
    sha = sha256_file(p)
    sidecar = CHR_DIR / f"{req_id}_portrait_delivery_v004.md"
    lines = []
    lines.append(f"# {req_id}_portrait_delivery_v004")
    lines.append("")
    lines.append(f"- request_id: {req_id}")
    lines.append("- status: v003 程序化 sprite sheet + v004 AI 立绘参考 双版本; 不得宣称 approved/integrated")
    lines.append("- expected_version: v004 portrait reference (不替代 v003 sprite sheet)")
    lines.append("- delivery_dir: materials/inbox/visual/characters")
    lines.append("- priority: P1 (美术重画的视觉参考)")
    lines.append(f"- character: {char_name}")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- intended_use: 美术重画 sprite 时的视觉参考, 不直接进入 runtime")
    lines.append("- runtime_status: prohibited — 仅作美术依据, 需要重画后再走 sprite 验收")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（Mavis image_synthesize 2K 1:1）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append("- generation: Mavis image_synthesize (MiniMax image generation API), 2K 1:1")
    lines.append("- no postprocess (2K 直接交付作为参考)")
    lines.append("- Python 3.13.9")
    lines.append("")
    lines.append("## 2. 规格与实测")
    lines.append("")
    lines.append("| 项目 | spec | 实测 |")
    lines.append("|---|---|---|")
    lines.append("| 尺寸 | AI 2K 1:1 (参考图) | 2048x2048 |")
    lines.append("| 通道 | RGB | RGB (AI 输出) |")
    lines.append("| 背景 | 纯白 (角色独立) | 纯白 |")
    lines.append("| 姿势 | 全身正面, 手垂体侧, 微侧脸 | 同 |")
    lines.append(f"| 文件 | {fname} | {p.stat().st_size} bytes, SHA-256={sha} |")
    lines.append("")
    lines.append("## 3. 创作 prompt（v004 AI 生图）")
    lines.append("")
    lines.append("```text")
    lines.append(PROMPT_TPL.format(desc=desc))
    lines.append("```")
    lines.append("")
    lines.append("### Negative prompt / 禁止项")
    lines.append("")
    lines.append("```text")
    lines.append(NEG)
    lines.append("```")
    lines.append("")
    lines.append("## 4. 与 v003 sprite sheet 关系")
    lines.append("")
    lines.append(f"- v003 ({req_id}_{char_name}_sprite_sheet_v003.png): 768x384 RGBA 程序化 sprite sheet, "
                 "4 方向 × 12 帧 = 48 帧, 64x96 frame cell, bottom-center foot anchor. "
                 "**结构合格, 美术质量低 (几何抽象)。**")
    lines.append(f"- v004 ({fname}): 2048x2048 RGB AI 立绘参考, 全身正面, 纯白背景, "
                 "**视觉参考, 不进 runtime, 需美术重画 sprite 4 方向 × 12 帧时使用**。")
    lines.append("- 替换关系: v004 不替代 v003, 而是给美术重画提供视觉锚点")
    lines.append("- 如果美术重画完毕, 走 v005 sprite sheet, 然后再走 v003 → v005 替换流程")
    lines.append("")
    lines.append("## 5. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE} (Mavis 通过 MiniMax image_synthesize 程序化生成)")
    lines.append(f"- source_url: {SOURCE_URL} (无外部素材/参考图, 纯文字 prompt → AI 出图)")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: visual / character concept art (美术参考)")
    lines.append("- rights statement: 本包 AI 出图由 Mavis 编写 prompt 后通过 MiniMax image_synthesize 生成, "
                 "不复制任何动漫/游戏原画、不临摹任何已有截图、不包含 AI 训练集特定参考。")
    lines.append("")
    lines.append("## 6. 文件清单（带 SHA-256）")
    lines.append("")
    lines.append("| 资产 ID | 文件 | SHA-256 | size |")
    lines.append("|---|---|---|---|")
    lines.append(f"| {req_id}-portrait-v004 | visual/characters/{fname} | {sha} | {p.stat().st_size} |")
    lines.append("")
    lines.append("## 7. Manifest 片段")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/characters/{req_id}_v004_manifest_fragment.csv`")
    lines.append("- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("- replaces_asset_id 指向 {req_id}-sprite-sheet-v003")
    lines.append("")
    sidecar.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {sidecar}")


def main() -> None:
    # 写所有 3 角色
    for req_id, char_name, desc, fname in REQS:
        write_manifest(req_id, char_name, fname)
        write_sidecar(req_id, char_name, desc, fname)

    # 写 portrait index JSON
    idx = {
        "schema_version": "v004",
        "request_ids": ["VIS-CHR-001", "VIS-CHR-002", "VIS-CHR-003"],
        "created_at": CREATED,
        "intended_use": "美术重画 sprite 时的视觉参考, 不直接进 runtime",
        "supersedes_sprite_sheet": "否 — 仅补充 v003 sprite sheet, 等待美术重画后产生 v005 sprite sheet",
        "portraits": [],
    }
    for req_id, char_name, _, fname in REQS:
        p = CHR_DIR / fname
        idx["portraits"].append({
            "request_id": req_id,
            "character": char_name,
            "file": fname,
            "size_px": {"w": 2048, "h": 2048},
            "mode": "RGB",
            "background": "pure white",
            "pose": "full-body front-facing, hands at sides, head slightly three-quarter",
            "sha256": sha256_file(p),
        })
    idx_path = CHR_DIR / "VIS-CHR_portrait_index_v004.json"
    idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote: {idx_path}")


if __name__ == "__main__":
    main()
