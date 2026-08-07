#!/usr/bin/env python3
"""Validate technical contracts for first-phase visual and audio deliveries.

This is a read-only gate. It never promotes, rewrites, or normalizes an asset.
Request, sidecar, rights, manifest, and runtime hash validation remains owned by
check_materials.py; this tool validates dimensions, alpha, frame manifests, and
audio format/loop/loudness data.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import wave
import zlib
from pathlib import Path
from typing import Any


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CONTRACT_PATH = Path("materials") / "runtime_asset_requirements.json"


def _paeth_predictor(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def _unfilter_png_rows(
    payload: bytes,
    width: int,
    height: int,
    bytes_per_pixel: int,
    row_bytes: int,
) -> list[bytes] | None:
    expected = height * (row_bytes + 1)
    if len(payload) != expected:
        return None
    rows: list[bytes] = []
    cursor = 0
    previous = bytearray(row_bytes)
    for _ in range(height):
        filter_type = payload[cursor]
        cursor += 1
        filtered = payload[cursor:cursor + row_bytes]
        cursor += row_bytes
        row = bytearray(row_bytes)
        for index, value in enumerate(filtered):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                predictor = _paeth_predictor(left, above, upper_left)
            else:
                return None
            row[index] = (value + predictor) & 0xFF
        rows.append(bytes(row))
        previous = row
    return rows


def _png_alpha_usage(
    idat: bytes,
    width: int,
    height: int,
    bit_depth: int,
    color_type: int,
    interlace: int,
) -> tuple[bool, bool] | None:
    """Return whether decoded pixels contain transparency and visible content."""
    if interlace != 0 or bit_depth != 8 or color_type not in {4, 6} or not idat:
        return None
    bytes_per_pixel = 2 if color_type == 4 else 4
    try:
        payload = zlib.decompress(idat)
    except zlib.error:
        return None
    rows = _unfilter_png_rows(payload, width, height, bytes_per_pixel, width * bytes_per_pixel)
    if rows is None:
        return None
    alpha_offset = bytes_per_pixel - 1
    alpha_values = (
        row[index]
        for row in rows
        for index in range(alpha_offset, len(row), bytes_per_pixel)
    )
    has_transparent = False
    has_visible = False
    for alpha in alpha_values:
        has_transparent = has_transparent or alpha < 255
        has_visible = has_visible or alpha > 0
        if has_transparent and has_visible:
            break
    return has_transparent, has_visible


def _issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"code": code, "path": path, "message": message})


def _repo_path(project_root: Path, raw: Any, issues: list[dict[str, str]], label: str) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        _issue(issues, "missing_path", label, "path is required")
        return None
    value = Path(raw)
    if value.is_absolute() or ".." in value.parts:
        _issue(issues, "unsafe_path", label, "path must be repository-relative")
        return None
    return project_root / value


def _load_json(path: Path, issues: list[dict[str, str]], label: str) -> dict[str, Any] | list[Any] | None:
    if not path.is_file():
        _issue(issues, "missing_file", label, f"missing file: {path}")
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _issue(issues, "invalid_json", label, str(exc))
        return None
    if not isinstance(raw, (dict, list)):
        _issue(issues, "invalid_json_root", label, "expected an object or array")
        return None
    return raw


def _png_info(path: Path, issues: list[dict[str, str]], label: str) -> dict[str, Any] | None:
    if not path.is_file():
        _issue(issues, "missing_file", label, f"missing PNG: {path}")
        return None
    try:
        data = path.read_bytes()
    except OSError as exc:
        _issue(issues, "unreadable_file", label, str(exc))
        return None
    if not data.startswith(PNG_SIGNATURE):
        _issue(issues, "invalid_png", label, "PNG signature is missing")
        return None
    if len(data) < 33 or data[12:16] != b"IHDR":
        _issue(issues, "invalid_png", label, "IHDR is missing")
        return None
    width, height, bit_depth, color_type, _compression, _filter, _interlace = struct.unpack(
        ">IIBBBBB", data[16:29]
    )
    has_trns = False
    idat_parts: list[bytes] = []
    cursor = 8
    while cursor + 12 <= len(data):
        length = struct.unpack(">I", data[cursor:cursor + 4])[0]
        chunk_type = data[cursor + 4:cursor + 8]
        if chunk_type == b"tRNS":
            has_trns = True
        elif chunk_type == b"IDAT":
            idat_parts.append(data[cursor + 8:cursor + 8 + length])
        cursor += 12 + length
        if chunk_type == b"IEND":
            break
    alpha_usage = _png_alpha_usage(
        b"".join(idat_parts), width, height, bit_depth, color_type, _interlace
    )
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "has_alpha": color_type in {4, 6} or has_trns,
        "has_transparent_pixels": alpha_usage[0] if alpha_usage is not None else None,
        "has_visible_pixels": alpha_usage[1] if alpha_usage is not None else None,
    }


def _check_png(
    path: Path,
    issues: list[dict[str, str]],
    label: str,
    expected_size: tuple[int, int],
    require_alpha: bool,
) -> dict[str, Any] | None:
    info = _png_info(path, issues, label)
    if info is None:
        return None
    if (info["width"], info["height"]) != expected_size:
        _issue(
            issues,
            "png_dimensions",
            label,
            f"expected {expected_size[0]}x{expected_size[1]}, got {info['width']}x{info['height']}",
        )
    if require_alpha and not info["has_alpha"]:
        _issue(issues, "png_alpha", label, "true alpha channel is required")
    return info


def _source_value(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("source"), str):
        return value["source"]
    return None


def _check_map(project_root: Path, spec: dict[str, Any], issues: list[dict[str, str]]) -> None:
    metadata = _repo_path(project_root, spec.get("metadata_file"), issues, "map.metadata_file")
    if metadata is None:
        return
    raw = _load_json(metadata, issues, "map.metadata_file")
    if not isinstance(raw, dict):
        return
    if raw.get("request_id") != spec.get("request_id"):
        _issue(issues, "request_id", "map.metadata_file", "metadata request_id does not match VIS-MAP-001")
    runtime_size = raw.get("runtime_size")
    expected_size = tuple(spec.get("runtime_size") or [])
    if runtime_size != list(expected_size):
        _issue(issues, "map_runtime_size", "map.runtime_size", f"expected {list(expected_size)}, got {runtime_size!r}")
    layers = raw.get("layers") if isinstance(raw.get("layers"), dict) else {}
    for layer_name in spec.get("required_layers", []):
        source = _source_value(layers.get(layer_name))
        if source is None:
            _issue(issues, "map_layer_missing", f"map.layers.{layer_name}", "layer source is required")
            continue
        layer_path = _repo_path(project_root, source, issues, f"map.layers.{layer_name}")
        if layer_path is not None:
            _check_png(
                layer_path,
                issues,
                f"map.layers.{layer_name}",
                (int(expected_size[0]), int(expected_size[1])),
                layer_name in set(spec.get("alpha_layers") or []),
            )
    data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
    for data_name in spec.get("required_data", []):
        data_path = _repo_path(project_root, data.get(data_name), issues, f"map.data.{data_name}")
        if data_path is not None and not data_path.is_file():
            _issue(issues, "map_data_missing", f"map.data.{data_name}", f"missing data file: {data_path}")


def _check_character(project_root: Path, spec: dict[str, Any], issues: list[dict[str, str]]) -> None:
    request_id = str(spec.get("request_id") or "character")
    metadata = _repo_path(project_root, spec.get("metadata_file"), issues, f"{request_id}.metadata_file")
    if metadata is None:
        return
    raw = _load_json(metadata, issues, f"{request_id}.metadata_file")
    if not isinstance(raw, dict):
        return
    if raw.get("request_id") != request_id:
        _issue(issues, "request_id", f"{request_id}.metadata_file", "metadata request_id does not match request")
    frame_size = (raw.get("frame_width"), raw.get("frame_height"))
    accepted_sizes = {tuple(item) for item in spec.get("accepted_frame_sizes", []) if isinstance(item, list) and len(item) == 2}
    if frame_size not in accepted_sizes:
        _issue(issues, "frame_size", f"{request_id}.frame_size", f"frame size {frame_size!r} is not in {sorted(accepted_sizes)!r}")
    animations_raw = raw.get("animations")
    animations = animations_raw if isinstance(animations_raw, dict) else {
        str(item.get("id")): item
        for item in (animations_raw or [])
        if isinstance(item, dict) and item.get("id")
    }
    source_infos: dict[str, dict[str, Any] | None] = {}
    expected_animations = spec.get("animations") if isinstance(spec.get("animations"), dict) else {}
    for direction in spec.get("directions", []):
        for animation_name, expected_count in expected_animations.items():
            animation_id = f"{direction}_{animation_name}"
            animation = animations.get(animation_id)
            if not isinstance(animation, dict):
                _issue(issues, "animation_missing", f"{request_id}.animations.{animation_id}", "animation is required")
                continue
            frames = animation.get("frames") if isinstance(animation.get("frames"), list) else []
            if len(frames) != int(expected_count):
                _issue(issues, "frame_count", f"{request_id}.animations.{animation_id}", f"expected {expected_count} frames, got {len(frames)}")
            rects: list[tuple[int, int, int, int]] = []
            for index, frame in enumerate(frames):
                if not isinstance(frame, dict):
                    _issue(issues, "frame_invalid", f"{request_id}.animations.{animation_id}[{index}]", "frame must be an object")
                    continue
                source = frame.get("source") or animation.get("source")
                rect = frame.get("rect")
                if not isinstance(source, str) or not isinstance(rect, list) or len(rect) != 4:
                    _issue(issues, "frame_metadata", f"{request_id}.animations.{animation_id}[{index}]", "source and [x,y,width,height] rect are required")
                    continue
                try:
                    rect_tuple = tuple(int(value) for value in rect)
                except (TypeError, ValueError):
                    _issue(issues, "frame_rect", f"{request_id}.animations.{animation_id}[{index}]", "rect must contain integers")
                    continue
                if rect_tuple[2:] != frame_size:
                    _issue(issues, "frame_rect_size", f"{request_id}.animations.{animation_id}[{index}]", f"rect size must equal {frame_size!r}")
                rects.append(rect_tuple)
                if source not in source_infos:
                    source_path = _repo_path(project_root, source, issues, f"{request_id}.animations.{animation_id}.source")
                    source_infos[source] = (
                        _png_info(source_path, issues, f"{request_id}.{source}")
                        if source_path is not None
                        else None
                    )
                info = source_infos[source]
                if info is not None and (rect_tuple[0] < 0 or rect_tuple[1] < 0 or rect_tuple[0] + rect_tuple[2] > info["width"] or rect_tuple[1] + rect_tuple[3] > info["height"]):
                    _issue(issues, "frame_bounds", f"{request_id}.animations.{animation_id}[{index}]", "frame rect is outside source image")
            if len(set(rects)) < min(2, int(expected_count)):
                _issue(issues, "frame_distinctness", f"{request_id}.animations.{animation_id}", "animation needs distinct frame rectangles")
    for source, info in source_infos.items():
        if info is None:
            continue
        if not info["has_alpha"] or info["color_type"] not in {4, 6}:
            _issue(issues, "sprite_alpha", f"{request_id}.{source}", "sprite sheet must contain a true alpha channel")
        elif info["has_transparent_pixels"] is not True:
            _issue(issues, "sprite_transparency", f"{request_id}.{source}", "sprite sheet must contain decoded transparent pixels; an opaque baked checkerboard is invalid")
        elif info["has_visible_pixels"] is not True:
            _issue(issues, "sprite_blank", f"{request_id}.{source}", "sprite sheet must contain visible character pixels")


def _check_environments(project_root: Path, spec: dict[str, Any], issues: list[dict[str, str]]) -> None:
    request_id = str(spec.get("request_id") or "environments")
    metadata = _repo_path(project_root, spec.get("metadata_file"), issues, f"{request_id}.metadata_file")
    if metadata is None:
        return
    raw = _load_json(metadata, issues, f"{request_id}.metadata_file")
    if not isinstance(raw, dict):
        return
    if raw.get("request_id") != request_id:
        _issue(issues, "request_id", f"{request_id}.metadata_file", "metadata request_id does not match request")
    scenes = raw.get("scenes") if isinstance(raw.get("scenes"), dict) else {}
    expected_size = tuple(spec.get("size") or [])
    for scene_name in spec.get("scenes", []):
        source = _source_value(scenes.get(scene_name))
        if source is None:
            _issue(issues, "scene_missing", f"{request_id}.scenes.{scene_name}", "scene source is required")
            continue
        path = _repo_path(project_root, source, issues, f"{request_id}.scenes.{scene_name}")
        if path is not None:
            _check_png(path, issues, f"{request_id}.scenes.{scene_name}", (int(expected_size[0]), int(expected_size[1])), False)


def _numeric(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _valid_ogg(path: Path) -> bool:
    """Check Ogg page framing without depending on an external decoder."""
    try:
        data = path.read_bytes()
    except OSError:
        return False
    offset = 0
    page_count = 0
    while offset < len(data):
        if len(data) - offset < 27 or data[offset:offset + 4] != b"OggS":
            return False
        if data[offset + 4] != 0:
            return False
        segment_count = data[offset + 26]
        table_end = offset + 27 + segment_count
        if table_end > len(data):
            return False
        page_size = sum(data[offset + 27:table_end])
        page_end = table_end + page_size
        if page_end > len(data):
            return False
        offset = page_end
        page_count += 1
    return page_count > 0


def _check_audio(project_root: Path, spec: dict[str, Any], issues: list[dict[str, str]]) -> dict[str, float]:
    request_id = str(spec.get("request_id") or "audio")
    metadata_path = _repo_path(project_root, spec.get("metadata_file"), issues, f"{request_id}.metadata_file")
    measurements_path = _repo_path(project_root, spec.get("measurement_file"), issues, f"{request_id}.measurement_file")
    metadata = _load_json(metadata_path, issues, f"{request_id}.metadata_file") if metadata_path is not None else None
    measurements = _load_json(measurements_path, issues, f"{request_id}.measurement_file") if measurements_path is not None else None
    meta_map = metadata if isinstance(metadata, dict) else {}
    measurement_map = {
        str(item.get("file")): item
        for item in (measurements if isinstance(measurements, list) else [])
        if isinstance(item, dict) and item.get("file")
    }
    durations: dict[str, float] = {}
    duration_range = tuple(spec.get("duration_seconds") or [])
    lufs_range = tuple(spec.get("loudness_lufs") or [])
    peak_max = float(spec.get("peak_dbfs_max"))
    for stem in spec.get("stems", []):
        stem = str(stem)
        meta = meta_map.get(stem)
        if not isinstance(meta, dict):
            _issue(issues, "audio_metadata_missing", f"{request_id}.{stem}", "audio.meta.json entry is required")
        wav_path = project_root / "materials" / "inbox" / "audio" / "bgm" / f"{stem}_48k24b.wav"
        if request_id == "AUD-AMB-002":
            wav_path = project_root / "materials" / "inbox" / "audio" / "ambience" / f"{stem}_48k24b.wav"
        ogg_path = wav_path.with_name(f"{stem}.ogg")
        if not ogg_path.is_file():
            _issue(issues, "audio_runtime_missing", f"{request_id}.{stem}", f"missing OGG candidate: {ogg_path}")
        elif not _valid_ogg(ogg_path):
            _issue(issues, "audio_invalid_ogg", f"{request_id}.{stem}", "OGG candidate has invalid page framing")
        duration: float | None = None
        if not wav_path.is_file():
            _issue(issues, "audio_master_missing", f"{request_id}.{stem}", f"missing 48k24b WAV master: {wav_path}")
        else:
            try:
                with wave.open(str(wav_path), "rb") as source:
                    if source.getframerate() != 48000:
                        _issue(issues, "audio_sample_rate", f"{request_id}.{stem}", f"expected 48000 Hz, got {source.getframerate()}")
                    if source.getsampwidth() != 3:
                        _issue(issues, "audio_bit_depth", f"{request_id}.{stem}", f"expected 24-bit PCM, got {source.getsampwidth() * 8}-bit")
                    if source.getnchannels() != 2:
                        _issue(issues, "audio_channels", f"{request_id}.{stem}", f"expected stereo, got {source.getnchannels()} channels")
                    duration = source.getnframes() / source.getframerate() if source.getframerate() else None
            except (OSError, wave.Error) as exc:
                _issue(issues, "audio_invalid_wav", f"{request_id}.{stem}", str(exc))
        if duration is not None:
            durations[stem] = duration
            if not (float(duration_range[0]) <= duration <= float(duration_range[1])):
                _issue(issues, "audio_duration", f"{request_id}.{stem}", f"expected {duration_range[0]}-{duration_range[1]} seconds, got {duration:.3f}")
        measurement = measurement_map.get(f"{stem}.wav")
        if not isinstance(measurement, dict):
            _issue(issues, "audio_measurement_missing", f"{request_id}.{stem}", "measurement entry is required")
        else:
            lufs = _numeric(measurement.get("integrated_loudness_lufs"))
            peak = _numeric(measurement.get("peak_dbfs"))
            if lufs is None or not (float(lufs_range[0]) <= lufs <= float(lufs_range[1])):
                _issue(issues, "audio_loudness", f"{request_id}.{stem}", f"integrated loudness must be {lufs_range[0]} to {lufs_range[1]} LUFS")
            if peak is None or peak > peak_max:
                _issue(issues, "audio_peak", f"{request_id}.{stem}", f"peak must be <= {peak_max} dBFS")
        if isinstance(meta, dict):
            required_meta = ("duration", "sample_rate_hz", "bit_depth", "channels", "loop_safe", "loop_start_sample", "loop_end_sample")
            for field in required_meta:
                if field not in meta:
                    _issue(issues, "audio_meta_field", f"{request_id}.{stem}.{field}", "required audio metadata is missing")
            meta_duration = _numeric(meta.get("duration"))
            if duration is not None and meta_duration is not None and abs(meta_duration - duration) > 0.1:
                _issue(issues, "audio_meta_duration", f"{request_id}.{stem}.duration", "metadata duration does not match WAV")
            if meta.get("loop_safe") is not True:
                _issue(issues, "audio_loop", f"{request_id}.{stem}.loop_safe", "loop_safe must be true")
            if not isinstance(meta.get("loop_start_sample"), int) or not isinstance(meta.get("loop_end_sample"), int) or int(meta.get("loop_end_sample", 0)) <= int(meta.get("loop_start_sample", 0)):
                _issue(issues, "audio_loop_points", f"{request_id}.{stem}", "valid loop_start_sample and loop_end_sample are required")
    tolerance = spec.get("matched_duration_tolerance_seconds")
    if tolerance is not None and len(durations) == len(spec.get("stems", [])) and max(durations.values()) - min(durations.values()) > float(tolerance):
        _issue(issues, "audio_pair_duration", request_id, f"matched variants differ by more than {tolerance} seconds")
    return durations


def validate_project(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    issues: list[dict[str, str]] = []
    contract_path = project_root / CONTRACT_PATH
    contract = _load_json(contract_path, issues, "contract")
    if not isinstance(contract, dict):
        return {"ok": False, "issues": issues}
    map_spec = contract.get("map")
    if isinstance(map_spec, dict):
        _check_map(project_root, map_spec, issues)
    for spec in contract.get("characters", []):
        if isinstance(spec, dict):
            _check_character(project_root, spec, issues)
    environment_spec = contract.get("environments")
    if isinstance(environment_spec, dict):
        _check_environments(project_root, environment_spec, issues)
    for spec in contract.get("audio", []):
        if isinstance(spec, dict):
            _check_audio(project_root, spec, issues)
    return {"ok": not issues, "issues": issues, "issue_count": len(issues)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, help="UW project root; defaults to the repository root")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--require-complete", action="store_true", help="return failure while any spec is invalid")
    args = parser.parse_args()
    root = args.project_root.resolve() if args.project_root else Path(__file__).resolve().parents[2]
    result = validate_project(root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"runtime asset specs: {'ready' if result['ok'] else 'pending'} | issues={result.get('issue_count', len(result['issues']))}")
        for item in result["issues"]:
            print(f"- {item['code']}: {item['path']} - {item['message']}")
    return 1 if args.require_complete and not result["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
