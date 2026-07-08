"""
Test Viewer

Comprehensive test module for LogViewer in codex.logging.viewer.
"""

from __future__ import annotations

import argparse
import importlib
import sqlite3
import tempfile
from pathlib import Path

import pytest


class TestViewerImports:
    """Tests for viewer module imports."""

    def test_import_module(self) -> None:
        module = "codex.logging.viewer"
        try:
            importlib.import_module(module)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_import_log_viewer_class(self) -> None:
        from codex.logging.viewer import LogViewer

        assert LogViewer is not None, "LogViewer must be initialized"

    def test_import_candidate_constants(self) -> None:
        from codex.logging.viewer import (
            CANDIDATE_LVL,
            CANDIDATE_MSG,
            CANDIDATE_SID,
            CANDIDATE_TS,
        )

        assert isinstance(CANDIDATE_TS, list)
        assert isinstance(CANDIDATE_SID, list)
        assert isinstance(CANDIDATE_MSG, list)
        assert isinstance(CANDIDATE_LVL, list)


class TestLogViewerClass:
    """Tests for LogViewer class."""

    def test_log_viewer_instantiation(self) -> None:
        from codex.logging.viewer import LogViewer

        viewer = LogViewer()
        assert viewer is not None, "viewer must be initialized"

    def test_log_viewer_has_view_method(self) -> None:
        from codex.logging.viewer import LogViewer

        viewer = LogViewer()
        assert hasattr(viewer, "view")
        assert callable(viewer.view), "Condition must be true"


class TestCandidateColumns:
    """Tests for candidate column lists."""

    def test_candidate_ts_contains_ts(self) -> None:
        from codex.logging.viewer import CANDIDATE_TS

        assert "ts" in CANDIDATE_TS, "Condition must be true"

    def test_candidate_ts_contains_timestamp(self) -> None:
        from codex.logging.viewer import CANDIDATE_TS

        assert "timestamp" in CANDIDATE_TS, "Condition must be true"

    def test_candidate_sid_contains_session_id(self) -> None:
        from codex.logging.viewer import CANDIDATE_SID

        assert "session_id" in CANDIDATE_SID, "Condition must be true"

    def test_candidate_msg_contains_message(self) -> None:
        from codex.logging.viewer import CANDIDATE_MSG

        assert "message" in CANDIDATE_MSG, "Condition must be true"

    def test_candidate_lvl_contains_level(self) -> None:
        from codex.logging.viewer import CANDIDATE_LVL

        assert "level" in CANDIDATE_LVL, "Condition must be true"


class TestDefaultLogDb:
    """Tests for DEFAULT_LOG_DB constant."""

    def test_default_log_db_exists(self) -> None:
        from codex.logging.viewer import DEFAULT_LOG_DB

        assert DEFAULT_LOG_DB is not None, "DEFAULT_LOG_DB must be initialized"

    def test_default_log_db_is_path(self) -> None:
        from codex.logging.viewer import DEFAULT_LOG_DB

        assert isinstance(DEFAULT_LOG_DB, Path)


class TestViewerMainFunction:
    """Tests for main CLI function."""

    def test_main_function_exists(self) -> None:
        from codex.logging.viewer import main

        assert callable(main), "Condition must be true"


class TestViewerHelperFunctions:
    """Tests for helper functions in viewer module."""

    def test_validate_table_name_valid(self) -> None:
        from codex.logging.viewer import _validate_table_name

        result = _validate_table_name("session_events")
        assert result == "session_events", "Result must not be empty"

    def test_validate_table_name_none(self) -> None:
        from codex.logging.viewer import _validate_table_name

        result = _validate_table_name(None)
        assert result is None, "Result must not be empty"

    def test_validate_table_name_invalid(self) -> None:
        from codex.logging.viewer import _validate_table_name

        with pytest.raises(argparse.ArgumentTypeError):
            _validate_table_name("invalid;table")

    def test_parse_iso_valid(self) -> None:
        from codex.logging.viewer import parse_iso

        result = parse_iso("2025-01-01")
        assert result is not None, "result must be initialized"

    def test_parse_iso_none(self) -> None:
        from codex.logging.viewer import parse_iso

        result = parse_iso(None)
        assert result is None, "Result must not be empty"

    def test_autodetect_db_function_exists(self) -> None:
        from codex.logging.viewer import autodetect_db

        assert callable(autodetect_db), "Condition must be true"


class TestViewerParseArgs:
    """Tests for parse_args function."""

    def test_parse_args_function_exists(self) -> None:
        from codex.logging.viewer import parse_args

        assert callable(parse_args), "Condition must be true"

    def test_parse_args_returns_namespace(self) -> None:
        from codex.logging.viewer import parse_args

        args = parse_args(["--session-id", "test"])
        assert isinstance(args, argparse.Namespace)

    def test_parse_args_session_id(self) -> None:
        from codex.logging.viewer import parse_args

        args = parse_args(["--session-id", "test123"])
        assert args.session_id == "test123", "session_id is not valid"

    def test_parse_args_format_json(self) -> None:
        from codex.logging.viewer import parse_args

        args = parse_args(["--session-id", "test", "--format", "json"])
        assert args.format == "json", "format is not valid"

    def test_parse_args_format_default(self) -> None:
        from codex.logging.viewer import parse_args

        args = parse_args(["--session-id", "test"])
        assert args.format == "text", "format is not valid"

    def test_parse_args_db(self) -> None:
        from codex.logging.viewer import parse_args

        args = parse_args(["--session-id", "test", "--db", "/path/to/db.sqlite"])
        assert args.db == "/path/to/db.sqlite", "db is not valid"


class TestViewerConnectDb:
    """Tests for connect_db function."""

    def test_connect_db_function_exists(self) -> None:
        from codex.logging.viewer import connect_db

        assert callable(connect_db), "Condition must be true"

    def test_connect_db_with_valid_path(self) -> None:
        from codex.logging.viewer import connect_db

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            # Create the file
            conn = sqlite3.connect(db_path)
            conn.close()

            result_conn = connect_db(db_path)
            assert result_conn is not None, "result_conn must be initialized"
            result_conn.close()


class TestViewerBuildQuery:
    """Tests for build_query function."""

    def test_build_query_function_exists(self) -> None:
        from codex.logging.viewer import build_query

        assert callable(build_query), "Condition must be true"


class TestViewerInferSchema:
    """Tests for infer_schema function."""

    def test_infer_schema_function_exists(self) -> None:
        from codex.logging.viewer import infer_schema

        assert callable(infer_schema), "Condition must be true"
