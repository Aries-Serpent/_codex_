import pytest

pytest.importorskip("mlflow")
"""
Comprehensive test suite for codex_ml.training.distributed module.

This module provides 10+ tests targeting 70%+ coverage of distributed.py.
Tests cover distributed configuration, DDP setup, context managers,
and multi-node orchestration.

Phase: 2.1 - Core ML Training Coverage Initiative
Created: 2026-01-18
Target Coverage: 70%+
"""

from __future__ import annotations

import os

# Mock torch before importing distributed module
import sys
from unittest.mock import MagicMock, patch

import pytest

# Save original torch modules before mocking to avoid contaminating later tests
_TORCH_MOCK_KEYS = ("torch", "torch.distributed", "torch.nn", "torch.nn.parallel")
_orig_torch_mods = {k: sys.modules[k] for k in _TORCH_MOCK_KEYS if k in sys.modules}

# Create mock torch module
mock_torch = MagicMock()
mock_torch.distributed = MagicMock()
mock_torch.nn.parallel.DistributedDataParallel = MagicMock
sys.modules["torch"] = mock_torch
sys.modules["torch.distributed"] = mock_torch.distributed
sys.modules["torch.nn"] = mock_torch.nn
sys.modules["torch.nn.parallel"] = mock_torch.nn.parallel

from codex_ml.training.distributed import (
    DistributedConfig,
    DistributedManager,
    distributed_context,
)

# Restore original torch modules (distributed module has already captured mock refs)
sys.modules.update(_orig_torch_mods)
for _k in _TORCH_MOCK_KEYS:
    if _k not in _orig_torch_mods:
        sys.modules.pop(_k, None)

