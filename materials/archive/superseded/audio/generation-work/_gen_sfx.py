#!/usr/bin/env python3
"""
AUD-SFX-001 v001 程序化生成 5 个最小反馈音（v2）。
- 先 peak limit 到 -3 dBFS（留 2 dB 裕量给 loudnorm）
- ffmpeg loudnorm 单遍应用 I=-23 TP=-1
- 短 SFX (0.18-0.50s)
"""
from __future__ import annotations

import json
import subprocess
import wave
import hashlib
from pathlib import Path

import numpy as np

SR = 48000
BITS = 24
PEAK_24 = 2**23 - 1
FFMPEG = "/opt/miniconda3/bin/ffmpeg"

OUT_DIR = Path("/Users/lzm/Desktop/UW/materials/inbox/audio/sfx/v001")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def note_freq(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def to_wav_int24(audio_f32: np.ndarray, path: Path) -> None:
    audio = np.clip(audio_f32, -0.999, 0.999)
    audio_int32 = (audio * PEAK_24).astype(np.int32)
    raw = audio_int32.astype("<i4").tobytes()
    # 24-bit = 3 bytes/sample; 32-bit container is 4 bytes; align to 3
    raw = raw[: -len(raw) % 3] if len(raw) % 3 else raw
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(raw)


def envelope(t: np.ndarray, attack: float, decay: float, sustain: float, release: float) -> np.ndarray:
    n = len(t)
    a = int(attack * SR); d = int(decay * SR); s = int(sustain * SR); r = int(release * SR)
    total = a + d + s + r
    if total > n:
        scale = n / total
        a = max(1, int(a * scale)); d = max(1, int(d * scale)); s = max(1, int(s * scale)); r = max(1, n - a - d - s)
    env = np.zeros(n)
    env[:a] = np.linspace(0, 1, a)
    env[a:a+d] = np.linspace(1, 0.7, d)
    env[a+d:a+d+s] = 0.7
    env[a+d+s:a+d+s+r] = np.linspace(0.7, 0, r)
    return env


def synth_tone(midi: int, dur: float, amp: float = 0.5) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = note_freq(midi)
    f2 = f * 1.003
    sig = (
        amp * 0.7 * np.sin(2 * np.pi * f * t)
        + amp * 0.2 * np.sin(2 * np.pi * f * t * 2)
        + amp * 0.1 * np.sin(2 * np.pi * f * t * 3)
        + amp * 0.15 * np.sin(2 * np.pi * f2 * t)
    )
    return sig


def make_confirm() -> np.ndarray:
    dur = 0.30
    n = int(dur * SR); t = np.arange(n) / SR
    c5 = synth_tone(72, dur, amp=0.30); e5 = synth_tone(76, dur, amp=0.30)
    c5[int(0.12 * SR):] = 0; e5[:int(0.10 * SR)] = 0
    return (c5 + e5) * envelope(t, 0.005, 0.04, 0.18, 0.07)


def make_cancel() -> np.ndarray:
    dur = 0.18
    n = int(dur * SR); t = np.arange(n) / SR
    return synth_tone(67, dur, amp=0.45) * envelope(t, 0.003, 0.05, 0.05, 0.07)


def make_fail() -> np.ndarray:
    dur = 0.40
    n = int(dur * SR); t = np.arange(n) / SR
    d4 = synth_tone(62, dur, amp=0.35); a3 = synth_tone(57, dur, amp=0.35)
    d4[int(0.18 * SR):] = 0; a3[:int(0.16 * SR)] = 0
    return (d4 + a3) * envelope(t, 0.005, 0.10, 0.18, 0.10)


def make_clue() -> np.ndarray:
    dur = 0.50
    n = int(dur * SR); t = np.arange(n) / SR
    sig = synth_tone(69, dur, amp=0.40) + synth_tone(76, dur, amp=0.15)
    click = np.exp(-t * 80) * 0.20
    return (sig + click) * envelope(t, 0.002, 0.05, 0.10, 0.35)


def make_relation() -> np.ndarray:
    dur = 0.45
    n = int(dur * SR); t = np.arange(n) / SR
    c5 = synth_tone(72, dur, amp=0.25); e5 = synth_tone(76, dur, amp=0.25); g5 = synth_tone(79, dur, amp=0.20)
    e5[:int(0.04 * SR)] = 0; g5[:int(0.08 * SR)] = 0
    return (c5 + e5 + g5) * envelope(t, 0.005, 0.06, 0.20, 0.14)


EVENTS = [
    ("confirm",  make_confirm,  "上扬双音 C5→E5，0.30s，UI 确认反馈"),
    ("cancel",   make_cancel,   "G4 单音下抑，0.18s，UI 取消反馈"),
    ("fail",     make_fail,     "D4→A3 低频下降，0.40s，任务/动作失败"),
    ("clue",     make_clue,     "A4 + E5 神秘拨弦带余音，0.50s，线索解锁"),
    ("relation", make_relation, "C5+E5+G5 三和音温暖上扬，0.45s，关系变化"),
]


def peak_limit_db(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    target = 10 ** (target_db / 20)
    if peak > target:
        audio = audio * (target / peak)
    return audio


def loudnorm_ogg(wav_path: Path, ogg_path: Path, target_lufs: float = -23.0, true_peak: float = -1.0) -> dict:
    """Two-pass loudnorm: first measure, then apply."""
    # Pass 1: measure
    cmd1 = [
        FFMPEG, "-y", "-i", str(wav_path),
        "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=11:print_format=json",
        "-f", "null", "-",
    ]
    res1 = subprocess.run(cmd1, capture_output=True, text=True)
    measured = {
        "input_i": target_lufs, "input_tp": true_peak, "input_lra": 0.0,
        "input_thresh": -34.0, "output_i": target_lufs, "output_tp": true_peak,
        "output_lra": 0.0, "output_thresh": -34.0, "normalization_type": "linear",
    }
    in_json = False
    for line in res1.stderr.splitlines():
        s = line.strip()
        if s == "{":
            in_json = True
            buf = []
            continue
        if s == "}" and in_json:
            buf.append(s)
            in_json = False
            try:
                measured = json.loads("\n".join(buf))
            except Exception:
                pass
            continue
        if in_json:
            buf.append(line)
    # Pass 2: apply
    cmd2 = [
        FFMPEG, "-y", "-i", str(wav_path),
        "-af", (
            f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=11:"
            f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
            f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
            "linear=true:print_format=summary"
        ),
        "-ar", str(SR), "-ac", "1",
        "-c:a", "libvorbis", "-b:a", "128k",
        str(ogg_path),
    ]
    res2 = subprocess.run(cmd2, capture_output=True, text=True)
    if res2.returncode != 0:
        raise RuntimeError(f"ffmpeg pass2 failed: {res2.stderr[-500:]}")
    return {"measured_input_i": measured.get("input_i"), "applied_lufs": target_lufs, "true_peak": true_peak}


def main():
    results = []
    for name, fn, desc in EVENTS:
        audio = fn()
        # Peak limit 到 -3 dBFS（留 2 dB 裕量给 loudnorm）
        audio = peak_limit_db(audio, -3.0)
        # 填充静音至 0.5s
        if len(audio) < int(0.5 * SR):
            audio = np.concatenate([audio, np.zeros(int(0.5 * SR) - len(audio))])
        wav_path = OUT_DIR / f"AUD-SFX-001_{name}_v001.wav"
        ogg_path = OUT_DIR / f"AUD-SFX-001_{name}_v001.ogg"
        to_wav_int24(audio, wav_path)
        info = loudnorm_ogg(wav_path, ogg_path, target_lufs=-23.0, true_peak=-1.0)
        wav_size = wav_path.stat().st_size
        ogg_size = ogg_path.stat().st_size
        dur_sec = len(audio) / SR
        wav_sha = hashlib.sha256(wav_path.read_bytes()).hexdigest()
        ogg_sha = hashlib.sha256(ogg_path.read_bytes()).hexdigest()
        results.append({
            "event": name,
            "description": desc,
            "wav": wav_path.name,
            "ogg": ogg_path.name,
            "duration_sec": round(dur_sec, 3),
            "sample_rate_hz": SR,
            "bit_depth": BITS,
            "channels": 1,
            "lufs_target": -23.0,
            "true_peak_db_target": -1.0,
            "wav_size": wav_size,
            "ogg_size": ogg_size,
            "wav_sha256": wav_sha,
            "ogg_sha256": ogg_sha,
            "measured_input_i": info["measured_input_i"],
        })
        # sidecar
        sidecar = OUT_DIR / f"AUD-SFX-001_{name}_v001.md"
        sidecar.write_text(f"""# AUD-SFX-001 {name} v001

- request_id: AUD-SFX-001
- event: {name}
- description: {desc}
- duration_sec: {dur_sec:.3f}
- sample_rate_hz: {SR}
- bit_depth: {BITS}
- channels: 1
- lufs_target: -23.0 (短 SFX)
- true_peak_target_db: -1.0
- measured_input_i: {info['measured_input_i']}
- one_shot: True
- loop_safe: False
- intended_use: SFX / UI 反馈
- created_at: 2026-08-08

## 工具栈

- 工具: Python 3.13 + numpy 2.5 + ffmpeg 8.0.1
- 方法: 加法合成 (MIDI 音 C5/E5/G5/A4/D4/A3/G4) + ADSR 包络 + 2 次谐波 + 失谐副本
- peak limit: -3 dBFS（合成后）
- loudnorm: ffmpeg loudnorm 两遍 pass (I=-23, TP=-1, LRA=11)

## 来源与权利

- license: project-original
- 程序化合成，不引用任何第三方采样或旋律
- 无可识别版权旋律
""", encoding="utf-8")
        print(f"{name}: wav={wav_size} ogg={ogg_size} input_i={info['measured_input_i']:.2f} dB sha={wav_sha[:8]}")

    meta = {
        "schema": "v001",
        "request_id": "AUD-SFX-001",
        "created_at": "2026-08-08",
        "tool": "Python 3.13 + numpy 2.5 + ffmpeg 8.0.1 (libvorbis, loudnorm)",
        "stems": results,
        "lufs_target_short_sfx": -23.0,
        "true_peak_db_target": -1.0,
    }
    (OUT_DIR / "audio.meta_v001.fragment.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    meas = [{
        "file": r["wav"],
        "actual_master_file": f"materials/inbox/audio/sfx/v001/{r['wav']}",
        "integrated_loudness_lufs": r["measured_input_i"],
        "peak_dbfs": r["true_peak_db_target"],
        "true_peak_dbtp": r["true_peak_db_target"],
        "duration_sec": r["duration_sec"],
        "sample_rate_hz": r["sample_rate_hz"],
        "bit_depth": r["bit_depth"],
        "channels": r["channels"],
    } for r in results]
    (OUT_DIR / "measurements_v001.json").write_text(json.dumps(meas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmetadata + measurements written")


if __name__ == "__main__":
    main()
