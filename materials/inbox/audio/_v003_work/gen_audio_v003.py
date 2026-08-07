#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v003 音频生成器：BGM-002 / BGM-003 / AMB-002。

输出：48kHz/24-bit/stereo PCM WAV master + 192kbps OGG Vorbis runtime。
响度：EBU R128 (ffmpeg loudnorm 二阶段)。
循环：文件内首尾 4 秒 raised-cosine 交叉淡化（loop_safe=true），同包版本等长。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import wave as wave_open
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy import signal

ROOT = Path(r"C:\Users\liang\Desktop\UW")
BGM_DIR = ROOT / "materials" / "inbox" / "audio" / "bgm"
AMB_DIR = ROOT / "materials" / "inbox" / "audio" / "ambience"
WORK_DIR = ROOT / "materials" / "inbox" / "audio" / "_v003_work"

SR = 48000
BITS = 24
PEAK_24 = 2 ** 23 - 1  # 24-bit signed max for 32-bit container
FFMPEG = "ffmpeg"

# EBU R128 目标
BGM_LUFS = -18.0  # 范围 -20..-17, 取 -18
BGM_TP_DBTP = -2.0  # spec ≤ -1，留裕度
AMB_LUFS = -23.0  # 范围 -26..-22, 取 -23
AMB_TP_DBTP = -3.0  # spec ≤ -2，留裕度

OGG_BR_A = "192k"  # 范围 160-224 kbps
OGG_MINRATE = "160k"
OGG_MAXRATE = "224k"


# ----------------------------- 通用工具 -----------------------------

def db_to_linear(db: float) -> float:
    return 10.0 ** (db / 20.0)


def to_stereo(audio: np.ndarray, sr: int, width: float = 0.08) -> np.ndarray:
    if audio.ndim == 2:
        return audio
    delay = int(sr * 0.0012)  # ~1.2 ms
    left = audio
    right = np.zeros_like(audio)
    if delay < len(audio):
        right[delay:] = audio[:-delay]
    right = right * (1 - width) + audio * width
    return np.stack([left, right], axis=1)


def make_loop_xfade(audio: np.ndarray, sr: int, fade_sec: float = 4.0) -> np.ndarray:
    """文件本身首尾 raised-cosine 交叉淡化，使音频自身可无缝循环。"""
    fade = int(fade_sec * sr)
    if len(audio) < fade * 2 + sr:
        return audio
    env = 0.5 * (1.0 + np.cos(np.linspace(0.0, np.pi, fade)))
    audio = audio.copy()
    tail = audio[-fade:] * env
    head = audio[:fade] * (1.0 - env)
    audio[:fade] += tail
    return audio[:-fade]


def pink_noise(n: int, rng: np.random.Generator, amp: float = 1.0) -> np.ndarray:
    """Voss-McCartney 粉噪近似。"""
    rows = 16
    cols = int(np.ceil(n / rows))
    white = rng.standard_normal((rows, cols))
    pink = np.cumsum(white, axis=0)
    pink -= pink.mean(axis=0, keepdims=True)
    out = pink.flatten()[:n]
    m = np.max(np.abs(out))
    if m > 0:
        out = out / m
    return out * amp


def highpass(x: np.ndarray, cutoff_hz: float, sr: int, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, cutoff_hz / (sr / 2), btype="high")
    return signal.filtfilt(b, a, x)


def lowpass(x: np.ndarray, cutoff_hz: float, sr: int, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, cutoff_hz / (sr / 2), btype="low")
    return signal.filtfilt(b, a, x)


def bandpass(x: np.ndarray, lo: float, hi: float, sr: int, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, [lo / (sr / 2), hi / (sr / 2)], btype="band")
    return signal.filtfilt(b, a, x)


