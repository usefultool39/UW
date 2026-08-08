from __future__ import annotations

import json
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SFX_DIR = ROOT / "materials/inbox/audio/sfx/current"


def test_sfx_candidate_measurements_match_wav_headers():
    measurements = json.loads((SFX_DIR / "measurements.json").read_text(encoding="utf-8"))
    measurement_map = {row["file"]: row for row in measurements}

    for wav_path in sorted(SFX_DIR.glob("AUD-SFX-001_*.wav")):
        with wave.open(str(wav_path), "rb") as source:
            actual_duration = source.getnframes() / source.getframerate()
            assert source.getframerate() == 48000
            assert source.getnchannels() == 1
            assert source.getsampwidth() == 3

        row = measurement_map[wav_path.name]
        assert abs(float(row["duration_sec"]) - actual_duration) < 0.00002
        assert row["sample_rate_hz"] == 48000
        assert row["channels"] == 1
        assert row["bit_depth"] == 24
