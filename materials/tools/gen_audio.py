#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUD-BGM-001 / AUD-AMB-001 程序化音频生成器。

输出：
  audio/bgm/AUD-BGM-001_village_dawn_<a|b>_v001.wav + .ogg
  audio/ambience/AUD-AMB-001_drizzle_village_<a|b>_v001.wav + .ogg

规范（来自 01_REQUEST_CATALOG.md / 03_TECHNICAL_SPECS.md）：
  - 48 kHz / 24-bit WAV 源
  - OGG (Vorbis ~160 kbps) 运行时预览
  - 综合响度约 -18 LUFS，True Peak ≤ -1 dBTP
  - 无缝循环：首尾用 raised-cosine 交叉淡化，无点击、无呼吸断点
  - 不使用人声、采样旋律引用、史诗鼓组
"""

import json
import os
import subprocess
import wave as wave_open
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = Path("/Users/lzm/Desktop/UW/materials")
OUT = ROOT / "inbox" / "audio"
FFMPEG = "/opt/miniconda3/bin/ffmpeg"

SR = 48000
BITS = 24
# 24-bit 文件使用 32-bit 容器，峰值 -1 dBFS 对应 0x7FFFFF
PEAK = 2 ** 23 - 1
LUFS_TARGET = -18.0
TP_LIMIT = -1.0


def db_to_linear(db):
    return 10 ** (db / 20)


def normalize_lufs(audio, target_lufs=LUFS_TARGET, true_peak_limit=TP_LIMIT):
    """响度归一：RMS 增益到目标，再限制 True Peak（含 0.5 dB 裕量）。"""
    if audio.ndim > 1:
        ref = audio.mean(axis=1)
    else:
        ref = audio
    rms = np.sqrt(np.mean(ref ** 2))
    if rms == 0:
        return audio
    gain = db_to_linear(target_lufs) / rms
    audio = audio * gain
    peak = np.max(np.abs(audio))
    lim = db_to_linear(true_peak_limit - 0.5)
    if peak > lim:
        audio = audio * (lim / peak)
    return np.clip(audio, -0.999, 0.999)


def to_stereo(audio, sr, width=0.08):
    """单声道转立体声：右声道轻微延迟产生宽度，避免完全同相。"""
    if audio.ndim > 1:
        return audio
    delay = int(sr * 0.0012)  # ~1.2 ms
    left = audio
    right = np.zeros_like(audio)
    right[delay:] = audio[:-delay]
    right = right * (1 - width) + audio * width
    return np.stack([left, right], axis=1)


def make_loop(audio, sr, fade_sec=4.0):
    """在结尾 fade_sec 与开头做 raised-cosine 交叉淡化，使文件本身即可循环。"""
    fade = int(fade_sec * sr)
    if len(audio) < fade * 2:
        return audio
    env = 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade)))
    tail = audio[-fade:] * env
    head = audio[:fade] * (1 - env)
    audio = audio.copy()
    audio[:fade] += tail
    return audio[:-fade]


def pink_noise(n, amp=1.0):
    """Voss-McCartney 粉噪近似。"""
    rows = 16
    cols = int(np.ceil(n / rows))
    white = np.random.randn(rows, cols)
    pink = np.cumsum(white, axis=0)
    pink -= np.mean(pink, axis=0)
    out = pink.flatten()[:n]
    out = out / np.max(np.abs(out))
    return out * amp


def rain_on_roof(n, sr, amp=0.35):
    """屋顶细雨：中高频粉噪 + 低频木屋顶共鸣。"""
    pink = pink_noise(n, amp=1.0)
    # 高通让雨声更细
    b, a = signal.butter(2, 600 / (sr / 2), btype="high")
    rain = signal.filtfilt(b, a, pink)
    # 低频屋顶共鸣
    b2, a2 = signal.butter(1, [60 / (sr / 2), 180 / (sr / 2)], btype="band")
    roof = signal.filtfilt(b2, a2, pink)
    return rain * amp + roof * amp * 0.5


def distant_water(n, sr, amp=0.18):
    """远处水流：低通粉噪 + 缓慢振幅波动。"""
    pink = pink_noise(n, amp=1.0)
    b, a = signal.butter(2, 300 / (sr / 2), btype="low")
    water = signal.filtfilt(b, a, pink)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * np.arange(n) / sr)
    return water * lfo * amp


def wind_chime(n, sr, amp=0.08, density=0.0006):
    """稀疏风铃：随机短促正弦 burst。"""
    out = np.zeros(n)
    # 风铃五声音阶近似：G5, A5, D6, E6, A6
    freqs = [783.99, 880.00, 1174.66, 1318.51, 1760.00]
    hits = np.random.poisson(density * n)
    for _ in range(hits):
        t0 = np.random.randint(0, n - int(0.5 * sr))
        dur = int((0.4 + np.random.rand() * 0.8) * sr)
        if t0 + dur > n:
            continue
        f = np.random.choice(freqs)
        t = np.arange(dur) / sr
        env = np.exp(-t * (4 + np.random.rand() * 4))
        out[t0:t0 + dur] += np.sin(2 * np.pi * f * t) * env * amp
    return out


def sparse_birds(n, sr, amp=0.04, density=0.0003):
    """稀疏鸟鸣：短促 chirp。"""
    out = np.zeros(n)
    hits = np.random.poisson(density * n)
    for _ in range(hits):
        t0 = np.random.randint(0, n - int(0.3 * sr))
        dur = int((0.08 + np.random.rand() * 0.12) * sr)
        if t0 + dur > n:
            continue
        t = np.arange(dur) / sr
        f0 = 2000 + np.random.randint(0, 3000)
        f1 = f0 + np.random.randint(-500, 1000)
        freq = f0 + (f1 - f0) * t / t[-1]
        env = np.sin(np.pi * t / t[-1]) ** 2
        chirp = np.sin(2 * np.pi * np.cumsum(freq) / sr) * env * amp
        out[t0:t0 + dur] += chirp
    return out


def wooden_door_creak(n, sr, amp=0.05, density=0.00008):
    """偶尔木门吱呀：低通扫频噪声。"""
    out = np.zeros(n)
    hits = np.random.poisson(density * n)
    for _ in range(hits):
        t0 = np.random.randint(0, n - int(1.0 * sr))
        dur = int((0.3 + np.random.rand() * 0.5) * sr)
        if t0 + dur > n:
            continue
        t = np.arange(dur) / sr
        noise = np.random.randn(dur)
        b, a = signal.butter(2, [200 / (sr / 2), 800 / (sr / 2)], btype="band")
        noise = signal.filtfilt(b, a, noise)
        env = np.exp(-t * 3) * np.sin(np.pi * t / t[-1]).clip(0, 1) ** 0.5
        out[t0:t0 + dur] += noise * env * amp
    return out


def karplus_strong(freq, dur, sr, amp=1.0):
    """Karplus-Strong 合成木质感拨弦。"""
    N = int(sr / freq)
    if N < 2:
        N = 2
    samples = int(dur * sr)
    buf = np.random.uniform(-1, 1, N)
    out = np.zeros(samples)
    for i in range(samples):
        out[i] = buf[i % N]
        # 低通平均
        buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N])
    env = np.exp(-np.arange(samples) / (sr * (0.3 + 1.5 / freq * 200)))
    return out * env * amp


def soft_pluck_melody(n, sr, seed=1, amp=0.12):
    """轻柔拨弦旋律：使用五声音阶，节奏稀疏。"""
    rng = np.random.default_rng(seed)
    # D 大调五声音阶：D3, E3, F#3, A3, B3, D4, E4, F#4, A4
    base = 146.83  # D3
    ratios = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2, 9 / 4, 5 / 2, 3]
    notes = [base * r for r in ratios]
    out = np.zeros(n)
    # 每 1.6-2.4 秒一次拨弦
    t = 0.0
    while t < n / sr - 1.5:
        dur = 2.0 + rng.random() * 1.2
        f = rng.choice(notes)
        s0 = int(t * sr)
        pluck = karplus_strong(f, dur, sr, amp=amp * (0.6 + rng.random() * 0.4))
        s1 = min(s0 + len(pluck), n)
        out[s0:s1] += pluck[:s1 - s0]
        t += 0.6 + rng.random() * 1.2
    return out


def soft_pad(n, sr, root=146.83, amp=0.06):
    """柔和铺底：两三个低八度正弦 + 轻微失谐。"""
    t = np.arange(n) / sr
    freqs = [root, root * 1.5, root * 2, root * 2 * 1.003]
    out = np.zeros(n)
    for f in freqs:
        out += np.sin(2 * np.pi * f * t) * amp / len(freqs)
    # 缓慢颤音
    lfo = 1 + 0.03 * np.sin(2 * np.pi * 0.12 * t)
    return out * lfo


def distant_bell(n, sr, interval=8.0, amp=0.05):
    """远处钟/玻璃音：稀疏，每 interval 秒一次。"""
    out = np.zeros(n)
    f = 880.0  # A5
    t = interval
    while t < n / sr:
        s0 = int(t * sr)
        dur = int(3.0 * sr)
        if s0 + dur > n:
            break
        x = np.arange(dur) / sr
        # 钟状：基频 + 泛音 + 指数衰减
        partials = [1, 2.0, 3.0, 4.2]
        bell = sum(np.sin(2 * np.pi * f * p * x) * (0.5 ** i)
                   for i, p in enumerate(partials))
        env = np.exp(-x * 1.8)
        out[s0:s0 + dur] += bell * env * amp
        t += interval + np.random.uniform(-1.5, 2.0)
    return out


def subtle_dissonance(n, sr, amp=0.025):
    """底层不稳定音程：暗示北境异常。"""
    t = np.arange(n) / sr
    # 小三度 / 三全音混合，极慢拍频
    f1, f2 = 110.0, 146.83  # A2 vs D3（三全音感偏暖，这里选 D3 + 升 F？不，保持 D3 + A2 纯五）
    # 改为 D3 + F#3 大三，再混入微微升高的 D#3 制造拍频
    out = (np.sin(2 * np.pi * 146.83 * t) * 0.5 +
           np.sin(2 * np.pi * 185.00 * t) * 0.5 +
           np.sin(2 * np.pi * 147.85 * t) * 0.25)  # 微偏差
    # 低通让它只作为"底色"
    b, a = signal.butter(2, 250 / (sr / 2), btype="low")
    out = signal.filtfilt(b, a, out)
    return out * amp


def generate_bgm(seed=1, version="a"):
    rng = np.random.default_rng(seed)
    dur = 96 if version == "a" else 88
    n = dur * SR
    out = np.zeros(n)
    out += soft_pluck_melody(n, SR, seed=seed, amp=0.14 if version == "a" else 0.10)
    out += soft_pad(n, SR, root=146.83 if version == "a" else 110.00,
                    amp=0.055 if version == "a" else 0.075)
    out += distant_bell(n, SR, interval=10.0 if version == "a" else 14.0,
                        amp=0.035 if version == "a" else 0.05)
    out += subtle_dissonance(n, SR, amp=0.018 if version == "a" else 0.025)
    # 极低底噪，避免"死寂"
    out += pink_noise(n, amp=0.004)
    return make_loop(out, SR, fade_sec=5.0)


def generate_ambience(seed=2, version="a"):
    rng = np.random.default_rng(seed)
    dur = 120 if version == "a" else 110
    n = dur * SR
    out = np.zeros(n)
    out += rain_on_roof(n, SR, amp=0.28 if version == "a" else 0.22)
    out += distant_water(n, SR, amp=0.12 if version == "a" else 0.22)
    out += wind_chime(n, SR, amp=0.06 if version == "a" else 0.04,
                      density=0.0005 if version == "a" else 0.0003)
    out += sparse_birds(n, SR, amp=0.03 if version == "a" else 0.05,
                        density=0.00025 if version == "a" else 0.0004)
    out += wooden_door_creak(n, SR, amp=0.035 if version == "a" else 0.02,
                             density=0.00008 if version == "a" else 0.00004)
    return make_loop(out, SR, fade_sec=6.0)


def write_wav(path, data):
    """直接写真 24-bit PCM WAV（wave 模块手写，避免 32→24 转换丢 48dB）。"""
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
    data = normalize_lufs(data)
    data = to_stereo(data, SR)
    pcm24 = np.clip(data, -1.0, 1.0) * PEAK
    pcm24 = pcm24.astype(np.int32)
    with wave_open.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)  # 24-bit
        w.setframerate(SR)
        interleaved = np.zeros(pcm24.shape[0] * 2, dtype=np.int32)
        interleaved[0::2] = pcm24[:, 0]
        interleaved[1::2] = pcm24[:, 1]
        # 24-bit 小端：低 3 字节
        bytes_out = bytearray()
        for v in interleaved:
            v = int(v) & 0xFFFFFF
            bytes_out += bytes((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF))
        w.writeframes(bytes(bytes_out))


def write_ogg(wav_path, ogg_path):
    subprocess.run([
        FFMPEG, "-y", "-i", str(wav_path),
        "-c:a", "libvorbis", "-q:a", "5",
        "-ar", str(SR), "-ac", "2",
        str(ogg_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    (OUT / "bgm").mkdir(parents=True, exist_ok=True)
    (OUT / "ambience").mkdir(parents=True, exist_ok=True)
    meta = {}

    for ver in ("a", "b"):
        # BGM
        bgm = generate_bgm(seed=1001 if ver == "a" else 1002, version=ver)
        name = f"AUD-BGM-001_village_dawn_{ver}_v001"
        wav = OUT / "bgm" / f"{name}.wav"
        ogg = OUT / "bgm" / f"{name}.ogg"
        write_wav(wav, bgm)
        write_ogg(wav, ogg)
        meta[name] = {"type": "bgm", "duration": round(len(bgm) / SR, 2), "version": ver}

        # Ambience
        amb = generate_ambience(seed=2001 if ver == "a" else 2002, version=ver)
        name = f"AUD-AMB-001_drizzle_village_{ver}_v001"
        wav = OUT / "ambience" / f"{name}.wav"
        ogg = OUT / "ambience" / f"{name}.ogg"
        write_wav(wav, amb)
        write_ogg(wav, ogg)
        meta[name] = {"type": "ambience", "duration": round(len(amb) / SR, 2), "version": ver}

    (OUT / "audio.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print("Audio generated:")
    for k, v in meta.items():
        print(f"  {k}: {v['duration']}s {v['type']}")


if __name__ == "__main__":
    main()
