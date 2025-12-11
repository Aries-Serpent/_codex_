import os
from pathlib import Path

from codex_ml.logging import run_logger


def test_jsonify_handles_paths_and_mappings():
    data = {"path": Path("/tmp/test"), "nested": {"num": 1, "list": [Path("/a"), 2]}}
    normalized = run_logger._jsonify(data)
    assert normalized["path"] == "/tmp/test"
    assert normalized["nested"]["list"][0] == "/a"


def test_normalize_cli_various_inputs():
    assert run_logger._normalize_cli(None) == {"argv": []}
    assert run_logger._normalize_cli(["cmd", "--opt"]) == {"argv": ["cmd", "--opt"]}

    payload = run_logger._normalize_cli({"argv": [1, "two"], "options": {"a": 1}})
    assert payload["argv"] == ["1", "two"]
    assert payload["options"] == {"a": 1}


def test_rotation_kwargs_respects_environment(monkeypatch):
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "1024")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_AGE_S", "")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "2")

    options = run_logger._rotation_kwargs()
    assert options["max_bytes"] == 1024
    assert "max_age_s" in options and options["max_age_s"] is None
    assert options["backup_count"] == 2

    # Cleanup to avoid cross-test contamination
    for key in list(run_logger._ROTATION_ENV):
        os.environ.pop(key, None)
