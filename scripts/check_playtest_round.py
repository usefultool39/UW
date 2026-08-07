#!/usr/bin/env python3
"""Validate QA-PLAY-001 human playtest record completeness without inventing evidence."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUND_DIR = ROOT / "materials" / "inbox" / "research" / "playtest"
PLAYER_IDS = ("player01", "player02", "player03")
RECORD_NAMES = tuple(f"QA-PLAY-001_{player_id}.md" for player_id in PLAYER_IDS)
FIELD_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*):\s*(.*?)\s*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ENUMS = {
    "understood_day_goal": {"yes", "partial", "no"},
    "named_action_cost": {"yes", "partial", "no"},
    "named_action_benefit": {"yes", "partial", "no"},
    "bypassed_day_gate": {"yes", "no"},
    "continue_interest": {"yes", "uncertain", "no"},
    "completed_precapture_route": {"yes"},
    "reached_alice_captured": {"yes"},
    "post_capture_progress_blocked": {"yes"},
    "recognized_choice_echo": {"yes", "partial", "no"},
    "understood_capture_reason": {"yes", "partial", "no"},
    "consent_recorded": {"yes"},
}
REQUIRED_TEXT = {
    "status",
    "player_id",
    "session_date",
    "device_input",
    "prior_experience",
    "recording_file",
    "highest_frequency_blocker",
    "endpoint_explanation",
}
REQUIRED_INTS = {"first_effective_interaction_seconds", "hint_count", "total_session_minutes"}
COMPLETE_STATUS = "received-human-run"
PENDING_STATUS = "pending-human-run"


@dataclass(frozen=True)
class RecordResult:
    path: Path
    player_id: str
    status: str
    complete: bool
    errors: tuple[str, ...]
    fields: dict[str, str]


def parse_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FIELD_RE.match(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def validate_record(path: Path, expected_player_id: str) -> RecordResult:
    if not path.is_file():
        return RecordResult(path, expected_player_id, "missing", False, ("record file is missing",), {})

    fields = parse_fields(path)
    status = fields.get("status", "")
    player_id = fields.get("player_id", "")
    errors: list[str] = []

    if player_id != expected_player_id:
        errors.append(f"player_id must be {expected_player_id!r}")
    if status not in {PENDING_STATUS, COMPLETE_STATUS}:
        errors.append(f"status must be {PENDING_STATUS!r} or {COMPLETE_STATUS!r}")

    if status == COMPLETE_STATUS:
        for key in sorted(REQUIRED_TEXT):
            if not fields.get(key, "").strip():
                errors.append(f"{key} is required for a completed human run")
        if fields.get("session_date") and not DATE_RE.fullmatch(fields["session_date"]):
            errors.append("session_date must use YYYY-MM-DD")
        for key, allowed in ENUMS.items():
            value = fields.get(key, "")
            if value not in allowed:
                errors.append(f"{key} must be one of {sorted(allowed)}")
        for key in sorted(REQUIRED_INTS):
            raw = fields.get(key, "")
            try:
                value = int(raw)
                if value < 0:
                    raise ValueError
            except (TypeError, ValueError):
                errors.append(f"{key} must be a non-negative integer")

    complete = status == COMPLETE_STATUS and not errors
    return RecordResult(path, player_id or expected_player_id, status or "missing", complete, tuple(errors), fields)


def evaluate_round(round_dir: Path = DEFAULT_ROUND_DIR) -> dict:
    records = [
        validate_record(round_dir / name, player_id)
        for name, player_id in zip(RECORD_NAMES, PLAYER_IDS)
    ]
    complete_count = sum(record.complete for record in records)
    invalid_count = sum(bool(record.errors) for record in records)
    return {
        "round_id": "QA-PLAY-001",
        "status": "received-human-run" if complete_count == len(records) else "pending-human-run",
        "complete_count": complete_count,
        "expected_count": len(records),
        "invalid_count": invalid_count,
        "records": [
            {
                "path": str(record.path),
                "player_id": record.player_id,
                "status": record.status,
                "complete": record.complete,
                "errors": list(record.errors),
            }
            for record in records
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round-dir", type=Path, default=DEFAULT_ROUND_DIR)
    parser.add_argument("--require-complete", action="store_true", help="fail unless all three human records are complete")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    result = evaluate_round(args.round_dir)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"{result['round_id']}: {result['status']} "
            f"({result['complete_count']}/{result['expected_count']} complete, "
            f"{result['invalid_count']} invalid)"
        )
        for record in result["records"]:
            suffix = f"; errors: {', '.join(record['errors'])}" if record["errors"] else ""
            print(f"- {record['player_id']}: {record['status']}{suffix}")

    if result["invalid_count"]:
        return 2
    if args.require_complete and result["status"] != "received-human-run":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
