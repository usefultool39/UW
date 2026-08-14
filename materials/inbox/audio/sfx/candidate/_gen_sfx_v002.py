"""
AUD-SFX-001 v002 candidate generator
5 个 UI 反馈音,每个有独立时长 (180-480ms) + 各自不同音色族
- confirm: 短促上行双音 chord (200ms)
- cancel: 短促下行 sub (180ms)
- fail: 短促双音 descend (220ms)
- clue:  中长 sparkle discovery (480ms)
- relation: 中长暖色 chord (360ms)
- 全部 48kHz / 24-bit / mono / 头 0.005s fade-in / 尾 0.030s exp decay tail
- peak normalize 到 -1.0 dBFS, 实际有效时长 = 语义时长 + 30ms tail
- 写入 materials/inbox/audio/sfx/candidate/AUD-SFX-001_<name>_v002.wav
"""
import os
import numpy as np
from scipy.io import wavfile

OUT_DIR = r"C:\Users\liang\Desktop\UW\materials\inbox\audio\sfx\candidate"
SR = 48000
PEAK_TARGET = 0.89  # -1.0 dBFS

def write_wav_24bit_mono(path, samples_float):
    """samples_float: in [-1, 1]; convert to 24-bit PCM WAV"""
    peak = float(np.max(np.abs(samples_float))) if samples_float.size else 0.0
    if peak > 0:
        samples_float = samples_float * (PEAK_TARGET / peak)
    pcm = np.clip(samples_float, -1.0, 1.0)
    # 24-bit signed little-endian
    pcm_int = np.round(pcm * 8388607.0).astype(np.int32)
    # Pack as 3 bytes
    out = bytearray()
    for v in pcm_int:
        if v < 0:
            v = v + (1 << 24)
        out.append(v & 0xFF)
        out.append((v >> 8) & 0xFF)
        out.append((v >> 16) & 0xFF)
    data_size = len(out)
    file_size = 36 + data_size
    with open(path, 'wb') as f:
        f.write(b'RIFF')
        f.write(file_size.to_bytes(4, 'little'))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write((16).to_bytes(4, 'little'))
        f.write((1).to_bytes(2, 'little'))          # PCM
        f.write((1).to_bytes(2, 'little'))          # mono
        f.write(SR.to_bytes(4, 'little'))
        f.write((SR * 3).to_bytes(4, 'little'))     # byte rate
        f.write((3).to_bytes(2, 'little'))          # block align (1ch * 3byte)
        f.write((24).to_bytes(2, 'little'))         # bits per sample
        f.write(b'data')
        f.write(data_size.to_bytes(4, 'little'))
        f.write(out)

def envelope_attack_release(n_samples, attack_ms=4.0, release_ms=40.0):
    a = max(1, int(SR * attack_ms / 1000))
    r = max(1, int(SR * release_ms / 1000))
    env = np.ones(n_samples, dtype=np.float64)
    if a > 0:
        env[:a] = np.linspace(0.0, 1.0, a)
    if r > 0 and n_samples > a + r:
        env[n_samples - r:] = np.linspace(1.0, 0.001, r)
    return env

def add_reverb_tail(sig, tail_ms=30, decay=4.0):
    """在 sig 后面追加指数衰减 tail (无新激励,仅静音时的衰减)"""
    tail_n = int(SR * tail_ms / 1000)
    t = np.arange(tail_n) / SR
    tail = np.exp(-decay * t)
    # shape to match end of signal smoothly
    last_amp = abs(sig[-1]) if sig.size else 0.0
    tail = tail * last_amp
    return np.concatenate([sig, tail])

def synth_confirm():
    """短促上行双音 (200ms) — UI 确认"""
    duration_ms = 200
    n = int(SR * duration_ms / 1000)
    t = np.arange(n) / SR
    # 第一个音 660Hz (E5), 在 80ms 跳到 880Hz (A5)
    f1, f2 = 660.0, 880.0
    boundary = int(SR * 0.080)
    sig = np.zeros(n)
    sig[:boundary] = 0.65 * np.sin(2 * np.pi * f1 * t[:boundary])
    sig[boundary:] = 0.65 * np.sin(2 * np.pi * f2 * t[boundary:])
    # attack 4ms, release 30ms
    env = envelope_attack_release(n, 4, 30)
    sig = sig * env
    # tail
    sig = add_reverb_tail(sig, 25)
    return sig

def synth_cancel():
    """短促下行 sub (180ms) — 取消/后退"""
    duration_ms = 180
    n = int(SR * duration_ms / 1000)
    t = np.arange(n) / SR
    # 从 440Hz 下行到 220Hz, 一次平滑 glide
    f_start, f_end = 440.0, 220.0
    phase = 2 * np.pi * (f_start * t + (f_end - f_start) * t * t / 2)
    sig = 0.7 * np.sin(phase)
    # attack 4ms, release 30ms
    env = envelope_attack_release(n, 4, 30)
    sig = sig * env
    sig = add_reverb_tail(sig, 25)
    return sig