def write_wav_24bit(path: Path, data: np.ndarray) -> None:
    """24-bit PCM stereo WAV（32-bit 容器）。data shape (N,2) float in [-1, 1]."""
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    pcm = np.clip(data, -1.0, 1.0) * PEAK_24
    pcm = pcm.astype(np.int32)
    with wave_open.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)  # 24-bit
        w.setframerate(SR)
        # 交错写入 L/R
        interleaved = np.empty(pcm.shape[0] * 2, dtype=np.int32)
        interleaved[0::2] = pcm[:, 0]
        interleaved[1::2] = pcm[:, 1]
        out = bytearray()
        for v in interleaved:
            v = int(v) & 0xFFFFFF
            out += bytes((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF))
        w.writeframes(bytes(out))


def write_ogg(wav_path: Path, ogg_path: Path) -> Dict[str, float]:
    """写 OGG Vorbis，bitrate 限制在 160-224 kbps。返回 {bitrate_bps, duration_sec}。"""
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-i", str(wav_path),
        "-c:a", "libvorbis",
        "-b:a", OGG_BR_A, "-minrate", OGG_MINRATE, "-maxrate", OGG_MAXRATE,
        "-ar", str(SR), "-ac", "2",
        str(ogg_path),
    ]
    subprocess.run(cmd, check=True)
    # 实测
    probe = subprocess.run([
        FFMPEG + "probe" if False else "ffprobe", "-v", "error",
        "-show_format", str(ogg_path),
    ], capture_output=True, text=True, encoding="utf-8", errors="replace")
    info: Dict[str, float] = {}
    for line in probe.stdout.splitlines():
        s = line.strip()
        if s.startswith("bit_rate="):
            try:
                info["bitrate_bps"] = float(s.split("=", 1)[1])
            except ValueError:
                pass
        elif s.startswith("duration="):
            try:
                info["duration_sec"] = float(s.split("=", 1)[1])
            except ValueError:
                pass
    return info


def measure_lufs(wav_path: Path) -> Dict[str, float]:
    """用 ffmpeg ebur128 解析 JSON 风格输出。"""
    cmd = [
        FFMPEG, "-hide_banner", "-nostats",
        "-i", str(wav_path),
        "-af", "ebur128=peak=true",
        "-f", "null", "-",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = p.stderr
    # 解析 I: / LRA: / Peak:  (ffmpeg ebur128 的 summary)
    integrated = None
    tp_db = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            # I:         -18.3 LUFS
            try:
                integrated = float(line.split()[1])
            except (IndexError, ValueError):
                pass
        elif line.startswith("Peak:"):
            # Peak:      -1.2 dBFS
            try:
                tp_db = float(line.split()[1])
            except (IndexError, ValueError):
                pass
    return {"integrated_lufs": integrated, "true_peak_dbtp": tp_db}


def loudnorm_pass(wav_in: Path, wav_out: Path, target_i: float, target_tp: float,
                  measured_i: float, measured_tp: float, measured_lra: float,
                  measured_thresh: float) -> None:
    """两阶段 loudnorm 修正。"""
    filter_str = (
        f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:"
        f"measured_I={measured_i}:measured_TP={measured_tp}:"
        f"measured_LRA={measured_lra}:measured_thresh={measured_thresh}:"
        f"linear=true:print_format=summary"
    )
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-i", str(wav_in),
        "-af", filter_str,
        "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le",
        str(wav_out),
    ]
    subprocess.run(cmd, check=True)


def normalize_to_target(wav_in: Path, wav_out: Path, target_i: float, target_tp: float) -> Dict[str, float]:
    """两遍 loudnorm，先测量再 apply。"""
    # 第一遍：测量
    cmd1 = [
        FFMPEG, "-hide_banner", "-nostats",
        "-i", str(wav_in),
        "-af", f"loudnorm=I={target_i}:TP={target_tp}:LRA=11:print_format=json",
        "-f", "null", "-",
    ]
    p = subprocess.run(cmd1, capture_output=True, text=True, encoding="utf-8", errors="replace")
    summary = p.stderr.splitlines()
    # 找第一行 { 和最后一行 }
    json_start = None
    json_end = None
    for i, line in enumerate(summary):
        s = line.strip()
        if json_start is None and s.startswith("{"):
            json_start = i
        if json_start is not None and s == "}":
            json_end = i
            break
    if json_start is None or json_end is None:
        raise RuntimeError(f"loudnorm 第一遍未返回 JSON: {p.stderr[-500:]}")
    block = "\n".join(summary[json_start:json_end + 1])
    data = json.loads(block)
    measured_i = float(data.get("input_i", target_i))
    measured_tp = float(data.get("input_tp", target_tp))
    measured_lra = float(data.get("input_lra", 11))
    measured_thresh = float(data.get("input_thresh", -34))

    # 第二遍：应用
    loudnorm_pass(wav_in, wav_out, target_i, target_tp,
                  measured_i, measured_tp, measured_lra, measured_thresh)
    return {
        "measured_i_first_pass": measured_i,
        "measured_tp_first_pass": measured_tp,
        "measured_lra_first_pass": measured_lra,
        "measured_thresh_first_pass": measured_thresh,
    }


