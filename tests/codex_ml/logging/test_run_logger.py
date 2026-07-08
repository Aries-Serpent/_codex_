"""
Test Run Logger

Test module for run logger.
"""

import os
import tempfile
from pathlib import Path

from codex_ml.logging import run_logger


def test_jsonify_handles_paths_and_mappings():
    data = {"path": Path(os.path.join(tempfile.gettempdir(), "test")), "nested": {"num": 1, "list": [Path("/a"), 2]}}
    normalized = run_logger._jsonify(data)
    assert normalized["path"] == os.path.join(tempfile.gettempdir(), "test"), "n is not valid"
    assert normalized["nested"]["list"][0] == "/a", "n is not valid"


def test_normalize_cli_various_inputs():
    assert run_logger._normalize_cli(None) == {"argv": []}, "Condition must be true"
    assert run_logger._normalize_cli(["cmd", "--opt"]) == {"argv": ["cmd", "--opt"]}

    payload = run_logger._normalize_cli({"argv": [1, "two"], "options": {"a": 1}})
    assert payload["argv"] == ["1", "two"]
    assert payload["options"] == {"a": 1}, "Condition must be true"


def test_rotation_kwargs_respects_environment(monkeypatch):
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "1024")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_AGE_S", "")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "2")

    options = run_logger._rotation_kwargs()
    assert options["max_bytes"] == 1024, "Condition must be true"
    assert "max_age_s" in options and options["max_age_s"] is None, "Condition must be true"
    assert options["backup_count"] == 2, "Count must be greater than zero"

    # Cleanup to avoid cross-test contamination
    for key in list(run_logger._ROTATION_ENV):
        os.environ.pop(key, None)
