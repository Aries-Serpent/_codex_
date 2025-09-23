import importlib
import json
from pathlib import Path

import codex_ml.monitoring.codex_logging as codex_logging
from codex_ml.monitoring.codex_logging import write_ndjson


def test_log_redaction(tmp_path: Path) -> None:
    p = tmp_path / "log.ndjson"
    # GitHub tokens are 36 characters after the ``ghp_`` prefix.
    secret = "ghp_" + "A" * 36  # pragma: allowlist secret
    write_ndjson(p, {"text": secret})
    data = json.loads(p.read_text().strip())
    assert "REDACTED" in data["text"]
    redactions = data.get("redactions", {}).get("text", {})
    assert redactions.get("secrets", 0) >= 1


def test_write_ndjson_creates_parent_dirs(tmp_path: Path) -> None:
    nested = tmp_path / "nested" / "logs" / "events.ndjson"
    write_ndjson(nested, {"text": "hello", "value": 1})

    assert nested.exists()
    lines = nested.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["text"] == "hello"
    assert data.get("value") == 1


def test_write_ndjson_rotates(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_ML_MAX_LOG_BYTES", "64")
    importlib.reload(codex_logging)
    try:
        path = tmp_path / "events.ndjson"
        for i in range(20):
            codex_logging.write_ndjson(path, {"text": f"event-{i}"})
        rotated = list(path.parent.glob("events.ndjson.*"))
        assert rotated, "expected rotated log files to be created"
    finally:
        monkeypatch.delenv("CODEX_ML_MAX_LOG_BYTES", raising=False)
        importlib.reload(codex_logging)
