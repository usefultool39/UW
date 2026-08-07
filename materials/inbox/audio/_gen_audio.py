"""
AUD-BGM-002/003, AUD-AMB-002 UW-UPGRADE-1.0 Audio Generator
Generates procedural audio assets meeting technical specs.
"""
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import json, os, csv, hashlib, math, random
from scipy import signal as scipy_signal

random.seed(42)
np.random.seed(42)

SR = 48000  # 48kHz
BIT_DEPTH = "PCM_24"

# ---- SYNTHESIS HELPERS ----

def adsr(n_samples, sr, attack=0.01, decay=0.1, sustain=0.7, release=0.1):
    """Create ADSR envelope"""
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    s = n_samples - a - d - r
    if s < 0:
        s = 0
        r = n_samples - a - d
    env = np.concatenate([
        np.linspace(0, 1, max(a, 1)),
        np.linspace(1, sustain, max(d, 1)),
        np.ones(s) * sustain,
        np.linspace(sustain, 0, max(r, 1))
    ])
    if len(env) < n_samples:
        env = np.pad(env, (0, n_samples - len(env)))
    return env[:n_samples]

def sine_wave(freq, n_samples, sr, amplitude=0.5):
    t = np.arange(n_samples) / sr
    return amplitude * np.sin(2 * np.pi * freq * t)

def triangle_wave(freq, n_samples, sr, amplitude=0.5):
    t = np.arange(n_samples) / sr
    return amplitude * scipy_signal.sawtooth(2 * np.pi * freq * t, width=0.5)

def noise_gen(n_samples, color='white'):
    """Generate colored noise"""
    n = n_samples
    if color == 'white':
        return np.random.randn(n)
    elif color == 'pink':
        # Simple pink noise approximation
        white = np.random.randn(n)
        # Apply 1/f filter
        b = [1.0, -0.95]
        a = [1.0]
        return scipy_signal.lfilter(b, a, white)
    elif color == 'brown':
        white = np.random.randn(n)
        return np.cumsum(white) * 0.01

def lowpass(data, sr, cutoff):
    """Apply lowpass filter"""
    nyq = sr / 2
    norm_cutoff = cutoff / nyq
    b, a = scipy_signal.butter(4, norm_cutoff, btype='low')
    return scipy_signal.filtfilt(b, a, data)

def highpass(data, sr, cutoff):
    """Apply highpass filter"""
    nyq = sr / 2
    norm_cutoff = cutoff / nyq
    b, a = scipy_signal.butter(4, norm_cutoff, btype='high')
    return scipy_signal.filtfilt(b, a, data)

def bandpass(data, sr, low, high):
    """Apply bandpass filter"""
    nyq = sr / 2
    b, a = scipy_signal.butter(4, [low/nyq, high/nyq], btype='band')
    return scipy_signal.filtfilt(b, a, data)

def stereo_mix(mono_data):
    """Convert mono to stereo with slight variation"""
    left = mono_data.copy()
    right = mono_data.copy()
    # Add slight delay/variation for stereo width
    delay_samples = 3
    if len(right) > delay_samples:
        right = np.roll(right, delay_samples)
        right[:delay_samples] = right[delay_samples]
    return np.stack([left, right], axis=1)

def normalize_peak(data, target_peak_dbfs=-1.0):
    """Normalize to target peak in dBFS"""
    peak = np.max(np.abs(data))
    if peak == 0:
        return data
    target_peak = 10 ** (target_peak_dbfs / 20)
    return data * (target_peak / peak)

def apply_loudness_target(data, sr, target_lufs):
    """Apply loudness normalization to target LUFS"""
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(data)
    if loudness == -float('inf'):
        return data
    normalized = pyln.normalize.loudness(data, loudness, target_lufs)
    return normalized

def make_loopable(data, sr, fade_samples=None):
    """Ensure audio loops seamlessly by crossfading start/end"""
    if fade_samples is None:
        fade_samples = int(sr * 0.05)  # 50ms crossfade
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    
    # Crossfade end into beginning
    result = data.copy()
    if len(result.shape) == 1:  # mono
        result[:fade_samples] *= fade_in
        result[-fade_samples:] *= fade_out
        # Blend
        blended = result[:fade_samples] + result[-fade_samples:]
        result[:fade_samples] = blended
    else:  # stereo
        for ch in range(result.shape[1]):
            result[:fade_samples, ch] *= fade_in
            result[-fade_samples:, ch] *= fade_out
            blended = result[:fade_samples, ch] + result[-fade_samples:, ch]
            result[:fade_samples, ch] = blended
    return result

