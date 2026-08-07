"""
AUD-SFX-001/002 UW-UPGRADE-1.0 Sound Effects Generator
Generates UI/feedback SFX + world/activity SFX as 48kHz/24-bit WAV + OGG.
"""
import os, json, hashlib, csv, struct, wave, subprocess, tempfile, shutil
import numpy as np
from scipy import signal as sig
from pathlib import Path

SR = 48000
BIT_DEPTH = 24
BASE = Path(r"C:\Users\liang\Desktop\UW\materials\inbox\audio\sfx")
PREFIX_SFX1 = "AUD-SFX-001"
PREFIX_SFX2 = "AUD-SFX-002"
BATCH = "UW-UPGRADE-1.0"
CREATOR = "WorkBuddy AI Asset Agent"
TOOL = "Python 3.13 + numpy/scipy procedural synthesis"
CREATED_AT = "2026-08-07T18:30:00+08:00"

os.makedirs(BASE, exist_ok=True)

# ---------- helpers ----------

def save_wav_24bit(path, samples, sr=SR):
    """Save stereo float [-1,1] as 24-bit WAV."""
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 8388607).astype(np.int32)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(3)
        wf.setframerate(sr)
        raw = b"".join(
            struct.pack("<iii", int_samples[i, 0] & 0xFFFFFF | (0xFF000000 if int_samples[i, 0] < 0 else 0),
                               int_samples[i, 1] & 0xFFFFFF | (0xFF000000 if int_samples[i, 1] < 0 else 0), 0)[:3]
            + struct.pack("<i", int_samples[i, 1] & 0xFFFFFF | (0xFF000000 if int_samples[i, 1] < 0 else 0))[:3]
            for i in range(len(int_samples))
        )
        # Actually let's do it properly
        wf.close()
    # Re-do with proper 24-bit packing
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(3)
        wf.setframerate(sr)
        frames = bytearray()
        for i in range(len(int_samples)):
            for ch in range(2):
                v = int(int_samples[i, ch])
                v = max(-8388608, min(8388607, v))
                if v < 0:
                    v = v + (1 << 24)
                frames.extend(v.to_bytes(3, byteorder="little"))
        wf.writeframes(bytes(frames))

def save_wav_24bit_fast(path, samples, sr=SR):
    """Save stereo float [-1,1] as 24-bit WAV (vectorized)."""
    samples = np.clip(samples, -1.0, 1.0)
    int_s = (samples * 8388607).astype(np.int32)
    # Interleave
    inter = np.empty(len(int_s) * 2, dtype=np.int32)
    inter[0::2] = int_s[:, 0]
    inter[1::2] = int_s[:, 1]
    # Clip to 24-bit range
    inter = np.clip(inter, -8388608, 8388607)
    # Convert to unsigned 24-bit
    inter_u = inter.astype(np.uint32)
    inter_u[inter < 0] += (1 << 24)
    # Pack as 3 bytes each
    raw = np.zeros((len(inter_u), 4), dtype=np.uint8)
    raw[:, 0] = inter_u & 0xFF
    raw[:, 1] = (inter_u >> 8) & 0xFF
    raw[:, 2] = (inter_u >> 16) & 0xFF
    raw[:, 3] = 0
    raw_bytes = raw[:, :3].tobytes()
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(3)
        wf.setframerate(sr)
        wf.writeframes(raw_bytes)

def encode_ogg(wav_path, ogg_path, quality=4):
    """Encode OGG Vorbis from WAV using soundfile."""
    try:
        import soundfile as sf
        data, sr = sf.read(str(wav_path), dtype="float32")
        sf.write(str(ogg_path), data, sr, format="OGG", subtype="VORBIS")
        return True
    except Exception:
        return False

