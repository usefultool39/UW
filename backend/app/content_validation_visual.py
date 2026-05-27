from __future__ import annotations

from typing import Any


Issue = dict[str, str]


def _add_issue(
    issues: list[Issue],
    *,
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append({"code": code, "path": path, "message": message})


def validate_visual_config(raw: dict[str, Any], rel_path: str, errors: list[Issue], warnings: list[Issue]) -> None:
    visual = raw.get("visual")
    if visual is None:
        return
    if not isinstance(visual, dict):
        _add_issue(errors, code="invalid_visual_config", path=f"{rel_path}.visual", message="Map visual config must be an object.")
        return

    tileset_manifest = visual.get("tileset_manifest")
    if tileset_manifest is not None and not isinstance(tileset_manifest, str):
        _add_issue(
            errors,
            code="invalid_visual_tileset_manifest",
            path=f"{rel_path}.visual.tileset_manifest",
            message="tileset_manifest must be a string path when present.",
        )

    camera = visual.get("camera")
    if camera is not None and not isinstance(camera, dict):
        _add_issue(errors, code="invalid_visual_config", path=f"{rel_path}.visual.camera", message="Camera config must be an object.")
    elif isinstance(camera, dict):
        for key in ("default_zoom", "background_zoom", "min_zoom", "max_zoom", "wheel_step", "follow_lerp"):
            value = camera.get(key)
            if value is not None and not isinstance(value, (int, float)):
                _add_issue(errors, code="invalid_visual_number", path=f"{rel_path}.visual.camera.{key}", message="Expected number.")
        min_zoom = camera.get("min_zoom")
        max_zoom = camera.get("max_zoom")
        if isinstance(min_zoom, (int, float)) and isinstance(max_zoom, (int, float)) and min_zoom > max_zoom:
            _add_issue(errors, code="invalid_visual_range", path=f"{rel_path}.visual.camera", message="min_zoom must be <= max_zoom.")

    movement = visual.get("movement")
    if movement is not None and not isinstance(movement, dict):
        _add_issue(errors, code="invalid_visual_config", path=f"{rel_path}.visual.movement", message="Movement config must be an object.")
    elif isinstance(movement, dict):
        for key in ("walk_speed", "min_walk_ms", "max_walk_ms"):
            value = movement.get(key)
            if value is not None and not isinstance(value, (int, float)):
                _add_issue(errors, code="invalid_visual_number", path=f"{rel_path}.visual.movement.{key}", message="Expected number.")
        min_ms = movement.get("min_walk_ms")
        max_ms = movement.get("max_walk_ms")
        if isinstance(min_ms, (int, float)) and isinstance(max_ms, (int, float)) and min_ms > max_ms:
            _add_issue(errors, code="invalid_visual_range", path=f"{rel_path}.visual.movement", message="min_walk_ms must be <= max_walk_ms.")

    performance = visual.get("performance")
    if performance is not None and not isinstance(performance, dict):
        _add_issue(errors, code="invalid_visual_config", path=f"{rel_path}.visual.performance", message="Performance config must be an object.")
    elif isinstance(performance, dict):
        for key in ("guide_interval_ms", "water_interval_ms", "weather_interval_ms"):
            value = performance.get(key)
            if value is not None and not isinstance(value, (int, float)):
                _add_issue(errors, code="invalid_visual_number", path=f"{rel_path}.visual.performance.{key}", message="Expected number.")
        if performance.get("bake_static_layers") is False:
            _add_issue(
                warnings,
                code="static_layer_bake_disabled",
                path=f"{rel_path}.visual.performance.bake_static_layers",
                message="Static layer baking is disabled; this may make local browser interaction slower.",
            )

