#!/usr/bin/env python3
"""Report whether the Pre-Capture materials and authored story are ready.

This is intentionally a read-only report. It does not change request statuses,
manifest rows, or story content. The authored story contract is deliberately
explicit so that a long Day 1-117 content bank cannot be mistaken for the
focused four-act Pre-Capture route.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


PRECAPTURE_REQUESTS = (
    "NAR-CANON-001",
    "NAR-PRECAP-001",
    "WORLD-MACRO-001",
    "WORLD-MICRO-001",
    "CHAR-DEPTH-001",
    "NAR-ADAPT-001",
    "QA-CANON-001",
)
# These are the first-phase runtime gates. A received binary is not enough:
# the request must also have a complete sidecar, an in-scope manifest source,
# and (where applicable) a runtime hash that passes check_materials.py.
RUNTIME_REQUESTS = (
    "VIS-UI-001",
    "VIS-POR-001",
    "AUD-BGM-001",
    "AUD-AMB-001",
    "VIS-MAP-001",
    "VIS-CHR-001",
    "VIS-CHR-002",
    "VIS-CHR-003",
    "VIS-ENV-001",
    "VIS-VFX-001",
    "VIS-KA-002",
    "AUD-BGM-002",
    "AUD-BGM-003",
    "AUD-AMB-002",
    "AUD-SFX-001",
    "AUD-SFX-002",
)
READY_STATUSES = {"received", "reviewing", "approved", "integrated"}
ACTS = ("act_0", "act_1", "act_2", "act_3")
CAPTURE_ENDING_IDS = {"precapture_alice_captured", "alice_captured"}
SIDECAR_RE = re.compile(r"_v\d+\.md$", re.IGNORECASE)
SIDECAR_FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(request_id|creator/source|created_at|license|source_url|intended_use)\s*:\s*(.*?)\s*$", re.IGNORECASE | re.MULTILINE)
IGNORED_NAMES = {".gitkeep", "README.md"}
REQUIRED_SIDECAR_FIELDS = {"request_id", "creator/source", "created_at", "license", "source_url", "intended_use"}


def _project_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    # This is the location used after installation at materials/tools/.
    return Path(__file__).resolve().parents[2]


def _load_requests(materials_root: Path) -> dict[str, dict[str, str]]:
    path = materials_root / "REQUESTS.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        return {
            (row.get("request_id") or "").strip(): row
            for row in csv.DictReader(fh)
            if (row.get("request_id") or "").strip()
        }


def _load_manifest(materials_root: Path) -> list[dict[str, str]]:
    path = materials_root / "MANIFEST.csv"
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _content_files(directory: Path, request_id: str | None = None) -> list[Path]:
    if not directory.is_dir():
        return []
    files = sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.name not in IGNORED_NAMES
    )
    if not request_id:
        return files
    prefix = f"{request_id}_"
    return [
        path
        for path in files
        if path.name.startswith(prefix)
        or any(parent.name.startswith(prefix) for parent in path.parents if parent != directory)
    ]


def _sidecar_issues(path: Path, request_id: str) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"cannot read sidecar {path.name}: {exc}"]

    values = {
        key.lower(): value.strip()
        for key, value in SIDECAR_FIELD_RE.findall(text)
    }
    issues = [
        f"sidecar {path.name} missing field {field}"
        for field in sorted(REQUIRED_SIDECAR_FIELDS)
        if not values.get(field)
    ]
    declared_request = values.get("request_id")
    if declared_request and declared_request != request_id:
        issues.append(
            f"sidecar {path.name} request_id={declared_request} does not match {request_id}"
        )
    return issues


def _request_report(
    project_root: Path,
    row: dict[str, str] | None,
    manifest_rows: list[dict[str, str]],
) -> dict[str, Any]:
    if row is None:
        return {
            "status": "missing-request",
            "source_present": False,
            "sidecar_present": False,
            "manifest_present": False,
            "ready": False,
            "issues": ["request is missing from REQUESTS.csv"],
        }

    request_id = (row.get("request_id") or "").strip()
    raw_dir = (row.get("deliverable_dir") or "").strip()
    deliverable = project_root / raw_dir
    files = _content_files(deliverable, request_id)
    sidecars = [path for path in files if SIDECAR_RE.search(path.name)]
    entries = [
        item
        for item in manifest_rows
        if (item.get("request_id") or "").strip() == request_id
    ]
    valid_manifest_sources = []
    out_of_scope_sources = []
    for item in entries:
        source_raw = (item.get("source_file") or "").strip()
        if not source_raw:
            continue
        # MANIFEST source_file paths are relative to materials/, unlike the
        # REQUESTS deliverable_dir paths which are repository-relative.
        source = project_root / "materials" / source_raw
        if source.is_file():
            valid_manifest_sources.append(source)
            try:
                in_deliverable = source.resolve().is_relative_to(deliverable.resolve())
            except AttributeError:
                in_deliverable = str(source.resolve()).startswith(str(deliverable.resolve()))
            if not in_deliverable:
                out_of_scope_sources.append(source_raw)

    issues: list[str] = []
    status = (row.get("status") or "").strip()
    if status not in READY_STATUSES:
        issues.append(f"status={status or 'empty'}")
    if not deliverable.is_dir():
        issues.append(f"missing deliverable_dir={raw_dir or 'empty'}")
    if not files:
        issues.append("no files in deliverable directory")
    if not sidecars:
        issues.append("no versioned sidecar")
    else:
        for sidecar in sidecars:
            issues.extend(_sidecar_issues(sidecar, request_id))
    if not entries:
        issues.append("no MANIFEST.csv row")
    elif not valid_manifest_sources:
        issues.append("MANIFEST rows have no existing source_file")
    if out_of_scope_sources:
        issues.append("MANIFEST source_file outside deliverable_dir")

    return {
        "status": status or "empty",
        "deliverable_dir": raw_dir,
        "file_count": len(files),
        "sidecar_count": len(sidecars),
        "manifest_count": len(entries),
        "manifest_source_count": len(valid_manifest_sources),
        "source_present": bool(files),
        "sidecar_present": bool(sidecars),
        "manifest_present": bool(valid_manifest_sources),
        "ready": not issues,
        "issues": issues,
    }


def _event_markers(event: dict[str, Any]) -> tuple[str | None, bool]:
    act = event.get("precapture_act")
    if act is None and isinstance(event.get("metadata"), dict):
        act = event["metadata"].get("precapture_act")
    if act is None and isinstance(event.get("authored"), dict):
        act = event["authored"].get("precapture_act")
    key_node = bool(event.get("precapture_key_node"))
    return (str(act) if act is not None else None, key_node)


def _choice_effects(event: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    for choice in event.get("choices", []):
        if not isinstance(choice, dict):
            continue
        effects = choice.get("effects")
        if isinstance(effects, dict):
            result.append((str(choice.get("id") or "choice"), effects))
    return result


def _written_flags(effects: dict[str, Any]) -> set[str]:
    flags = set()
    for key in ("flags", "flag_deltas"):
        value = effects.get(key)
        if isinstance(value, dict):
            flags.update(str(item) for item in value)
    return flags


def _read_flags(event: dict[str, Any]) -> set[str]:
    trigger = event.get("trigger")
    if not isinstance(trigger, dict):
        return set()
    flags = set()
    for key in ("required_flags", "required_any_flags", "forbidden_flags"):
        value = trigger.get(key)
        if isinstance(value, dict):
            flags.update(str(item) for item in value)
    return flags


def _story_report(project_root: Path) -> dict[str, Any]:
    paths = [
        project_root / "data" / "story" / "events_chapter_01.json",
        project_root / "data" / "story" / "events_precapture_chapter_01.json",
    ]
    if not paths[0].is_file():
        return {
            "events": 0,
            "marked_nodes": 0,
            "acts": [],
            "capture_endpoints": [],
            "cross_node_echoes": 0,
            "ready": False,
            "issues": [f"missing story file={paths[0].relative_to(project_root)}"],
        }
    try:
        event_rows: list[dict[str, Any]] = []
        for path in paths:
            if not path.is_file():
                continue
            raw = json.loads(path.read_text(encoding="utf-8"))
            rows = raw.get("events") if isinstance(raw, dict) else raw
            if isinstance(rows, list):
                event_rows.extend(row for row in rows if isinstance(row, dict))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "events": 0,
            "marked_nodes": 0,
            "acts": [],
            "capture_endpoints": [],
            "cross_node_echoes": 0,
            "ready": False,
            "issues": [f"cannot load story file: {exc}"],
        }

    events = event_rows
    if not events:
        return {
            "events": 0,
            "marked_nodes": 0,
            "acts": [],
            "capture_endpoints": [],
            "cross_node_echoes": 0,
            "ready": False,
            "issues": ["story events must be a non-empty list"],
        }

    marked: list[tuple[str, dict[str, Any]]] = []
    acts: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            continue
        act, key_node = _event_markers(event)
        if act is not None:
            acts.add(act)
        if act is not None or key_node:
            marked.append((str(event.get("id") or ""), event))

    endpoint_ids: set[str] = set()
    endpoint_events: list[tuple[str, dict[str, Any]]] = []
    for event_id, event in marked:
        endpoint = event.get("precapture_endpoint")
        if endpoint is not None:
            endpoint_ids.add(str(endpoint))
            endpoint_events.append((event_id, event))
        for _choice_id, effects in _choice_effects(event):
            ending_id = effects.get("ending_id")
            if ending_id is not None:
                endpoint_ids.add(str(ending_id))

    writers: list[tuple[str, str]] = []
    readers: list[tuple[str, str]] = []
    for event_id, event in marked:
        for choice_id, effects in _choice_effects(event):
            for flag in _written_flags(effects):
                writers.append((f"{event_id}:{choice_id}", flag))
        for flag in _read_flags(event):
            readers.append((event_id, flag))
    echoes = {
        (writer_id, flag, reader_id)
        for writer_id, flag in writers
        for reader_id, read_flag in readers
        if flag == read_flag and writer_id.split(":", 1)[0] != reader_id
    }

    issues: list[str] = []
    missing_acts = [act for act in ACTS if act not in acts]
    if missing_acts:
        issues.append(f"missing authored acts={','.join(missing_acts)}")
    if not 8 <= len(marked) <= 12:
        issues.append(f"marked key nodes={len(marked)}; expected 8-12")
    if not endpoint_ids.intersection(CAPTURE_ENDING_IDS):
        issues.append("missing fixed Alice capture endpoint")
    if len(endpoint_events) != 1:
        issues.append(f"fixed capture endpoint events={len(endpoint_events)}; expected exactly 1")
    elif endpoint_events[0][0] != marked[-1][0]:
        issues.append("fixed capture endpoint must be the final marked key node")
    else:
        endpoint_id, endpoint_event = endpoint_events[0]
        marker = str(endpoint_event.get("precapture_endpoint") or "")
        choice_endings = {
            str(effects.get("ending_id"))
            for _choice_id, effects in _choice_effects(endpoint_event)
            if effects.get("ending_id") is not None
        }
        if marker not in choice_endings:
            issues.append(f"capture endpoint {endpoint_id} lacks matching choice ending_id")
    if len(echoes) < 3:
        issues.append(f"cross-node echoes={len(echoes)}; expected at least 3")

    return {
        "events": len(events),
        "marked_nodes": len(marked),
        "marked_event_ids": [event_id for event_id, _ in marked],
        "acts": sorted(acts),
        "capture_endpoints": sorted(endpoint_ids),
        "cross_node_echoes": len(echoes),
        "ready": not issues,
        "issues": issues,
    }


def evaluate(project_root: Path) -> dict[str, Any]:
    materials_root = project_root / "materials"
    requests = _load_requests(materials_root)
    manifest = _load_manifest(materials_root)
    narrative_report = {
        request_id: _request_report(project_root, requests.get(request_id), manifest)
        for request_id in PRECAPTURE_REQUESTS
    }
    runtime_report = {
        request_id: _request_report(project_root, requests.get(request_id), manifest)
        for request_id in RUNTIME_REQUESTS
    }
    narrative_materials_ready = all(item["ready"] for item in narrative_report.values())
    runtime_materials_ready = all(item["ready"] for item in runtime_report.values())
    materials_ready = narrative_materials_ready and runtime_materials_ready
    story = _story_report(project_root)
    return {
        "phase": "0.5.0-pre-capture",
        "status": "ready" if materials_ready and story["ready"] else "pending",
        "materials_ready": materials_ready,
        "narrative_materials_ready": narrative_materials_ready,
        "runtime_materials_ready": runtime_materials_ready,
        "story_ready": story["ready"],
        "requests": narrative_report,
        "runtime_requests": runtime_report,
        "story": story,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, help="UW project root; defaults to the repository root")
    parser.add_argument("--require-complete", action="store_true", help="return failure while any readiness gate is pending")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    try:
        result = evaluate(_project_root(args.project_root))
    except (OSError, KeyError, ValueError) as exc:
        print(f"precapture readiness error: {exc}")
        return 2

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"Pre-Capture: {result['status']} | "
            f"materials={'ready' if result['materials_ready'] else 'pending'} | "
            f"story={'ready' if result['story_ready'] else 'pending'}"
        )
        for request_id, item in result["requests"].items():
            suffix = f"; issues: {', '.join(item['issues'])}" if item["issues"] else ""
            print(f"- {request_id}: {item['status']}{suffix}")
        print(
            "- runtime materials: "
            f"{'ready' if result['runtime_materials_ready'] else 'pending'} "
            f"({len(result['runtime_requests'])} required requests)"
        )
        for request_id, item in result["runtime_requests"].items():
            suffix = f"; issues: {', '.join(item['issues'])}" if item["issues"] else ""
            print(f"  - {request_id}: {item['status']}{suffix}")
        story = result["story"]
        suffix = f"; issues: {', '.join(story['issues'])}" if story["issues"] else ""
        print(
            f"- story: {story['events']} events, {story['marked_nodes']} marked key nodes, "
            f"acts={','.join(story['acts']) or 'none'}, echoes={story['cross_node_echoes']}"
            f"{suffix}"
        )

    if args.require_complete and result["status"] != "ready":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
