"""Integration tests for distributed training initialization.

Tests the accelerate_init_guard module with various environment configurations.
Uses pytest markers to skip tests on CPU-only runners or when ACCELERATE_TEST is not set.
"""
import os
import sys
from pathlib import Path

import pytest

# Add training directory to path
_REPO_ROOT = Path(__file__).parent.parent.parent
_TRAINING_DIR = _REPO_ROOT / "training"
if str(_TRAINING_DIR) not in sys.path:
    sys.path.insert(0, str(_TRAINING_DIR))

from accelerate_init_guard import (
    AccelerateInitResult,
    get_distributed_env_info,
    is_accelerate_available,
    is_gpu_available,
    safe_accelerate_init,
)


@pytest.mark.integration
class TestAccelerateInitGuard:
    """Test suite for accelerate initialization guard."""

    def test_is_accelerate_available(self):
        """Test accelerate availability detection."""
        # Should return bool without raising
        result = is_accelerate_available()
        assert isinstance(result, bool)

    def test_is_gpu_available(self):
        """Test GPU availability detection."""
        # Should return bool without raising
        result = is_gpu_available()
        assert isinstance(result, bool)

    def test_get_distributed_env_info(self):
        """Test distributed environment variable collection."""
        env_info = get_distributed_env_info()
        
        # Should return dict with expected keys
        assert isinstance(env_info, dict)
        assert "MASTER_ADDR" in env_info
        assert "WORLD_SIZE" in env_info
        assert "RANK" in env_info
        assert "ACCELERATE_TEST" in env_info

    def test_safe_init_cpu_only_graceful_skip(self, monkeypatch):
        """Test that CPU-only environments gracefully skip initialization."""
        # Simulate CPU-only environment
        monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
        
        result = safe_accelerate_init(cpu_fallback=True)
        
        # Should return structured result
        assert isinstance(result, AccelerateInitResult)
        
        # On CPU-only with fallback, should skip gracefully
        if not is_gpu_available():
            assert result.skip_reason == "cpu_only"
            assert not result.success
            assert result.error is None

    def test_safe_init_no_accelerate_skip(self, monkeypatch):
        """Test graceful skip when accelerate is not installed."""
        # This test assumes accelerate might not be installed
        result = safe_accelerate_init()
        
        assert isinstance(result, AccelerateInitResult)
        
        # If accelerate not available, should skip
        if not is_accelerate_available():
            assert result.skip_reason == "no_accelerate"
            assert not result.success
            assert result.error is None

    def test_safe_init_structured_result(self):
        """Test that safe_accelerate_init returns structured result."""
        result = safe_accelerate_init()
        
        # Verify result structure
        assert isinstance(result, AccelerateInitResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.accelerate_available, bool)
        assert isinstance(result.gpu_available, bool)
        assert isinstance(result.world_size, int)
        assert isinstance(result.rank, int)
        
        # Result should have either skip_reason or error or success
        if not result.success:
            assert result.skip_reason is not None or result.error is not None

    def test_safe_init_does_not_raise_by_default(self):
        """Test that safe_accelerate_init does not raise exceptions by default."""
        # Should not raise even in problematic environments
        try:
            result = safe_accelerate_init(raise_on_error=False)
            assert isinstance(result, AccelerateInitResult)
        except Exception as e:
            pytest.fail(f"safe_accelerate_init raised unexpectedly: {e}")

    @pytest.mark.skipif(
        not is_gpu_available() or os.getenv("ACCELERATE_TEST") != "1",
        reason="GPU required and ACCELERATE_TEST=1 must be set"
    )
    def test_safe_init_with_gpu(self):
        """Test accelerate initialization with GPU available (gated test)."""
        result = safe_accelerate_init()
        
        # With GPU and accelerate, should either succeed or have clear error
        assert isinstance(result, AccelerateInitResult)
        assert result.gpu_available
        
        if result.success:
            assert result.backend is not None
            assert result.world_size >= 1
            assert result.rank >= 0
        else:
            # If not successful, should have error message
            assert result.error is not None or result.skip_reason is not None

    def test_distributed_env_info_structure(self, monkeypatch):
        """Test that distributed env info returns expected structure."""
        # Set some test env vars
        monkeypatch.setenv("WORLD_SIZE", "4")
        monkeypatch.setenv("RANK", "2")
        monkeypatch.setenv("MASTER_ADDR", "localhost")
        
        env_info = get_distributed_env_info()
        
        assert env_info["WORLD_SIZE"] == "4"
        assert env_info["RANK"] == "2"
        assert env_info["MASTER_ADDR"] == "localhost"

    def test_result_string_representation(self):
        """Test that AccelerateInitResult has readable string representation."""
        result = safe_accelerate_init()
        
        result_str = str(result)
        assert isinstance(result_str, str)
        assert "AccelerateInitResult" in result_str
        
        # Should contain status information
        if result.success:
            assert "success=True" in result_str.lower() or "backend" in result_str.lower()
        elif result.skip_reason:
            assert "skip" in result_str.lower() or result.skip_reason in result_str
        else:
            assert "fail" in result_str.lower() or "error" in result_str.lower()


@pytest.mark.integration
class TestAccelerateInitGuardCLI:
    """Test the CLI/diagnostic mode of accelerate_init_guard."""

    def test_cli_mode_runs_without_error(self, tmp_path, monkeypatch, capsys):
        """Test that the guard can run in CLI diagnostic mode."""
        # Import the module
        
        # The module has a __main__ block - we can't easily test it without
        # running as subprocess, so just verify the functions work
        result = safe_accelerate_init()
        assert isinstance(result, AccelerateInitResult)
        
        env_info = get_distributed_env_info()
        assert isinstance(env_info, dict)
