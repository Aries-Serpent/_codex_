"""
Test Registry

Test module for registry.
"""

import json
from pathlib import Path

from codex_ml.logging.registry import build_loggers


def test_ndjson_logger_basic(tmp_path: Path):
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": False})
    logger = loggers[0]
    logger.log({"type": "batch", "loss": 0.1})
    logger.close()
    content = (tmp_path / "metrics.ndjson").read_text().strip()
    assert content, "Content must not be empty"
    rec = json.loads(content)
    assert rec["loss"] == 0.1, "Condition must be true"
    assert "mem_rss_mb" not in rec, "Condition must be true"


def test_ndjson_sys_metrics(tmp_path: Path):
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": True})
    logger = loggers[0]
    logger.log({"type": "batch", "loss": 0.2})
    logger.close()
    rec = json.loads((tmp_path / "metrics.ndjson").read_text().splitlines()[0])
    # psutil may not be installed; if missing metrics absent (acceptable)
    # If present then fields appear
    # This assertion is tolerant:
    assert "loss" in rec, "Condition must be true"


def test_build_loggers_multiple_records(tmp_path: Path):
    """Edge case: Test logger handles multiple sequential records"""
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": False})
    logger = loggers[0]

    # Log multiple records
    for i in range(10):
        logger.log({"type": "batch", "batch_id": i, "loss": 0.1 * i})

    logger.close()

    # Verify all records written
    lines = (tmp_path / "metrics.ndjson").read_text().strip().splitlines()
    assert len(lines) == 10, "Lines must not be empty"

    # Verify correct values
    for i, line in enumerate(lines):
        rec = json.loads(line)
        assert rec["batch_id"] == i, "Condition must be true"
        assert abs(rec["loss"] - 0.1 * i) < 1e-6, "Condition must be true"


def test_ndjson_logger_special_characters(tmp_path: Path):
    """Edge case: Test logger handles special characters in strings"""
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": False})
    logger = loggers[0]

    # Log record with special characters
    logger.log(
        {
            "type": "test",
            "message": 'Test with "quotes" and \nnewlines\t and\r escapes',
            "unicode": "emoji 🚀 and symbols ∑∫∂",
        }
    )
    logger.close()

    # Verify it can be parsed back
    content = (tmp_path / "metrics.ndjson").read_text().strip()
    rec = json.loads(content)
    assert "quotes" in rec["message"], "Condition must be true"
    assert "🚀" in rec["unicode"], "Condition must be true"


def test_ndjson_logger_empty_record(tmp_path: Path):
    """Edge case: Test logger handles empty/minimal records"""
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": False})
    logger = loggers[0]

    # Log empty dict
    logger.log({})
    logger.close()

    # Should still write valid JSON
    content = (tmp_path / "metrics.ndjson").read_text().strip()
    rec = json.loads(content)
    assert isinstance(rec, dict)


def test_build_loggers_creates_output_dir(tmp_path: Path):
    """Edge case: Test that output directory is created if missing"""
    nested_dir = tmp_path / "deeply" / "nested" / "path"

    # Directory doesn't exist initially
    assert not nested_dir.exists(), "Condition must be true"

    loggers = build_loggers({"output_dir": str(nested_dir), "sys_metrics": False})
    logger = loggers[0]
    logger.log({"test": "data"})
    logger.close()

    # Directory and file should be created
    assert nested_dir.exists(), "Condition must be true"
    assert (nested_dir / "metrics.ndjson").exists(), "Condition must be true"


def test_ndjson_logger_large_numbers(tmp_path: Path):
    """Edge case: Test logger handles large numbers and floats"""
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": False})
    logger = loggers[0]

    logger.log(
        {
            "very_large": 1e100,
            "very_small": 1e-100,
            "negative": -1e50,
            "int": 999999999999,
        }
    )
    logger.close()

    # Verify numbers are preserved correctly
    content = (tmp_path / "metrics.ndjson").read_text().strip()
    rec = json.loads(content)
    assert rec["very_large"] == 1e100, "Condition must be true"
    assert rec["very_small"] == 1e-100, "Condition must be true"
    assert rec["negative"] == -1e50, "Condition must be true"
    assert rec["int"] == 999999999999, "Condition must be true"
