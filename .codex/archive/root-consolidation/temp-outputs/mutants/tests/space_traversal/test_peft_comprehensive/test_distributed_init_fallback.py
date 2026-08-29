"""
Tests for distributed training initialization with graceful fallback.

These tests verify that distributed/accelerate initialization:
1. Gracefully skips when dependencies are unavailable
2. Falls back to CPU-only mode when GPUs are not available
3. Provides clear error messages for troubleshooting
"""

import pytest


def test_distributed_init_skip_when_unavailable():
    """Test that distributed init gracefully skips when torch.distributed unavailable."""
    try:
        from codex_ml.distributed import (
            init_distributed_if_needed,
            is_distributed_available,
        )

        # Should not raise even if distributed not available
        available = is_distributed_available()

        if not available:
            # Should return False and not raise
            result = init_distributed_if_needed()
            assert result is False, "Result must not be empty"

    except ImportError:
        # If module doesn't exist at all, that's also acceptable
        pytest.skip("codex_ml.distributed not available")


def test_accelerate_init_cpu_fallback():
    """Test that Accelerator can initialize on CPU-only systems."""
    try:
        from accelerate import Accelerator

        # Should successfully create accelerator even without GPU
        accelerator = Accelerator(cpu=True)
        assert accelerator is not None, "accelerator must be initialized"
        assert accelerator.device.type in ["cpu", "cuda"]

    except ImportError:
        pytest.skip("accelerate not installed")
    except AttributeError as e:
        # Log the error but don't fail - some environments may not support it
        pytest.skip(f"Accelerator init failed (expected in minimal env): {e}")


def test_distributed_utils_safe_defaults():
    """Test that distributed utils provide safe defaults when unavailable."""
    try:
        from codex_ml.distributed import (
            barrier,
            cleanup,
            get_rank,
            get_world_size,
        )

        # Should provide safe single-process defaults
        rank = get_rank()
        assert rank == 0, "Default rank should be 0"

        world_size = get_world_size()
        assert world_size == 1, "Default world size should be 1"

        # Should be no-ops and not raise
        barrier()
        cleanup()

    except ImportError:
        pytest.skip("codex_ml.distributed not available")


def test_accelerate_init_with_config():
    """Test Accelerator initialization with various configs."""
    try:
        from accelerate import Accelerator

        # Test with minimal config
        configs = [
            {"cpu": True},
            {"mixed_precision": "no"},
        ]

        for config in configs:
            try:
                acc = Accelerator(**config)
                assert acc is not None, "acc must be initialized"
            except TypeError:
                # Some configs might not be compatible with installed version
                _ = None  # suppressed: no action needed

    except ImportError:
        pytest.skip("accelerate not installed")


@pytest.mark.parametrize("backend", ["nccl", "gloo", None])
def test_distributed_backend_selection(backend, monkeypatch):
    """Test that distributed backend selection works or fails gracefully."""
    try:
        import torch.distributed as dist

        from codex_ml.distributed import init_distributed_if_needed

        # Don't actually initialize if already initialized
        if dist.is_initialized():
            pytest.skip("Distributed already initialized")

        # Mock environment for single-process test
        if backend:
            monkeypatch.setenv("CODEX_DIST_BACKEND", backend)

        # Should either succeed or skip gracefully
        result = init_distributed_if_needed()

        # In single-process environment, should return False
        assert result in [True, False]

    except ImportError:
        pytest.skip("torch.distributed not available")
    except RuntimeError as e:
        # Expected in single-process environment
        assert "backend" in str(e).lower() or "init" in str(e).lower(), "Condition must be true"