# ----------------------------- BGM 内容合成 -----------------------------

def karplus_strong(freq: float, dur: float, sr: int, amp: float = 1.0,
                   damping: float = 0.5) -> np.ndarray:
    N = max(2, int(sr / freq))
    samples = int(dur * sr)
    buf = np.random.uniform(-1.0, 1.0, N)
    out = np.zeros(samples)
    for i in range(samples):
        out[i] = buf[i % N]
        buf[i % N] = damping * (buf[i % N] + buf[(i + 1) % N]) * 0.5
    env = np.exp(-np.arange(samples) / (sr * (0.3 + 1.5 / freq * 200)))
    return out * env * amp


def bgm_002_boundary(version: str, dur_sec: float) -> np.ndarray:
    """BGM-002：边界调查。restrained、sparse、不和谐、负空间。"""
    rng = np.random.default_rng(3001 if version == "a" else 3002)
    n = int(dur_sec * SR)
    out = np.zeros(n)

    # 1) 稀疏短句：每 5-9 秒一次铃/木音，刻意错拍
    bell_freqs = [392.0, 440.0, 523.25, 587.33, 698.46]  # G4 A4 C5 D5 F5
    t = 3.0
    while t < dur_sec - 2.0:
        f = rng.choice(bell_freqs) * (0.998 + rng.random() * 0.004)  # 微微走调
        dur = 0.6 + rng.random() * 0.8
        pluck = karplus_strong(f, dur, SR, amp=0.18 * (0.5 + rng.random() * 0.5),
                               damping=0.5)
        s0 = int(t * SR)
        s1 = min(s0 + len(pluck), n)
        out[s0:s1] += pluck[:s1 - s0]
        t += 4.0 + rng.random() * 5.0

    # 2) 极低底噪/空气感（间断风），不连续
    base = pink_noise(n, rng, amp=1.0)
    base = lowpass(base, 240, SR, order=2)
    base = base * 0.07
    # 加一个慢 LFO 让风"呼吸"
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.06 * np.arange(n) / SR)
    out += base * lfo

    # 3) 极稀疏、隐晦的 dissonant pad：低八度 D + 微偏高 Bb
    tt = np.arange(n) / SR
    f1, f2 = 73.42, 116.54  # D2, Bb2 (不和谐小三度/三全音感)
    pad = (np.sin(2 * np.pi * f1 * tt) * 0.5 + np.sin(2 * np.pi * f2 * tt) * 0.4
           + np.sin(2 * np.pi * f1 * 1.003 * tt) * 0.3)
    pad = lowpass(pad, 220, SR, order=2)
    out += pad * 0.05

    # 4) 中间 1-2 次鸟/风"缺失"暗示：突然一段更安静
    if version == "a":
        gap_start = int(0.62 * dur_sec * SR)
        gap_end = int(0.74 * dur_sec * SR)
    else:
        gap_start = int(0.45 * dur_sec * SR)
        gap_end = int(0.55 * dur_sec * SR)
    if gap_end - gap_start > 0:
        env = np.ones(n)
        env[gap_start:gap_end] = 0.35
        # 渐入渐出
        ramp = int(0.5 * SR)
        env[gap_start:gap_start + ramp] = np.linspace(1.0, 0.35, ramp)
        env[gap_end - ramp:gap_end] = np.linspace(0.35, 1.0, ramp)
        out *= env

    # 5) 远处不稳呼吸：~每 11-17 秒一次极轻的窄带噪声 burst
    t = 7.0
    while t < dur_sec - 2.0:
        burst = pink_noise(int(1.2 * SR), rng, amp=1.0)
        burst = bandpass(burst, 800, 1600, SR, order=2)
        e = np.exp(-np.arange(len(burst)) / SR * 2.5)
        burst = burst * e * 0.04
        s0 = int(t * SR)
        s1 = min(s0 + len(burst), n)
        out[s0:s1] += burst[:s1 - s0]
        t += 11.0 + rng.random() * 6.0

    # 安全
    out = np.clip(out, -0.9, 0.9)
    return out


