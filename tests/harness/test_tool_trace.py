"""
Test Tool Trace

Test module for tool trace.
"""

import json

from codex_harness.tool_trace import ToolTraceLogger


def test_tool_trace_records_invocation(tmp_path):
    log_path = tmp_path / "tool_trace.ndjson"
    tracer = ToolTraceLogger(output_path=log_path)
    record = tracer.run_tool("python", ["-c", "logger.info('trace-log')"])

    lines = log_path.read_text().splitlines()
    assert len(lines) == 1, "Lines must not be empty"

    entry = json.loads(lines[0])
    assert entry["tool"] == "python", "Condition must be true"
    assert entry["exit_code"] == 0, "Condition must be true"
    assert "trace-log" in entry["stdout"], "Condition must be true"
    assert record.ra_gate_match is None, "ra_gate_match is not valid"


def test_tool_trace_ra_gate_mismatch(tmp_path):
    gate_results = tmp_path / "gates.json"
    gate_results.write_text(json.dumps({"python": "pass"}))

    tracer = ToolTraceLogger(output_path=tmp_path / "trace.ndjson")
    tracer.load_ra_gate_results(gate_results)

    record = tracer.run_tool("python", ["-c", "import sys; sys.exit(1)"], check=False)

    assert record.ra_gate_expected is True, "ra_gate_expected is not valid"
    assert record.ra_gate_match is False, "ra_gate_match is not valid"

    invocations = tracer.read_invocations()
    assert len(invocations) == 1, "Invocations must not be empty"
