from __future__ import annotations

import json
from pathlib import Path

from scripts.space_traversal import coverage_ingest_stub
from scripts.space_traversal import decode_validate_and_extract
from scripts.space_traversal import generate_baseline
from scripts.space_traversal import stable_manifest
from scripts.space_traversal import validate_snapshot_schema

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/pasted.txt"
SCHEMA = ROOT / "scripts/space_traversal/schemas/validate_report_schema.json"
COVERAGE_XML = ROOT / "scripts/space_traversal/fixtures/coverage.xml"


def test_decode_and_validate_roundtrip(tmp_path: Path) -> None:
    output = tmp_path / "decoded.json"
    extract = tmp_path / "gaps.json"

    result = decode_validate_and_extract.decode_and_validate(
        input_path=FIXTURE,
        output_path=output,
        extract_path=extract,
        schema_path=SCHEMA,
        stable_output=True,
        generate_baseline=False,
    )

    assert result["decoded"]["report"]["id"] == "artifact-001"
    written = json.loads(output.read_text())
    assert written["metadata"]["source"] == "unit-test"
    extracted = json.loads(extract.read_text())
    assert extracted["count"] == 2


def test_validate_snapshot_schema_accepts_fixture() -> None:
    decoded = decode_validate_and_extract.decode_base64_gzip(FIXTURE)
    validate_snapshot_schema.validate_snapshot(decoded, SCHEMA)


def test_stable_manifest_deterministic(tmp_path: Path) -> None:
    payload = {"b": 2, "a": [2, 1, {"z": 1, "y": 0}]}
    first = stable_manifest.write_stable_json(payload, tmp_path / "first.json")
    second = stable_manifest.write_stable_json(payload, tmp_path / "second.json")

    assert first.read_text() == second.read_text()


def test_generate_baseline_summary(tmp_path: Path) -> None:
    decoded = decode_validate_and_extract.decode_base64_gzip(FIXTURE)
    destination = tmp_path / "baseline.json"
    summary = {
        "report": {"id": decoded["report"]["id"], "generated_at": decoded["report"].get("generated_at", "")},
        "gap_count": len(decoded.get("gaps", [])),
    }
    stable_manifest.write_stable_json(summary, destination)
    loaded = json.loads(destination.read_text())
    assert loaded["gap_count"] == 2


def test_coverage_ingest_stub_reads_fixture(tmp_path: Path) -> None:
    output = tmp_path / "coverage.json"
    report_path = coverage_ingest_stub.write_stub_report(COVERAGE_XML, output)
    content = json.loads(report_path.read_text())
    assert content["coverage"]["src/example.py"]["covered"] == 2
