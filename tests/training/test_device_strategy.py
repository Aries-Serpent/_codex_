"""Tests for device strategy module."""

from __future__ import annotations

import pytest

from codex_ml.training.device_strategy import (
    DeviceConfig,
    DeviceMapper,
    get_device_config,
)
from codex_ml.utils.optional import optional_import

torch, _HAS_TORCH = optional_import("torch")

pytestmark = pytest.mark.skipif(not _HAS_TORCH, reason="torch not available")


class TestDeviceConfig:
    """Tests for DeviceConfig class."""

    def test_auto_detect_creates_valid_config(self):
        """Test that auto_detect returns a valid DeviceConfig."""
        config = DeviceConfig.auto_detect()
        
        assert config.device in ("cpu", "cuda", "mps") or config.device.startswith("cuda:")
        assert config.dtype is not None
        assert isinstance(config.mixed_precision, bool)

    def test_auto_detect_on_cpu(self):
        """Test auto_detect behavior on CPU-only system."""
        # This test will pass on any system, but validates CPU path
        config = DeviceConfig.auto_detect()
        
        # On CPU-only, should use float32 without mixed precision
        if config.device == "cpu":
            assert config.dtype == torch.float32
            assert config.mixed_precision is False
            assert config.autocast_dtype is None

    def test_apply_to_model(self):
        """Test applying config to a model."""
        model = torch.nn.Linear(10, 5)
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        
        model_result = config.apply_to_model(model)
        
        # Check device
        param = next(model_result.parameters())
        assert str(param.device) == "cpu"
        assert param.dtype == torch.float32

    def test_apply_to_model_with_mixed_precision(self):
        """Test that mixed precision keeps model in float32."""
        model = torch.nn.Linear(10, 5)
        config = DeviceConfig(
            device="cpu", dtype=torch.float16, mixed_precision=True, autocast_dtype=torch.float16
        )
        
        model_result = config.apply_to_model(model)
        
        # With mixed precision, model should stay in float32
        param = next(model_result.parameters())
        assert param.dtype == torch.float32

    def test_apply_to_tensor(self):
        """Test applying config to a tensor."""
        tensor = torch.randn(5, 10)
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        
        result = config.apply_to_tensor(tensor)
        
        assert str(result.device) == "cpu"
        assert result.dtype == torch.float32

    def test_apply_to_tensor_dtype_conversion(self):
        """Test tensor dtype conversion."""
        tensor = torch.randn(5, 10, dtype=torch.float32)
        config = DeviceConfig(device="cpu", dtype=torch.float16, mixed_precision=False)
        
        result = config.apply_to_tensor(tensor)
        
        assert result.dtype == torch.float16

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_apply_to_model_cuda(self):
        """Test applying config to model on CUDA."""
        model = torch.nn.Linear(10, 5)
        config = DeviceConfig(device="cuda", dtype=torch.float32, mixed_precision=False)
        
        model_result = config.apply_to_model(model)
        
        param = next(model_result.parameters())
        assert param.device.type == "cuda"

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_auto_detect_cuda(self):
        """Test auto_detect on CUDA system."""
        config = DeviceConfig.auto_detect()
        
        # On CUDA system, should use cuda
        assert config.device == "cuda"
        # Should use mixed precision
        assert config.mixed_precision is True
        # Should use fp16 or bf16
        assert config.dtype in (torch.float16, torch.bfloat16)

    def test_get_autocast_context(self):
        """Test autocast context creation."""
        config = DeviceConfig(
            device="cuda", dtype=torch.float16, mixed_precision=True, autocast_dtype=torch.float16
        )
        
        ctx = config.get_autocast_context(enabled=True)
        
        # Should return a context manager
        assert hasattr(ctx, "__enter__")
        assert hasattr(ctx, "__exit__")

    def test_get_autocast_context_disabled(self):
        """Test autocast context when disabled."""
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        
        ctx = config.get_autocast_context(enabled=False)
        
        # Should return nullcontext
        assert hasattr(ctx, "__enter__")
        assert hasattr(ctx, "__exit__")

    def test_to_dict(self):
        """Test dictionary serialization."""
        config = DeviceConfig(
            device="cuda",
            dtype=torch.float16,
            mixed_precision=True,
            autocast_dtype=torch.float16,
        )
        
        result = config.to_dict()
        
        assert result["device"] == "cuda"
        assert "float16" in result["dtype"].lower()
        assert result["mixed_precision"] is True
        assert result["autocast_dtype"] is not None


