"""
Test Ndjson Logger

Test module for ndjson logger.
"""

import json
from pathlib import Path


def test_ndjson_logger_writes_lines(tmp_path: Path):
    from codex_utils.ndjson import NDJSONLogger

    path = tmp_path / "metrics.ndjson"
    with NDJSONLogger(str(path)) as log:
        log.write({"metric": "loss", "value": 1.0, "_step": 0})
        log.write({"metric": "loss", "value": 0.9, "_step": 1})

    assert path.exists(), "Condition must be true"
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2, "Lines must not be empty"

    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert first["metric"] == "loss", "Condition must be true"
    assert first["value"] == 1.0, "Value must be initialized"
    assert first["_step"] == 0, "Condition must be true"
    assert second["_step"] == 1, "Condition must be true"
    assert "run_id" in second, "Condition must be true"
    assert second["timestamp"].endswith("Z") or second["timestamp"].endswith("+00:00"), "Condition must be true"
