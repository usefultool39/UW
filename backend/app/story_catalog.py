"""Load main story node definitions (flags gating) from JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def default_catalog_path(project_root: Path) -> Path:
    return project_root / "data" / "story" / "main_nodes.json"


def load_main_nodes(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"nodes": {}}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {"nodes": {}}


def requirements_met(flags: dict[str, int], requires: dict[str, Any]) -> bool:
    if not requires:
        return True
    for key, want in requires.items():
        have = flags.get(key, 0)
        if isinstance(want, bool):
            if bool(have) != want:
                return False
        elif have != int(want):
            return False
    return True


def can_enter_node(
    nodes: dict[str, Any], current_id: str, target_id: str, flags: dict[str, int]
) -> tuple[bool, str]:
    raw = nodes.get(target_id)
    if not isinstance(raw, dict):
        return False, "unknown_node"
    req = raw.get("requires") or {}
    if not isinstance(req, dict):
        req = {}
    if not requirements_met(flags, req):
        return False, "requirements_not_met"
    allowed_from = raw.get("from")  # optional: list of ids that may transition here
    if isinstance(allowed_from, list) and allowed_from:
        if current_id not in allowed_from:
            return False, "invalid_transition"
    return True, "ok"
