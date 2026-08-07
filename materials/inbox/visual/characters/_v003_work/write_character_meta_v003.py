#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIS-CHR-001/002/003 v003 sidecar + manifest fragment 写入器。"""

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
TOOL_MODEL = "procedural-character-v003 (Python Pillow 11.3.0 + numpy 2.3.5)"
CREATED = "2026-08-07"
LICENSE = "owned"
SOURCE_URL = "none"
ATTR_REQUIRED = "false"
ATTR_TEXT = ""

REQS = [
    ("VIS-CHR-001", "kirito", "黑发深蓝衣的卢利特村男孩"),
    ("VIS-CHR-002", "alice", "金发白裙的卢利特村女孩"),
    ("VIS-CHR-003", "eugeo", "浅棕发绿衣的卢利特村男孩"),
]

# 角色级 描述
BRIEF = (
    "Three original production sprite packages for a bright, readable 2D narrative "
    "RPG: Kirito, Alice, and Eugeo as children in Rulid Village. Use one consistent "
    "frame cell size (64x96 px) across all characters. For each character and each "
    "direction down/left/right/up, create idle 2 frames, walk 6 distinct frames, "
    "and interact 4 distinct frames. Deliver non-interlaced 8-bit RGBA sprite sheets "
    "whose decoded pixels contain both transparent background and visible character "
    "pixels. Include no checkerboard, no background, no baked shadow, no text, no "
    "scenery. Lock every frame to the same bottom-center foot anchor and consistent "
    "body scale. Characters must remain recognizable at 44-52 pixels tall."
)

PROMPT = (
    "Original stylized child character sprite, top-down 3/4 view, 64x96 frame cell, "
    "non-interlaced 8-bit RGBA with real alpha (no checkerboard, no background). "
    "Anatomically simplified: head (~16px wide sphere with hair covering forehead), "
    "torso (~14x22 rectangle with two-tone clothing + center accent), arms (3px "
    "wide rectangles attached at shoulder y=body_top-8, hand 5px ellipse at end), "
    "legs (4px wide rectangles + 6px shoes at bottom). Bottom-center foot anchor at "
    "(32, 92) is identical across all 48 frames per character. Walk cycle: 6 frames "
    "with two-leg alternating phase (0:left-forward, 3:right-forward, 6:return) + "
    "1px body bounce on transition frames. Interact: 4 frames right-arm raise "
    "(0:rest, 1:lift+8, 2:lift+14, 3:lower+4). Idle: 2 frames 1px breathing. "
    "Down view shows two eyes + nose hint; up view shows hair only; left/right "
    "side shows one eye and side hair. Color palette per character: Kirito dark "
    "blue/black, Alice white/blue, Eugeo green/brown."
)

NEG = (
    "no checkerboard; no opaque RGB pretending to be alpha; no single pose per "
    "animation name; no anime frames copied; no game sprite cloning; no baked "
    "shadow; no background; no text; no UI; no scenery; no AI-copied material; "
    "no third-party art."
)

LICENSE_NOTE = "owned (procedural synthesis by Mavis, no third-party art, no AI-cloned material)"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest_frag(req_id: str, char_name: str) -> None:
    frag = CHR_DIR / f"{req_id}_manifest_fragment_v003.csv"
    sheet = CHR_DIR / f"{req_id}_{char_name}_sprite_sheet_v003.png"
    js = CHR_DIR / f"{req_id}_frames_v003.json"
    with frag.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        w.writerow([
            f"{req_id}-sprite-sheet-v003", req_id, "received",
            f"visual/characters/{sheet.name}", "",
            sha256_file(sheet), CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
            ATTR_REQUIRED, ATTR_TEXT, "", "", "",
            f"{req_id}-sprite-sheet-v002",
            f"768x384 RGBA sprite sheet (4 directions x 12 frames); "
            f"non-interlaced 8-bit alpha; {sheet.stat().st_size} bytes",
        ])
        w.writerow([
            f"{req_id}-frames-json-v003", req_id, "received",
            f"visual/characters/{js.name}", "",
            sha256_file(js), CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
            ATTR_REQUIRED, ATTR_TEXT, "", "", "",
            "",
            f"Frame manifest: rect, animation, index, duration_ms, fps, anchor, footprint",
        ])
    print(f"  wrote: {frag}")


