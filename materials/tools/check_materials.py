#!/usr/bin/env python3
"""Validate the materials request registry and inbox sidecars using stdlib only."""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = ROOT / "REQUESTS.csv"
MANIFEST = ROOT / "MANIFEST.csv"
REPO_ROOT = ROOT.parent
VALID_STATUSES = {
    "requested", "received", "reviewing", "changes_requested",
    "approved", "integrated", "deferred", "rejected",
}
VALID_MANIFEST_STATUSES = {
    "approved-candidate", "approved-for-direction", "changes_requested",
    "received", "review-only", "integrated", "deferred", "rejected",
}
RUNTIME_ALLOWED_STATUSES = {"approved-candidate", "integrated"}
MANIFEST_COLUMNS = {
    "asset_id", "request_id", "status", "source_file", "runtime_file",
    "sha256", "creator", "tool_model", "created_at", "license",
    "source_url", "attribution_required", "attribution_text",
    "approved_by", "approved_at", "integrated_at", "replaces_asset_id", "notes",
}
RUNTIME_PREFIX = Path("frontend/public/assets/runtime")

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".psd", ".clip",
    ".wav", ".ogg", ".mp3", ".m4a", ".aac", ".mp4", ".mov", ".zip",
}
HASH_NORMALIZED_TEXT_SUFFIXES = {".csv", ".json", ".md", ".svg", ".txt"}


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



def _sha256(path: Path) -> str:
    if path.suffix.lower() in HASH_NORMALIZED_TEXT_SUFFIXES:
        # Git's autocrlf may materialize text files as CRLF on Windows while
        # MANIFEST hashes record the canonical LF bytes used in the repository.
        data = path.read_bytes().replace(b"\r\n", b"\n")
        return hashlib.sha256(data).hexdigest()
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(raw: str, *, base: Path, label: str) -> tuple[Path | None, str | None]:
    value = raw.strip()
    if not value:
        return None, f"{label} is empty"
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None, f"{label} must be a repository-relative path: {value}"
    return base / candidate, None


def validate_manifest(request_ids: set[str]) -> int:
    errors = 0
    manifest_rows: set[tuple[str, str]] = set()
    runtime_paths: set[str] = set()

    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = set(reader.fieldnames or [])
        missing = MANIFEST_COLUMNS - fields
        if missing:
            fail(f"MANIFEST.csv missing columns: {sorted(missing)}")
            return 1

        for line, row in enumerate(reader, start=2):
            asset_id = (row.get("asset_id") or "").strip()
            request_id = (row.get("request_id") or "").strip()
            status = (row.get("status") or "").strip()
            source_raw = (row.get("source_file") or "").strip()
            runtime_raw = (row.get("runtime_file") or "").strip()
            expected_hash = (row.get("sha256") or "").strip().lower()
            approved_by = (row.get("approved_by") or "").strip()
            approved_at = (row.get("approved_at") or "").strip()
            integrated_at = (row.get("integrated_at") or "").strip()
            replaces = (row.get("replaces_asset_id") or "").strip()

            if not asset_id:
                fail(f"MANIFEST.csv:{line} missing asset_id")
                errors += 1
            row_key = (asset_id, source_raw)
            if row_key in manifest_rows:
                fail(f"MANIFEST.csv:{line} duplicate asset/source row {asset_id}: {source_raw}")
                errors += 1
            manifest_rows.add(row_key)

            is_registry_metadata = status == "received" and Path(source_raw).suffix.lower() in {".json", ".csv"}
            if request_id not in request_ids and not is_registry_metadata:
                fail(f"MANIFEST.csv:{line} unknown request_id {request_id!r}")
                errors += 1
            if status not in VALID_MANIFEST_STATUSES:
                fail(f"MANIFEST.csv:{line} invalid status {status!r}")
                errors += 1
            if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                fail(f"MANIFEST.csv:{line} invalid sha256 for {asset_id}")
                errors += 1

            source, path_error = _safe_relative_path(source_raw, base=ROOT, label="source_file")
            if path_error:
                fail(f"MANIFEST.csv:{line} {path_error}")
                errors += 1
            elif source is None or not source.is_file():
                fail(f"MANIFEST.csv:{line} missing source_file {source_raw}")
                errors += 1
            elif expected_hash and _sha256(source) != expected_hash:
                fail(f"MANIFEST.csv:{line} source hash mismatch for {asset_id}")
                errors += 1

            if runtime_raw:
                runtime_rel = Path(runtime_raw)
                runtime_key = runtime_rel.as_posix()
                if status not in RUNTIME_ALLOWED_STATUSES:
                    fail(f"MANIFEST.csv:{line} status {status!r} cannot declare runtime_file for {asset_id}")
                    errors += 1
                if not approved_by or not approved_at:
                    fail(f"MANIFEST.csv:{line} runtime_file needs approved_by and approved_at for {asset_id}")
                    errors += 1
                if runtime_rel.parts[:len(RUNTIME_PREFIX.parts)] != RUNTIME_PREFIX.parts:
                    fail(f"MANIFEST.csv:{line} runtime_file must stay under {RUNTIME_PREFIX}: {runtime_raw}")
                    errors += 1
                if runtime_key in runtime_paths:
                    fail(f"MANIFEST.csv:{line} duplicate runtime_file {runtime_raw}")
                    errors += 1
                runtime_paths.add(runtime_key)
                runtime, runtime_error = _safe_relative_path(runtime_raw, base=REPO_ROOT, label="runtime_file")
                if runtime_error:
                    fail(f"MANIFEST.csv:{line} {runtime_error}")
                    errors += 1
                elif runtime is None or not runtime.is_file():
                    fail(f"MANIFEST.csv:{line} missing runtime_file {runtime_raw}")
                    errors += 1
                elif expected_hash and _sha256(runtime) != expected_hash:
                    fail(f"MANIFEST.csv:{line} runtime hash mismatch for {asset_id}")
                    errors += 1
                if not integrated_at:
                    fail(f"MANIFEST.csv:{line} runtime_file needs integrated_at for {asset_id}")
                    errors += 1
            elif integrated_at:
                fail(f"MANIFEST.csv:{line} integrated_at exists without runtime_file for {asset_id}")
                errors += 1

            # replaces_asset_id is historical provenance and may point to an
            # archived row intentionally omitted from the current manifest.
            _ = replaces

    runtime_root = REPO_ROOT / RUNTIME_PREFIX
    if runtime_root.is_dir():
        for runtime in sorted(path for path in runtime_root.rglob("*") if path.is_file()):
            runtime_key = runtime.relative_to(REPO_ROOT).as_posix()
            if runtime_key not in runtime_paths:
                fail(f"unregistered runtime file: {runtime_key}")
                errors += 1

    return errors

def main() -> int:
    request_ids, errors = validate_requests()
    errors += validate_inbox(request_ids)
    errors += validate_manifest(request_ids)
    if errors:
        print(f"materials check failed: {errors} error(s)")
        return 1
    print(f"materials check passed: {len(request_ids)} requests; manifest sources and runtime hashes verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