def measure_loudness(samples, sr=SR):
    """Simple RMS-based loudness estimate."""
    if samples.ndim == 1:
        samples = samples[:, np.newaxis]
    rms = np.sqrt(np.mean(samples ** 2) + 1e-12)
    lufs = 20 * np.log10(rms + 1e-12) - 0.691
    peak = np.max(np.abs(samples))
    peak_db = 20 * np.log10(peak + 1e-12)
    return round(lufs, 1), round(peak_db, 1)

def make_envelope(n, attack_s=0.005, release_s=0.05, sr=SR):
    """ADSR-like envelope: quick attack, sustain, release."""
    attack = int(attack_s * sr)
    release = int(release_s * sr)
    env = np.ones(n)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0 and release < n:
        env[-release:] = np.linspace(1, 0, release)
    return env

def apply_env(samples, attack_s=0.005, release_s=0.05, sr=SR):
    env = make_envelope(len(samples), attack_s, release_s, sr)
    if samples.ndim == 2:
        env = env[:, np.newaxis]
    return samples * env

def to_stereo(mono):
    return np.column_stack([mono, mono])

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------- SFX generators ----------

def gen_button_click():
    """Short UI click - 0.1s, crisp high freq burst with fast decay."""
    dur = 0.1
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Mix of click and body
    click = 0.5 * np.exp(-t * 80) * np.sin(2 * np.pi * 2200 * t)
    body = 0.3 * np.exp(-t * 40) * np.sin(2 * np.pi * 800 * t)
    noise = 0.15 * np.exp(-t * 120) * np.random.randn(n)
    s = click + body + noise
    s = apply_env(s, 0.001, 0.05)
    return to_stereo(s)

def gen_button_hover():
    """Subtle hover - 0.15s, soft rising tone."""
    dur = 0.15
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 600 + 400 * (t / dur)
    s = 0.2 * np.exp(-t * 15) * np.sin(2 * np.pi * freq * t)
    s = apply_env(s, 0.01, 0.08)
    return to_stereo(s)

def gen_tab_switch():
    """Tab switch - 0.2s, two-tone slide."""
    dur = 0.2
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 400 + 800 * np.sin(np.pi * t / dur)
    s = 0.3 * np.exp(-t * 10) * np.sin(2 * np.pi * freq * t)
    s = apply_env(s, 0.005, 0.1)
    return to_stereo(s)

def gen_menu_open():
    """Menu open - 0.3s, rising swoosh."""
    dur = 0.3
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 200 + 1200 * (t / dur)
    s = 0.25 * np.sin(2 * np.pi * freq * t)
    noise = 0.1 * np.exp(-t * 8) * np.random.randn(n)
    # Lowpass the noise
    b, a = sig.butter(4, 2000 / (SR / 2), btype="low")
    noise = sig.filtfilt(b, a, noise)
    s = s + noise
    s = apply_env(s, 0.01, 0.1)
    return to_stereo(s)

def gen_menu_close():
    """Menu close - 0.25s, descending swoosh."""
    dur = 0.25
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 1400 - 1000 * (t / dur)
    s = 0.25 * np.sin(2 * np.pi * freq * t)
    noise = 0.1 * np.exp(-t * 10) * np.random.randn(n)
    b, a = sig.butter(4, 2000 / (SR / 2), btype="low")
    noise = sig.filtfilt(b, a, noise)
    s = s + noise
    s = apply_env(s, 0.005, 0.12)
    return to_stereo(s)

def gen_notification():
    """Notification chime - 0.5s, two-note bell."""
    dur = 0.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    note1 = 0.3 * np.exp(-t * 5) * np.sin(2 * np.pi * 880 * t)
    note2_start = int(0.15 * SR)
    note2 = np.zeros(n)
    note2[note2_start:] = 0.3 * np.exp(-np.arange(n - note2_start) / SR * 5) * np.sin(2 * np.pi * 1320 * np.arange(n - note2_start) / SR)
    s = note1 + note2
    s = apply_env(s, 0.005, 0.15)
    return to_stereo(s)