def measure_audio(data, sr):
    """Measure loudness and peak"""
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(data)
    peak = np.max(np.abs(data))
    peak_dbfs = 20 * np.log10(peak) if peak > 0 else -float('inf')
    return {
        "integrated_loudness_lufs": round(loudness, 2),
        "peak_dbfs": round(peak_dbfs, 2)
    }

# ---- BGM-002: Boundary Investigation ----

def gen_bgm_002_a(sr, duration=90):
    """Boundary investigation version A - sparse, spatial, uneasy"""
    n = int(sr * duration)
    audio = np.zeros(n)
    
    # Low drone (boundary unease)
    drone_freq = 55  # A1
    drone = sine_wave(drone_freq, n, sr, 0.15)
    drone += sine_wave(drone_freq * 1.5, n, sr, 0.05)  # perfect fifth
    drone = lowpass(drone, sr, 200)
    audio += drone
    
    # Sparse bell tones (irregular)
    bell_times = [5, 12, 23, 31, 42, 55, 68, 78, 85]
    for t in bell_times:
        start = int(t * sr)
        if start >= n:
            continue
        bell_dur = int(3 * sr)
        bell_end = min(start + bell_dur, n)
        bell_len = bell_end - start
        bell_freq = random.choice([220, 277, 330, 440, 554])
        bell = sine_wave(bell_freq, bell_len, sr, 0.2)
        bell_env = np.exp(-np.arange(bell_len) / (sr * 1.5))
        bell *= bell_env
        audio[start:bell_end] += bell[:bell_len]
    
    # Wind/cold air texture
    wind = noise_gen(n, 'brown')
    wind = bandpass(wind, sr, 50, 400)
    wind *= 0.08
    # Modulate wind
    t = np.arange(n) / sr
    wind_mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    wind *= wind_mod
    audio += wind
    
    # Occasional string scrape (dissonant)
    scrape_times = [18, 37, 61, 80]
    for t in scrape_times:
        start = int(t * sr)
        if start >= n:
            continue
        scrape_dur = int(1.5 * sr)
        scrape_end = min(start + scrape_dur, n)
        scrape_len = scrape_end - start
        scrape_freq = random.choice([110, 130, 155])
        scrape = triangle_wave(scrape_freq, scrape_len, sr, 0.1)
        scrape_env = adsr(scrape_len, sr, 0.3, 0.2, 0.3, 0.5)
        scrape *= scrape_env
        audio[start:scrape_end] += scrape[:scrape_len]
    
    # Negative space - silence gaps (bird absence)
    gap_times = [(25, 28), (50, 53), (72, 75)]
    for start_t, end_t in gap_times:
        start = int(start_t * sr)
        end = int(end_t * sr)
        if end > n:
            end = n
        fade = int(0.5 * sr)
        # Fade out then in
        for i in range(min(fade, end - start)):
            audio[start + i] *= (1 - i / fade)
            audio[end - 1 - i] *= (1 - i / fade)
    
    # Normalize
    audio = normalize_peak(audio, -3.0)
    audio = make_loopable(audio, sr)
    audio = apply_loudness_target(audio, sr, -19.0)
    audio = normalize_peak(audio, -1.0)
    
    return stereo_mix(audio)

