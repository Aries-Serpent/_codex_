import json
import time

from codex_ml.logging.ndjson_logger import NDJSONLogger, timestamped_record


def test_ndjson_logger_rotates(tmp_path):
    target = tmp_path / "metrics.ndjson"
    logger = NDJSONLogger(target, max_bytes=40, backup_count=2)
    for idx in range(5):
        logger.log(timestamped_record(idx=idx))
    rotated = list(tmp_path.glob("metrics.ndjson.*"))
    assert rotated, "expected rotation to occur"
    assert target.exists()
    assert any(p.name.endswith(".1") for p in rotated)


def test_ndjson_logger_adds_run_id_and_timestamp(tmp_path):
    logger = NDJSONLogger(tmp_path / "metrics.ndjson")
    logger.log({"metric": "loss", "value": 1})
    payload = json.loads((tmp_path / "metrics.ndjson").read_text().strip())
    assert payload["metric"] == "loss"
    assert payload["value"] == 1
    assert payload["run_id"]
    assert payload["timestamp"].endswith("Z") or payload["timestamp"].endswith("+00:00")


def test_ndjson_logger_legacy_toggle_suppresses_additions(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_TRACKING_LEGACY_NDJSON", "1")
    logger = NDJSONLogger(tmp_path / "legacy.ndjson")
    logger.log({"metric": "acc", "value": 0.9})
    payload = json.loads((tmp_path / "legacy.ndjson").read_text().strip())
    assert "run_id" not in payload
    assert "timestamp" not in payload
    monkeypatch.delenv("CODEX_TRACKING_LEGACY_NDJSON", raising=False)


def test_ndjson_logger_time_rotation(tmp_path):
    target = tmp_path / "metrics.ndjson"
    logger = NDJSONLogger(target, max_age_s=0, backup_count=1)
    logger.log({"metric": "loss", "value": 1})
    time.sleep(0.01)
    logger.log({"metric": "loss", "value": 2})
    assert target.exists()
    rotated = target.with_name("metrics.ndjson.1")
    assert rotated.exists()
