import importlib
from pathlib import Path


def _reload_writers():
    writers = importlib.import_module("codex_ml.tracking.writers")
    return importlib.reload(writers)


def _summary_extra(idx: int) -> dict:
    base_uri = f"file:///tmp/mlruns/{idx}"
    return {
        "dependencies": {"psutil_available": False, "nvml_available": False},
        "tracking_uri": base_uri,
        "requested_uri": base_uri,
        "effective_uri": base_uri,
        "fallback_reason": "",
        "allow_remote_flag": "",
        "allow_remote": False,
        "system_metrics_enabled": False,
    }


def _emit_summary(writers_module, summary_path: Path, idx: int) -> None:
    writers_module._emit_summary(
        summary_path,
        "mlflow",
        "enabled",
        extra=_summary_extra(idx),
    )


def test_summary_rotation_rolls_by_max_bytes(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "200")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_AGE_S", "3600")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "2")

    writers = _reload_writers()
    writers._reset_summary_rotation_state_for_tests()

    summary_path = tmp_path / "tracking_summary.ndjson"
    for idx in range(12):
        _emit_summary(writers, summary_path, idx)

    variants = sorted(p.name for p in summary_path.parent.glob("tracking_summary.ndjson*"))
    assert "tracking_summary.ndjson" in variants
    assert "tracking_summary.ndjson.1" in variants
    assert "tracking_summary.ndjson.2" in variants


def test_summary_rotation_rolls_by_max_age(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_BYTES", "")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_MAX_AGE_S", "0")
    monkeypatch.setenv("CODEX_TRACKING_NDJSON_BACKUP_COUNT", "2")

    writers = _reload_writers()
    writers._reset_summary_rotation_state_for_tests()

    summary_path = tmp_path / "tracking_summary.ndjson"
    for idx in range(3):
        _emit_summary(writers, summary_path, idx)

    variants = sorted(p.name for p in summary_path.parent.glob("tracking_summary.ndjson*"))
    assert "tracking_summary.ndjson" in variants
    assert "tracking_summary.ndjson.1" in variants
    assert "tracking_summary.ndjson.2" in variants
