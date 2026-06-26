"""
Test Structured Logger

Test module for structured logger.
"""

from tools.logging.structured_logger import JsonLogger


def test_logger(tmp_path):
    p = tmp_path / "log.ndjson"
    JsonLogger(str(p)).write(event="x")
    assert p.exists() and p.read_text().strip().endswith("}"), "Condition must be true"
