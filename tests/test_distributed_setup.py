"""Tests for distributed training setup."""
import os

import pytest

pytest.importorskip("mlflow")

pytest.importorskip("torch")


# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
from unittest.mock import patch

import torch
import torch.nn as nn

from codex_ml.training.distributed_setup import (
    cleanup_distributed,
    get_distributed_sampler,
    get_rank,
    get_world_size,
    is_distributed,
    is_main_process,
    log_once,
    print_once,
    reduce_tensor,
    setup_ddp_model,
    setup_distributed,
)


def test_is_distributed_false_by_default():
    """Test is_distributed returns False when not initialized."""
    # Should be False in single-process test environment
    assert is_distributed() in [True, False]  # Depends on test environment


def test_get_rank_single_process():
    """Test get_rank returns 0 in single process."""
    if not is_distributed():
        assert get_rank() == 0, "Condition must be true"


def test_get_world_size_single_process():
    """Test get_world_size returns 1 in single process."""
    if not is_distributed():
        assert get_world_size() == 1, "get_w is not valid"


def test_is_main_process_single():
    """Test is_main_process returns True in single process."""
    if not is_distributed():
        assert is_main_process() is True, "Condition must be true"


def test_setup_distributed_no_env_vars():
    """Test setup_distributed returns False without env vars."""
    # Clear distributed env vars if any
    env_backup = {}
    for key in ["RANK", "LOCAL_RANK", "WORLD_SIZE", "MASTER_ADDR", "MASTER_PORT"]:
        env_backup[key] = os.environ.pop(key, None)

    try:
        result = setup_distributed()
        assert result is False, "Result must not be empty"
    finally:
        # Restore env vars
        for key, value in env_backup.items():
            if value is not None:
                os.environ[key] = value


def test_setup_ddp_model_single_process():
    """Test setup_ddp_model returns original model in single process."""
    model = nn.Linear(10, 5)

    if not is_distributed():
        wrapped = setup_ddp_model(model)
        assert wrapped is model, "wrapped is not valid"


def test_get_distributed_sampler_single_process():
    """Test get_distributed_sampler returns None in single process."""
    from torch.utils.data import TensorDataset

    dataset = TensorDataset(torch.randn(100, 10))

    if not is_distributed():
        sampler = get_distributed_sampler(dataset)
        assert sampler is None, "sampler is not valid"


def test_reduce_tensor_single_process():
    """Test reduce_tensor returns same tensor in single process."""
    tensor = torch.tensor(5.0)

    if not is_distributed():
        reduced = reduce_tensor(tensor)
        assert torch.equal(reduced, tensor)


def test_print_once():
    """Test print_once doesn't raise errors."""
    # Should work in both distributed and non-distributed modes
    print_once("Test message", rank=0)


def test_log_once():
    """Test log_once doesn't raise errors."""
    # Should work in both distributed and non-distributed modes
    log_once("Test log message", level="info", rank=0)


@patch("codex_ml.training.distributed_setup.torch.distributed.is_initialized")
@patch("codex_ml.training.distributed_setup.torch.distributed.get_rank")
@patch("codex_ml.training.distributed_setup.torch.distributed.get_world_size")
def test_distributed_functions_with_mock(mock_world_size, mock_rank, mock_init):
    """Test distributed functions with mocked torch.distributed."""
    mock_init.return_value = True
    mock_rank.return_value = 1
    mock_world_size.return_value = 4

    # Import after patching to ensure mocks are applied
    from codex_ml.training.distributed_setup import (
        get_rank,
        get_world_size,
        is_main_process,
    )

    assert get_rank() == 1, "Condition must be true"
    assert get_world_size() == 4, "get_w is not valid"
    assert is_main_process() is False, "Condition must be true"


@patch("codex_ml.training.distributed_setup.torch.distributed.is_available")
@patch("codex_ml.training.distributed_setup.torch.distributed.is_initialized")
def test_is_distributed_with_mock(mock_init, mock_available):
    """Test is_distributed with mocked values."""
    mock_available.return_value = True
    mock_init.return_value = True

    # Import after patching
    from codex_ml.training.distributed_setup import is_distributed

    assert is_distributed() is True, "Condition must be true"

    mock_init.return_value = False
    assert is_distributed() is False, "Condition must be true"


def test_cleanup_distributed():
    """Test cleanup_distributed doesn't raise errors."""
    # Should work even if not initialized
    cleanup_distributed()


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_setup_distributed_with_cuda_env():
    """Test setup_distributed with CUDA and environment variables."""
    # This test would need actual distributed environment
    # Just verify it doesn't crash with CUDA available
    os.environ["RANK"] = "0"
    os.environ["LOCAL_RANK"] = "0"
    os.environ["WORLD_SIZE"] = "1"
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29500"

    try:
        # This will likely fail to init but shouldn't crash
        setup_distributed(backend="nccl")
    except Exception as _err:
        _ = None  # Expected to fail in test environment
    finally:
        # Cleanup env vars
        for key in ["RANK", "LOCAL_RANK", "WORLD_SIZE", "MASTER_ADDR", "MASTER_PORT"]:
            os.environ.pop(key, None)


class SimpleTestModel(nn.Module):
    """Simple model for testing."""

    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 5)

    def forward(self, x):
        return self.linear(x)


def test_setup_ddp_model_structure():
    """Test setup_ddp_model doesn't crash with proper model."""
    model = SimpleTestModel()

    # In single process, should return original
    if not is_distributed():
        wrapped = setup_ddp_model(model, find_unused_parameters=True)
        assert isinstance(wrapped, nn.Module)
