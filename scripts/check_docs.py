#!/usr/bin/env python3
"""Enforce UW's single-version documentation structure."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REQUIRED = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    DOCS / "README.md",
    DOCS / "PROJECT.md",
    DOCS / "PLAN.md",
    DOCS / "DELIVERY.md",
    DOCS / "art" / "ASSET_REVIEW.md",
]
FORBIDDEN_DIRS = [
    DOCS / "product",
    DOCS / "planning",
    DOCS / "delivery",
    DOCS / "research",
    DOCS / "archive",
]
FORBIDDEN_DOC_NAME = re.compile(
    r"(?:STATUS_|NEXT_PHASE|HANDOFF|ROADMAP|MVP_SCOPE|PRODUCT_BRIEF|PRODUCT_DIRECTION|"
    r"REQUIREMENTS|PLAYTEST|VERSIONING|RELEASE_PROCESS|(?:19|20)\d{6}|_v\d+)",
    re.IGNORECASE,
)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def version_sources(errors: list[str]) -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    frontend = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))["version"]
    backend_text = (ROOT / "backend" / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', backend_text, re.MULTILINE)
    backend = match.group(1) if match else "<missing>"
    if len({version, frontend, backend}) != 1:
        fail(f"version mismatch: VERSION={version}, frontend={frontend}, backend={backend}", errors)


def structure(errors: list[str]) -> None:
    for path in REQUIRED:
        if not path.is_file():
            fail(f"missing required document: {path.relative_to(ROOT)}", errors)
    for path in FORBIDDEN_DIRS:
        if path.exists():
            fail(f"obsolete documentation directory restored: {path.relative_to(ROOT)}", errors)
    for path in DOCS.rglob("*.md"):
        if FORBIDDEN_DOC_NAME.search(path.name) and path.parent.name != "adr":
            fail(f"parallel/versioned document name is forbidden: {path.relative_to(ROOT)}", errors)


def links(errors: list[str]) -> None:
    files = [*REQUIRED, *DOCS.rglob("*.md")]
    seen: set[Path] = set()
    for path in files:
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        for raw in LINK.findall(text):
            target = raw.strip().split("#", 1)[0]
            if not target or "://" in target or target.startswith(("mailto:", "/")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(f"broken link in {path.relative_to(ROOT)}: {target}", errors)


def main() -> int:
    errors: list[str] = []
    version_sources(errors)
    structure(errors)
    links(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"documentation check failed: {len(errors)} error(s)")
        return 1
    print("documentation check passed: one version, one plan, links valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
