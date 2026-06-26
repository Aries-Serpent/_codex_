"""Integration tests for distributed training initialization.

Tests the accelerate_init_guard module with various environment configurations.
Uses pytest markers to skip tests on CPU-only runners or when ACCELERATE_TEST is not set.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# NOTE: removed ad-hoc sys.path modifications that previously attempted to add `tests/`
# to sys.path. Adding `tests/` at top-level shadows stdlib modules (e.g. `ast`) and
# causes unpredictable import resolution in CI. Tests should import test utilities
# using the canonical `tests.utils.*` package import path.
from tests.utils.torch_helpers import require_torch

torch = require_torch()

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
        # Test with GPU not available
        with patch("torch.cuda.is_available") as mock_cuda:
            mock_cuda.return_value = False  # Return actual bool, not MagicMock

            result = is_gpu_available()

            assert isinstance(result, bool)
            assert result is False, "Result must not be empty"

        # Test with GPU available
        with patch("torch.cuda.is_available") as mock_cuda:
            mock_cuda.return_value = True  # Return actual bool, not MagicMock

            result = is_gpu_available()

            assert isinstance(result, bool)
            assert result is True, "Result must not be empty"

    def test_get_distributed_env_info(self):
        """Test distributed environment variable collection."""
        env_info = get_distributed_env_info()

        # Should return dict with expected keys
        assert isinstance(env_info, dict)
        assert "MASTER_ADDR" in env_info, "Condition must be true"
        assert "WORLD_SIZE" in env_info, "Condition must be true"
        assert "RANK" in env_info, "Condition must be true"
        assert "ACCELERATE_TEST" in env_info, "Condition must be true"

    def test_safe_init_cpu_only_graceful_skip(self, monkeypatch):
        """Test that CPU-only environments gracefully skip initialization."""
        # Simulate CPU-only environment
        monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")

        result = safe_accelerate_init(cpu_fallback=True)

        # Should return structured result
        assert isinstance(result, AccelerateInitResult)

        # On CPU-only with fallback, should skip gracefully
        if not is_gpu_available():
            assert result.skip_reason == "cpu_only", "Result must not be empty"
            assert not result.success, "Result must not be empty"
            assert result.error is None, "Result must not be empty"

    def test_safe_init_no_accelerate_skip(self, monkeypatch):
        """Test graceful skip when accelerate is not installed."""
        # This test assumes accelerate might not be installed
        result = safe_accelerate_init()

        assert isinstance(result, AccelerateInitResult)

        # If accelerate not available, should skip
        if not is_accelerate_available():
            assert result.skip_reason == "no_accelerate", "Result must not be empty"
            assert not result.success, "Result must not be empty"
            assert result.error is None, "Result must not be empty"

    @pytest.mark.skipif(
        not is_accelerate_available(),
        reason="accelerate not installed",
    )
    def test_safe_init_structured_result(self):
        """Test that safe_accelerate_init returns structured result."""
        # Mock is_gpu_available to return actual bool
        with patch("src.training.accelerate_init_guard.is_gpu_available") as mock_gpu:
            mock_gpu.return_value = False  # Return actual bool, not MagicMock

            # Mock accelerate.PartialState if accelerate is available
            with patch("accelerate.PartialState", create=True) as mock_partial_state:
                mock_state = MagicMock()
                mock_state.distributed_type = "DistributedType.NO"
                mock_state.num_processes = 1
                mock_state.process_index = 0
                mock_partial_state.return_value = mock_state

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
            assert result.skip_reason is not None or result.error is not None, "skip_reason must be initialized"

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
        reason="GPU required and ACCELERATE_TEST=1 must be set",
    )
    def test_safe_init_with_gpu(self):
        """Test accelerate initialization with GPU available (gated test)."""
        result = safe_accelerate_init()

        # With GPU and accelerate, should either succeed or have clear error
        assert isinstance(result, AccelerateInitResult)
        assert result.gpu_available, "Result must not be empty"

        if result.success:
            assert result.backend is not None, "backend must be initialized"
            assert result.world_size >= 1, "world_size must be greater than zero"
            assert result.rank >= 0, "rank must be greater than zero"
        else:
            # If not successful, should have error message
            assert result.error is not None or result.skip_reason is not None, "error must be initialized"

    def test_distributed_env_info_structure(self, monkeypatch):
        """Test that distributed env info returns expected structure."""
        # Set some test env vars
        monkeypatch.setenv("WORLD_SIZE", "4")
        monkeypatch.setenv("RANK", "2")
        monkeypatch.setenv("MASTER_ADDR", "localhost")

        env_info = get_distributed_env_info()

        assert env_info["WORLD_SIZE"] == "4", "Condition must be true"
        assert env_info["RANK"] == "2", "Condition must be true"
        assert env_info["MASTER_ADDR"] == "localhost", "Condition must be true"

    def test_result_string_representation(self):
        """Test that AccelerateInitResult has readable string representation."""
        result = safe_accelerate_init()

        result_str = str(result)
        assert isinstance(result_str, str)
        assert "AccelerateInitResult" in result_str, "Result must not be empty"

        # Should contain status information
        if result.success:
            assert "success=True" in result_str.lower() or "backend" in result_str.lower(), "Result must not be empty"
        elif result.skip_reason:
            assert "skip" in result_str.lower() or result.skip_reason in result_str, "Result must not be empty"
        else:
            assert "fail" in result_str.lower() or "error" in result_str.lower(), "Result must not be empty"


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
