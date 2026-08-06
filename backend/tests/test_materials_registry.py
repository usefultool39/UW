from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "materials" / "tools" / "check_materials.py"
spec = importlib.util.spec_from_file_location("check_materials_registry", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, str]:
    materials = tmp_path / "materials"
    source = materials / "inbox" / "test" / "asset.bin"
    runtime = tmp_path / "frontend" / "public" / "assets" / "runtime" / "asset.bin"
    source.parent.mkdir(parents=True)
    runtime.parent.mkdir(parents=True)
    source.write_bytes(b"stable-asset")
    runtime.write_bytes(source.read_bytes())
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = materials / "MANIFEST.csv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "asset_id", "request_id", "status", "source_file", "runtime_file", "sha256",
        "creator", "tool_model", "created_at", "license", "source_url",
        "attribution_required", "attribution_text", "approved_by", "approved_at",
        "integrated_at", "replaces_asset_id", "notes",
    ]
    with manifest.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "asset_id": "TEST-ASSET",
            "request_id": "TEST-001",
            "status": "approved-candidate",
            "source_file": "inbox/test/asset.bin",
            "runtime_file": "frontend/public/assets/runtime/asset.bin",
            "sha256": digest,
            "integrated_at": "2026-08-06T00:00:00+08:00",
        })
    return materials, manifest, runtime, digest


def test_manifest_validates_source_and_runtime_hashes(tmp_path, monkeypatch):
    materials, manifest, _runtime, _digest = _fixture(tmp_path)
    monkeypatch.setattr(module, "ROOT", materials)
    monkeypatch.setattr(module, "MANIFEST", manifest)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

    assert module.validate_manifest({"TEST-001"}) == 0


def test_manifest_rejects_runtime_hash_drift(tmp_path, monkeypatch, capsys):
    materials, manifest, runtime, _digest = _fixture(tmp_path)
    runtime.write_bytes(b"tampered")
    monkeypatch.setattr(module, "ROOT", materials)
    monkeypatch.setattr(module, "MANIFEST", manifest)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

    assert module.validate_manifest({"TEST-001"}) == 1
    assert "runtime hash mismatch" in capsys.readouterr().out
