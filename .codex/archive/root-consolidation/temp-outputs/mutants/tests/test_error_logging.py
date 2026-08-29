"""
Test Error Logging

Test module for error logging.
"""

#!/usr/bin/env python3
"""Tests for error_logging utility."""
from pathlib import Path

import pytest

from src.utils.error_logging import append_error


def test_append_error_creates_file(tmp_path, monkeypatch):
    """Test that append_error creates the error log file."""
    error_log = tmp_path / "error_log.md"
    monkeypatch.setattr("src.utils.error_logging._ERROR_LOG_PATH", error_log)

    append_error("1.1", "test operation", "test error message", "test context")

    assert error_log.exists(), "Error should be raised or set"
    content = error_log.read_text()
    assert "1.1" in content, "Content must not be empty"
    assert "test operation" in content, "Content must not be empty"
    assert "test error message" in content, "Content must not be empty"
    assert "test context" in content, "Content must not be empty"


def test_append_error_appends_multiple_entries(tmp_path, monkeypatch):
    """Test that multiple errors are appended correctly."""
    error_log = tmp_path / "error_log.md"
    monkeypatch.setattr("src.utils.error_logging._ERROR_LOG_PATH", error_log)

    append_error("1.1", "first op", "first error", "first context")
    append_error("2.2", "second op", "second error", "second context")

    content = error_log.read_text()
    assert "1.1" in content, "Content must not be empty"
    assert "2.2" in content, "Content must not be empty"
    assert content.count("Question from ChatGPT") == 2, "Content must not be empty"


def test_append_error_creates_parent_directories(tmp_path, monkeypatch):
    """Test that parent directories are created if they don't exist."""
    error_log = tmp_path / "nested" / "dir" / "error_log.md"
    monkeypatch.setattr("src.utils.error_logging._ERROR_LOG_PATH", error_log)

    append_error("3.1", "nested test", "error msg", "context")

    assert error_log.exists(), "Error should be raised or set"
    assert error_log.parent.exists(), "Error should be raised or set"


def test_append_error_handles_exception_gracefully(tmp_path, monkeypatch):
    """Test that errors in append_error don't raise exceptions."""
    # Use an invalid path that will cause write to fail
    error_log = Path("/invalid/path/that/does/not/exist/error_log.md")
    monkeypatch.setattr("src.utils.error_logging._ERROR_LOG_PATH", error_log)

    # Should not raise an exception
    try:
        append_error("4.1", "failing op", "error", "context")
    except Exception as e:
        pytest.fail(f"append_error raised exception: {e}")


def test_append_error_formats_message_correctly(tmp_path, monkeypatch):
    """Test that the error message is formatted according to template."""
    error_log = tmp_path / "error_log.md"
    monkeypatch.setattr("src.utils.error_logging._ERROR_LOG_PATH", error_log)

    append_error("5.1", "format test", "test message", "test context")

    content = error_log.read_text()
    assert "Question from ChatGPT @codex" in content, "Content must not be empty"
    assert "While performing [5.1:format test]" in content, "Content must not be empty"
    assert "encountered the following error: test message" in content, "Content must not be empty"
    assert "Context: test context" in content, "Content must not be empty"
    assert "What are the possible causes" in content, "Content must not be empty"