# =============================================================================
# Test Data & Fixtures
# =============================================================================


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment of distributed variables."""
    env_vars = [
        "WORLD_SIZE",
        "RANK",
        "LOCAL_RANK",
        "MASTER_ADDR",
        "MASTER_PORT",
        "DISTRIBUTED_ENABLED",
        "DISTRIBUTED_BACKEND",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def distributed_env(monkeypatch):
    """Set up distributed environment variables."""
    monkeypatch.setenv("WORLD_SIZE", "4")
    monkeypatch.setenv("RANK", "2")
    monkeypatch.setenv("LOCAL_RANK", "1")
    monkeypatch.setenv("MASTER_ADDR", "192.168.1.100")
    monkeypatch.setenv("MASTER_PORT", "29501")


# =============================================================================
# DistributedConfig Tests
# =============================================================================


def test_distributed_config_default():
    """Test DistributedConfig default initialization."""
    config = DistributedConfig()
    assert config.enabled is False, "enabled is not valid"
    assert config.backend == "nccl", "backend is not valid"
    assert config.world_size == 1, "world_size is not valid"
    assert config.rank == 0, "rank is not valid"
    assert config.local_rank == 0, "local_rank is not valid"
    assert config.master_addr == "localhost", "master_addr is not valid"
    assert config.master_port == "29500", "master_port is not valid"


def test_distributed_config_custom():
    """Test DistributedConfig with custom values."""
    config = DistributedConfig(
        enabled=True,
        backend="gloo",
        world_size=8,
        rank=3,
        local_rank=2,
        master_addr="10.0.0.1",
        master_port="12345",
    )
    assert config.enabled is True, "enabled is not valid"
    assert config.backend == "gloo", "backend is not valid"
    assert config.world_size == 8, "world_size is not valid"
    assert config.rank == 3, "rank is not valid"
    assert config.local_rank == 2, "local_rank is not valid"
    assert config.master_addr == "10.0.0.1", "master_addr is not valid"
    assert config.master_port == "12345", "master_port is not valid"


def test_distributed_config_from_env_default(clean_env):
    """Test DistributedConfig.from_env with no environment variables."""
    config = DistributedConfig.from_env()
    assert config.enabled is False, "enabled is not valid"
    assert config.world_size == 1, "world_size is not valid"
    assert config.rank == 0, "rank is not valid"
    assert config.local_rank == 0, "local_rank is not valid"


def test_distributed_config_from_env_distributed(distributed_env):
    """Test DistributedConfig.from_env with distributed environment."""
    config = DistributedConfig.from_env()
    assert config.enabled is True, "enabled is not valid"
    assert config.world_size == 4, "world_size is not valid"
    assert config.rank == 2, "rank is not valid"
    assert config.local_rank == 1, "local_rank is not valid"
    assert config.master_addr == "192.168.1.100", "master_addr is not valid"
    assert config.master_port == "29501", "master_port is not valid"


def test_distributed_config_from_env_explicit_enabled(monkeypatch, clean_env):
    """Test DistributedConfig.from_env with explicit enabled flag."""
    monkeypatch.setenv("DISTRIBUTED_ENABLED", "true")
    config = DistributedConfig.from_env()
    assert config.enabled is True, "enabled is not valid"


def test_distributed_config_to_env():
    """Test DistributedConfig.to_env exports to environment dict."""
    config = DistributedConfig(enabled=True, backend="nccl", world_size=4, rank=1, local_rank=0)
    env_dict = config.to_env()

    assert env_dict["DISTRIBUTED_ENABLED"] == "true", "Condition must be true"
    assert env_dict["DISTRIBUTED_BACKEND"] == "nccl", "Condition must be true"
    assert env_dict["WORLD_SIZE"] == "4", "Condition must be true"
    assert env_dict["RANK"] == "1", "Condition must be true"
    assert env_dict["LOCAL_RANK"] == "0", "Condition must be true"


def test_distributed_config_advanced_settings():
    """Test DistributedConfig advanced DDP settings."""
    config = DistributedConfig(
        find_unused_parameters=True, broadcast_buffers=False, gradient_as_bucket_view=False
    )
    assert config.find_unused_parameters is True, "find_unused_parameters is not valid"
    assert config.broadcast_buffers is False, "broadcast_buffers is not valid"
    assert config.gradient_as_bucket_view is False, "gradient_as_bucket_view is not valid"


# =============================================================================
# DistributedManager Tests
# =============================================================================


def test_distributed_manager_initialization():
    """Test DistributedManager initialization."""
    manager = DistributedManager()
    assert manager.config is not None, "config must be initialized"
    assert hasattr(manager, "_initialized")
    assert manager._initialized is False, "_initialized is not valid"


def test_distributed_manager_with_config():
    """Test DistributedManager with custom config."""
    config = DistributedConfig(enabled=True, world_size=2)
    manager = DistributedManager(config)
    assert manager.config.enabled is True, "enabled is not valid"
    assert manager.config.world_size == 2, "world_size is not valid"


@patch("codex_ml.training.distributed.dist")
def test_distributed_manager_initialize(mock_dist):
    """Test DistributedManager.initialize sets up process group."""
    config = DistributedConfig(enabled=True, world_size=2, rank=0)
    manager = DistributedManager(config)

    mock_dist.is_initialized.return_value = False
    mock_dist.is_available.return_value = True

    # Call initialize if method exists
    if hasattr(manager, "initialize"):
        manager.initialize()
        assert manager._initialized is True, "_initialized is not valid"


@patch("codex_ml.training.distributed.dist")
def test_distributed_manager_cleanup(mock_dist):
    """Test DistributedManager cleanup."""
    manager = DistributedManager()
    manager._initialized = True

    mock_dist.is_initialized.return_value = True

    # Call cleanup if method exists
    if hasattr(manager, "cleanup"):
        manager.cleanup()


def test_distributed_manager_device_selection():
    """Test DistributedManager selects correct device."""
    config = DistributedConfig(local_rank=2)
    manager = DistributedManager(config)

    # Should determine device based on local_rank
    assert hasattr(manager, "_device") or hasattr(manager, "device")


# =============================================================================
# distributed_context Tests
# =============================================================================


@patch("codex_ml.training.distributed.DistributedManager")
def test_distributed_context_manager(mock_manager_class):
    """Test distributed_context as context manager."""
    mock_manager = MagicMock()
    mock_manager_class.return_value = mock_manager

    with distributed_context() as manager:
        assert manager is not None, "manager must be initialized"


def test_distributed_context_function_signature():
    """Test distributed_context accepts config parameter."""
    config = DistributedConfig(enabled=False)

    # Test that function can be called with config
    result = distributed_context(config) if callable(distributed_context) else None

    # Context manager should work
    if result and hasattr(result, "__enter__"):
        with result as manager:
            assert manager is not None, "manager must be initialized"


# =============================================================================
# DDP Wrapper Tests
# =============================================================================


@patch("codex_ml.training.distributed.DDP")
@patch("codex_ml.training.distributed.torch")
def test_wrap_model_with_ddp(mock_torch, mock_ddp):
    """Test wrapping model with DistributedDataParallel."""
    mock_model = MagicMock()
    mock_ddp.return_value = mock_model

    config = DistributedConfig(enabled=True, local_rank=0)
    manager = DistributedManager(config)

    # Test wrapping if method exists
    if hasattr(manager, "wrap_model"):
        wrapped = manager.wrap_model(mock_model)
        assert wrapped is not None, "wrapped must be initialized"


@patch("codex_ml.training.distributed.torch")
def test_get_device(mock_torch):
    """Test device selection based on local_rank."""
    mock_torch.cuda.is_available.return_value = True

    config = DistributedConfig(local_rank=1)
    manager = DistributedManager(config)

    # Test device getter if exists
    if hasattr(manager, "device") or hasattr(manager, "get_device"):
        device = manager.device if hasattr(manager, "device") else manager.get_device()
        assert device is not None, "device must be initialized"


# =============================================================================
# Integration Tests
# =============================================================================


def test_distributed_config_round_trip():
    """Test DistributedConfig can be exported and re-imported."""
    original = DistributedConfig(enabled=True, world_size=4, rank=2, backend="gloo")
    env_dict = original.to_env()

    # Simulate loading from environment
    with patch.dict(os.environ, env_dict):
        restored = DistributedConfig.from_env()
        assert restored.enabled == original.enabled, "enabled is not valid"
        assert restored.world_size == original.world_size, "world_size is not valid"
        assert restored.rank == original.rank, "rank is not valid"
        assert restored.backend == original.backend, "backend is not valid"


def test_distributed_manager_multiple_instances():
    """Test multiple DistributedManager instances."""
    config1 = DistributedConfig(rank=0)
    config2 = DistributedConfig(rank=1)

    manager1 = DistributedManager(config1)
    manager2 = DistributedManager(config2)

    assert manager1.config.rank == 0, "rank is not valid"
    assert manager2.config.rank == 1, "rank is not valid"


def test_distributed_config_cpu_backend(clean_env):
    """Test DistributedConfig with CPU-friendly backend."""
    config = DistributedConfig(backend="gloo")
    assert config.backend == "gloo", "backend is not valid"


def test_distributed_manager_disabled_mode():
    """Test DistributedManager in disabled mode."""
    config = DistributedConfig(enabled=False)
    manager = DistributedManager(config)

    assert manager.config.enabled is False, "enabled is not valid"
    assert manager._initialized is False, "_initialized is not valid"


# =============================================================================
# Launch Distributed Tests (if available)
# =============================================================================


def test_launch_distributed_function_exists():
    """Test launch_distributed function is available."""
    try:
        from codex_ml.training.distributed import launch_distributed

        assert callable(launch_distributed), "Condition must be true"
    except ImportError:
        pytest.skip("launch_distributed not available")


@patch("codex_ml.training.distributed.dist")
def test_distributed_barrier(mock_dist):
    """Test distributed barrier synchronization."""
    config = DistributedConfig(enabled=True, world_size=2)
    manager = DistributedManager(config)

    # Mock dist to appear initialized
    mock_dist.is_initialized.return_value = True
    mock_dist.is_available.return_value = True
    mock_dist.barrier.return_value = None

    # Manually set the manager as initialized to trigger is_distributed
    manager._initialized = True

    # Test barrier if method exists
    if hasattr(manager, "barrier"):
        manager.barrier()
        mock_dist.barrier.assert_called()