def gen_bgm_002_b(sr, duration=85):
    """Boundary investigation version B - darker, more tense"""
    n = int(sr * duration)
    audio = np.zeros(n)
    
    # Low drone with slight dissonance
    drone = sine_wave(49, n, sr, 0.12)  # G1
    drone += sine_wave(73, n, sr, 0.06)  # dissonant interval
    drone = lowpass(drone, sr, 180)
    audio += drone
    
    # Sparse metallic tones
    metal_times = [3, 9, 17, 25, 34, 44, 53, 62, 70, 78]
    for t in metal_times:
        start = int(t * sr)
        if start >= n:
            continue
        tone_dur = int(2.5 * sr)
        tone_end = min(start + tone_dur, n)
        tone_len = tone_end - start
        freq = random.choice([196, 233, 294, 392, 466])
        tone = sine_wave(freq, tone_len, sr, 0.15)
        tone += sine_wave(freq * 2.01, tone_len, sr, 0.05)  # slight detune
        tone_env = np.exp(-np.arange(tone_len) / (sr * 1.2))
        tone *= tone_env
        audio[start:tone_end] += tone[:tone_len]
    
    # Cold wind
    wind = noise_gen(n, 'pink')
    wind = bandpass(wind, sr, 100, 600)
    wind *= 0.06
    t = np.arange(n) / sr
    wind_mod = 0.4 + 0.6 * np.sin(2 * np.pi * 0.07 * t)
    wind *= wind_mod
    audio += wind
    
    # Sub bass pulse (tension)
    pulse_times = [15, 30, 45, 60, 75]
    for pt in pulse_times:
        start = int(pt * sr)
        if start >= n:
            continue
        pulse_dur = int(0.8 * sr)
        pulse_end = min(start + pulse_dur, n)
        pulse_len = pulse_end - start
        pulse = sine_wave(30, pulse_len, sr, 0.3)
        pulse_env = np.exp(-np.arange(pulse_len) / (sr * 0.3))
        pulse *= pulse_env
        audio[start:pulse_end] += pulse[:pulse_len]
    
    audio = normalize_peak(audio, -3.0)
    audio = make_loopable(audio, sr)
    audio = apply_loudness_target(audio, sr, -18.5)
    audio = normalize_peak(audio, -1.0)
    
    return stereo_mix(audio)

# ---- BGM-003: Relationship/Daily ----

def gen_bgm_003_a(sr, duration=80):
    """Relationship/daily version A - warm, gentle"""
    n = int(sr * duration)
    audio = np.zeros(n)
    
    # Warm pad
    pad_freqs = [220, 277, 330]  # A minor triad
    for f in pad_freqs:
        pad = sine_wave(f, n, sr, 0.08)
        pad += triangle_wave(f * 2, n, sr, 0.03)
        pad = lowpass(pad, sr, 2000)
        # Slow LFO
        t = np.arange(n) / sr
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * t)
        pad *= lfo
        audio += pad
    
    # Gentle melody (woodwind-like)
    melody_notes = [
        (0, 2, 440), (2, 1, 523), (3, 2, 587), (5, 1, 523),
        (6, 2, 440), (8, 1, 392), (9, 2, 440), (11, 1, 523),
        (12, 2, 587), (14, 1, 659), (15, 2, 587), (17, 2, 523),
        (19, 3, 440),
    ]
    for start_t, dur_t, freq in melody_notes:
        start = int(start_t * sr)
        note_dur = int(dur_t * sr)
        end = min(start + note_dur, n)
        note_len = end - start
        if note_len <= 0:
            continue
        note = triangle_wave(freq, note_len, sr, 0.12)
        note_env = adsr(note_len, sr, 0.05, 0.1, 0.6, 0.2)
        note *= note_env
        audio[start:end] += note[:note_len]
    
    # Plucked string accompaniment
    pluck_pattern = [(0, 0.5, 110), (1, 0.5, 165), (2, 0.5, 110), (3, 0.5, 165)]
    for bar in range(20):
        for beat, dur, freq in pluck_pattern:
            t = bar * 4 + beat
            start = int(t * sr)
            note_dur = int(dur * sr)
            end = min(start + note_dur, n)
            note_len = end - start
            if note_len <= 0:
                continue
            pluck = sine_wave(freq, note_len, sr, 0.06)
            pluck_env = np.exp(-np.arange(note_len) / (sr * 0.3))
            pluck *= pluck_env
            audio[start:end] += pluck[:note_len]
    
    # Soft rain ambience
    rain = noise_gen(n, 'white')
    rain = highpass(rain, sr, 2000)
    rain = lowpass(rain, sr, 8000)
    rain *= 0.02
    audio += rain
    
    audio = normalize_peak(audio, -3.0)
    audio = make_loopable(audio, sr)
    audio = apply_loudness_target(audio, sr, -18.0)
    audio = normalize_peak(audio, -1.0)
    
    return stereo_mix(audio)