def gen_success():
    """Success confirmation - 0.4s, rising arpeggio."""
    dur = 0.4
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for i, freq in enumerate([523, 659, 784]):
        start = int(i * 0.1 * SR)
        decay = np.exp(-np.arange(n - start) / SR * 6)
        s[start:] += 0.25 * decay * np.sin(2 * np.pi * freq * np.arange(n - start) / SR)
    s = apply_env(s, 0.005, 0.1)
    return to_stereo(s)

def gen_error():
    """Error buzz - 0.3s, low descending buzz."""
    dur = 0.3
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 200 - 80 * (t / dur)
    s = 0.35 * np.sin(2 * np.pi * freq * t)
    # Add buzz harmonics
    s += 0.1 * np.sin(2 * np.pi * freq * 3 * t)
    s = apply_env(s, 0.005, 0.08)
    return to_stereo(s)

def gen_quest_accept():
    """Quest accept - 0.5s, parchment seal sound."""
    dur = 0.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Paper crinkle
    noise = 0.15 * np.exp(-t * 6) * np.random.randn(n)
    b, a = sig.butter(4, 4000 / (SR / 2), btype="low")
    noise = sig.filtfilt(b, a, noise)
    # Seal thump
    thump = 0.3 * np.exp(-t * 25) * np.sin(2 * np.pi * 120 * t)
    # Chime
    chime = 0.2 * np.exp(-t * 4) * np.sin(2 * np.pi * 660 * t)
    s = noise + thump + chime
    s = apply_env(s, 0.005, 0.12)
    return to_stereo(s)

def gen_quest_complete():
    """Quest complete - 0.8s, triumphant short fanfare."""
    dur = 0.8
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    notes = [(0.0, 523), (0.15, 659), (0.3, 784), (0.45, 1047)]
    for start_s, freq in notes:
        start = int(start_s * SR)
        decay = np.exp(-np.arange(n - start) / SR * 3)
        s[start:] += 0.2 * decay * np.sin(2 * np.pi * freq * np.arange(n - start) / SR)
    s = apply_env(s, 0.005, 0.2)
    return to_stereo(s)

def gen_day_settle():
    """Day settlement - 1.0s, gentle bell + page turn."""
    dur = 1.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    bell = 0.2 * np.exp(-t * 2) * np.sin(2 * np.pi * 440 * t)
    bell2 = 0.1 * np.exp(-t * 2) * np.sin(2 * np.pi * 660 * t)
    # Page turn noise
    noise = 0.08 * np.exp(-t * 3) * np.random.randn(n)
    b, a = sig.butter(4, 3000 / (SR / 2), btype="low")
    noise = sig.filtfilt(b, a, noise)
    s = bell + bell2 + noise
    s = apply_env(s, 0.01, 0.3)
    return to_stereo(s)

def gen_page_turn():
    """Page turn - 0.3s, paper rustle."""
    dur = 0.3
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = 0.3 * np.random.randn(n)
    # Bandpass filter for paper sound
    b, a = sig.butter(4, [2000 / (SR / 2), 6000 / (SR / 2)], btype="band")
    noise = sig.filtfilt(b, a, noise)
    env = np.exp(-t * 12) * (1 - np.exp(-t * 50))
    s = noise * env
    s = apply_env(s, 0.002, 0.08)
    return to_stereo(s)

# --- World SFX ---

def gen_footstep_grass():
    """Grass footstep - 0.15s, soft crunch."""
    dur = 0.15
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = 0.35 * np.random.randn(n)
    b, a = sig.butter(4, [500 / (SR / 2), 2500 / (SR / 2)], btype="band")
    noise = sig.filtfilt(b, a, noise)
    env = np.exp(-t * 30) * (1 - np.exp(-t * 100))
    s = noise * env * 0.6
    s = apply_env(s, 0.001, 0.05)
    return to_stereo(s)

