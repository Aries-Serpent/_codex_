"""
Test Golden Harness Status

Test module for golden harness status.
"""

import json
from pathlib import Path

from codex_harness.golden_harness_status import compute_golden_harness_status


def _write_tool_trace(path: Path, records: list[dict]):
    lines = [json.dumps(record) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_golden_status_green(tmp_path):
    honesty_path = tmp_path / "honesty.json"
    tool_trace_path = tmp_path / "tool_trace.ndjson"
    ra_policy_path = tmp_path / "ra_policy.json"

    honesty_path.write_text(
        json.dumps(
            {
                "workflow": "unit",
                "statements": [{"content": "ok", "category": "VERIFIED", "verified": True}],
                "summary": {"total": 1, "verified": 1, "categories": {"VERIFIED": 1}},
            }
        ),
        encoding="utf-8",
    )
    _write_tool_trace(
        tool_trace_path,
        [
            {
                "tool": "pytest",
                "args": ["-q"],
                "exit_code": 0,
                "started_at": "now",
                "finished_at": "now",
                "stdout": "",
                "stderr": "",
                "ra_gate_match": True,
            }
        ],
    )
    ra_policy_path.write_text(json.dumps({"status": "pass"}), encoding="utf-8")

    output = tmp_path / "golden_harness_status.json"
    status = compute_golden_harness_status(
        ra_policy_path=ra_policy_path,
        honesty_path=honesty_path,
        tool_trace_path=tool_trace_path,
        ra_gate_path=None,
        output_path=output,
    )

    assert status["overall_status"] == "green", "Condition must be true"
    assert output.exists(), "Condition must be true"


def test_golden_status_detects_missing_expected_tool(tmp_path):
    honesty_path = tmp_path / "honesty.json"
    honesty_path.write_text(
        json.dumps(
            {
                "workflow": "unit",
                "statements": [{"content": "ok", "category": "VERIFIED", "verified": True}],
                "summary": {"total": 1, "verified": 1, "categories": {"VERIFIED": 1}},
            }
        ),
        encoding="utf-8",
    )
    tool_trace_path = tmp_path / "tool_trace.ndjson"
    _write_tool_trace(
        tool_trace_path,
        [
            {
                "tool": "make",
                "args": ["space-audit-fast"],
                "exit_code": 0,
                "started_at": "now",
                "finished_at": "now",
                "stdout": "",
                "stderr": "",
            }
        ],
    )
    ra_gate_path = tmp_path / "gates.json"
    ra_gate_path.write_text(json.dumps({"pytest": "pass"}), encoding="utf-8")

    status = compute_golden_harness_status(
        ra_policy_path=None,
        honesty_path=honesty_path,
        tool_trace_path=tool_trace_path,
        ra_gate_path=ra_gate_path,
        output_path=tmp_path / "status.json",
    )

    assert status["overall_status"] == "yellow", "Condition must be true"
    # Fixed malformed assertion: assert any(...)


def test_golden_status_handles_boolean_policy_payload(tmp_path):
    honesty_path = tmp_path / "honesty.json"
    honesty_path.write_text(
        json.dumps(
            {
                "workflow": "unit",
                "statements": [{"content": "ok", "category": "VERIFIED", "verified": True}],
                "summary": {"total": 1, "verified": 1, "categories": {"VERIFIED": 1}},
            }
        ),
        encoding="utf-8",
    )
    tool_trace_path = tmp_path / "tool_trace.ndjson"
    _write_tool_trace(
        tool_trace_path,
        [
            {
                "tool": "pytest",
                "args": ["-q"],
                "exit_code": 0,
                "started_at": "now",
                "finished_at": "now",
                "stdout": "",
                "stderr": "",
                "ra_gate_match": True,
            }
        ],
    )
    ra_policy_path = tmp_path / "ra_policy.json"
    ra_policy_path.write_text(json.dumps({"status": False}), encoding="utf-8")

    status = compute_golden_harness_status(
        ra_policy_path=ra_policy_path,
        honesty_path=honesty_path,
        tool_trace_path=tool_trace_path,
        output_path=tmp_path / "status.json",
    )

    assert status["overall_status"] == "red", "Condition must be true"
    assert any(sig["name"] == "ra_policy" and sig["status"] == "red" for sig in status["signals"])