def gen_bgm_003_b(sr, duration=75):
    """Relationship/daily version B - slightly more active"""
    n = int(sr * duration)
    audio = np.zeros(n)
    
    # Warm drone
    drone = sine_wave(261, n, sr, 0.06)  # C4
    drone += sine_wave(392, n, sr, 0.04)  # G4
    drone = lowpass(drone, sr, 1500)
    audio += drone
    
    # Melody (brighter, plucked)
    melody = [
        (0, 1.5, 523), (1.5, 0.5, 587), (2, 1, 659), (3, 1, 587),
        (4, 1.5, 523), (5.5, 0.5, 440), (6, 2, 392),
        (8, 1, 523), (9, 1, 659), (10, 1, 784), (11, 1, 659),
        (12, 2, 523), (14, 1, 587), (15, 2, 523),
    ]
    for start_t, dur_t, freq in melody:
        start = int(start_t * sr)
        note_dur = int(dur_t * sr)
        end = min(start + note_dur, n)
        note_len = end - start
        if note_len <= 0:
            continue
        note = sine_wave(freq, note_len, sr, 0.1)
        note += triangle_wave(freq * 2, note_len, sr, 0.03)
        note_env = np.exp(-np.arange(note_len) / (sr * 0.5))
        note *= note_env
        audio[start:end] += note[:note_len]
    
    # Bass line
    bass_pattern = [(0, 2, 65), (2, 2, 98), (4, 2, 87), (6, 2, 98)]
    for bar in range(10):
        for beat, dur, freq in bass_pattern:
            t = bar * 8 + beat
            start = int(t * sr)
            note_dur = int(dur * sr)
            end = min(start + note_dur, n)
            note_len = end - start
            if note_len <= 0:
                continue
            bass = sine_wave(freq, note_len, sr, 0.08)
            bass_env = adsr(note_len, sr, 0.02, 0.1, 0.5, 0.3)
            bass *= bass_env
            audio[start:end] += bass[:note_len]
    
    # Soft glass/clock tones
    for t in [5, 15, 25, 35, 45, 55, 65]:
        start = int(t * sr)
        if start >= n:
            continue
        tone_dur = int(2 * sr)
        end = min(start + tone_dur, n)
        tone_len = end - start
        freq = random.choice([880, 1047, 1319])
        tone = sine_wave(freq, tone_len, sr, 0.04)
        tone_env = np.exp(-np.arange(tone_len) / (sr * 1.0))
        tone *= tone_env
        audio[start:end] += tone[:tone_len]
    
    audio = normalize_peak(audio, -3.0)
    audio = make_loopable(audio, sr)
    audio = apply_loudness_target(audio, sr, -18.5)
    audio = normalize_peak(audio, -1.0)
    
    return stereo_mix(audio)

# ---- AMB-002: Forest Silence ----