def bgm_003_relationship(version: str, dur_sec: float) -> np.ndarray:
    """BGM-003：日常关系。温暖但不甜腻，节奏温柔前进。"""
    rng = np.random.default_rng(4001 if version == "a" else 4002)
    n = int(dur_sec * SR)
    out = np.zeros(n)

    # 1) 轻柔拨弦主旋律：五声音阶，每 1.4-2.2 秒一次
    base = 220.00  # A3
    ratios = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2, 9 / 4, 5 / 2]
    notes = [base * r for r in ratios]
    t = 1.5
    last_note = None
    while t < dur_sec - 2.0:
        # 避免连续相同音符
        choices = [n_ for n_ in notes if n_ != last_note]
        f = rng.choice(choices)
        last_note = f
        dur = 1.2 + rng.random() * 1.0
        amp = 0.16 * (0.6 + rng.random() * 0.4)
        pluck = karplus_strong(f, dur, SR, amp=amp, damping=0.5)
        s0 = int(t * SR)
        s1 = min(s0 + len(pluck), n)
        out[s0:s1] += pluck[:s1 - s0]
        t += 0.6 + rng.random() * 1.6

    # 2) 极低 pad（A1 + E2 五度）+ 极轻颤音
    tt = np.arange(n) / SR
    pad_freqs = [55.0, 82.41, 110.0]  # A1, E2, A2
    pad = np.zeros(n)
    for f in pad_freqs:
        pad += np.sin(2 * np.pi * f * tt) / len(pad_freqs)
    pad = lowpass(pad, 280, SR, order=2)
    lfo = 1 + 0.025 * np.sin(2 * np.pi * 0.11 * tt)
    out += pad * lfo * 0.07

    # 3) 极低底噪（避免死寂）
    base = pink_noise(n, rng, amp=1.0)
    base = lowpass(base, 300, SR, order=2)
    out += base * 0.006

    # 4) 偶尔远处小物件：高音不规则短 burst（不构成可识别旋律）
    t = 4.0
    while t < dur_sec - 2.0:
        dur = int((0.4 + rng.random() * 0.5) * SR)
        f = 2000 + rng.random() * 1500
        x = np.arange(dur) / SR
        chirp = np.sin(2 * np.pi * f * x) * np.exp(-x * 6)
        s0 = int(t * SR)
        s1 = min(s0 + dur, n)
        out[s0:s1] += chirp[:s1 - s0] * 0.025
        t += 7.0 + rng.random() * 6.0

    out = np.clip(out, -0.9, 0.9)
    return out


# ----------------------------- AMB 内容合成 -----------------------------

