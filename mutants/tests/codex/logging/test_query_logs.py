"""Tests for codex.logging.query_logs module.

Phase 6 tests covering:
- LogQueryEngine search functionality
- parse_when datetime parsing
- build_query SQL generation
- format_text output formatting
- main CLI entry point
"""

from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest


def test_import_module():
    """Test that module can be imported."""
    module = "codex.logging.query_logs"
    try:
        importlib.import_module(module)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")


class TestParseWhen:
    """Tests for parse_when datetime parsing function."""

    @pytest.fixture
    def parse_when(self):
        """Import parse_when function."""
        from codex.logging.query_logs import parse_when

        return parse_when

    def test_parse_zulu_timestamp(self, parse_when):
        """Test parsing Zulu (Z) timestamp."""
        result = parse_when("2025-08-19T12:34:56Z")
        assert result.year == 2025, "Result must not be empty"
        assert result.month == 8, "Result must not be empty"
        assert result.day == 19, "Result must not be empty"
        assert result.hour == 12, "Result must not be empty"
        assert result.minute == 34, "Result must not be empty"
        assert result.second == 56, "Result must not be empty"
        # Zulu should produce aware datetime
        assert result.tzinfo is not None, "tzinfo must be initialized"

    def test_parse_offset_aware_timestamp(self, parse_when):
        """Test parsing offset-aware timestamp."""
        result = parse_when("2025-08-19T12:34:56+00:00")
        assert result.year == 2025, "Result must not be empty"
        assert result.tzinfo is not None, "tzinfo must be initialized"

    def test_parse_negative_offset_timestamp(self, parse_when):
        """Test parsing negative offset timestamp."""
        result = parse_when("2025-08-19T07:34:56-05:00")
        assert result.year == 2025, "Result must not be empty"
        assert result.hour == 7, "Result must not be empty"
        assert result.tzinfo is not None, "tzinfo must be initialized"

    def test_parse_naive_timestamp(self, parse_when):
        """Test parsing naive (no timezone) timestamp."""
        result = parse_when("2025-08-19T12:34:56")
        assert result.year == 2025, "Result must not be empty"
        # Naive input returns naive datetime
        assert result.tzinfo is None, "Result must not be empty"

    def test_parse_date_only(self, parse_when):
        """Test parsing date-only string."""
        result = parse_when("2025-08-19")
        assert result.year == 2025, "Result must not be empty"
        assert result.month == 8, "Result must not be empty"
        assert result.day == 19, "Result must not be empty"

    def test_parse_with_whitespace(self, parse_when):
        """Test parsing timestamp with leading/trailing whitespace."""
        result = parse_when("  2025-08-19T12:34:56Z  ")
        assert result.year == 2025, "Result must not be empty"

    def test_parse_non_string_raises_type_error(self, parse_when):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="expects str"):
            parse_when(123)

    def test_parse_invalid_format_raises_value_error(self, parse_when):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid datetime"):
            parse_when("not-a-date")