def gen_footstep_stone():
    """Stone footstep - 0.15s, hard click."""
    dur = 0.15
    n = int(dur * SR)
    t = np.arange(n) / SR
    click = 0.4 * np.exp(-t * 60) * np.sin(2 * np.pi * 150 * t)
    noise = 0.2 * np.exp(-t * 50) * np.random.randn(n)
    b, a = sig.butter(4, 1500 / (SR / 2), btype="high")
    noise = sig.filtfilt(b, a, noise)
    s = click + noise
    s = apply_env(s, 0.001, 0.05)
    return to_stereo(s)

def gen_footstep_wood():
    """Wood footstep - 0.15s, hollow thud."""
    dur = 0.15
    n = int(dur * SR)
    t = np.arange(n) / SR
    thud = 0.4 * np.exp(-t * 35) * np.sin(2 * np.pi * 180 * t)
    noise = 0.15 * np.exp(-t * 45) * np.random.randn(n)
    b, a = sig.butter(4, 800 / (SR / 2), btype="low")
    noise = sig.filtfilt(b, a, noise)
    s = thud + noise
    s = apply_env(s, 0.001, 0.05)
    return to_stereo(s)

def gen_door_open():
    """Door creak - 0.6s, slow wood creak."""
    dur = 0.6
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Creak: modulated sawtooth
    freq = 80 + 40 * np.sin(2 * np.pi * 3 * t)
    creak = 0.2 * sig.sawtooth(2 * np.pi * freq * t) * np.exp(-t * 2)
    # Add friction noise
    noise = 0.1 * np.random.randn(n)
    b, a = sig.butter(4, [300 / (SR / 2), 2000 / (SR / 2)], btype="band")
    noise = sig.filtfilt(b, a, noise)
    noise *= np.exp(-t * 2) * (1 - np.exp(-t * 10))
    s = creak + noise
    s = apply_env(s, 0.02, 0.15)
    return to_stereo(s)

def gen_door_close():
    """Door close - 0.4s, thud + latch."""
    dur = 0.4
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Thud at start
    thud = 0.45 * np.exp(-t * 20) * np.sin(2 * np.pi * 100 * t)
    # Latch click at end
    latch_start = int(0.3 * SR)
    latch_t = np.arange(n - latch_start) / SR
    latch = np.zeros(n)
    latch[latch_start:] = 0.3 * np.exp(-latch_t * 80) * np.sin(2 * np.pi * 1200 * latch_t)
    s = thud + latch
    s = apply_env(s, 0.002, 0.08)
    return to_stereo(s)

def gen_item_pickup():
    """Item pickup - 0.3s, light chime + rustle."""
    dur = 0.3
    n = int(dur * SR)
    t = np.arange(n) / SR
    chime = 0.25 * np.exp(-t * 8) * np.sin(2 * np.pi * 1200 * t)
    chime2 = 0.15 * np.exp(-t * 8) * np.sin(2 * np.pi * 1800 * t)
    noise = 0.08 * np.exp(-t * 15) * np.random.randn(n)
    s = chime + chime2 + noise
    s = apply_env(s, 0.003, 0.1)
    return to_stereo(s)

def gen_book_open():
    """Book open - 0.4s, cover + page."""
    dur = 0.4
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Cover creak
    cover = 0.2 * np.exp(-t * 8) * np.sin(2 * np.pi * 300 * t)
    # Page rustle
    page_start = int(0.15 * SR)
    page = np.zeros(n)
    noise = np.random.randn(n - page_start)
    b, a = sig.butter(4, [2000 / (SR / 2), 6000 / (SR / 2)], btype="band")
    noise = sig.filtfilt(b, a, noise)
    page[page_start:] = 0.15 * np.exp(-np.arange(n - page_start) / SR * 10) * noise
    s = cover + page
    s = apply_env(s, 0.005, 0.1)
    return to_stereo(s)

