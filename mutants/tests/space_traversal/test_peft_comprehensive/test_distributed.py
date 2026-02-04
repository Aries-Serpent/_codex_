"""Tests for distributed training module."""

import pytest
import torch
import os

from codex_ml.training.distributed import (
    DistributedConfig,
    DistributedManager,
    distributed_context,
)


class TestDistributedConfig:
    """Test DistributedConfig class."""

    def test_default_config(self):
        """Test default configuration."""
        config = DistributedConfig()
        assert config.enabled is False
        assert config.world_size == 1
        assert config.rank == 0
        assert config.backend == "nccl"

    def test_from_env(self, monkeypatch):
        """Test config from environment."""
        monkeypatch.setenv("WORLD_SIZE", "4")
        monkeypatch.setenv("RANK", "2")
        monkeypatch.setenv("LOCAL_RANK", "1")

        config = DistributedConfig.from_env()
        assert config.world_size == 4
        assert config.rank == 2
        assert config.local_rank == 1
        assert config.enabled is True  # Auto-enabled when world_size > 1

    def test_to_env(self):
        """Test exporting config to environment variables."""
        config = DistributedConfig(
            enabled=True,
            world_size=4,
            rank=2,
            local_rank=1,
        )

        env_vars = config.to_env()
        assert env_vars["WORLD_SIZE"] == "4"
        assert env_vars["RANK"] == "2"
        assert env_vars["LOCAL_RANK"] == "1"
        assert env_vars["DISTRIBUTED_ENABLED"] == "true"


class TestDistributedManager:
    """Test DistributedManager class."""

    def test_single_process(self):
        """Test manager in single process mode."""
        manager = DistributedManager()
        assert manager.is_main_process is True
        assert manager.is_distributed is False

    def test_device_selection(self):
        """Test device selection."""
        manager = DistributedManager()
        device = manager.device
        if torch.cuda.is_available():
            assert device.type == "cuda"
        else:
            assert device.type == "cpu"

    def test_context_manager(self):
        """Test distributed context manager."""
        with distributed_context() as manager:
            assert manager is not None
            assert manager.is_main_process is True

    def test_setup_without_distributed(self):
        """Test setup when distributed is disabled."""
        config = DistributedConfig(enabled=False)
        manager = DistributedManager(config)

        result = manager.setup()
        assert result is False
        assert manager.is_distributed is False

    def test_cleanup_no_op(self):
        """Test cleanup when not initialized."""
        manager = DistributedManager()
        # Should not raise an error
        manager.cleanup()


class TestModelWrapping:
    """Test model wrapping functionality."""

    def test_wrap_model_single(self):
        """Test model wrapping in single process."""
        model = torch.nn.Linear(10, 5)
        manager = DistributedManager()

        wrapped = manager.wrap_model(model)
        assert isinstance(wrapped, torch.nn.Linear)
        # Should be moved to device but not wrapped in DDP
        assert wrapped.weight.device.type in ["cuda", "cpu"]

    def test_wrap_model_preserves_parameters(self):
        """Test that wrapping preserves model parameters."""
        model = torch.nn.Linear(10, 5)
        manager = DistributedManager()

        original_weight = model.weight.data.clone()
        wrapped = manager.wrap_model(model)

        # Parameters should be preserved (accounting for device transfer)
        assert torch.allclose(wrapped.weight.data.cpu(), original_weight, rtol=1e-5)


class TestDataLoaderWrapping:
    """Test dataloader wrapping functionality."""

    def test_wrap_dataloader_single(self):
        """Test dataloader wrapping in single process."""
        dataset = torch.utils.data.TensorDataset(torch.randn(100, 10), torch.randint(0, 2, (100,)))

        manager = DistributedManager()
        dataloader = manager.wrap_dataloader(dataset, batch_size=32)

        assert isinstance(dataloader, torch.utils.data.DataLoader)
        assert dataloader.batch_size == 32

    def test_wrap_dataloader_kwargs(self):
        """Test dataloader wrapping with additional kwargs."""
        dataset = torch.utils.data.TensorDataset(torch.randn(100, 10), torch.randint(0, 2, (100,)))

        manager = DistributedManager()
        dataloader = manager.wrap_dataloader(dataset, batch_size=16, num_workers=2, shuffle=True)

        assert dataloader.batch_size == 16
        assert dataloader.num_workers == 2


class TestDistributedOperations:
    """Test distributed operations."""

    def test_barrier_single_process(self):
        """Test barrier in single process mode."""
        manager = DistributedManager()
        # Should not raise an error
        manager.barrier()

    def test_all_reduce_single_process(self):
        """Test all_reduce in single process mode."""
        manager = DistributedManager()
        tensor = torch.tensor([1.0, 2.0, 3.0])

        result = manager.all_reduce(tensor)
        assert torch.equal(result, tensor)

    def test_broadcast_single_process(self):
        """Test broadcast in single process mode."""
        manager = DistributedManager()
        tensor = torch.tensor([1.0, 2.0, 3.0])

        result = manager.broadcast(tensor, src=0)
        assert torch.equal(result, tensor)


class TestLaunchScript:
    """Test launch script functionality."""

    def test_launch_script_exists(self):
        """Test that launch script exists."""
        from pathlib import Path

        script_path = Path("scripts/launch_distributed.py")
        assert script_path.exists()
        assert script_path.is_file()

    def test_launch_script_help(self):
        """Test launch script help output."""
        import subprocess

        result = subprocess.run(
            ["python", "scripts/launch_distributed.py", "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Launch distributed training" in result.stdout


@pytest.mark.skipif(not os.environ.get("RAY_AVAILABLE"), reason="Ray not installed")
class TestRayIntegration:
    """Test Ray integration (optional)."""

    def test_ray_module_imports(self):
        """Test that Ray module can be imported."""
        from codex_ml.training import ray_distributed

        assert hasattr(ray_distributed, "check_ray_available")
        assert hasattr(ray_distributed, "RAY_AVAILABLE")

    def test_check_ray_available(self):
        """Test Ray availability check."""
        from codex_ml.training.ray_distributed import check_ray_available

        # Should return True if Ray is installed, False otherwise
        result = check_ray_available()
        assert isinstance(result, bool)
