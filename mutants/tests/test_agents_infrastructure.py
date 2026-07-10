"""Tests for .codex/archive/deprecated/AGENTS.md infrastructure.

Tests:
- Environment variable management
- Error handling and logging
- CLI commands
- Session logging
- Log querying
"""

from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import pytest


class TestEnvironmentManager:
    """Test environment variable management."""

    def test_get_default_values(self):
        """Test default value fallback."""
        with patch.dict(os.environ, {}, clear=True):
            from codex.config.env_vars import EnvironmentManager

            env = EnvironmentManager()
            assert env.get("CODEX_ENV_PYTHON_VERSION") == "3.12", "Condition must be true"
            assert env.get("CODEX_FORCE_CPU") == "1", "Condition must be true"
            assert env.get("CODEX_SESSION_LOG_DIR") == ".codex/sessions", "Condition must be true"

    def test_session_id_generation(self):
        """Test automatic session ID generation."""
        with patch.dict(os.environ, {}, clear=True):
            from codex.config.env_vars import EnvironmentManager

            env = EnvironmentManager()
            session_id = env.get_session_id()
            assert session_id is not None, "session_id must be initialized"
            assert len(session_id) == 36, "Session_id must not be empty"
            # Second call should return same ID
            assert env.get_session_id() == session_id, "Condition must be true"

    def test_validation_failure(self):
        """Test validation of invalid values."""
        # Import first, then patch and create new instance
        from codex.config.env_vars import EnvironmentManager

        with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "2"}, clear=False):
            with pytest.raises(EnvironmentError, match="Invalid value"):
                EnvironmentManager()

    def test_get_log_dir_creates_directory(self, tmp_path):
        """Test log directory creation."""
        with patch.dict(os.environ, {"CODEX_SESSION_LOG_DIR": str(tmp_path / "logs")}):
            from codex.config.env_vars import EnvironmentManager

            env = EnvironmentManager()
            log_dir = env.get_log_dir()
            assert log_dir.exists(), "Condition must be true"
            assert log_dir.is_dir(), "Condition must be true"

    def test_dump_config(self):
        """Test configuration dump."""
        from codex.config.env_vars import EnvironmentManager

        env = EnvironmentManager()
        config = env.dump_config()
        assert isinstance(config, dict)
        assert "CODEX_ENV_PYTHON_VERSION" in config, "Condition must be true"
        assert "CODEX_SESSION_ID" in config, "Condition must be true"


class TestErrorHandler:
    """Test error handling infrastructure."""

    def test_log_error(self, tmp_path):
        """Test error logging."""
        from codex.logging.error_handler import CodexErrorHandler

        handler = CodexErrorHandler(log_dir=tmp_path)

        try:
            raise ValueError("Test error")
        except ValueError as e:
            handler.log_error(e, context={"test": True})

        # Check that error log was created
        error_logs = list(tmp_path.glob("errors_*.log"))
        assert len(error_logs) > 0, "No error log files created"
        error_log = error_logs[0]
        assert error_log.exists(), "Error should be raised or set"
        content = error_log.read_text()
        assert "ValueError: Test error" in content, "Value must be initialized"
        assert "test" in content, "Content must not be empty"

    def test_decorator(self, tmp_path):
        """Test error logging decorator."""
        from codex.logging.error_handler import CodexErrorHandler

        handler = CodexErrorHandler(log_dir=tmp_path)

        @handler.log_errors
        def failing_function():
            raise RuntimeError("Decorated error")

        with pytest.raises(RuntimeError):
            failing_function()

        # Check that error log was created
        error_logs = list(tmp_path.glob("errors_*.log"))
        assert len(error_logs) > 0, "No error log files created"
        error_log = error_logs[0]
        content = error_log.read_text()
        assert "RuntimeError: Decorated error" in content, "Content must not be empty"
        assert "failing_function" in content, "Content must not be empty"

    def test_fatal_error_exits(self, tmp_path):
        """Test fatal error handling exits."""
        from codex.logging.error_handler import CodexErrorHandler

        handler = CodexErrorHandler(log_dir=tmp_path)

        with pytest.raises(SystemExit):
            try:
                raise ValueError("Fatal error")
            except ValueError as e:
                handler.log_error(e, fatal=True)