def gen_clue_select():
    """Clue discovery - 0.5s, cyan ping + reveal."""
    dur = 0.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Rising ping
    freq = 800 + 600 * (t / dur)
    ping = 0.3 * np.exp(-t * 4) * np.sin(2 * np.pi * freq * t)
    # Shimmer
    shimmer = 0.1 * np.exp(-t * 3) * np.sin(2 * np.pi * 2400 * t)
    s = ping + shimmer
    s = apply_env(s, 0.005, 0.15)
    return to_stereo(s)

def gen_sacred_ink():
    """Sacred arts cast - 0.8s, golden hum + ink write."""
    dur = 0.8
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Low golden hum
    hum = 0.2 * np.exp(-t * 1.5) * np.sin(2 * np.pi * 220 * t)
    hum2 = 0.15 * np.exp(-t * 1.5) * np.sin(2 * np.pi * 330 * t)
    # Ink scratch (filtered noise)
    noise = 0.12 * np.random.randn(n)
    b, a = sig.butter(4, [3000 / (SR / 2), 7000 / (SR / 2)], btype="band")
    noise = sig.filtfilt(b, a, noise)
    noise *= np.exp(-t * 1.5) * (1 - np.exp(-t * 20))
    s = hum + hum2 + noise
    s = apply_env(s, 0.02, 0.2)
    return to_stereo(s)

def gen_boundary_ripple():
    """Boundary disturbance - 0.6s, low boom + shimmer."""
    dur = 0.6
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Low boom
    boom = 0.35 * np.exp(-t * 4) * np.sin(2 * np.pi * 60 * t)
    # Shimmer
    shimmer = 0.12 * np.exp(-t * 3) * np.sin(2 * np.pi * 1800 * t)
    # Distortion noise
    noise = 0.08 * np.exp(-t * 5) * np.random.randn(n)
    b, a = sig.butter(4, 1000 / (SR / 2), btype="high")
    noise = sig.filtfilt(b, a, noise)
    s = boom + shimmer + noise
    s = apply_env(s, 0.005, 0.15)
    return to_stereo(s)

def gen_relationship_up():
    """Relationship increase - 0.4s, warm rising tone."""
    dur = 0.4
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 440 + 220 * (t / dur)
    tone = 0.25 * np.exp(-t * 5) * np.sin(2 * np.pi * freq * t)
    warm = 0.15 * np.exp(-t * 4) * np.sin(2 * np.pi * 660 * t)
    s = tone + warm
    s = apply_env(s, 0.01, 0.1)
    return to_stereo(s)

def gen_reward():
    """Reward received - 0.5s, coin/sparkle sound."""
    dur = 0.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Two-tone coin
    note1 = 0.25 * np.exp(-t * 6) * np.sin(2 * np.pi * 988 * t)
    note2_start = int(0.08 * SR)
    note2 = np.zeros(n)
    note2[note2_start:] = 0.25 * np.exp(-np.arange(n - note2_start) / SR * 6) * np.sin(2 * np.pi * 1319 * np.arange(n - note2_start) / SR)
    # Sparkle
    spark = 0.1 * np.exp(-t * 4) * np.sin(2 * np.pi * 2637 * t)
    s = note1 + note2 + spark
    s = apply_env(s, 0.003, 0.12)
    return to_stereo(s)