def amb_002_normal(dur_sec: float) -> np.ndarray:
    """AMB-002 normal：森林正常环境声（克制风 + 远鸟 + 叶 + 远枝）。"""
    rng = np.random.default_rng(5001)
    n = int(dur_sec * SR)
    out = np.zeros(n)

    # 1) 风：低通粉噪 + 慢 LFO
    pink = pink_noise(n, rng, amp=1.0)
    wind = lowpass(pink, 600, SR, order=2)
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.08 * np.arange(n) / SR
                                + rng.uniform(0, 6.28))
    out += wind * lfo * 0.20

    # 2) 远鸟：稀疏短 chirp，每 4-9 秒
    t = 2.0
    while t < dur_sec - 1.5:
        if rng.random() < 0.7:
            f0 = 1800 + rng.random() * 2500
            f1 = f0 + rng.uniform(-400, 800)
            dur = int((0.08 + rng.random() * 0.14) * SR)
            x = np.arange(dur) / SR
            freq = f0 + (f1 - f0) * x / max(x[-1], 1e-6)
            chirp = np.sin(2 * np.pi * np.cumsum(freq) / SR)
            env = np.sin(np.pi * x / max(x[-1], 1e-6)) ** 2
            s0 = int(t * SR)
            s1 = min(s0 + dur, n)
            out[s0:s1] += chirp[:s1 - s0] * env[:s1 - s0] * 0.04
        t += 4.0 + rng.random() * 5.0

    # 3) 远处叶沙沙：带通粉噪
    leaf = pink_noise(n, rng, amp=1.0)
    leaf = bandpass(leaf, 2000, 5000, SR, order=2)
    lfo2 = 0.4 + 0.6 * np.sin(2 * np.pi * 0.13 * np.arange(n) / SR + 1.2)
    out += leaf * lfo2 * 0.04

    # 4) 远细枝：每 6-12 秒一次极轻短促噪声
    t = 3.0
    while t < dur_sec - 1.0:
        dur = int((0.05 + rng.random() * 0.12) * SR)
        burst = pink_noise(dur, rng, amp=1.0)
        burst = highpass(burst, 4000, SR, order=2)
        e = np.exp(-np.arange(dur) / SR * 18)
        s0 = int(t * SR)
        s1 = min(s0 + dur, n)
        out[s0:s1] += (burst * e)[:s1 - s0] * 0.025
        t += 6.0 + rng.random() * 6.0

    # 5) 极低空气压力：30-80Hz 抬一点
    air = pink_noise(n, rng, amp=1.0)
    air = lowpass(air, 80, SR, order=2)
    out += air * 0.03

    out = np.clip(out, -0.9, 0.9)
    return out


def amb_002_silent(dur_sec: float) -> np.ndarray:
    """AMB-002 silent：不自然的"边界静默"。
    - 保留低空气压力 + 远细枝 + 部分远鸟/叶消失
    - 移除连续风/鸟/叶 LFO
    - 频段空缺：300-1800Hz 明显压制
    """
    rng = np.random.default_rng(5002)
    n = int(dur_sec * SR)
    out = np.zeros(n)

    # 1) 极低空气压力：相同 base noise 但 80Hz 以下
    air = pink_noise(n, rng, amp=1.0)
    air = lowpass(air, 80, SR, order=2)
    out += air * 0.025  # 比 normal 略弱，制造"压力"感

    # 2) 远细枝：保留但更稀、更轻
    t = 2.5
    while t < dur_sec - 1.0:
        dur = int((0.04 + rng.random() * 0.10) * SR)
        burst = pink_noise(dur, rng, amp=1.0)
        burst = highpass(burst, 4500, SR, order=2)
        e = np.exp(-np.arange(dur) / SR * 22)
        s0 = int(t * SR)
        s1 = min(s0 + dur, n)
        out[s0:s1] += (burst * e)[:s1 - s0] * 0.018
        t += 8.0 + rng.random() * 8.0

    # 3) 频段空缺：用 narrow bandstop 制造 300-1800Hz 凹陷
    # 先加入一些"中频颤动"但被陷波滤掉
    mid = pink_noise(n, rng, amp=1.0)
    # 陷波 1：300-1800
    notch = bandstop(mid, 300, 1800, SR, order=4)
    # 残留下：低频（<300）+ 高频（>1800），再衰减
    notch = lowpass(notch, 250, SR, order=2) + highpass(notch, 1900, SR, order=2)
    out += notch * 0.04

    # 4) 极稀薄、几乎不存在的远鸟：每 14-22 秒一次
    t = 5.0
    while t < dur_sec - 1.5:
        if rng.random() < 0.35:
            f0 = 1700 + rng.random() * 1500
            dur = int((0.06 + rng.random() * 0.10) * SR)
            x = np.arange(dur) / SR
            chirp = np.sin(2 * np.pi * f0 * x)
            env = np.sin(np.pi * x / max(x[-1], 1e-6)) ** 2
            s0 = int(t * SR)
            s1 = min(s0 + dur, n)
            out[s0:s1] += chirp[:s1 - s0] * env[:s1 - s0] * 0.015
        t += 14.0 + rng.random() * 8.0

    # 5) 微 DC 漂移（极轻，制造不稳定感）
    drift = np.sin(2 * np.pi * 0.04 * np.arange(n) / SR) * 0.002
    out += drift

    out = np.clip(out, -0.9, 0.9)
    return out


