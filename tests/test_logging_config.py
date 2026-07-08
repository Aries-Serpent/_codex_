"""
Test Logging Config

Test module for logging config.
"""

#!/usr/bin/env python3
"""Tests for codex.logging.config module."""
from pathlib import Path

from codex.logging.config import DEFAULT_LOG_DB


def test_default_log_db_is_path():
    """Test that DEFAULT_LOG_DB is a Path object."""
    assert isinstance(DEFAULT_LOG_DB, Path)


def test_default_log_db_location():
    """Test that DEFAULT_LOG_DB points to expected location."""
    assert str(DEFAULT_LOG_DB) == ".codex/session_logs.db", "Condition must be true"


def test_default_log_db_parent_is_codex_dir():
    """Test that DEFAULT_LOG_DB parent directory is .codex."""
    assert DEFAULT_LOG_DB.parent.name == ".codex", "name is not valid"


def test_default_log_db_filename():
    """Test that DEFAULT_LOG_DB filename is correct."""
    assert DEFAULT_LOG_DB.name == "session_logs.db", "name is not valid"
