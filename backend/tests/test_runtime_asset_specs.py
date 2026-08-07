from __future__ import annotations

import importlib.util
import json
import struct
import sys
import wave
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "materials" / "tools" / "check_runtime_asset_specs.py"
spec = importlib.util.spec_from_file_location("runtime_asset_specs", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_active_contract_targets_non_destructive_v004_rework():
    contract = json.loads(
        (ROOT / "materials" / "runtime_asset_requirements.json").read_text(encoding="utf-8")
    )

    def contract_characters_metadata(data):
        return [item["metadata_file"] for item in data["characters"]]
    assert "_map_v005.json" in contract["map"]["metadata_file"]
    assert "_scenes_v005.json" in contract["environments"]["metadata_file"]
    assert all("_frames_v008.json" in path for path in contract_characters_metadata(contract))

    for audio in contract["audio"]:
        assert audio["metadata_file"].endswith("audio.meta_v004.fragment.json")
        assert audio["measurement_file"].endswith("measurements_v004.json")
        assert all(stem.endswith("_v004") for stem in audio["stems"])


def _write_png(
    path: Path,
    width: int,
    height: int,
    color_type: int,
    *,
    transparent: bool = True,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    channels = {2: 3, 6: 4}[color_type]
    visible_pixel = bytes([255] * channels)
    if transparent and channels == 4:
        transparent_pixel = bytes([255, 255, 255, 0])
        row = b"\0" + visible_pixel + transparent_pixel * (width - 1)
    else:
        row = b"\0" + visible_pixel * width
    payload = zlib.compress(row * height)
    path.write_bytes(
        module.PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", payload)
        + chunk(b"IEND", b"")
    )


def _write_wav(path: Path, seconds: float = 1.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(48000 * seconds)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(3)
        output.setframerate(48000)
        output.writeframes(b"\0" * frames * 2 * 3)


def test_png_info_distinguishes_true_alpha(tmp_path):
    rgb = tmp_path / "rgb.png"
    rgba = tmp_path / "rgba.png"
    _write_png(rgb, 4, 4, 2)
    _write_png(rgba, 4, 4, 6)

    rgb_info = module._png_info(rgb, [], "rgb")
    rgba_info = module._png_info(rgba, [], "rgba")

    assert rgb_info and rgb_info["has_alpha"] is False
    assert rgba_info and rgba_info["has_alpha"] is True


def test_check_png_reports_dimensions_and_alpha(tmp_path):
    asset = tmp_path / "asset.png"
    _write_png(asset, 4, 4, 2)
    issues: list[dict[str, str]] = []

    module._check_png(asset, issues, "asset", (8, 8), True)

    assert {item["code"] for item in issues} == {"png_dimensions", "png_alpha"}


def test_character_manifest_accepts_complete_rgba_frame_contract(tmp_path):
    source = tmp_path / "sprites.png"
    _write_png(source, 48 * 64, 96, 6)
    animations = {}
    cursor = 0
    for direction in ("down", "left", "right", "up"):
        for name, count in (("idle", 2), ("walk", 6), ("interact", 4)):
            frames = []
            for _ in range(count):
                frames.append({"source": "sprites.png", "rect": [cursor * 64, 0, 64, 96]})
                cursor += 1
            animations[f"{direction}_{name}"] = {"frames": frames}

    metadata = {
        "request_id": "VIS-CHR-001",
        "frame_width": 64,
        "frame_height": 96,
        "animations": animations,
    }
    metadata_path = tmp_path / "frames.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    issues: list[dict[str, str]] = []

    module._check_character(
        tmp_path,
        {
            "request_id": "VIS-CHR-001",
            "metadata_file": "frames.json",
            "accepted_frame_sizes": [[64, 96]],
            "directions": ["down", "left", "right", "up"],
            "animations": {"idle": 2, "walk": 6, "interact": 4},
        },
        issues,
    )

    assert issues == []


def test_character_manifest_rejects_non_alpha_sheet(tmp_path):
    source = tmp_path / "sprites.png"
    _write_png(source, 64, 96, 2)
    metadata = {
        "request_id": "VIS-CHR-001",
        "frame_width": 64,
        "frame_height": 96,
        "animations": {
            "down_idle": {
                "frames": [
                    {"source": "sprites.png", "rect": [0, 0, 64, 96]},
                    {"source": "sprites.png", "rect": [0, 0, 64, 96]},
                ]
            }
        },
    }
    metadata_path = tmp_path / "frames.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    issues: list[dict[str, str]] = []

    module._check_character(
        tmp_path,
        {
            "request_id": "VIS-CHR-001",
            "metadata_file": "frames.json",
            "accepted_frame_sizes": [[64, 96]],
            "directions": ["down"],
            "animations": {"idle": 2},
        },
        issues,
    )

    assert any(item["code"] == "sprite_alpha" for item in issues)
    assert any(item["code"] == "frame_distinctness" for item in issues)


def test_character_manifest_rejects_opaque_rgba_sheet(tmp_path):
    source = tmp_path / "sprites.png"
    _write_png(source, 128, 96, 6, transparent=False)
    metadata = {
        "request_id": "VIS-CHR-001",
        "frame_width": 64,
        "frame_height": 96,
        "animations": {
            "down_idle": {
                "frames": [
                    {"source": "sprites.png", "rect": [0, 0, 64, 96]},
                    {"source": "sprites.png", "rect": [64, 0, 64, 96]},
                ]
            }
        },
    }
    metadata_path = tmp_path / "frames.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    issues: list[dict[str, str]] = []

    module._check_character(
        tmp_path,
        {
            "request_id": "VIS-CHR-001",
            "metadata_file": "frames.json",
            "accepted_frame_sizes": [[64, 96]],
            "directions": ["down"],
            "animations": {"idle": 2},
        },
        issues,
    )

    assert any(item["code"] == "sprite_transparency" for item in issues)


def test_audio_contract_rejects_bad_delivery(tmp_path):
    stem = "AUD-BGM-002_boundary_investigation_a_v002"
    _write_wav(tmp_path / "materials" / "inbox" / "audio" / "bgm" / f"{stem}_48k24b.wav")
    (tmp_path / "materials" / "inbox" / "audio" / "bgm" / f"{stem}.ogg").write_bytes(b"candidate")
    (tmp_path / "audio.meta.json").write_text("{}", encoding="utf-8")
    measurement = [{"file": f"{stem}.wav", "integrated_loudness_lufs": -70.0, "peak_dbfs": 0.0}]
    (tmp_path / "measurements.json").write_text(json.dumps(measurement), encoding="utf-8")
    issues: list[dict[str, str]] = []

    module._check_audio(
        tmp_path,
        {
            "request_id": "AUD-BGM-002",
            "metadata_file": "audio.meta.json",
            "measurement_file": "measurements.json",
            "stems": [stem],
            "duration_seconds": [75, 110],
            "loudness_lufs": [-20, -17],
            "peak_dbfs_max": -1,
        },
        issues,
    )

    codes = {item["code"] for item in issues}
    assert {"audio_invalid_ogg", "audio_metadata_missing", "audio_duration", "audio_loudness", "audio_peak"} <= codes


def test_ogg_page_validator_accepts_a_well_framed_empty_page(tmp_path):
    page = bytearray(27)
    page[:4] = b"OggS"
    page[4] = 0
    page[26] = 1
    ogg = tmp_path / "valid.ogg"
    ogg.write_bytes(bytes(page) + b"\0")

    assert module._valid_ogg(ogg) is True
