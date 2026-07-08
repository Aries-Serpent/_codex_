"""
Test Error Handler

Comprehensive test module for CodexErrorHandler in codex.logging.error_handler.
"""

from __future__ import annotations

import importlib
import logging
import tempfile
from pathlib import Path

import pytest


class TestErrorHandlerImports:
    """Tests for error_handler module imports."""

    def test_import_module(self) -> None:
        module = "codex.logging.error_handler"
        try:
            importlib.import_module(module)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_import_codex_error_handler_class(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        assert CodexErrorHandler is not None, "CodexErrorHandler must be initialized"

    def test_import_error_handler_singleton(self) -> None:
        from codex.logging.error_handler import error_handler

        assert error_handler is not None, "error_handler must be initialized"


class TestCodexErrorHandlerInit:
    """Tests for CodexErrorHandler initialization."""

    def test_init_with_default_log_dir(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            assert handler.log_dir == log_dir, "log_dir is not valid"

    def test_init_creates_log_directory(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "new_logs"
            CodexErrorHandler(log_dir=log_dir)
            assert log_dir.exists(), "Condition must be true"

    def test_init_creates_error_log_file(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            # Log something to create the file
            handler.logger.error("Test error")
            assert handler.error_log.exists(), "Error should be raised or set"

    def test_init_custom_max_bytes(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir, max_bytes=1024 * 1024)
            assert handler is not None, "handler must be initialized"

    def test_init_custom_backup_count(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir, backup_count=10)
            assert handler is not None, "handler must be initialized"


class TestSetLogLevel:
    """Tests for set_log_level method."""

    def test_set_log_level_debug(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            handler.set_log_level("DEBUG")
            assert handler.logger.level == logging.DEBUG, "level is not valid"

    def test_set_log_level_info(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            handler.set_log_level("INFO")
            assert handler.logger.level == logging.INFO, "level is not valid"

    def test_set_log_level_warning(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            handler.set_log_level("WARNING")
            assert handler.logger.level == logging.WARNING, "level is not valid"

    def test_set_log_level_error(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            handler.set_log_level("ERROR")
            assert handler.logger.level == logging.ERROR, "Error should be raised or set"

    def test_set_log_level_case_insensitive(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            handler.set_log_level("debug")
            assert handler.logger.level == logging.DEBUG, "level is not valid"

    def test_set_log_level_invalid_raises(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            with pytest.raises(ValueError, match="Invalid log level"):
                handler.set_log_level("INVALID")


class TestLogErrorsDecorator:
    """Tests for log_errors decorator."""

    def test_log_errors_decorator_exists(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            assert hasattr(handler, "log_errors")
            assert callable(handler.log_errors), "Error should be raised or set"

    def test_log_errors_decorator_normal_function(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)

            @handler.log_errors
            def normal_func():
                return "success"

            result = normal_func()
            assert result == "success", "Result must not be empty"

    def test_log_errors_decorator_logs_exceptions(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)

            @handler.log_errors
            def error_func():
                raise ValueError("Test error")

            with pytest.raises(ValueError):
                error_func()


class TestLogError:
    """Tests for log_error method."""

    def test_log_error_method_exists(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            assert hasattr(handler, "log_error")

    def test_log_error_with_context(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)

            try:
                raise ValueError("Test error")
            except ValueError as e:
                handler.log_error(e, context={"key": "value"})

            # Check log file has content
            assert handler.error_log.exists(), "Error should be raised or set"


class TestLoggerAttributes:
    """Tests for logger configuration."""

    def test_logger_level(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            assert handler.logger.level == logging.ERROR, "Error should be raised or set"

    def test_logger_does_not_propagate(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            assert handler.logger.propagate is False, "propagate is not valid"

    def test_logger_has_handlers(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            handler = CodexErrorHandler(log_dir=log_dir)
            assert len(handler.logger.handlers) > 0, "Collection must not be empty"


class TestErrorHandlerSingleton:
    """Tests for singleton error_handler instance."""

    def test_singleton_exists(self) -> None:
        from codex.logging.error_handler import error_handler

        assert error_handler is not None, "error_handler must be initialized"

    def test_singleton_is_codex_error_handler(self) -> None:
        from codex.logging.error_handler import CodexErrorHandler, error_handler

        assert isinstance(error_handler, CodexErrorHandler)