def synth_fail():
    """短促双音 descend (220ms) — 错误/失败"""
    duration_ms = 220
    n = int(SR * duration_ms / 1000)
    t = np.arange(n) / SR
    f1, f2 = 330.0, 220.0
    boundary = int(SR * 0.100)
    sig = np.zeros(n)
    sig[:boundary] = 0.7 * np.sin(2 * np.pi * f1 * t[:boundary])
    sig[boundary:] = 0.7 * np.sin(2 * np.pi * f2 * t[boundary:])
    # 加一点奇次谐波暗示"严肃"
    sig = sig + 0.15 * (np.sin(2 * np.pi * f2 * 2 * t) + 0.5 * np.sin(2 * np.pi * f2 * 3 * t))
    env = envelope_attack_release(n, 4, 30)
    sig = sig * env
    sig = add_reverb_tail(sig, 30)
    return sig

def synth_clue():
    """中长 sparkle discovery (480ms) — 线索发现"""
    duration_ms = 480
    n = int(SR * duration_ms / 1000)
    t = np.arange(n) / SR
    # 上升 arpeggio: C5 -> E5 -> G5 -> C6, 120ms each
    notes = [(523.25, 0.0, 0.120),
             (659.25, 0.120, 0.240),
             (783.99, 0.240, 0.360),
             (1046.50, 0.360, 0.480)]
    sig = np.zeros(n)
    for f, t0, t1 in notes:
        i0 = int(SR * t0)
        i1 = int(SR * t1)
        ti = t[i0:i1] - t0
        # main tone + sparkle harmonic
        sig[i0:i1] += 0.55 * np.sin(2 * np.pi * f * ti)
        sig[i0:i1] += 0.18 * np.sin(2 * np.pi * f * 2 * ti)
    env = envelope_attack_release(n, 4, 40)
    sig = sig * env
    sig = add_reverb_tail(sig, 30)
    return sig

def synth_relation():
    """中长暖色 chord (360ms) — 关系变化"""
    duration_ms = 360
    n = int(SR * duration_ms / 1000)
    t = np.arange(n) / SR
    # C major 三和弦 C4-E4-G4, 整体缓慢 swell
    freqs = [261.63, 329.63, 392.00]
    sig = np.zeros(n)
    for f in freqs:
        sig += 0.25 * np.sin(2 * np.pi * f * t)
        sig += 0.08 * np.sin(2 * np.pi * f * 2 * t)
    # swell: 0 -> peak 0.20s -> 0.36s
    swell = np.ones(n)
    swell[:int(SR*0.04)] = np.linspace(0, 1, int(SR*0.04))
    swell[int(SR*0.20):] = np.linspace(1, 0.001, n - int(SR*0.20))
    sig = sig * swell
    sig = add_reverb_tail(sig, 35)
    return sig

ITEMS = [
    ("confirm",  synth_confirm),
    ("cancel",   synth_cancel),
    ("fail",     synth_fail),
    ("clue",     synth_clue),
    ("relation", synth_relation),
]

def main():
    print(f"OUT_DIR = {OUT_DIR}")
    os.makedirs(OUT_DIR, exist_ok=True)
    summary = []
    for name, fn in ITEMS:
        sig = fn()
        path = os.path.join(OUT_DIR, f"AUD-SFX-001_{name}_v002.wav")
        write_wav_24bit_mono(path, sig)
        size = os.path.getsize(path)
        duration_ms = round(len(sig) / SR * 1000, 1)
        # measure peak
        peak_amp = float(np.max(np.abs(sig)))
        peak_dbfs = round(20 * np.log10(peak_amp + 1e-12), 2)
        # RMS
        rms = float(np.sqrt(np.mean(sig**2)))
        rms_dbfs = round(20 * np.log10(rms + 1e-12), 2)
        print(f"  {name:10s}  size={size:6d}B  dur={duration_ms:6.1f}ms  peak={peak_dbfs:6.2f}dBFS  rms={rms_dbfs:6.2f}dBFS")
        summary.append((name, path, size, duration_ms, peak_dbfs, rms_dbfs))
    # 写 measurements.json
    import json
    measurements = []
    for name, path, size, dur_ms, peak_dbfs, rms_dbfs in summary:
        # ebur128 integrated 需要 ffmpeg; 这里记录已知 peak/rms, integrated 由 ffmpeg 单独跑
        measurements.append({
            "file": f"AUD-SFX-001_{name}_v002.wav",
            "actual_master_file": path,
            "duration_sec": dur_ms / 1000.0,
            "sample_rate_hz": SR,
            "bit_depth": 24,
            "channels": 1,
            "peak_dbfs": peak_dbfs,
            "rms_dbfs": rms_dbfs,
            "size_bytes": size
        })
    with open(os.path.join(OUT_DIR, "measurements.json"), "w", encoding="utf-8") as f:
        json.dump(measurements, f, indent=2, ensure_ascii=False)
    print(f"\nWrote measurements.json with {len(measurements)} entries")

if __name__ == "__main__":
    main()
