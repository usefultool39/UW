#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""音频响度校准：以 ffmpeg loudnorm 测量为反馈，迭代调整增益直到
integrated ≈ -18 LUFS 且 True Peak ≤ -1.5 dBTP（含裕量）。

用法：python3 tools/calibrate_audio.py
"""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path("/Users/lzm/Desktop/UW/materials")
AUD = ROOT / "inbox" / "audio"
FFMPEG = "/opt/miniconda3/bin/ffmpeg"
TARGET_I = -18.0
TP_LIMIT = -1.5


def measure(path):
    r = subprocess.run(
        [FFMPEG, "-nostats", "-i", str(path), "-af", "loudnorm=print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"\{[^}]*\}", r.stderr, re.S)
    if not m:
        return None
    d = json.loads(m.group(0))
    return float(d["input_i"]), float(d["input_tp"])


def apply_gain(path, gain_db):
    """用 ffmpeg 直接应用增益并重写 24-bit PCM，避免 scipy 24 位读写的歧义。"""
    tmp = path.with_suffix(".cal.wav")
    subprocess.run([
        FFMPEG, "-y", "-i", str(path), "-af", f"volume={gain_db:.3f}dB",
        "-c:a", "pcm_s24le", "-ar", str(path.suffix and 48000), "-ac", "2",
        str(tmp)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp.replace(path)
    return gain_db


def main():
    files = sorted((AUD / "bgm").glob("*.wav")) + sorted((AUD / "ambience").glob("*.wav"))
    for f in files:
        for it in range(3):
            m = measure(f)
            if m is None:
                print("measure failed:", f)
                break
            i, tp = m
            delta = TARGET_I - i
            # 峰值保护：若加 delta 后 TP 超限，则压缩 delta
            if tp + delta > TP_LIMIT:
                delta = TP_LIMIT - tp
            if abs(delta) < 0.2:
                print(f"{f.name:<45} iter{it}  OK  I={i:+.2f}  TP={tp:+.2f}")
                break
            apply_gain(f, delta)
        else:
            i, tp = measure(f)
            print(f"{f.name:<45} FINAL I={i:+.2f} TP={tp:+.2f} (未完全收敛)")


if __name__ == "__main__":
    main()