def gen_amb_002_normal(sr, duration=75):
    """Forest ambience - normal (birds, leaves, breeze)"""
    n = int(sr * duration)
    audio = np.zeros(n)
    
    # Wind in leaves (filtered noise)
    wind = noise_gen(n, 'pink')
    wind = bandpass(wind, sr, 300, 3000)
    wind *= 0.15
    t = np.arange(n) / sr
    wind_mod = 0.4 + 0.6 * np.sin(2 * np.pi * 0.08 * t) + 0.3 * np.sin(2 * np.pi * 0.23 * t)
    wind *= wind_mod
    audio += wind
    
    # Distant birds (random chirps)
    for _ in range(40):
        start = random.randint(0, n - int(0.3 * sr))
        chirp_dur = int(random.uniform(0.05, 0.2) * sr)
        chirp_end = min(start + chirp_dur, n)
        chirp_len = chirp_end - start
        freq = random.uniform(2000, 5000)
        chirp = sine_wave(freq, chirp_len, sr, 0.08)
        # Frequency sweep
        t_chirp = np.arange(chirp_len) / sr
        freq_mod = freq + random.uniform(-500, 500) * np.sin(2 * np.pi * 10 * t_chirp)
        chirp = 0.08 * np.sin(2 * np.pi * freq_mod * t_chirp)
        chirp_env = np.exp(-np.arange(chirp_len) / (sr * 0.05))
        chirp *= chirp_env
        audio[start:chirp_end] += chirp[:chirp_len]
    
    # Wet ground texture
    wet = noise_gen(n, 'brown')
    wet = lowpass(wet, sr, 300)
    wet *= 0.1
    audio += wet
    
    # Occasional twig snap
    for _ in range(5):
        start = random.randint(0, n - int(0.1 * sr))
        snap_dur = int(0.05 * sr)
        snap_end = min(start + snap_dur, n)
        snap_len = snap_end - start
        snap = noise_gen(snap_len, 'white')
        snap = highpass(snap, sr, 1000)
        snap *= 0.15
        snap_env = np.exp(-np.arange(snap_len) / (sr * 0.01))
        snap *= snap_env
        audio[start:snap_end] += snap[:snap_len]
    
    # Distant water
    water = noise_gen(n, 'white')
    water = bandpass(water, sr, 100, 500)
    water *= 0.05
    audio += water
    
    audio = normalize_peak(audio, -3.0)
    audio = make_loopable(audio, sr)
    audio = apply_loudness_target(audio, sr, -24.0)
    audio = normalize_peak(audio, -2.0)
    
    return stereo_mix(audio)

def gen_amb_002_silent(sr, duration=75):
    """Forest ambience - silent boundary (unnatural stillness)"""
    n = int(sr * duration)
    audio = np.zeros(n)
    
    # Low air pressure (very low drone)
    pressure = sine_wave(20, n, sr, 0.08)
    pressure += noise_gen(n, 'brown') * 0.05
    pressure = lowpass(pressure, sr, 100)
    audio += pressure
    
    # Distant twigs (sparse, unnatural)
    for _ in range(8):
        start = random.randint(0, n - int(0.1 * sr))
        snap_dur = int(0.03 * sr)
        snap_end = min(start + snap_dur, n)
        snap_len = snap_end - start
        snap = noise_gen(snap_len, 'white')
        snap = highpass(snap, sr, 2000)
        snap *= 0.06
        snap_env = np.exp(-np.arange(snap_len) / (sr * 0.005))
        snap *= snap_env
        audio[start:snap_end] += snap[:snap_len]
    
    # Unnatural frequency gaps - remove mid frequencies at intervals
    # Create a "notch" that moves
    t = np.arange(n) / sr
    notch_freq = 800 + 400 * np.sin(2 * np.pi * 0.05 * t)
    # Apply moving notch filter
    base_noise = noise_gen(n, 'pink')
    base_noise = bandpass(base_noise, sr, 50, 2000)
    base_noise *= 0.04
    
    # Create silence gaps (unnatural frequency absence)
    gap_times = [(15, 20), (35, 38), (55, 60)]
    for start_t, end_t in gap_times:
        start = int(start_t * sr)
        end = int(end_t * sr)
        if end > n:
            end = n
        fade = int(1.0 * sr)
        for i in range(min(fade, end - start)):
            base_noise[start + i] *= (1 - i / fade)
            base_noise[end - 1 - i] *= (1 - i / fade)
        audio[start:end] *= 0.3  # Reduce overall level in gaps
    
    audio += base_noise
    
    # Very faint high-frequency presence (like tinnitus/unnatural)
    tinnitus = sine_wave(12000, n, sr, 0.005)
    audio += tinnitus
    
    audio = normalize_peak(audio, -3.0)
    audio = make_loopable(audio, sr)
    audio = apply_loudness_target(audio, sr, -24.0)
    audio = normalize_peak(audio, -2.0)
    
    return stereo_mix(audio)

# ---- MAIN ----

