"""
Test Offline Ndjson Logger

Test module for offline ndjson logger.
"""

from __future__ import annotations

import json

from codex_ml.tracking.offline import NDJSONLogger


def test_ndjson_logger_rotation(tmp_path):
    path = tmp_path / "events.ndjson"
    logger = NDJSONLogger(path, max_bytes=200, backup_count=2, enable_rotation=True)

    for index in range(50):
        logger.write({"index": index, "message": "x" * 10})

    assert path.exists(), "Condition must be true"
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                json.loads(line)