class TestBuildQuery:
    """Tests for build_query SQL generation function."""

    @pytest.fixture
    def build_query(self):
        """Import build_query function."""
        from codex.logging.query_logs import build_query

        return build_query

    @pytest.fixture
    def base_mapcol(self):
        """Base column mapping for tests."""
        return {
            "id": "id",
            "timestamp": "ts",
            "role": "role",
            "message": "message",
            "session_id": "session_id",
            "metadata": "metadata",
        }

    def test_build_basic_query(self, build_query, base_mapcol):
        """Test building basic query with no filters."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after=None,
            before=None,
            order="asc",
            limit=None,
            offset=None,
        )
        assert "SELECT" in sql, "Condition must be true"
        assert "FROM session_events" in sql, "Condition must be true"
        assert "ORDER BY ts ASC" in sql, "Condition must be true"
        assert params == [], "params is not valid"

    def test_build_query_with_session_filter(self, build_query, base_mapcol):
        """Test query with session_id filter."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id="test-session",
            role=None,
            after=None,
            before=None,
            order="asc",
            limit=None,
            offset=None,
        )
        assert "WHERE" in sql, "Condition must be true"
        assert "session_id = ?" in sql, "Condition must be true"
        assert "test-session" in params, "Condition must be true"

    def test_build_query_with_role_filter(self, build_query, base_mapcol):
        """Test query with role filter."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role="user",
            after=None,
            before=None,
            order="asc",
            limit=None,
            offset=None,
        )
        assert "role = ?" in sql, "Condition must be true"
        assert "user" in params, "Condition must be true"

    def test_build_query_with_after_filter(self, build_query, base_mapcol):
        """Test query with after timestamp filter."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after="2025-01-01",
            before=None,
            order="asc",
            limit=None,
            offset=None,
        )
        assert "ts >= ?" in sql, "ts must be greater than zero"
        assert "2025-01-01" in params, "Condition must be true"

    def test_build_query_with_before_filter(self, build_query, base_mapcol):
        """Test query with before timestamp filter."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after=None,
            before="2025-12-31",
            order="asc",
            limit=None,
            offset=None,
        )
        assert "ts <= ?" in sql, "ts is not valid"
        assert "2025-12-31" in params, "Condition must be true"

    def test_build_query_with_limit(self, build_query, base_mapcol):
        """Test query with limit."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after=None,
            before=None,
            order="asc",
            limit=100,
            offset=None,
        )
        assert "LIMIT ?" in sql, "Condition must be true"
        assert 100 in params, "Condition must be true"

    def test_build_query_with_offset(self, build_query, base_mapcol):
        """Test query with offset."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after=None,
            before=None,
            order="asc",
            limit=100,
            offset=50,
        )
        assert "OFFSET ?" in sql, "Condition must be true"
        assert 50 in params, "Condition must be true"

    def test_build_query_desc_order(self, build_query, base_mapcol):
        """Test query with descending order."""
        sql, _params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after=None,
            before=None,
            order="desc",
            limit=None,
            offset=None,
        )
        assert "ORDER BY ts DESC" in sql, "Condition must be true"

    def test_build_query_invalid_order_defaults_to_asc(self, build_query, base_mapcol):
        """Test that invalid order defaults to ASC."""
        sql, _params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id=None,
            role=None,
            after=None,
            before=None,
            order="invalid",
            limit=None,
            offset=None,
        )
        assert "ORDER BY ts ASC" in sql, "Condition must be true"

    def test_build_query_missing_required_columns_raises(self, build_query):
        """Test that missing required columns raises ValueError."""
        incomplete_mapcol = {
            "timestamp": None,
            "role": None,
            "message": None,
        }
        with pytest.raises(ValueError, match="Required columns missing"):
            build_query(
                table="session_events",
                mapcol=incomplete_mapcol,
                session_id=None,
                role=None,
                after=None,
                before=None,
                order="asc",
                limit=None,
                offset=None,
            )

    def test_build_query_with_all_filters(self, build_query, base_mapcol):
        """Test query with all filters combined."""
        sql, params = build_query(
            table="session_events",
            mapcol=base_mapcol,
            session_id="test-session",
            role="assistant",
            after="2025-01-01",
            before="2025-12-31",
            order="desc",
            limit=50,
            offset=10,
        )
        assert "WHERE" in sql, "Condition must be true"
        assert "session_id = ?" in sql, "Condition must be true"
        assert "role = ?" in sql, "Condition must be true"
        assert "ts >= ?" in sql, "ts must be greater than zero"
        assert "ts <= ?" in sql, "ts is not valid"
        assert "ORDER BY ts DESC" in sql, "Condition must be true"
        assert "LIMIT ?" in sql, "Condition must be true"
        assert "OFFSET ?" in sql, "Condition must be true"
        assert len(params) == 6, "Params must not be empty"


class TestFormatText:
    """Tests for format_text output formatting function."""

    @pytest.fixture
    def format_text(self):
        """Import format_text function."""
        from codex.logging.query_logs import format_text

        return format_text

    @pytest.fixture
    def mock_rows(self):
        """Create mock rows for testing."""

        # Create mock Row objects with dict-like access
        class MockRow:
            def __init__(self, data):
                self._data = data

            def __getitem__(self, key):
                return self._data.get(key)

            def keys(self):
                return self._data.keys()

        return [
            MockRow(
                {
                    "ts": "2025-01-01T10:00:00",
                    "role": "user",
                    "message": "Hello",
                    "session_id": "S1",
                    "metadata": None,
                }
            ),
            MockRow(
                {
                    "ts": "2025-01-01T10:01:00",
                    "role": "assistant",
                    "message": "Hi there",
                    "session_id": "S1",
                    "metadata": '{"key": "value"}',
                }
            ),
        ]

    @pytest.fixture
    def base_mapcol(self):
        """Base column mapping for tests."""
        return {
            "timestamp": "ts",
            "role": "role",
            "message": "message",
            "session_id": "session_id",
            "metadata": "metadata",
        }

    def test_format_text_basic(self, format_text, mock_rows, base_mapcol):
        """Test basic text formatting."""
        result = format_text(mock_rows, base_mapcol, show_meta=False)
        assert "2025-01-01T10:00:00" in result, "Result must not be empty"
        assert "(user)" in result, "Result must not be empty"
        assert "Hello" in result, "Result must not be empty"
        assert "[S1]" in result, "Result must not be empty"

    def test_format_text_with_metadata(self, format_text, mock_rows, base_mapcol):
        """Test text formatting with metadata shown."""
        result = format_text(mock_rows, base_mapcol, show_meta=True)
        assert '{"key": "value"}' in result, "Result must not be empty"

    def test_format_text_missing_columns_raises(self, format_text, mock_rows):
        """Test that missing required columns raises ValueError."""
        incomplete_mapcol = {
            "timestamp": None,
            "role": None,
            "message": None,
        }
        with pytest.raises(ValueError, match="Required columns missing"):
            format_text(mock_rows, incomplete_mapcol, show_meta=False)

    def test_format_text_empty_rows(self, format_text, base_mapcol):
        """Test formatting empty row list."""
        result = format_text([], base_mapcol, show_meta=False)
        assert result == "", "Result must not be empty"


class TestLogQueryEngine:
    """Tests for LogQueryEngine class."""

    @pytest.fixture
    def engine(self):
        """Create LogQueryEngine instance."""
        from codex.logging.query_logs import LogQueryEngine

        return LogQueryEngine()

    def test_engine_instantiation(self, engine):
        """Test that engine can be instantiated."""
        assert engine is not None, "engine must be initialized"

    @patch("codex.logging.db_manager.db_manager")
    def test_search_basic(self, mock_db_manager, engine):
        """Test basic search functionality."""
        # Mock the database manager
        mock_conn = MagicMock()
        mock_conn.row_factory = None
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_db_manager.connection.return_value.__exit__ = MagicMock(return_value=False)

        result = engine.search("test query")

        mock_db_manager.init_schema.assert_called_once()
        assert isinstance(result, list)

    @patch("codex.logging.db_manager.db_manager")
    def test_search_with_role_filter(self, mock_db_manager, engine):
        """Test search with role filter."""
        mock_conn = MagicMock()
        mock_conn.row_factory = None
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_db_manager.connection.return_value.__exit__ = MagicMock(return_value=False)

        engine.search("test query", role="user")

        # Check that role was passed in the query
        call_args = mock_conn.execute.call_args
        assert call_args is not None, "call_args must be initialized"
        sql = call_args[0][0]
        params = call_args[0][1]
        assert "role = ?" in sql, "Condition must be true"
        assert "user" in params, "Condition must be true"


class TestResolvDbPath:
    """Tests for _resolve_db_path function."""

    @pytest.fixture
    def resolve_db_path(self):
        """Import _resolve_db_path function."""
        from codex.logging.query_logs import _resolve_db_path

        return _resolve_db_path

    def test_resolve_existing_path(self, resolve_db_path, tmp_path):
        """Test resolving an existing path."""
        db_file = tmp_path / "test.db"
        db_file.touch()
        result = resolve_db_path(str(db_file))
        assert "test.db" in result, "Result must not be empty"

    def test_resolve_nonexistent_path(self, resolve_db_path, tmp_path):
        """Test resolving a non-existent path."""
        result = resolve_db_path(str(tmp_path / "nonexistent.db"))
        assert "nonexistent" in result, "Result must not be empty"


class TestMain:
    """Tests for main CLI entry point."""

    @patch("codex.logging.query_logs.open_db")
    @patch("codex.logging.query_logs.infer_probable_table")
    @patch("codex.logging.query_logs.infer_columns")
    def test_main_with_help(self, mock_infer_cols, mock_infer_table, mock_open_db):
        """Test main with --help flag."""
        from codex.logging.query_logs import main

        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        # --help exits with code 0
        assert exc_info.value.code == 0, "Value must be initialized"

    def test_main_exits_on_missing_db(self):
        """Test that main exits when database doesn't exist."""
        from codex.logging.query_logs import main

        # Should exit with error when db doesn't exist
        result = main(["--db", "/nonexistent/path/to/db.sqlite"])
        assert result != 0 or result is None, "Result must not be empty"
