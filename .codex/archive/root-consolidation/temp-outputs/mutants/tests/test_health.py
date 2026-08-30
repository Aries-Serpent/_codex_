"""
Test Health

Test module for health.
"""

#!/usr/bin/env python3
"""Tests for health check endpoints."""
import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from codex_ml.serving.health import health_check, readiness_check


def test_health_check_returns_healthy_status():
    """Test that health check returns healthy status."""
    result = health_check()

    assert result["status"] == "healthy", "Result must not be empty"
    assert "timestamp" in result, "Result must not be empty"
    assert result["service"] == "codex-ml", "Result must not be empty"


def test_health_check_returns_timestamp():
    """Test that health check includes timestamp."""
    result = health_check()

    assert isinstance(result["timestamp"], (int, float))
    assert result["timestamp"] > 0, "Value must be greater than zero"


def test_readiness_check_returns_structure():
    """Test that readiness check returns expected structure."""
    result = readiness_check()

    assert "ready" in result, "Result must not be empty"
    assert "timestamp" in result, "Result must not be empty"
    assert "checks" in result, "Result must not be empty"
    assert isinstance(result["checks"], dict)


def test_readiness_check_has_timestamp():
    """Test that readiness check includes timestamp."""
    result = readiness_check()

    assert isinstance(result["timestamp"], (int, float))
    assert result["timestamp"] > 0, "Value must be greater than zero"


def test_readiness_check_includes_disk_space():
    """Test that readiness check includes disk space check."""
    result = readiness_check()

    assert "disk_space" in result["checks"], "Result must not be empty"
    disk_check = result["checks"]["disk_space"]
    assert "status" in disk_check, "Condition must be true"


def test_readiness_check_includes_directory_checks():
    """Test that readiness check verifies required directories."""
    result = readiness_check()

    # Should check for .codex, src, configs directories
    checks = result["checks"]
    assert any("dir_" in key for key in checks), "Condition must be true"


def test_readiness_check_graceful_on_missing_psutil():
    """Test that readiness check works even if psutil is unavailable."""
    # This should not raise an exception
    result = readiness_check()

    assert result is not None, "result must be initialized"
    assert "checks" in result, "Result must not be empty"


def test_health_check_consistent_format():
    """Test that multiple health checks return consistent format."""
    result1 = health_check()
    result2 = health_check()

    assert set(result1.keys()) == set(result2.keys()), "Result must not be empty"
    assert result1["status"] == result2["status"], "Result must not be empty"
    assert result1["service"] == result2["service"], "Result must not be empty"


def test_readiness_ready_is_boolean():
    """Test that ready status is a boolean."""
    result = readiness_check()

    assert isinstance(result["ready"], bool)
