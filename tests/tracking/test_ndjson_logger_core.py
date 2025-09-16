from codex_ml.logging.ndjson_logger import NDJSONLogger, timestamped_record


def test_ndjson_logger_rotates(tmp_path):
    target = tmp_path / "metrics.ndjson"
    logger = NDJSONLogger(target, max_bytes=40)
    for idx in range(5):
        logger.log(timestamped_record(idx=idx))
    rotated = list(tmp_path.glob("metrics.ndjson.*"))
    assert rotated, "expected rotation to occur"
    assert target.exists()