def gen_capture_silence():
    """Capture moment - 1.5s, convergence + impact + silence."""
    dur = 1.5
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Phase 1: Convergence (0-0.8s) - rising tones converging
    p1_end = int(0.8 * SR)
    conv_t = t[:p1_end]
    freq1 = 200 + 300 * (conv_t / 0.8)
    freq2 = 400 + 100 * (conv_t / 0.8)
    freq3 = 600 - 300 * (conv_t / 0.8)
    conv = 0.15 * np.sin(2 * np.pi * freq1 * conv_t) + 0.12 * np.sin(2 * np.pi * freq2 * conv_t) + 0.1 * np.sin(2 * np.pi * freq3 * conv_t)
    conv_env = np.linspace(0, 1, p1_end) ** 2
    conv *= conv_env
    # Phase 2: Impact (0.8-1.0s) - low thump
    p2_start = int(0.8 * SR)
    p2_end = int(1.0 * SR)
    impact_t = np.arange(p2_end - p2_start) / SR
    impact = 0.4 * np.exp(-impact_t * 10) * np.sin(2 * np.pi * 80 * impact_t)
    # Phase 3: Fade (1.0-1.5s) - ringing silence
    p3_start = int(1.0 * SR)
    p3_t = np.arange(n - p3_start) / SR
    fade = 0.08 * np.exp(-p3_t * 2) * np.sin(2 * np.pi * 1200 * p3_t)
    s = np.zeros(n)
    s[:p1_end] = conv
    s[p2_start:p2_end] += impact
    s[p3_start:] += fade
    s = apply_env(s, 0.02, 0.3)
    return to_stereo(s)

def gen_rain_drop():
    """Rain drop hit - 0.1s, tiny plink."""
    dur = 0.1
    n = int(dur * SR)
    t = np.arange(n) / SR
    plink = 0.3 * np.exp(-t * 50) * np.sin(2 * np.pi * 3000 * t)
    noise = 0.1 * np.exp(-t * 80) * np.random.randn(n)
    s = plink + noise
    s = apply_env(s, 0.001, 0.03)
    return to_stereo(s)

# ---------- SFX definitions ----------

SFX_001_UI = [
    ("button_click", "Button click", gen_button_click),
    ("button_hover", "Button hover", gen_button_hover),
    ("tab_switch", "Tab switch", gen_tab_switch),
    ("menu_open", "Menu open", gen_menu_open),
    ("menu_close", "Menu close", gen_menu_close),
    ("notification", "Notification chime", gen_notification),
    ("success", "Success confirmation", gen_success),
    ("error", "Error buzz", gen_error),
    ("quest_accept", "Quest accept", gen_quest_accept),
    ("quest_complete", "Quest complete", gen_quest_complete),
    ("day_settle", "Day settlement", gen_day_settle),
    ("page_turn", "Page turn", gen_page_turn),
]

SFX_002_WORLD = [
    ("footstep_grass", "Grass footstep", gen_footstep_grass),
    ("footstep_stone", "Stone footstep", gen_footstep_stone),
    ("footstep_wood", "Wood footstep", gen_footstep_wood),
    ("door_open", "Door open creak", gen_door_open),
    ("door_close", "Door close thud", gen_door_close),
    ("item_pickup", "Item pickup", gen_item_pickup),
    ("book_open", "Book open", gen_book_open),
    ("clue_select", "Clue discovery", gen_clue_select),
    ("sacred_ink", "Sacred arts cast", gen_sacred_ink),
    ("boundary_ripple", "Boundary disturbance", gen_boundary_ripple),
    ("relationship_up", "Relationship increase", gen_relationship_up),
    ("reward", "Reward received", gen_reward),
    ("capture_silence", "Capture moment", gen_capture_silence),
    ("rain_drop", "Rain drop hit", gen_rain_drop),
]

# ---------- main ----------

