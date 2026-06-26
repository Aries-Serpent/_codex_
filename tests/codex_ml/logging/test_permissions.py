"""Test file permission controls for logging."""

import os
import tempfile
from pathlib import Path

import pytest

from codex_ml.logging.ndjson_logger import NDJSONLogger
from codex_ml.logging.permissions import (
    DEFAULT_LOG_FILE_MODE,
    get_log_file_mode,
)


@pytest.fixture
def env_mode_override():
    """Fixture to safely override and restore CODEX_LOG_FILE_MODE."""
    original_value = os.environ.get("CODEX_LOG_FILE_MODE")

    def _set_mode(mode_str):
        os.environ["CODEX_LOG_FILE_MODE"] = mode_str

    yield _set_mode

    # Restore original value
    if original_value is None:
        os.environ.pop("CODEX_LOG_FILE_MODE", None)
    else:
        os.environ["CODEX_LOG_FILE_MODE"] = original_value


def test_default_permissions():
    """Verify default 0o600 permissions are applied to log files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test.ndjson"
        logger = NDJSONLogger(log_path)
        logger.log({"test": "data"})

        # Check file permissions
        stat_info = log_path.stat()
        mode = stat_info.st_mode & 0o777
        assert (mode == DEFAULT_LOG_FILE_MODE, "mode is not valid"
        ), f"Expected {oct(DEFAULT_LOG_FILE_MODE)}, got {oct(mode)}"


def test_environment_override(env_mode_override):
    """Verify CODEX_LOG_FILE_MODE environment override works."""
    env_mode_override("0o640")
    assert get_log_file_mode() == 0o640, "Condition must be true"


def test_environment_override_integration(env_mode_override):
    """Verify environment override is applied to actual log files."""
    env_mode_override("0o640")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test_override.ndjson"
        logger = NDJSONLogger(log_path)
        logger.log({"test": "override"})

        # Check file permissions
        stat_info = log_path.stat()
        mode = stat_info.st_mode & 0o777
        assert mode == 0o640, f"Expected 0o640, got {oct(mode)}"


def test_invalid_environment_value(env_mode_override):
    """Verify invalid CODEX_LOG_FILE_MODE falls back to default."""
    env_mode_override("invalid_mode")
    assert get_log_file_mode() == DEFAULT_LOG_FILE_MODE, "Condition must be true"


def test_batch_logging_permissions():
    """Verify log_many() also uses correct permissions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "test_batch.ndjson"
        logger = NDJSONLogger(log_path)
        logger.log_many([{"test": "data1"}, {"test": "data2"}])

        # Check file permissions
        stat_info = log_path.stat()
        mode = stat_info.st_mode & 0o777
        assert (mode == DEFAULT_LOG_FILE_MODE, "mode is not valid"
        ), f"Expected {oct(DEFAULT_LOG_FILE_MODE)}, got {oct(mode)}"


def test_tracking_writer_permissions():
    """Verify tracking writer also uses correct permissions."""

    # Check if codex_ml.tracking is available
    try:
        from codex_ml.tracking.writers import OfflineJSONWriter
    except ImportError:
        # Skip test if tracking module not available
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tracking_path = Path(tmpdir) / "tracking" / "summary.jsonl"

        # Create writer and write data
        writer = OfflineJSONWriter(tracking_path)
        writer.append({"test": "tracking_data"})

        # Check file permissions
        stat_info = tracking_path.stat()
        mode = stat_info.st_mode & 0o777
        assert (mode == DEFAULT_LOG_FILE_MODE, "mode is not valid"
        ), f"Expected {oct(DEFAULT_LOG_FILE_MODE)}, got {oct(mode)}"
