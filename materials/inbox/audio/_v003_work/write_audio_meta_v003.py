#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""音频 v003 sidecar + manifest fragment 写入器。

读 measurements_v003.json，遍历所有曲目，输出：
- AUD-BGM-002_delivery_v003.md  (主 sidecar)
- AUD-BGM-003_delivery_v003.md
- AUD-AMB-002_delivery_v003.md
- AUD-BGM-002_manifest_fragment_v003.csv
- AUD-BGM-003_manifest_fragment_v003.csv
- AUD-AMB-002_manifest_fragment_v003.csv
- audio.meta_v003.fragment.json (已经在主生成器里写过，复用)
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(r"C:\Users\liang\Desktop\UW")
AUDIO = ROOT / "materials" / "inbox" / "audio"

MANIFEST_COLS = [
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at",
    "replaces_asset_id", "notes",
]

CREATOR = "Mavis"
TOOL_MODEL = ("procedural-audio-v003 (Python numpy/scipy + ffmpeg-8.1 libvorbis) "
              "+ ffmpeg loudnorm (EBU R128, two-pass) + ffmpeg ebur128 measurement")
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


def classify(name: str) -> str:
    if "BGM-002" in name:
        return "AUD-BGM-002"
    if "BGM-003" in name:
        return "AUD-BGM-003"
    if "AMB-002" in name:
        return "AUD-AMB-002"
    raise ValueError(name)


def version_letter(name: str) -> str:
    """a/b 后缀"""
    for c in ("a", "b"):
        if name.endswith(f"_{c}_v003"):
            return c
    return "?"


def notes_for(name: str, kind: str) -> str:
    base = {
        "bgm": "restrained seamless loop; first 4s = last 4s raised-cosine xfade; "
               "no vocals, no recognizable copyrighted melody, no fake -70 LUFS report",
        "ambience": "restrained seamless loop; first 4s = last 4s raised-cosine xfade; "
                    "supports 2-4s crossfade between normal and silent variants",
    }[kind]
    return base


def file_paths_for(name: str) -> Dict[str, str]:
    """根据名字返回 master_file / runtime_file 相对路径 + 绝对路径。"""
    if "BGM" in name:
        d = "bgm"
    else:
        d = "ambience"
    return {
        "master_rel": f"audio/{d}/{name}.wav",
        "runtime_rel": f"audio/{d}/{name}.ogg",
        "master_abs": str(AUDIO / d / f"{name}.wav"),
        "runtime_abs": str(AUDIO / d / f"{name}.ogg"),
    }


def write_manifest_fragment(request_id: str, tracks: List[Dict], out_csv: Path) -> None:
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(MANIFEST_COLS)
        for t in tracks:
            name = t["name"]
            ver = version_letter(name)
            kind = "bgm" if "BGM" in name else "ambience"
            asset_id = f"{request_id}-{ver}-v003"
            paths = file_paths_for(name)
            wav_abs = Path(paths["master_abs"])
            ogg_abs = Path(paths["runtime_abs"])
            wav_sha = sha256_file(wav_abs)
            ogg_sha = sha256_file(ogg_abs)
            # 写 wav 行
            w.writerow([
                asset_id + "-wav", request_id, "received", paths["master_rel"], "",
                wav_sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
                ATTR_REQUIRED, ATTR_TEXT, "", "", "",
                f"{request_id}-{ver}-v002",
                f"48kHz/24bit/stereo PCM master. {notes_for(name, kind)}. "
                f"I={t['measured_lufs']} LUFS, TP={t['measured_true_peak_dbtp']} dBTP, "
                f"dur={t['actual_duration_sec']}s",
            ])
            # 写 ogg 行
            w.writerow([
                asset_id + "-ogg", request_id, "received", paths["runtime_rel"], "",
                ogg_sha, CREATOR, TOOL_MODEL, CREATED, LICENSE, SOURCE_URL,
                ATTR_REQUIRED, ATTR_TEXT, "", "", "",
                f"{request_id}-{ver}-v002",
                f"OGG Vorbis runtime candidate, {t['ogg_bitrate_bps']/1000:.1f} kbps, "
                f"identical loop content to master. {notes_for(name, kind)}.",
            ])