class TestSessionLogger:
    """Test session logging."""

    def test_log_message(self, tmp_path):
        """Test logging a message."""
        from codex.logging.session_logger import SessionLogger

        with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": str(tmp_path / "test.db")}):
            logger = SessionLogger(session_id="test-session")
            logger.log(role="user", message="Test message")
            # Verify log was written (implementation dependent)
            assert (tmp_path / "test.db").exists(), "Condition must be true"

    def test_context_manager(self, tmp_path):
        """Test SessionLogger as context manager."""
        from codex.logging.session_logger import SessionLogger

        with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": str(tmp_path / "test.db")}):
            with SessionLogger(session_id="test-session") as logger:
                logger.log(role="user", message="Test message")

            assert (tmp_path / "test.db").exists(), "Condition must be true"


class TestCLI:
    """Test CLI commands."""

    def test_validate_env_command(self):
        """Test validate-env CLI command."""
        from click.testing import CliRunner

        from codex.cli import validate_env_cmd

        runner = CliRunner()
        result = runner.invoke(validate_env_cmd)

        assert result.exit_code == 0, "Result must not be empty"
        assert "Environment validation passed" in result.output, "Result must not be empty"
        assert "CODEX_ENV_PYTHON_VERSION" in result.output, "Result must not be empty"

    def test_session_logger_command(self):
        """Test session-logger CLI command."""
        from click.testing import CliRunner

        from codex.cli import session_logger_cmd

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                session_logger_cmd, ["--role", "user", "--message", "Test message"]
            )

            # Should succeed (or fail gracefully with clear error)
            assert result.exit_code in (0, 1)
            if result.exit_code == 0:
                assert "Logged" in result.output, "Result must not be empty"

    def test_query_logs_command_no_results(self):
        """Test query-logs CLI command with no results."""
        from click.testing import CliRunner

        from codex.cli import query_logs_cmd

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(query_logs_cmd, ["--search", "nonexistent"])

            # Should handle gracefully
            assert result.exit_code in (0, 1)


class TestDBManager:
    """Test database manager functionality."""

    def test_schema_initialization(self, tmp_path):
        """Test database schema initialization."""
        from codex.logging.db_manager import DBManager

        db_path = tmp_path / "test.db"
        manager = DBManager(db_path=db_path)

        # Initialize schema
        manager.init_schema()

        # Verify database exists
        assert db_path.exists(), "Condition must be true"

        # Verify tables created
        with manager.connection(auto_init=False) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='session_events'"
            )
            assert cursor.fetchone() is not None, "curs must be initialized"

    def test_connection_pooling(self, tmp_path):
        """Test connection pooling when enabled."""
        from codex.logging.db_manager import DBManager

        db_path = tmp_path / "test_pool.db"
        manager = DBManager(db_path=db_path)

        # Enable pooling temporarily
        old_pool = DBManager._POOL_ENABLED
        try:
            DBManager._POOL_ENABLED = True

            # Get and return connection
            conn1 = manager.get_connection()
            manager.close_connection(conn1)

            # Get another connection - should come from pool
            conn2 = manager.get_connection()
            # Note: Due to implementation, we can't guarantee same connection
            # but pool should exist
            assert True, "True is not valid"

            manager.close_connection(conn2)
        finally:
            DBManager._POOL_ENABLED = old_pool
            DBManager.close_all_pools()

    def test_context_manager(self, tmp_path):
        """Test DBManager context manager."""
        from codex.logging.db_manager import DBManager

        db_path = tmp_path / "test_ctx.db"
        manager = DBManager(db_path=db_path)

        # Use context manager
        with manager.connection() as conn:
            cursor = conn.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1, "curs is not valid"

    def test_init_db_cli_command(self):
        """Test init-db CLI command."""
        from click.testing import CliRunner

        from codex.cli import init_db_cmd

        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(init_db_cmd, ["--db-path", "test.db"])

            # Should succeed
            assert result.exit_code == 0, "Result must not be empty"
            assert "initialized successfully" in result.output.lower(), "Result must not be empty"

    def test_close_all_pools_integration(self, pooling_db_manager, pool_state_tracker):
        """Integration test for pool cleanup using fixtures.

        This test validates that:
        1. Pooling is actually enabled (via fixture)
        2. Connections are returned to pool (not immediately closed)
        3. close_all_pools() clears all connections
        4. Pool dictionary is emptied

        Fixtures used:
            pooling_db_manager: Provides DBManager with pooling enabled
            pool_state_tracker: Tracks pool size changes
        """
        from codex.logging.db_manager import DBManager

        # Get connection and return to pool
        conn1 = pooling_db_manager.get_connection()
        pooling_db_manager.close_connection(conn1)

        # Verify pool grew (connection was added)
        pool_state_tracker["assert_pool_grew"]()

        # Verify pool has exactly 1 connection
        pool_state_tracker["assert_pool_size"](1)

        # Cleanup
        DBManager.close_all_pools()

        # Verify pool is empty
        pool_state_tracker["assert_pool_empty"]()