def bandstop(x: np.ndarray, lo: float, hi: float, sr: int, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, [lo / (sr / 2), hi / (sr / 2)], btype="bandstop")
    return signal.filtfilt(b, a, x)


# ----------------------------- 流水线 -----------------------------

def make_audio_track(name: str, mono: np.ndarray, dur_sec: float,
                     target_i: float, target_tp: float, fade_sec: float) -> Dict:
    """完整生成一个文件：loop xfade -> stereo -> loudnorm -> ogg -> measure。"""
    print(f"  [{name}] generate {dur_sec:.2f}s mono content...")
    looped = make_loop_xfade(mono, SR, fade_sec=fade_sec)
    actual_dur = len(looped) / SR
    print(f"  [{name}] looped dur={actual_dur:.2f}s, target={dur_sec:.2f}s")
    stereo = to_stereo(looped, SR)
    raw_wav = WORK_DIR / f"{name}_raw.wav"
    write_wav_24bit(raw_wav, stereo)
    print(f"  [{name}] raw wav written ({raw_wav.stat().st_size/1024:.0f} KB)")

    # loudnorm 两遍
    norm_wav = WORK_DIR / f"{name}_norm.wav"
    info = normalize_to_target(raw_wav, norm_wav, target_i, target_tp)
    print(f"  [{name}] first-pass: I={info['measured_i_first_pass']:.2f} "
          f"TP={info['measured_tp_first_pass']:.2f}")

    # 测最终
    meas = measure_lufs(norm_wav)
    print(f"  [{name}] final: I={meas['integrated_lufs']} LUFS, "
          f"TP={meas['true_peak_dbtp']} dBTP")

    # 写主文件
    if "BGM" in name:
        out_wav = BGM_DIR / f"{name}.wav"
    else:
        out_wav = AMB_DIR / f"{name}.wav"
    out_wav.write_bytes(norm_wav.read_bytes())

    # 写 OGG
    out_ogg = out_wav.with_suffix(".ogg")
    ogg_info = write_ogg(out_wav, out_ogg)
    print(f"  [{name}] ogg: {out_ogg.stat().st_size/1024:.0f} KB, "
          f"br={ogg_info.get('bitrate_bps', 0)/1000:.1f} kbps, "
          f"dur={ogg_info.get('duration_sec', 0):.2f}s")

    return {
        "name": name,
        "target_duration_sec": dur_sec,
        "actual_duration_sec": round(actual_dur, 3),
        "loop_safe": True,
        "loop_fade_sec": fade_sec,
        "loop_start_sample": 0,
        "loop_end_sample": int(actual_dur * SR),
        "target_lufs": target_i,
        "target_true_peak_dbtp": target_tp,
        "measured_lufs": meas["integrated_lufs"],
        "measured_true_peak_dbtp": meas["true_peak_dbtp"],
        "first_pass_lufs": info["measured_i_first_pass"],
        "first_pass_tp_dbtp": info["measured_tp_first_pass"],
        "first_pass_lra": info["measured_lra_first_pass"],
        "first_pass_thresh": info["measured_thresh_first_pass"],
        "sample_rate_hz": SR,
        "bit_depth": BITS,
        "channels": 2,
        "master_format": "wav",
        "runtime_format": "ogg",
        "ogg_bitrate_bps": int(ogg_info.get("bitrate_bps", 0)),
        "ogg_duration_sec": round(ogg_info.get("duration_sec", 0), 3),
    }