def write_sidecar(req_id: str, char_name: str, desc: str) -> None:
    sheet = CHR_DIR / f"{req_id}_{char_name}_sprite_sheet_v003.png"
    js = CHR_DIR / f"{req_id}_frames_v003.json"
    frame_data = json.loads(js.read_text(encoding="utf-8"))
    sidecar = CHR_DIR / f"{req_id}_delivery_v003.md"
    lines = []
    lines.append(f"# {req_id}_delivery_v003")
    lines.append("")
    lines.append(f"- request_id: {req_id}")
    lines.append("- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated")
    lines.append("- expected_version: v003 (本包替换 v002, v002 文件保留作为审计证据)")
    lines.append("- delivery_dir: materials/inbox/visual/characters")
    lines.append("- priority: P1, first-phase runtime blocker")
    lines.append(f"- character: {char_name} ({desc})")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- runtime_status: prohibited until project owner acceptance chain passes")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（程序化绘制，每个像素由 Pillow 计算）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append("- Pillow 11.3.0")
    lines.append("- Python 3.13.9")
    lines.append("")
    lines.append("## 2. 规格与实测")
    lines.append("")
    lines.append("| 项目 | spec | 实测 |")
    lines.append("|---|---|---|")
    lines.append(f"| Frame cell | 64x96 | {frame_data['frame_cell_px']['w']}x{frame_data['frame_cell_px']['h']} |")
    lines.append(f"| Sheet 总尺寸 | 一角色一 sheet (4 方向 × 12 帧) | {frame_data['sheet_px']['w']}x{frame_data['sheet_px']['h']} |")
    lines.append(f"| 方向 | down/left/right/up | {','.join(frame_data['directions'])} |")
    lines.append(f"| idle 帧数 | 2 | {frame_data['animations']['idle']['frames']} |")
    lines.append(f"| walk 帧数 | 6 | {frame_data['animations']['walk']['frames']} |")
    lines.append(f"| interact 帧数 | 4 | {frame_data['animations']['interact']['frames']} |")
    lines.append(f"| 锚点 | bottom-center, 锁死 (32, 92) | {frame_data['anchor']} |")
    lines.append(f"| collision footprint | 12x4 底部居中 | {frame_data['collision_footprint']} |")
    lines.append(f"| 通道 | RGBA, 8-bit, 非隔行 | {frame_data['alpha_mode']} |")
    lines.append(f"| 总帧数 | 4×(2+6+4)=48 帧 | {len(frame_data['frames'])} |")
    lines.append("")
    lines.append("## 3. 动画参数")
    lines.append("")
    lines.append("| animation | frames | fps | duration_ms | loop |")
    lines.append("|---|---|---|---|---|")
    for a, info in frame_data["animations"].items():
        lines.append(f"| {a} | {info['frames']} | {info['fps']} | {info['duration_ms']} | {info['loop']} |")
    lines.append("")
    lines.append("## 4. 创作提示词（合成描述）")
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
    lines.append("## 5. seed / settings / 修整")
    lines.append("")
    lines.append("- 配色: Kirito=深蓝/黑, Alice=白/金/蓝, Eugeo=绿/棕 (procedurally drawn)")
    lines.append("- 帧 cell 64x96 全部角色一致; bottom-center foot anchor (32, 92) 锁死")
    lines.append("- walk 6 帧使用 sin/cos 周期相位 (idx/6) 驱动两腿前后 + 1px 弹跳")
    lines.append("- interact 4 帧右臂/前臂 raise: [0, 8, 14, 4] 像素 y 偏移")
    lines.append("- idle 2 帧: 1px 上下呼吸")
    lines.append("- 输出 PNG RGBA optimize=True, non-interlaced alpha")
    lines.append("")
    lines.append("## 6. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE}（{LICENSE_NOTE}）")
    lines.append(f"- source_url: {SOURCE_URL}（程序化绘制，无外部素材/参考图/版权角色）")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: visual / character sprite (phaser runtime)")
    lines.append("- rights statement: 本包 sprite 由 Mavis 通过 Python + Pillow 程序化绘制，"
                 "采用原创几何形状 + 配色方案；不复制任何动漫/游戏原帧、"
                 "不包含 AI 训练集参考或第三方美术。")
    lines.append("")
    lines.append("## 7. 文件清单（带 SHA-256）")
    lines.append("")
    lines.append("| 资产 | 文件 | SHA-256 | size |")
    lines.append("|---|---|---|---|")
    lines.append(f"| {req_id}-sprite-sheet-v003 | visual/characters/{sheet.name} | "
                 f"{sha256_file(sheet)} | {sheet.stat().st_size} |")
    lines.append(f"| {req_id}-frames-json-v003 | visual/characters/{js.name} | "
                 f"{sha256_file(js)} | {js.stat().st_size} |")
    lines.append("")
    lines.append("## 8. Manifest 片段")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/visual/characters/{req_id}_manifest_fragment_v003.csv`")
    lines.append("- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("")
    lines.append("## 9. 短生成 brief")
    lines.append("")
    lines.append("```text")
    lines.append(BRIEF)
    lines.append("```")
    lines.append("")
    sidecar.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {sidecar}")


def main() -> None:
    for req_id, char_name, desc in REQS:
        write_manifest_frag(req_id, char_name)
        write_sidecar(req_id, char_name, desc)


if __name__ == "__main__":
    main()