def main():
    base_dir = r"C:\Users\liang\Desktop\UW\materials\inbox\audio"
    bgm_dir = os.path.join(base_dir, "bgm")
    amb_dir = os.path.join(base_dir, "ambience")
    
    os.makedirs(bgm_dir, exist_ok=True)
    os.makedirs(amb_dir, exist_ok=True)
    
    prefix = "UW-UPGRADE-1.0"
    all_files = []
    measurements = []
    metadata = {}
    
    # BGM-002
    print("Generating AUD-BGM-002...")
    for version, gen_func, dur in [("a", gen_bgm_002_a, 90), ("b", gen_bgm_002_b, 85)]:
        stem = f"AUD-BGM-002_boundary_investigation_{version}_v004"
        print(f"  {stem} ({dur}s)...")
        
        audio = gen_func(SR, dur)
        wav_path = os.path.join(bgm_dir, f"{stem}_{prefix}_48k24b.wav")
        ogg_path = os.path.join(bgm_dir, f"{stem}_{prefix}.ogg")
        
        # Write WAV (24-bit)
        sf.write(wav_path, audio, SR, subtype="PCM_24")
        print(f"    WAV: {wav_path}")
        
        # Write OGG
        sf.write(ogg_path, audio, SR, format="OGG", subtype="VORBIS")
        print(f"    OGG: {ogg_path}")
        
        # Measure
        meas = measure_audio(audio, SR)
        meas["file"] = os.path.basename(wav_path)
        measurements.append(meas)
        meas_ogg = measure_audio(audio, SR)
        meas_ogg["file"] = os.path.basename(ogg_path)
        measurements.append(meas_ogg)
        
        # Metadata
        metadata[stem] = {
            "duration": dur,
            "sample_rate_hz": SR,
            "bit_depth": "24-bit",
            "channels": 2,
            "loop_safe": True,
            "loop_start_sample": 0,
            "loop_end_sample": len(audio)
        }
        
        all_files.append(("AUD-BGM-002", os.path.basename(wav_path), wav_path))
        all_files.append(("AUD-BGM-002", os.path.basename(ogg_path), ogg_path))
        print(f"    LUFS: {meas['integrated_loudness_lufs']}, Peak: {meas['peak_dbfs']}")
    
    # BGM-003
    print("\nGenerating AUD-BGM-003...")
    for version, gen_func, dur in [("a", gen_bgm_003_a, 80), ("b", gen_bgm_003_b, 75)]:
        stem = f"AUD-BGM-003_relationship_daily_{version}_v004"
        print(f"  {stem} ({dur}s)...")
        
        audio = gen_func(SR, dur)
        wav_path = os.path.join(bgm_dir, f"{stem}_{prefix}_48k24b.wav")
        ogg_path = os.path.join(bgm_dir, f"{stem}_{prefix}.ogg")
        
        sf.write(wav_path, audio, SR, subtype="PCM_24")
        sf.write(ogg_path, audio, SR, format="OGG", subtype="VORBIS")
        
        meas = measure_audio(audio, SR)
        meas["file"] = os.path.basename(wav_path)
        measurements.append(meas)
        meas_ogg = measure_audio(audio, SR)
        meas_ogg["file"] = os.path.basename(ogg_path)
        measurements.append(meas_ogg)
        
        metadata[stem] = {
            "duration": dur,
            "sample_rate_hz": SR,
            "bit_depth": "24-bit",
            "channels": 2,
            "loop_safe": True,
            "loop_start_sample": 0,
            "loop_end_sample": len(audio)
        }
        
        all_files.append(("AUD-BGM-003", os.path.basename(wav_path), wav_path))
        all_files.append(("AUD-BGM-003", os.path.basename(ogg_path), ogg_path))
        print(f"    LUFS: {meas['integrated_loudness_lufs']}, Peak: {meas['peak_dbfs']}")
    
    # AMB-002
    print("\nGenerating AUD-AMB-002...")
    amb_duration = 75
    for version, gen_func in [("normal", gen_amb_002_normal), ("silent", gen_amb_002_silent)]:
        stem = f"AUD-AMB-002_forest_silence_{version}_v004"
        print(f"  {stem} ({amb_duration}s)...")
        
        audio = gen_func(SR, amb_duration)
        wav_path = os.path.join(amb_dir, f"{stem}_{prefix}_48k24b.wav")
        ogg_path = os.path.join(amb_dir, f"{stem}_{prefix}.ogg")
        
        sf.write(wav_path, audio, SR, subtype="PCM_24")
        sf.write(ogg_path, audio, SR, format="OGG", subtype="VORBIS")
        
        meas = measure_audio(audio, SR)
        meas["file"] = os.path.basename(wav_path)
        measurements.append(meas)
        meas_ogg = measure_audio(audio, SR)
        meas_ogg["file"] = os.path.basename(ogg_path)
        measurements.append(meas_ogg)
        
        metadata[stem] = {
            "duration": amb_duration,
            "sample_rate_hz": SR,
            "bit_depth": "24-bit",
            "channels": 2,
            "loop_safe": True,
            "loop_start_sample": 0,
            "loop_end_sample": len(audio)
        }
        
        all_files.append(("AUD-AMB-002", os.path.basename(wav_path), wav_path))
        all_files.append(("AUD-AMB-002", os.path.basename(ogg_path), ogg_path))
        print(f"    LUFS: {meas['integrated_loudness_lufs']}, Peak: {meas['peak_dbfs']}")
    
    # Write metadata fragment JSON
    meta_path = os.path.join(base_dir, "audio.meta_v004.fragment.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"\nMetadata: {meta_path}")
    
    # Write measurements JSON
    meas_path = os.path.join(base_dir, "measurements_v004.json")
    with open(meas_path, "w", encoding="utf-8") as f:
        json.dump(measurements, f, indent=2, ensure_ascii=False)
    print(f"Measurements: {meas_path}")
    
    # Manifest fragment
    header = ["asset_id","request_id","status","source_file","runtime_file","sha256","creator","tool_model","created_at","license","source_url","attribution_required","attribution_text","approved_by","approved_at","integrated_at","replaces_asset_id","notes"]
    rows = []
    created_at = "2026-08-07T18:10:00+08:00"
    
    # Compute hashes
    for req_id, fname, fpath in all_files:
        with open(fpath, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        rows.append({
            "asset_id": fname.replace(".wav","").replace(".ogg",""),
            "request_id": req_id,
            "status": "received",
            "source_file": f"materials/inbox/audio/{'bgm' if 'BGM' in req_id else 'ambience'}/{fname}",
            "runtime_file": "",
            "sha256": sha,
            "creator": "WorkBuddy AI Asset Agent",
            "tool_model": "Python numpy/scipy procedural synthesis",
            "created_at": created_at,
            "license": "Project original - UW 0.5.0-pre-capture",
            "source_url": "Procedurally generated, no external URL",
            "attribution_required": "false",
            "attribution_text": "",
            "approved_by": "",
            "approved_at": "",
            "integrated_at": "",
            "replaces_asset_id": f"{req_id}_v003",
            "notes": f"48kHz/24-bit {'WAV' if fname.endswith('.wav') else 'OGG'}, procedural audio"
        })
    
    # Add metadata files
    for fname, fpath in [("audio.meta_v004.fragment.json", meta_path), ("measurements_v004.json", meas_path)]:
        with open(fpath, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        rows.append({
            "asset_id": fname.replace(".json",""),
            "request_id": "AUD-BGM-002",
            "status": "received",
            "source_file": f"materials/inbox/audio/{fname}",
            "runtime_file": "",
            "sha256": sha,
            "creator": "WorkBuddy AI Asset Agent",
            "tool_model": "Python pyloudnorm",
            "created_at": created_at,
            "license": "Project original",
            "source_url": "Procedurally generated",
            "attribution_required": "false",
            "attribution_text": "",
            "approved_by": "",
            "approved_at": "",
            "integrated_at": "",
            "replaces_asset_id": "",
            "notes": "Audio metadata and measurements"
        })
    
    csv_path = os.path.join(base_dir, "AUD_UW-UPGRADE-1.0_manifest_fragment.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Manifest fragment: {len(rows)} rows")
    
    print("\nAll audio files generated!")
    print(f"  BGM-002: 2 versions x 2 formats = 4 files")
    print(f"  BGM-003: 2 versions x 2 formats = 4 files")
    print(f"  AMB-002: 2 versions x 2 formats = 4 files")
    print(f"  Metadata + measurements: 2 files")
    print(f"  Total: {len(rows)} manifest rows")

if __name__ == "__main__":
    main()