def gen_bgm_002() -> List[Dict]:
    print("=== BGM-002 boundary investigation ===")
    results = []
    # 两版 75-110 秒
    for ver, dur in (("a", 95.0), ("b", 88.0)):
        n = f"AUD-BGM-002_boundary_investigation_{ver}_v003"
        mono = bgm_002_boundary(ver, dur)
        results.append(make_audio_track(n, mono, dur, BGM_LUFS, BGM_TP_DBTP, fade_sec=4.0))
    return results


def gen_bgm_003() -> List[Dict]:
    print("=== BGM-003 relationship daily ===")
    results = []
    for ver, dur in (("a", 80.0), ("b", 70.0)):
        n = f"AUD-BGM-003_relationship_daily_{ver}_v003"
        mono = bgm_003_relationship(ver, dur)
        results.append(make_audio_track(n, mono, dur, BGM_LUFS, BGM_TP_DBTP, fade_sec=4.0))
    return results


def gen_amb_002() -> List[Dict]:
    print("=== AMB-002 forest silence pair ===")
    # 等长 60-90 秒
    dur = 80.0
    results = []
    n_normal = "AUD-AMB-002_forest_silence_normal_v003"
    n_silent = "AUD-AMB-002_forest_silence_silent_v003"
    mono_n = amb_002_normal(dur)
    mono_s = amb_002_silent(dur)
    results.append(make_audio_track(n_normal, mono_n, dur, AMB_LUFS, AMB_TP_DBTP, fade_sec=4.0))
    results.append(make_audio_track(n_silent, mono_s, dur, AMB_LUFS, AMB_TP_DBTP, fade_sec=4.0))
    # 检查等长
    assert abs(results[0]["actual_duration_sec"] - results[1]["actual_duration_sec"]) < 0.1, \
        "normal 与 silent 必须等长"
    return results


def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    BGM_DIR.mkdir(parents=True, exist_ok=True)
    AMB_DIR.mkdir(parents=True, exist_ok=True)

    all_results: List[Dict] = []
    all_results += gen_bgm_002()
    all_results += gen_bgm_003()
    all_results += gen_amb_002()

    # measurements_v003.json
    measurements = {
        "schema_version": "v003",
        "generated_at": "2026-08-07",
        "tool": "ffmpeg-loudnorm + ebur128 (EBU R128, two-pass)",
        "target_lufs": {"bgm": BGM_LUFS, "ambience": AMB_LUFS},
        "target_true_peak_dbtp": {"bgm": BGM_TP_DBTP, "ambience": AMB_TP_DBTP},
        "tracks": all_results,
    }
    meas_path = ROOT / "materials" / "inbox" / "audio" / "measurements_v003.json"
    meas_path.write_text(json.dumps(measurements, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote: {meas_path}")

    # audio.meta fragment v003
    meta_path = ROOT / "materials" / "inbox" / "audio" / "audio.meta_v003.fragment.json"
    meta: Dict[str, Dict] = {}
    for r in all_results:
        meta[r["name"]] = {
            "type": "bgm" if "BGM" in r["name"] else "ambience",
            "version": r["name"].split("_v003")[0].split("_")[-1],
            "duration": r["actual_duration_sec"],
            "sample_rate_hz": r["sample_rate_hz"],
            "bit_depth": r["bit_depth"],
            "channels": r["channels"],
            "lufs": r["measured_lufs"],
            "true_peak_dbtp": r["measured_true_peak_dbtp"],
            "loop_safe": r["loop_safe"],
            "loop_fade_sec": r["loop_fade_sec"],
            "loop_start_sample": r["loop_start_sample"],
            "loop_end_sample": r["loop_end_sample"],
            "master_format": r["master_format"],
            "runtime_format": r["runtime_format"],
            "ogg_bitrate_bps": r["ogg_bitrate_bps"],
            "master_file": f"bgm/{r['name']}.wav" if "BGM" in r["name"]
                            else f"ambience/{r['name']}.wav",
            "runtime_file": f"bgm/{r['name']}.ogg" if "BGM" in r["name"]
                            else f"ambience/{r['name']}.ogg",
        }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {meta_path}")


if __name__ == "__main__":
    main()
