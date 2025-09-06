from __future__ import annotations

from codex_ml.monitoring.schema import LOG_VERSION, LogRecord


def test_schema_and_redaction() -> None:
    rec = LogRecord(
        ts=1.0,
        run_id="r1",
        phase="train",
        step=1,
        metric="loss",
        value=0.1,
        meta={"api_key": "SECRET123", "note": "x" * 5000},  # pragma: allowlist secret
    )
    red = rec.redacted()
    data = red.dict()
    assert data["version"] == LOG_VERSION
    assert data["meta"]["api_key"] == "<redacted>"
    assert len(data["meta"]["note"]) == 4096