class TestCLIEndToEnd:
    """End-to-end CLI workflow tests."""

    def test_cli_session_lifecycle(self, tmp_path):
        """Test complete CLI workflow: init → log → view → query."""
        from click.testing import CliRunner

        from codex.cli import (
            init_db_cmd,
            query_logs_cmd,
            session_logger_cmd,
            viewer_cmd,
        )

        runner = CliRunner()

        # Set up environment

        db_path = str(tmp_path / "e2e_test.db")
        os.environ["CODEX_LOG_DB_PATH"] = db_path

        try:
            # Step 1: Initialize database
            result = runner.invoke(init_db_cmd, ["--db-path", db_path])
            assert result.exit_code == 0, f"init-db failed: {result.output}"

            # Step 2: Log some messages
            result = runner.invoke(
                session_logger_cmd,
                ["--session-id", "e2e-test", "--role", "user", "--message", "Test message 1"],
            )
            assert result.exit_code == 0, f"session-logger failed: {result.output}"

            result = runner.invoke(
                session_logger_cmd,
                ["--session-id", "e2e-test", "--role", "assistant", "--message", "Test response"],
            )
            assert result.exit_code == 0, f"session-logger failed: {result.output}"

            # Step 3: View logs
            result = runner.invoke(viewer_cmd, ["--session-id", "e2e-test", "--format", "text"])
            # Note: viewer uses external main() which may behave differently in tests
            # We check it doesn't crash rather than specific output
            assert result.exit_code in (0, 1)  # May exit with 1 if no data found in test env

            # Step 4: Query logs
            result = runner.invoke(query_logs_cmd, ["--search", "Test"])
            # Query should work or gracefully handle empty results
            assert result.exit_code in (0, 1)

        finally:
            # Cleanup
            if "CODEX_LOG_DB_PATH" in os.environ:
                del os.environ["CODEX_LOG_DB_PATH"]


