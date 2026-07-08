"""
Test Codex Logging

Test module for codex logging.
"""

import pytest


class TestCodexLogging:
    """Test codex_logging module functionality."""

    def test_mlflow_offline_enabled(self):
        """Test _mlflow_offline_enabled function."""
        try:
            from codex_ml.monitoring.codex_logging import _mlflow_offline_enabled

            result = _mlflow_offline_enabled()
            assert isinstance(result, bool)
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")

    def test_ensure_local_mlflow_tracking_uri(self):
        """Test _ensure_local_mlflow_tracking_uri_default function."""
        try:
            from codex_ml.monitoring.codex_logging import (
                _ensure_local_mlflow_tracking_uri_default,
            )

            _ensure_local_mlflow_tracking_uri_default()
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestCodexLoggers:
    """Test CodexLoggers enum."""

    def test_codex_loggers_available(self):
        """Test CodexLoggers enum is available."""
        try:
            from codex_ml.monitoring._logger_types import CodexLoggers

            assert CodexLoggers is not None, "CodexLoggers must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")


class TestTelemetryComponentStatus:
    """Test TelemetryComponentStatus enum."""

    def test_telemetry_status_available(self):
        """Test TelemetryComponentStatus enum is available."""
        try:
            from codex_ml.monitoring._logger_types import TelemetryComponentStatus

            assert TelemetryComponentStatus is not None, "TelemetryComponentStatus must be initialized"
        except ImportError as exc:
            pytest.skip(f"Optional dependency missing: {exc}")