def main():
    all_measurements = []
    manifest_rows = []
    header = ["asset_id","request_id","status","source_file","runtime_file","sha256","creator","tool_model","created_at","license","source_url","attribution_required","attribution_text","approved_by","approved_at","integrated_at","replaces_asset_id","notes"]

    for request_id, sfx_list, prefix in [
        ("AUD-SFX-001", SFX_001_UI, PREFIX_SFX1),
        ("AUD-SFX-002", SFX_002_WORLD, PREFIX_SFX2),
    ]:
        print(f"\n=== Generating {request_id} ({len(sfx_list)} SFX) ===")
        for sfx_id, desc, gen_func in sfx_list:
            print(f"  {sfx_id}...", end=" ", flush=True)
            samples = gen_func()
            dur = len(samples) / SR
            # Normalize to -18 LUFS target (approximate via peak)
            peak = np.max(np.abs(samples))
            if peak > 0:
                target_peak = 0.7
                gain = target_peak / peak
                samples = samples * gain
            # Save WAV
            wav_name = f"{request_id}_{sfx_id}_{BATCH}_48k24b.wav"
            wav_path = BASE / wav_name
            save_wav_24bit_fast(wav_path, samples)
            # Save OGG
            ogg_name = f"{request_id}_{sfx_id}_{BATCH}.ogg"
            ogg_path = BASE / ogg_name
            encode_ogg(wav_path, ogg_path)
            # Measure
            lufs, peak_db = measure_loudness(samples)
            # SHA-256
            wav_sha = sha256_file(wav_path)
            ogg_sha = sha256_file(ogg_path)
            wav_size = os.path.getsize(wav_path)
            ogg_size = os.path.getsize(ogg_path)
            print(f"({dur:.2f}s, {lufs} LUFS, {peak_db} dBFS)")
            
            all_measurements.append({
                "file": wav_name,
                "sfx_id": sfx_id,
                "request_id": request_id,
                "description": desc,
                "duration_sec": round(dur, 2),
                "integrated_loudness_lufs": lufs,
                "peak_dbfs": peak_db,
                "sample_rate_hz": SR,
                "bit_depth": BIT_DEPTH,
                "channels": 2,
            })
            
            for fname, sha, size, ext in [
                (wav_name, wav_sha, wav_size, "wav"),
                (ogg_name, ogg_sha, ogg_size, "ogg"),
            ]:
                asset_id = fname.replace(f"_{BATCH}_48k24b.wav", "").replace(f"_{BATCH}.ogg", "").replace(".", "_")
                manifest_rows.append({
                    "asset_id": f"{asset_id}-{ext}",
                    "request_id": request_id,
                    "status": "received",
                    "source_file": f"materials/inbox/audio/sfx/{fname}",
                    "runtime_file": "",
                    "sha256": sha,
                    "creator": CREATOR,
                    "tool_model": TOOL,
                    "created_at": CREATED_AT,
                    "license": "Project original - UW 0.5.0-pre-capture",
                    "source_url": "Procedurally generated",
                    "attribution_required": "false",
                    "attribution_text": "",
                    "approved_by": "",
                    "approved_at": "",
                    "integrated_at": "",
                    "replaces_asset_id": "",
                    "notes": f"SFX: {desc} ({ext.upper()})"
                })

    # Save measurements
    meas_path = BASE / "sfx_measurements_v004.json"
    with open(meas_path, "w", encoding="utf-8") as f:
        json.dump(all_measurements, f, indent=2, ensure_ascii=False)
    manifest_rows.append({
        "asset_id": "sfx_measurements_v004",
        "request_id": "AUD-SFX-001",
        "status": "received",
        "source_file": f"materials/inbox/audio/sfx/sfx_measurements_v004.json",
        "runtime_file": "",
        "sha256": sha256_file(meas_path),
        "creator": CREATOR,
        "tool_model": TOOL,
        "created_at": CREATED_AT,
        "license": "Project original - UW 0.5.0-pre-capture",
        "source_url": "Procedurally generated",
        "attribution_required": "false",
        "attribution_text": "",
        "approved_by": "",
        "approved_at": "",
        "integrated_at": "",
        "replaces_asset_id": "",
        "notes": "SFX measurements metadata"
    })

    # Save manifest
    csv_path = BASE / "AUD-SFX-001-002_manifest_fragment.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"\nTotal SFX: {len(SFX_001_UI) + len(SFX_002_WORLD)}")
    print(f"Total files: {len(manifest_rows)} (incl metadata)")
    print(f"Manifest: {csv_path.name}")
    print("AUD-SFX-001/002 complete!")

if __name__ == "__main__":
    main()
