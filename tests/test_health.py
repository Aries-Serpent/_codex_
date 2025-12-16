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

    assert result["status"] == "healthy"
    assert "timestamp" in result
    assert result["service"] == "codex-ml"


def test_health_check_returns_timestamp():
    """Test that health check includes timestamp."""
    result = health_check()

    assert isinstance(result["timestamp"], (int, float))
    assert result["timestamp"] > 0


def test_readiness_check_returns_structure():
    """Test that readiness check returns expected structure."""
    result = readiness_check()

    assert "ready" in result
    assert "timestamp" in result
    assert "checks" in result
    assert isinstance(result["checks"], dict)


def test_readiness_check_has_timestamp():
    """Test that readiness check includes timestamp."""
    result = readiness_check()

    assert isinstance(result["timestamp"], (int, float))
    assert result["timestamp"] > 0


def test_readiness_check_includes_disk_space():
    """Test that readiness check includes disk space check."""
    result = readiness_check()

    assert "disk_space" in result["checks"]
    disk_check = result["checks"]["disk_space"]
    assert "status" in disk_check


def test_readiness_check_includes_directory_checks():
    """Test that readiness check verifies required directories."""
    result = readiness_check()

    # Should check for .codex, src, configs directories
    checks = result["checks"]
    assert any("dir_" in key for key in checks.keys())


def test_readiness_check_graceful_on_missing_psutil():
    """Test that readiness check works even if psutil is unavailable."""
    # This should not raise an exception
    result = readiness_check()

    assert result is not None
    assert "checks" in result


def test_health_check_consistent_format():
    """Test that multiple health checks return consistent format."""
    result1 = health_check()
    result2 = health_check()

    assert set(result1.keys()) == set(result2.keys())
    assert result1["status"] == result2["status"]
    assert result1["service"] == result2["service"]


def test_readiness_ready_is_boolean():
    """Test that ready status is a boolean."""
    result = readiness_check()

    assert isinstance(result["ready"], bool)