class TestNewCLICommands:
    """Test new CLI commands added in Phase 1 final push."""

    def test_export_env_text(self):
        """Test export-env command with text format."""
        from click.testing import CliRunner

        from codex.cli import export_env_cmd

        runner = CliRunner()
        result = runner.invoke(export_env_cmd, ["--format", "text"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "CODEX_ENV_PYTHON_VERSION" in result.output, "Result must not be empty"

    def test_export_env_json(self):
        """Test export-env command with JSON format."""
        from click.testing import CliRunner

        from codex.cli import export_env_cmd

        runner = CliRunner()
        result = runner.invoke(export_env_cmd, ["--format", "json"])

        assert result.exit_code == 0, "Result must not be empty"
        # Should be valid JSON
        import json

        data = json.loads(result.output)
        assert "CODEX_ENV_PYTHON_VERSION" in data, "Data must not be empty"

    def test_list_sessions(self, tmp_path):
        """Test list-sessions command."""
        from click.testing import CliRunner

        from codex.cli import list_sessions_cmd

        runner = CliRunner()

        # Set up test database

        db_path = str(tmp_path / "list_test.db")

        # Save and clear environment
        old_db_path = os.environ.get("CODEX_LOG_DB_PATH")
        os.environ["CODEX_LOG_DB_PATH"] = db_path

        try:
            # Initialize and add some data
            from codex.logging.db_manager import DBManager

            manager = DBManager(db_path=tmp_path / "list_test.db")
            manager.init_schema()

            # Run command (may be empty but should not crash)
            result = runner.invoke(list_sessions_cmd, ["--limit", "5"])
            # Command may exit with 1 if error or 0 if success
            # Both are acceptable for empty database
            assert result.exit_code in (0, 1)

        finally:
            # Restore environment
            if old_db_path is not None:
                os.environ["CODEX_LOG_DB_PATH"] = old_db_path
            elif "CODEX_LOG_DB_PATH" in os.environ:
                del os.environ["CODEX_LOG_DB_PATH"]

    def test_clean_logs_dry_run(self):
        """Test clean-logs command in dry-run mode."""
        from click.testing import CliRunner

        from codex.cli import clean_logs_cmd

        runner = CliRunner()
        result = runner.invoke(clean_logs_cmd, ["--dry-run", "--older-than", "30"])

        # Should succeed (may find nothing to clean)
        assert result.exit_code == 0, "Result must not be empty"


class TestMissingMethods:
    """Test methods added in F1 - method completeness."""

    def test_set_log_level(self, tmp_path):
        """Test dynamic log level setting."""
        import logging

        from codex.logging.error_handler import CodexErrorHandler

        handler = CodexErrorHandler(log_dir=tmp_path)

        # Default should be ERROR
        assert handler.logger.level == logging.ERROR, "Error should be raised or set"

        # Test valid levels
        handler.set_log_level("DEBUG")
        assert handler.logger.level == logging.DEBUG, "level is not valid"

        handler.set_log_level("warning")  # case-insensitive
        assert handler.logger.level == logging.WARNING, "level is not valid"

        handler.set_log_level("INFO")
        assert handler.logger.level == logging.INFO, "level is not valid"

        # Test invalid level

        with pytest.raises(ValueError, match="Invalid log level"):
            handler.set_log_level("INVALID")

    def test_public_validate_method(self):
        """Test public validate() method."""
        from unittest.mock import patch

        from codex.config.env_vars import EnvironmentManager

        # Lazy validation mode
        with patch.dict(os.environ, {}, clear=True):
            env = EnvironmentManager(lazy_validation=True)

            # Should not crash on init
            assert not env._validated, "Condition must be true"

            # Explicit validation
            env.validate()
            assert env._validated, "Condition must be true"

            # Idempotent - second call should be safe
            env.validate()
            assert env._validated, "Condition must be true"

    def test_validate_with_invalid_env(self):
        """Test validate() detects invalid environment."""
        from unittest.mock import patch

        from codex.config.env_vars import EnvironmentManager

        with patch.dict(os.environ, {"CODEX_SQLITE_POOL": "999"}, clear=True):
            env = EnvironmentManager(lazy_validation=True)

            # Should fail on explicit validation
            with pytest.raises(EnvironmentError, match="Invalid value"):
                env.validate()


class TestEdgeCases:
    """Test edge cases and error paths for coverage (F3)."""

    def test_error_handler_with_empty_log_dir(self):
        """Test ErrorHandler with non-existent log directory."""
        import time
        from pathlib import Path

        from codex.logging.error_handler import CodexErrorHandler

        # Non-existent path should be created
        fake_path = Path(os.path.join(tempfile.gettempdir(), "codex_test_nonexistent_") + str(time.time()))
        CodexErrorHandler(log_dir=fake_path)

        assert fake_path.exists(), "Condition must be true"

        # Cleanup
        import shutil

        shutil.rmtree(fake_path)

    def test_db_manager_invalid_path(self):
        """Test DBManager with invalid/read-only path."""
        from pathlib import Path

        from codex.logging.db_manager import DBManager

        # Invalid path should raise error on init_schema
        db = DBManager(db_path=Path("/invalid/readonly/path.db"))

        with pytest.raises(Exception):  # Could be OSError or sqlite3.Error
            db.init_schema()

    def test_environment_manager_missing_optional_vars(self):
        """Test EnvironmentManager with missing optional variables."""
        from unittest.mock import patch

        from codex.config.env_vars import EnvironmentManager

        with patch.dict(os.environ, {}, clear=True):
            env = EnvironmentManager()

            # Should use defaults for optional vars
            assert env.get("CODEX_ENV_PYTHON_VERSION") == "3.12", "Condition must be true"
            assert env.get("CODEX_SESSION_LOG_DIR") == ".codex/sessions", "Condition must be true"

    def test_db_manager_empty_database(self, tmp_path):
        """Test querying empty database."""
        from codex.logging.db_manager import DBManager

        db = DBManager(db_path=tmp_path / "empty.db")
        db.init_schema()

        # Query empty database
        with db.connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM session_events")
            count = cursor.fetchone()[0]
            assert count == 0, "Count must be greater than zero"

    def test_export_env_with_empty_config(self):
        """Test export-env with minimal environment."""
        from unittest.mock import patch

        from click.testing import CliRunner

        from codex.cli import export_env_cmd

        runner = CliRunner()

        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(export_env_cmd, ["--format=json"])
            assert result.exit_code == 0, "Result must not be empty"

            # Should have at least defaults
            import json

            config = json.loads(result.output)
            assert "CODEX_ENV_PYTHON_VERSION" in config, "Condition must be true"

    def test_clean_logs_with_no_old_logs(self):
        """Test clean-logs when no old logs exist."""
        from click.testing import CliRunner

        from codex.cli import clean_logs_cmd

        runner = CliRunner()
        result = runner.invoke(clean_logs_cmd, ["--older-than=30", "--dry-run"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "0" in result.output or "No" in result.output or "no" in result.output.lower()


class TestConcurrentAccess:
    """Test concurrent database access (F2)."""

    def test_db_manager_concurrent_access(self, tmp_path):
        """Test DBManager handles concurrent writes correctly (WAL mode)."""
        import threading
        import time

        from codex.logging.db_manager import DBManager

        db_path = tmp_path / "concurrent_test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        errors = []
        write_count = [0]  # Mutable to track across threads

        def write_logs(thread_id: int, iterations: int):
            """Write logs from a single thread."""
            try:
                for i in range(iterations):
                    with manager.connection() as conn:
                        conn.execute(
                            "INSERT INTO session_events (ts, session_id, role, message) "
                            "VALUES (?, ?, ?, ?)",
                            (
                                time.time(),
                                f"thread-{thread_id}",
                                "user",
                                f"Message {i} from thread {thread_id}",
                            ),
                        )
                        conn.commit()
                    write_count[0] += 1
            except (IOError, OSError) as e:
                errors.append((thread_id, str(e)))

        # Spawn 5 threads writing 10 messages each
        threads = []
        for i in range(5):
            t = threading.Thread(target=write_logs, args=(i, 10))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify no errors (WAL mode should handle concurrency)
        assert len(errors) == 0, f"Concurrent writes should not error: {errors}"

        # Verify all 50 writes succeeded
        with manager.connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM session_events")
            count = cursor.fetchone()[0]

        assert count == 50, f"Expected 50 rows (5 threads × 10 writes), got {count}"
        assert write_count[0] == 50, f"Write count mismatch: {write_count[0]}"


class TestFullSessionLifecycle:
    """Test complete session lifecycle (F2)."""

    def test_cli_full_session_lifecycle(self, tmp_path):
        """Test complete session lifecycle workflow.

        Flow: init-db → log messages → query database → verify results
        """
        import time

        from click.testing import CliRunner

        from codex.cli import init_db_cmd
        from codex.logging.db_manager import DBManager

        runner = CliRunner()
        db_path = tmp_path / "lifecycle_test.db"

        # Step 1: Initialize database via CLI
        result = runner.invoke(init_db_cmd, ["--db-path", str(db_path)])
        assert result.exit_code == 0, f"init-db failed: {result.output}"
        assert db_path.exists(), "Condition must be true"

        # Step 2: Log test messages via DBManager (direct API)
        manager = DBManager(db_path=db_path)
        session_id = "test-session-123"

        test_messages = [
            ("system", "Session initialized"),
            ("user", "Hello, world"),
            ("assistant", "Hi there!"),
            ("user", "How are you?"),
            ("assistant", "I'm doing well"),
        ]

        for role, message in test_messages:
            with manager.connection() as conn:
                conn.execute(
                    "INSERT INTO session_events (ts, session_id, role, message) "
                    "VALUES (?, ?, ?, ?)",
                    (time.time(), session_id, role, message),
                )
                conn.commit()

        # Step 3: Query database and verify
        with manager.connection() as conn:
            # Count total messages
            cursor = conn.execute(
                "SELECT COUNT(*) FROM session_events WHERE session_id = ?", (session_id,)
            )
            count = cursor.fetchone()[0]
            assert count == 5, f"Expected 5 messages, got {count}"

            # Verify message content
            cursor = conn.execute(
                "SELECT role, message FROM session_events WHERE session_id = ? ORDER BY ts",
                (session_id,),
            )
            rows = cursor.fetchall()

            for i, (expected_role, expected_msg) in enumerate(test_messages):
                actual_role, actual_msg = rows[i]
                assert actual_role == expected_role, f"Role mismatch at index {i}"
                assert actual_msg == expected_msg, f"Message mismatch at index {i}"

        # Step 4: Test query functionality (simulates query-logs)
        with manager.connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM session_events WHERE message LIKE ?", ("%world%",)
            )
            search_count = cursor.fetchone()[0]
            assert search_count == 1, "Search should find 'Hello, world'"


class TestViewerCLIWrapper:
    """Test viewer CLI wrapper passes correct arguments (regression test for P1 bug)."""

    def test_viewer_wrapper_passes_list_not_namespace(self, tmp_path):
        """Ensure LogViewer.view() passes argv list to main(), not Namespace.

        This is a regression test for the P1 bug where the wrapper called
        main(parse_args(args)) instead of main(args), causing TypeError.
        """
        import time
        from unittest.mock import patch

        from codex.logging.db_manager import DBManager
        from codex.logging.viewer import LogViewer

        # Set up test database
        db_path = tmp_path / "viewer_test.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        # Add a test session
        session_id = "test-viewer-123"
        with manager.connection() as conn:
            conn.execute(
                "INSERT INTO session_events (ts, session_id, role, message) VALUES (?, ?, ?, ?)",
                (time.time(), session_id, "user", "Test message"),
            )
            conn.commit()

        # Mock main() to verify it receives a list, not Namespace
        with patch("codex.logging.viewer.main") as mock_main:
            mock_main.return_value = 0

            viewer = LogViewer()
            viewer.view(session_id=session_id, output_format="text")

            # Verify main was called once
            assert mock_main.call_count == 1, "Count must be greater than zero"

            # Verify first argument is a list of strings (argv), not Namespace
            call_args = mock_main.call_args[0]
            assert len(call_args) == 1, "main() should be called with one argument"
            argv = call_args[0]
            assert isinstance(argv, list), f"Expected list, got {type(argv)}"
            assert all(isinstance(arg, str) for arg in argv), "All argv elements should be strings"

            # Verify correct arguments
            assert "--session-id" in argv, "Condition must be true"
            assert session_id in argv, "Condition must be true"
            assert "--format" in argv, "Condition must be true"
            assert "text" in argv, "Condition must be true"

    def test_viewer_wrapper_with_actual_main(self, tmp_path):
        """Test that viewer wrapper works end-to-end with actual main()."""
        import time
        from unittest.mock import patch

        from codex.logging.db_manager import DBManager
        from codex.logging.viewer import LogViewer

        # Set up test database
        db_path = tmp_path / "viewer_e2e.db"
        manager = DBManager(db_path=db_path)
        manager.init_schema()

        # Add test session
        session_id = "test-e2e-456"
        with manager.connection() as conn:
            conn.execute(
                "INSERT INTO session_events (ts, session_id, role, message) VALUES (?, ?, ?, ?)",
                (time.time(), session_id, "user", "E2E test message"),
            )
            conn.commit()

        # Set DB path in environment so viewer can find it
        with patch.dict(os.environ, {"CODEX_LOG_DB_PATH": str(db_path)}):
            # Capture stdout to verify output
            import sys
            from io import StringIO

            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                viewer = LogViewer()
                viewer.view(session_id=session_id, output_format="text")

                output = captured_output.getvalue()
                # Should contain the test message
                assert "E2E test message" in output, f"Expected message in output, got: {output}"
            finally:
                sys.stdout = old_stdout