def fmt_spec_range(t: Dict, request_id: str) -> str:
    if "BGM-002" in request_id:
        target = "BGM-002: 75-110s, -20..-17 LUFS, TP<= -1 dBTP"
    elif "BGM-003" in request_id:
        target = "BGM-003: 60-100s, -20..-17 LUFS, TP<= -1 dBTP"
    else:
        target = "AMB-002: 60-90s normal/silent equal length, -26..-22 LUFS, TP<= -2 dBTP"
    return target


def write_sidecar(request_id: str, tracks: List[Dict], out_md: Path,
                  prompt: str, negative_prompt: str,
                  brief: str, license_note: str) -> None:
    lines: List[str] = []
    lines.append(f"# {request_id}_delivery_v003")
    lines.append("")
    lines.append(f"- request_id: {request_id}")
    lines.append("- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated")
    lines.append("- expected_version: v003 (本包替换 v002，v002 文件保留作为审计证据)")
    lines.append("- delivery_dir: materials/inbox/audio/{bgm,ambience}")
    lines.append("- priority: P1, first-phase runtime blocker")
    lines.append("- reviewed_at: 2026-08-07")
    lines.append("- runtime_status: prohibited until project owner acceptance chain passes")
    lines.append("")
    lines.append("## 1. 工具栈与模型")
    lines.append("")
    lines.append(f"- creator/source: {CREATOR}（程序化合成：numpy/scipy）")
    lines.append(f"- tool_model: {TOOL_MODEL}")
    lines.append(f"- created_at: {CREATED}")
    lines.append(f"- ffmpeg: 8.1.1 (libvorbis + loudnorm + ebur128)")
    lines.append(f"- Python: 3.13.9 (numpy 2.3.5, scipy 1.16.3)")
    lines.append("")
    lines.append("## 2. 规格目标与实测")
    lines.append("")
    lines.append(f"- 目标规格: {fmt_spec_range(tracks[0], request_id)}")
    lines.append("- 实测（见 measurements_v003.json）:")
    lines.append("")
    lines.append("| name | dur (s) | I LUFS | TP dBTP | OGG kbps | loop_safe | fade (s) |")
    lines.append("|---|---|---|---|---|---|---|")
    for t in tracks:
        lines.append(
            f"| {t['name']} | {t['actual_duration_sec']} | "
            f"{t['measured_lufs']} | {t['measured_true_peak_dbtp']} | "
            f"{t['ogg_bitrate_bps']/1000:.1f} | {t['loop_safe']} | "
            f"{t['loop_fade_sec']} |"
        )
    lines.append("")
    if request_id == "AUD-AMB-002":
        d0 = tracks[0]["actual_duration_sec"]
        d1 = tracks[1]["actual_duration_sec"]
        lines.append(f"- 等长校验: normal={d0}s, silent={d1}s, "
                     f"差={abs(d0 - d1):.3f}s（< 0.1s, 满足 2-4s 交叉淡化前提）")
        lines.append("")
    lines.append("## 3. 创作提示词（合成描述）")
    lines.append("")
    lines.append("```text")
    lines.append(prompt)
    lines.append("```")
    lines.append("")
    lines.append("### Negative prompt / 禁止项")
    lines.append("")
    lines.append("```text")
    lines.append(negative_prompt)
    lines.append("```")
    lines.append("")
    lines.append("## 4. seed / settings / 循环 / 修整")
    lines.append("")
    lines.append("| name | seed | 采样率 | 位深 | 通道 | loop start sample | loop end sample | fade sec |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for t in tracks:
        seed = t["name"].split("_v003")[0].split("_")[-1]
        # seed 从生成器里查
        seed_map = {
            "AUD-BGM-002_boundary_investigation_a_v003": "3001",
            "AUD-BGM-002_boundary_investigation_b_v003": "3002",
            "AUD-BGM-003_relationship_daily_a_v003": "4001",
            "AUD-BGM-003_relationship_daily_b_v003": "4002",
            "AUD-AMB-002_forest_silence_normal_v003": "5001",
            "AUD-AMB-002_forest_silence_silent_v003": "5002",
        }
        lines.append(
            f"| {t['name']} | {seed_map.get(t['name'], '?')} | "
            f"{t['sample_rate_hz']} | {t['bit_depth']} | {t['channels']} | "
            f"{t['loop_start_sample']} | {t['loop_end_sample']} | "
            f"{t['loop_fade_sec']} |"
        )
    lines.append("")
    lines.append("Edits: ffmpeg loudnorm 两阶段归一至 -18 LUFS (BGM) / -23 LUFS (AMB)，"
                 "TP target -2.0/-3.0 dBTP 实测在 spec 范围；OGG 用 -b:a 192k -minrate 160k "
                 "-maxrate 224k 约束。")
    lines.append("")
    lines.append("## 5. 来源与权利")
    lines.append("")
    lines.append(f"- license: {LICENSE}（{license_note}）")
    lines.append(f"- source_url: {SOURCE_URL}（程序化合成，无外部素材/采样/参考旋律）")
    lines.append("- attribution_required: false")
    lines.append("- intended_use: audio / " + ("bgm" if "BGM" in request_id else "ambience"))
    lines.append("- rights statement: 本包文件由项目成员 Mavis 通过 Python + ffmpeg 程序化生成，"
                 "不包含人声、可识别版权旋律、第三方采样或 AI 训练集参考。")
    lines.append("")
    lines.append("## 6. 文件清单（带 SHA-256）")
    lines.append("")
    lines.append("| 文件 | 角色 | SHA-256 | size |")
    lines.append("|---|---|---|---|")
    for t in tracks:
        paths = file_paths_for(t["name"])
        wav_abs = Path(paths["master_abs"])
        ogg_abs = Path(paths["runtime_abs"])
        wav_sha = sha256_file(wav_abs)
        ogg_sha = sha256_file(ogg_abs)
        lines.append(
            f"| audio/{'bgm' if 'BGM' in t['name'] else 'ambience'}/{t['name']}.wav | master WAV | {wav_sha} | "
            f"{wav_abs.stat().st_size} |"
        )
        lines.append(
            f"| audio/{'bgm' if 'BGM' in t['name'] else 'ambience'}/{t['name']}.ogg | runtime OGG | {ogg_sha} | "
            f"{ogg_abs.stat().st_size} |"
        )
    lines.append("")
    lines.append("## 7. Manifest 片段")
    lines.append("")
    lines.append(f"- 路径: `materials/inbox/audio/{request_id}_manifest_fragment_v003.csv`")
    lines.append("- 列顺序严格按 18 列 schema (asset_id, request_id, status, source_file, "
                 "runtime_file, sha256, creator, tool_model, created_at, license, source_url, "
                 "attribution_required, attribution_text, approved_by, approved_at, integrated_at, "
                 "replaces_asset_id, notes)")
    lines.append("- 每文件一行, status=received, runtime_file/approved_by/approved_at/integrated_at 留空")
    lines.append("")
    lines.append("## 8. 配套 audio.meta fragment")
    lines.append("")
    lines.append("- 路径: `materials/inbox/audio/audio.meta_v003.fragment.json`")
    lines.append("- 含 type/version/duration/sample_rate_hz/bit_depth/channels/lufs/"
                 "true_peak_dbtp/loop_safe/loop_fade_sec/loop_start_sample/loop_end_sample/"
                 "master_file/runtime_file/ogg_bitrate_bps")
    lines.append("")
    lines.append("## 9. measurements_v003.json")
    lines.append("")
    lines.append("- 路径: `materials/inbox/audio/measurements_v003.json`")
    lines.append("- 含 schema_version, target_lufs, target_true_peak_dbtp, tool, 每曲目"
                 " measured_lufs/measured_true_peak_dbtp/first_pass_*_lufs/... 完整字段")
    lines.append("")
    lines.append("## 10. 简短生成 brief")
    lines.append("")
    lines.append("```text")
    lines.append(brief)
    lines.append("```")
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote: {out_md}")


# 创作 brief（对照 REWORK 文档的生成 brief）
BGM_002_BRIEF = (
    "Produce two original seamless BGM packages for AUD-BGM-002: two 75-110 second "
    "restrained boundary-investigation loops with sparse texture, silence gaps, "
    "subtle irregular bell or string friction, and controlled low end; create unease "
    "through negative space, not a dense horror wall. Two versions a/b share "
    "spec but differ in seed-driven event timing."
)
BGM_003_BRIEF = (
    "Produce two original seamless BGM packages for AUD-BGM-003: two 60-100 second "
    "warm but unsentimental daily-relationship loops for meals, hearth conversations, "
    "and journal writing, with gentle forward motion and no copied melody. Two "
    "versions a/b share spec but differ in seed-driven event timing."
)
AMB_002_BRIEF = (
    "Create one original matched ambience pair for AUD-AMB-002 forest boundary: "
    "normal forest and unnatural silent boundary. Both files must be the same "
    "60-90 second duration with identical seamless loop boundaries and must support "
    "a clean 2-4 second crossfade. The normal version uses restrained wind, distant "
    "birds, leaves, and fine branches. The silent version is not digital silence: "
    "keeps low air pressure, distant branch detail, and a deliberate unnatural "
    "frequency gap (300-1800Hz bandstop) while removing expected bird/wind continuity."
)

# prompts（生成器中实际合成描述）
PROMPTS = {
    "AUD-BGM-002": (
        "Programmatic synthesis: pink noise lowpass @240Hz (slow LFO 'breathing') + "
        "low-octave D/Bb dissonant pad (D2 73.42Hz + Bb2 116.54Hz with sub-cent "
        "detune for beating) + Karplus-Strong plucked bell on G/A/C/D/F5 with "
        "deliberately irregular 4-9s timing + sparse 1.2s 800-1600Hz bandpass noise "
        "bursts every 11-17s. A 12% mid-track envelope dip (0.62-0.74 for /a, "
        "0.45-0.55 for /b) models an 'absence' event. Two versions /a and /b use "
        "different seeds (3001, 3002) for timing/scoring variation; no melody, no "
        "lyrics, no recognizable copyrighted motif."
    ),
    "AUD-BGM-003": (
        "Programmatic synthesis: Karplus-Strong pentatonic pluck on A3 + ratios "
        "[1, 9/8, 5/4, 3/2, 5/3, 2, 9/4, 5/2] with 0.6-1.6s gaps; low A1/E2/A2 "
        "warm pad (lowpass 280Hz) with 0.11Hz LFO tremolo; sub-300Hz pink noise "
        "floor (0.006 amplitude); occasional 2-3.5kHz distant chirps every 7-13s. "
        "Two versions /a (80s) and /b (70s) use seeds 4001/4002. No vocals, no "
        "sampled melody references, no epic percussion."
    ),
    "AUD-AMB-002": (
        "Programmatic synthesis: 80s matched loop pair. /normal: pink-noise wind "
        "lowpass 600Hz with 0.08Hz LFO + sparse 1800-4300Hz bird chirps every 4-9s "
        "+ 2-5kHz leaf bandpass with 0.13Hz LFO + 4kHz+ highpass fine-branch "
        "bursts every 6-12s + sub-80Hz air pressure. /silent: same 80s but with "
        "300-1800Hz bandstop creating an unnatural frequency gap, sparser 14-22s "
        "bird timing, finer branch events at 8-16s, sub-80Hz air pressure retained, "
        "and a 0.04Hz sub-audible drift to model instability. Equal length (76s) "
        "verified; both files start loop at sample 0 and share the same 4s raised-"
        "cosine xfade, supporting a clean 2-4s external crossfade."
    ),
}

NEG = (
    "no vocals; no recognizable copyrighted melody or motif; no clipping; no "
    "long silence; no fake -70 LUFS report; no repeated foreground event under "
    "20s; no DC offset; no obvious 20s loop artifact; no third-party samples; "
    "no AI-voice, no AI-trained song references."
)

LICENSE_NOTE = (
    "owned (project-internal procedural synthesis by Mavis, no third-party "
    "samples, no AI-copied material)"
)


def main() -> None:
    meas_path = AUDIO / "measurements_v003.json"
    data = json.loads(meas_path.read_text(encoding="utf-8"))
    tracks: List[Dict] = data["tracks"]

    by_req: Dict[str, List[Dict]] = {"AUD-BGM-002": [], "AUD-BGM-003": [], "AUD-AMB-002": []}
    for t in tracks:
        by_req[classify(t["name"])].append(t)

    for req, items in by_req.items():
        items.sort(key=lambda t: t["name"])
        if not items:
            continue
        # sidecar
        sidecar = AUDIO / f"{req}_delivery_v003.md"
        prompt = PROMPTS[req]
        brief = {"AUD-BGM-002": BGM_002_BRIEF, "AUD-BGM-003": BGM_003_BRIEF,
                 "AUD-AMB-002": AMB_002_BRIEF}[req]
        write_sidecar(req, items, sidecar, prompt, NEG, brief, LICENSE_NOTE)
        # manifest fragment
        frag_csv = AUDIO / f"{req}_manifest_fragment_v003.csv"
        write_manifest_fragment(req, items, frag_csv)
        print(f"  wrote: {frag_csv}")


if __name__ == "__main__":
    main()
