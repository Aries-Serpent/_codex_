from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _reset_summary_loggers(monkeypatch: pytest.MonkeyPatch):
    from codex_ml.tracking import writers

    writers._SUMMARY_LOGGERS.clear()
    yield
    writers._SUMMARY_LOGGERS.clear()


def _write_summary(summary_path: Path, component: str = "mlflow") -> None:
    from codex_ml.tracking import writers

    writers._emit_summary(
        summary_path,
        component,
        "enabled",
        extra={
            "dependencies": {},
            "requested_uri": "file://requested",
            "effective_uri": "file://effective",
            "tracking_uri": "file://effective",
            "fallback_reason": "",
            "allow_remote_flag": "",
            "allow_remote_env": "MLFLOW_ALLOW_REMOTE",
            "allow_remote": False,
            "system_metrics_enabled": False,
        },
    )


def test_summary_rotates_by_size(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    summary_path = tmp_path / "tracking_summary.ndjson"
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "200")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "2")
    monkeypatch.delenv("CODEX_TRACKING_NDJSON_MAX_AGE_S", raising=False)

    for _ in range(6):
        _write_summary(summary_path)

    assert summary_path.exists()
    rotated = sorted(p.name for p in tmp_path.iterdir() if p.name.startswith("tracking_summary"))
    assert rotated == [
        "tracking_summary.ndjson",
        "tracking_summary.ndjson.1",
        "tracking_summary.ndjson.2",
    ]


def test_summary_rotates_by_age(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    summary_path = tmp_path / "tracking_summary.ndjson"
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_AGE_S", "0")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "3")
    monkeypatch.delenv("CODEX_TRACKING_NDJSON_MAX_BYTES", raising=False)

    for _ in range(4):
        _write_summary(summary_path)

    files = sorted(p.name for p in tmp_path.iterdir() if p.name.startswith("tracking_summary"))
    assert files == [
        "tracking_summary.ndjson",
        "tracking_summary.ndjson.1",
        "tracking_summary.ndjson.2",
        "tracking_summary.ndjson.3",
    ]
