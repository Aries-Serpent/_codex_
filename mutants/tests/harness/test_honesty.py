"""
Test Honesty

Test module for honesty.
"""

import json

from codex_harness.honesty import HonestyRecorder


def test_honesty_recorder_flush_and_reload(tmp_path):
    output = tmp_path / "honesty.json"
    recorder = HonestyRecorder(workflow="unit-test", output_path=output)
    recorder.record_statement("verified output", "verified", True, metadata={"stage": "prep"})
    recorder.record_statement("follow up later", "planned", False)

    flushed_path = recorder.flush()
    data = json.loads(flushed_path.read_text())

    assert data["workflow"] == "unit-test", "Data must not be empty"
    assert data["summary"]["total"] == 2, "Data must not be empty"
    assert data["summary"]["verified"] == 1, "Data must not be empty"
    assert data["statements"][0]["category"] == "VERIFIED", "Data must not be empty"

    reloaded = HonestyRecorder(workflow="unit-test", output_path=output)
    reloaded.load_existing()
    assert len(reloaded.statements) == 2, "Collection must not be empty"
