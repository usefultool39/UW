#!/usr/bin/env python3
"""Validate the materials request registry and inbox sidecars using stdlib only."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = ROOT / "REQUESTS.csv"
VALID_STATUSES = {
    "requested", "received", "reviewing", "changes_requested",
    "approved", "integrated", "deferred", "rejected",
}
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".psd", ".clip",
    ".wav", ".ogg", ".mp3", ".m4a", ".aac", ".mp4", ".mov", ".zip",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")


def validate_requests() -> tuple[set[str], int]:
    errors = 0
    ids: set[str] = set()
    required = {"request_id", "priority", "status", "deliverable_dir", "title"}
    with REQUESTS.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = required - set(reader.fieldnames or [])
        if missing:
            fail(f"REQUESTS.csv missing columns: {sorted(missing)}")
            return ids, 1
        for line, row in enumerate(reader, start=2):
            request_id = (row.get("request_id") or "").strip()
            if not request_id:
                fail(f"REQUESTS.csv:{line} missing request_id")
                errors += 1
                continue
            if request_id in ids:
                fail(f"REQUESTS.csv:{line} duplicate request_id {request_id}")
                errors += 1
            ids.add(request_id)
            status = (row.get("status") or "").strip()
            if status not in VALID_STATUSES:
                fail(f"REQUESTS.csv:{line} invalid status {status!r}")
                errors += 1
            deliverable = (row.get("deliverable_dir") or "").strip()
            path = ROOT.parent / deliverable
            if not path.is_dir():
                fail(f"REQUESTS.csv:{line} missing deliverable_dir {deliverable}")
                errors += 1
    return ids, errors


def validate_inbox(request_ids: set[str]) -> int:
    errors = 0
    inbox = ROOT / "inbox"
    # 找所有 master sidecar：<request_id>_<任意>_v001.md
    master_by_dir: dict[tuple[Path, str], Path] = {}
    for path in inbox.rglob("*"):
        if not path.is_file() or path.name in {".gitkeep", "README.md"}:
            continue
        if path.suffix.lower() != ".md":
            continue
        if not re.search(r"_v\d+", path.name):
            continue
        request_id = path.name.split("_", 1)[0]
        if request_id in request_ids:
            master_by_dir[(path.parent, request_id)] = path
    def find_master(p: Path, rid: str) -> Path | None:
        # 从自身向上逐级找 master sidecar
        cur = p.parent
        while True:
            m = master_by_dir.get((cur, rid))
            if m is not None:
                return m
            if cur == inbox:
                return None
            cur = cur.parent
    for path in inbox.rglob("*"):
        if not path.is_file() or path.name in {".gitkeep", "README.md"}:
            continue
        if path.suffix.lower() not in BINARY_SUFFIXES:
            continue
        stem = path.name.split(".", 1)[0]
        request_id = stem.split("_", 1)[0]
        if request_id not in request_ids:
            # 向上找最近的 request_id_ 前缀目录
            cur = path.parent
            while cur != inbox.parent:
                parent_stem = cur.name.split(".", 1)[0]
                parent_req = parent_stem.split("_", 1)[0]
                if parent_req in request_ids:
                    request_id = parent_req
                    break
                cur = cur.parent
            else:
                fail(f"unregistered request id in filename: {path.relative_to(ROOT)}")
                errors += 1
                continue
            if request_id not in request_ids:
                fail(f"unregistered request id in filename: {path.relative_to(ROOT)}")
                errors += 1
                continue
        master = find_master(path, request_id)
        if master is not None:
            continue
        sidecar = path.with_suffix(".md")
        if not sidecar.exists():
            fail(f"missing sidecar: {sidecar.relative_to(ROOT)}")
            errors += 1
    return errors


def main() -> int:
    request_ids, errors = validate_requests()
    errors += validate_inbox(request_ids)
    if errors:
        print(f"materials check failed: {errors} error(s)")
        return 1
    print(f"materials check passed: {len(request_ids)} requests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
