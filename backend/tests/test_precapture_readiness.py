from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "materials" / "tools"))

from check_precapture_readiness import evaluate  # noqa: E402


REQUEST_COLUMNS = ["request_id", "status", "deliverable_dir"]
MANIFEST_COLUMNS = ["request_id", "source_file"]
REQUEST_IDS = (
    "NAR-CANON-001",
    "NAR-PRECAP-001",
    "WORLD-MACRO-001",
    "WORLD-MICRO-001",
    "CHAR-DEPTH-001",
    "NAR-ADAPT-001",
    "QA-CANON-001",
)
RUNTIME_REQUEST_IDS = (
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


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _make_project(tmp_path: Path, *, endpoint: bool = True) -> Path:
    root = tmp_path / "UW"
    materials = root / "materials"
    requests_dir = materials / "inbox" / "precapture"
    requests_dir.mkdir(parents=True)

    request_rows = []
    manifest_rows = []
    for index, request_id in enumerate(REQUEST_IDS + RUNTIME_REQUEST_IDS):
        deliverable = f"materials/inbox/precapture/{request_id}"
        directory = root / deliverable
        directory.mkdir(parents=True)
        file_name = f"{request_id}_v001.md"
        (directory / file_name).write_text(
            "\n".join([
                f"- request_id: {request_id}",
                "- creator/source: user return",
                "- created_at: 2026-08-06",
                "- license: user-provided reference",
                "- source_url: https://example.test/source",
                "- intended_use: Pre-Capture review",
                "",
            ]),
            encoding="utf-8",
        )
        request_rows.append(
            {"request_id": request_id, "status": "received", "deliverable_dir": deliverable}
        )
        manifest_rows.append(
            {"request_id": request_id, "source_file": f"inbox/precapture/{request_id}/{file_name}"}
        )

    _write_csv(materials / "REQUESTS.csv", REQUEST_COLUMNS, request_rows)
    _write_csv(materials / "MANIFEST.csv", MANIFEST_COLUMNS, manifest_rows)

    events = []
    for index in range(8):
        event = {
            "id": f"precapture_{index}",
            "precapture_act": f"act_{min(index // 2, 3)}",
            "precapture_key_node": True,
            "trigger": {"required_flags": {f"echo_{index - 1}": 1}} if index else {},
            "choices": [
                {
                    "id": "advance",
                    "effects": {"flags": {f"echo_{index}": 1}},
                }
            ],
        }
        events.append(event)
    if endpoint:
        events[-1]["precapture_endpoint"] = "precapture_alice_captured"
        events[-1]["choices"][0]["effects"]["ending_id"] = "precapture_alice_captured"
    (root / "data" / "story").mkdir(parents=True)
    (root / "data" / "story" / "events_chapter_01.json").write_text(
        json.dumps({"events": events}), encoding="utf-8"
    )
    return root


def test_precapture_readiness_requires_all_four_acts_and_materials(tmp_path):
    result = evaluate(_make_project(tmp_path))

    assert result["status"] == "ready"
    assert result["materials_ready"] is True
    assert result["narrative_materials_ready"] is True
    assert result["runtime_materials_ready"] is True
    assert result["story_ready"] is True
    assert result["story"]["marked_nodes"] == 8
    assert result["story"]["cross_node_echoes"] >= 3


def test_precapture_readiness_requires_runtime_material_requests(tmp_path):
    root = _make_project(tmp_path)
    requests_path = root / "materials" / "REQUESTS.csv"
    with requests_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rows = [row for row in rows if row["request_id"] != "VIS-MAP-001"]
    _write_csv(requests_path, REQUEST_COLUMNS, rows)

    result = evaluate(root)

    assert result["status"] == "pending"
    assert result["narrative_materials_ready"] is True
    assert result["runtime_materials_ready"] is False
    assert result["materials_ready"] is False
    assert result["runtime_requests"]["VIS-MAP-001"]["status"] == "missing-request"


def test_precapture_readiness_reports_missing_fixed_endpoint(tmp_path):
    result = evaluate(_make_project(tmp_path, endpoint=False))

    assert result["status"] == "pending"
    assert result["materials_ready"] is True
    assert result["story_ready"] is False
    assert "missing fixed Alice capture endpoint" in result["story"]["issues"]


def test_precapture_readiness_rejects_incomplete_sidecar(tmp_path):
    root = _make_project(tmp_path)
    sidecar = root / "materials" / "inbox" / "precapture" / "NAR-CANON-001" / "NAR-CANON-001_v001.md"
    sidecar.write_text("- request_id: NAR-CANON-001\n", encoding="utf-8")

    result = evaluate(root)

    assert result["status"] == "pending"
    assert result["materials_ready"] is False
    assert "sidecar NAR-CANON-001_v001.md missing field license" in result["requests"]["NAR-CANON-001"]["issues"]


def test_precapture_readiness_rejects_manifest_source_from_another_request(tmp_path):
    root = _make_project(tmp_path)
    manifest = root / "materials" / "MANIFEST.csv"
    with manifest.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rows[0]["source_file"] = "inbox/precapture/NAR-PRECAP-001/NAR-PRECAP-001_v001.md"
    _write_csv(manifest, MANIFEST_COLUMNS, rows)

    result = evaluate(root)

    assert result["status"] == "pending"
    assert result["materials_ready"] is False
    assert "MANIFEST source_file outside deliverable_dir" in result["requests"]["NAR-CANON-001"]["issues"]


def test_precapture_readiness_requires_capture_endpoint_to_be_last(tmp_path):
    root = _make_project(tmp_path)
    story_path = root / "data" / "story" / "events_chapter_01.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    final_event = story["events"][-1]
    earlier_event = story["events"][-2]
    earlier_event["precapture_endpoint"] = final_event.pop("precapture_endpoint")
    earlier_event["choices"][0]["effects"]["ending_id"] = final_event["choices"][0]["effects"].pop("ending_id")
    story_path.write_text(json.dumps(story), encoding="utf-8")

    result = evaluate(root)

    assert result["story_ready"] is False
    assert "fixed capture endpoint must be the final marked key node" in result["story"]["issues"]


def test_precapture_readiness_requires_matching_choice_endpoint(tmp_path):
    root = _make_project(tmp_path)
    story_path = root / "data" / "story" / "events_chapter_01.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    story["events"][-1]["choices"][0]["effects"]["ending_id"] = "alice_captured"
    story_path.write_text(json.dumps(story), encoding="utf-8")

    result = evaluate(root)

    assert result["story_ready"] is False
    assert "capture endpoint precapture_7 lacks matching choice ending_id" in result["story"]["issues"]
