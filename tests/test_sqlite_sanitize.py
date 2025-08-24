"""Tests for SQLite table name sanitization."""

import pytest

from codex.logging.db_utils import _sanitize_table


def test_sanitize_table_accepts_valid() -> None:
    assert _sanitize_table("good_name") == "good_name"


def test_sanitize_table_rejects_invalid() -> None:
    with pytest.raises(ValueError):
        _sanitize_table("bad name;")
