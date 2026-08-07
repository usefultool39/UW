#!/usr/bin/env python3
"""Convert audio to 48kHz/24-bit master + OGG runtime + measure loudness."""
import subprocess
import re
import json
from pathlib import Path

FFMPEG = r'C:\Users\liang\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe'

audio_files = [
    'materials/inbox/audio/bgm/AUD-BGM-002_boundary_investigation_a_v002.wav',
    'materials/inbox/audio/bgm/AUD-BGM-002_boundary_investigation_b_v002.wav',
    'materials/inbox/audio/bgm/AUD-BGM-003_relationship_daily_a_v002.wav',
    'materials/inbox/audio/bgm/AUD-BGM-003_relationship_daily_b_v002.wav',
    'materials/inbox/audio/ambience/AUD-AMB-002_forest_silence_normal_v002.wav',
    'materials/inbox/audio/ambience/AUD-AMB-002_forest_silence_silent_v002.wav',
]

results = []
for f in audio_files:
    p = Path(f)
    master_48k = p.with_name(p.stem + '_48k24b.wav')
    ogg = p.with_suffix('.ogg')

    # Convert to 48kHz/24-bit
    cmd1 = [FFMPEG, '-y', '-i', str(p), '-ar', '48000', '-sample_fmt', 's32', '-acodec', 'pcm_s24le', str(master_48k)]
    r1 = subprocess.run(cmd1, capture_output=True, text=True)
    if r1.returncode != 0:
        print(f'FAIL 48k24b: {p.name}: {r1.stderr[-300:]}')
        continue

    # Convert to OGG
    cmd2 = [FFMPEG, '-y', '-i', str(p), '-c:a', 'libvorbis', '-q:a', '5', str(ogg)]
    r2 = subprocess.run(cmd2, capture_output=True, text=True)
    if r2.returncode != 0:
        print(f'FAIL ogg: {p.name}: {r2.stderr[-300:]}')
        continue

    # Measure loudness & peak (using ebur128)
    cmd3 = [FFMPEG, '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-']
    r3 = subprocess.run(cmd3, capture_output=True, text=True)
    summary = r3.stderr

    m_i = re.search(r'I:\s*([-]?\d+\.?\d*)\s*LUFS', summary)
    m_lra = re.search(r'LRA:\s*([-]?\d+\.?\d*)\s*LU', summary)
    m_tp = re.search(r'Peak:\s*([-]?\d+\.?\d*)\s*dBFS', summary)

    info = {
        'file': p.name,
        'master_48k24b_bytes': master_48k.stat().st_size,
        'ogg_bytes': ogg.stat().st_size,
        'integrated_loudness_lufs': float(m_i.group(1)) if m_i else None,
        'loudness_range_lu': float(m_lra.group(1)) if m_lra else None,
        'peak_dbfs': float(m_tp.group(1)) if m_tp else None,
    }
    results.append(info)
    print(f'OK: {p.name}')
    print(f'   48k24b -> {master_48k.name} ({master_48k.stat().st_size} bytes)')
    print(f'   ogg    -> {ogg.name} ({ogg.stat().st_size} bytes)')
    print(f'   I={info["integrated_loudness_lufs"]} LUFS, LRA={info["loudness_range_lu"]} LU, peak={info["peak_dbfs"]} dBFS')

# Save to a JSON file for the sidecars
out = Path('materials/inbox/audio/measurements_v002.json')
out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'\nSaved measurements to {out}')
