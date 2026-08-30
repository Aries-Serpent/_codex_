"""
Test Artifact Pipeline

Test module for artifact pipeline.
"""

#!/usr/bin/env python

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.space_traversal import (
    coverage_ingest_stub,
    decode_validate_and_extract,
    stable_manifest,
    validate_snapshot_schema,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/pasted.txt"
SCHEMA = ROOT / "scripts/space_traversal/schemas/validate_report_schema.json"
COVERAGE_XML = ROOT / "scripts/space_traversal/fixtures/coverage.xml"

DECODE_SCRIPT = "scripts/space_traversal/decode_validate_and_extract.py"
EXTRACT_SCRIPT = "scripts/space_traversal/extract_validate_gaps.py"


@pytest.mark.skipif(not Path(FIXTURE).exists(), reason="pasted fixture missing")
def test_decode_and_extract(tmp_path: Path):
    out_dir = tmp_path / "extracted"
    cmd = [
        sys.executable,
        DECODE_SCRIPT,
        "--input",
        str(FIXTURE),
        "--out-dir",
        str(out_dir),
        "--stable-output",
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0, "returncode is not valid"
    decoded = out_dir / "validate_decoded.json"
    gaps = out_dir / "gaps_extracted.json"
    summary = out_dir / "gaps_summary.md"
    assert decoded.exists(), "Condition must be true"
    assert gaps.exists(), "Condition must be true"
    assert summary.exists(), "Condition must be true"
    with open(gaps, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert isinstance(data, (list, dict))


def test_decode_and_validate_roundtrip(tmp_path: Path) -> None:
    pytest.importorskip("jsonschema")
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
    assert result["decoded"]["report"]["id"] == "artifact-001", "Result must not be empty"
    written = json.loads(output.read_text())
    assert written["metadata"]["source"] == "unit-test", "Data must not be empty"
    extracted = json.loads(extract.read_text())
    assert extracted["count"] == 2, "Count must be greater than zero"


def test_decode_and_validate_requires_jsonschema_when_schema_given() -> None:
    with pytest.raises(
        RuntimeError, match="schema_path was provided but jsonschema is not installed"
    ):
        with pytest.MonkeyPatch.context() as m:
            m.setitem(sys.modules, "jsonschema", None)
            decode_validate_and_extract.decode_and_validate(
                input_path=FIXTURE,
                schema_path=SCHEMA,
            )


def test_validate_snapshot_schema_accepts_fixture() -> None:
    decoded = decode_validate_and_extract.decode_base64_gzip(FIXTURE)
    validate_snapshot_schema.validate_snapshot(decoded, SCHEMA)


def test_stable_manifest_deterministic(tmp_path: Path) -> None:
    payload = {"b": 2, "a": [2, 1, {"z": 1, "y": 0}]}
    first = stable_manifest.write_stable_json(payload, tmp_path / "first.json")
    second = stable_manifest.write_stable_json(payload, tmp_path / "second.json")
    assert first.read_text() == second.read_text(), "Condition must be true"


def test_generate_baseline_summary(tmp_path: Path) -> None:
    decoded = decode_validate_and_extract.decode_base64_gzip(FIXTURE)
    destination = tmp_path / "baseline.json"
    summary = {
        "report": {
            "id": decoded["report"]["id"],
            "generated_at": decoded["report"].get("generated_at", ""),
        },
        "gap_count": len(decoded.get("gaps", [])),
    }
    stable_manifest.write_stable_json(summary, destination)
    loaded = json.loads(destination.read_text())
    assert loaded["gap_count"] == 2, "Count must be greater than zero"


def test_coverage_ingest_stub_reads_fixture(tmp_path: Path) -> None:
    output = tmp_path / "coverage.json"
    report_path = coverage_ingest_stub.write_stub_report(COVERAGE_XML, output)
    content = json.loads(report_path.read_text())
    # Defensive: check the parsed coverage object as dict (structure may differ)
    assert "src/example.py" in content["coverage"], "Content must not be empty"
    assert isinstance(content["coverage"]["src/example.py"], dict)