class TestDeviceMapper:
    """Tests for DeviceMapper registry."""

    def setup_method(self):
        """Clear strategies before each test."""
        DeviceMapper.clear_strategies()

    def test_register_and_get_strategy(self):
        """Test registering and retrieving a strategy."""
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        DeviceMapper.register_strategy("test_cpu", config)
        
        retrieved = DeviceMapper.get_strategy("test_cpu")
        
        assert retrieved.device == "cpu"
        assert retrieved.dtype == torch.float32

    def test_get_nonexistent_strategy_raises_error(self):
        """Test that getting a non-existent strategy raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            DeviceMapper.get_strategy("nonexistent")

    def test_list_strategies(self):
        """Test listing all strategies."""
        config1 = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        config2 = DeviceConfig(device="cuda", dtype=torch.float16, mixed_precision=True)
        
        DeviceMapper.register_strategy("cpu", config1)
        DeviceMapper.register_strategy("cuda", config2)
        
        strategies = DeviceMapper.list_strategies()
        
        assert "cpu" in strategies
        assert "cuda" in strategies
        assert len(strategies) == 2

    def test_clear_strategies(self):
        """Test clearing all strategies."""
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        DeviceMapper.register_strategy("test", config)
        
        DeviceMapper.clear_strategies()
        
        assert len(DeviceMapper.list_strategies()) == 0


class TestGetDeviceConfig:
    """Tests for get_device_config convenience function."""

    def setup_method(self):
        """Setup default strategies."""
        DeviceMapper.clear_strategies()
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        DeviceMapper.register_strategy("cpu_fp32", config)

    def test_get_device_config_by_strategy(self):
        """Test getting config by strategy name."""
        config = get_device_config(strategy="cpu_fp32")
        
        assert config.device == "cpu"
        assert config.dtype == torch.float32

    def test_get_device_config_with_explicit_device(self):
        """Test overriding device explicitly."""
        config = get_device_config(strategy="cpu_fp32", device="cuda")
        
        assert config.device == "cuda"
        # dtype should come from strategy
        assert config.dtype == torch.float32

    def test_get_device_config_with_explicit_dtype(self):
        """Test overriding dtype explicitly."""
        config = get_device_config(strategy="cpu_fp32", dtype=torch.float16)
        
        assert config.device == "cpu"
        assert config.dtype == torch.float16

    def test_get_device_config_with_explicit_mixed_precision(self):
        """Test overriding mixed_precision explicitly."""
        config = get_device_config(strategy="cpu_fp32", mixed_precision=True)
        
        assert config.mixed_precision is True

    def test_get_device_config_auto_default(self):
        """Test that no args uses auto-detect."""
        config = get_device_config()
        
        # Should return auto-detected config
        assert config.device is not None
        assert config.dtype is not None

    def test_get_device_config_invalid_strategy_falls_back(self):
        """Test that invalid strategy falls back to auto-detect."""
        with pytest.warns(UserWarning, match="not found"):
            config = get_device_config(strategy="invalid_strategy")
        
        # Should still return a valid config
        assert config.device is not None


class TestIntegration:
    """Integration tests for device strategy."""

    def test_full_workflow(self):
        """Test a complete workflow with device config."""
        # Create model
        model = torch.nn.Linear(10, 5)
        
        # Get auto-detected config
        config = DeviceConfig.auto_detect()
        
        # Apply to model
        model = config.apply_to_model(model)
        
        # Create sample tensor
        x = torch.randn(2, 10)
        x = config.apply_to_tensor(x)
        
        # Forward pass
        with config.get_autocast_context(enabled=config.mixed_precision):
            output = model(x)
        
        # Verify output shape
        assert output.shape == (2, 5)

    def test_dtype_consistency(self):
        """Test that model and tensor dtypes are consistent."""
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        
        model = torch.nn.Linear(10, 5)
        model = config.apply_to_model(model)
        
        tensor = torch.randn(2, 10)
        tensor = config.apply_to_tensor(tensor)
        
        # Get dtypes
        model_dtype = next(model.parameters()).dtype
        tensor_dtype = tensor.dtype
        
        assert model_dtype == tensor_dtype == torch.float32

    def test_device_mismatch_error_handling(self):
        """Test that we can handle device mismatches gracefully."""
        # This test just verifies the pattern; actual mismatch would error in torch
        config_cpu = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        
        model = torch.nn.Linear(10, 5)
        model = config_cpu.apply_to_model(model)
        
        x = torch.randn(2, 10)
        x = config_cpu.apply_to_tensor(x)
        
        # Should work fine
        output = model(x)
        assert output.shape == (2, 5)
