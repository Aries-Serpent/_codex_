"""Tests for device strategy module."""

from __future__ import annotations

import importlib
import types

import pytest

from codex_ml.training import device_strategy
from codex_ml.training.device_strategy import (
    DeviceConfig,
    DeviceMapper,
    get_device_config,
)

# Check if torch is available
try:
    import torch

    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False

pytestmark = pytest.mark.skipif(not _HAS_TORCH, reason="torch not available")


def _with_stub(monkeypatch: pytest.MonkeyPatch, *, cuda: bool, bf16: bool = False):
    """Create a stub torch module for testing."""
    module = importlib.reload(device_strategy)
    stub_cuda = types.SimpleNamespace(
        is_available=lambda: cuda,
        is_bf16_supported=lambda: bf16,
        get_device_capability=lambda: (8, 0) if bf16 else (7, 0),
    )
    stub_backends = types.SimpleNamespace(
        mps=types.SimpleNamespace(
            is_built=lambda: False,
            is_available=lambda: False,
        )
    )
    stub_device = types.SimpleNamespace
    stub = types.SimpleNamespace(
        float32=types.SimpleNamespace(dtype="fp32"),
        float16=types.SimpleNamespace(dtype="fp16"),
        bfloat16=types.SimpleNamespace(dtype="bf16"),
        cuda=stub_cuda,
        backends=stub_backends,
        device=stub_device,
    )
    monkeypatch.setattr(module, "torch", stub, raising=False)
    monkeypatch.setattr(module, "_HAS_TORCH", True, raising=False)
    module.DeviceMapper._STRATEGIES.clear()
    return module


class TestDeviceConfig:
    """Tests for DeviceConfig class."""

    def test_auto_detect_creates_valid_config(self):
        """Test that auto_detect returns a valid DeviceConfig."""
        config = DeviceConfig.auto_detect()

        assert config.device in ("cpu", "cuda", "mps") or config.device.startswith("cuda:")
        assert config.dtype is not None, "dtype must be initialized"
        assert isinstance(config.mixed_precision, bool)

    def test_auto_detect_on_cpu(self):
        """Test auto_detect behavior on CPU-only system."""
        config = DeviceConfig.auto_detect()

        # On CPU-only, should use float32 without mixed precision
        if config.device == "cpu":
            assert config.dtype == torch.float32, "dtype is not valid"
            assert config.mixed_precision is False, "mixed_precision is not valid"
            assert config.autocast_dtype is None, "autocast_dtype is not valid"

    @pytest.mark.requires_torch
    def test_apply_to_model(self):
        """Test applying config to a model."""
        model = torch.nn.Linear(10, 5)
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)

        model_result = config.apply_to_model(model)

        # Check device
        param = next(model_result.parameters())
        assert str(param.device) == "cpu", "Condition must be true"
        assert param.dtype == torch.float32, "dtype is not valid"

    @pytest.mark.requires_torch
    def test_apply_to_model_with_mixed_precision(self):
        """Test that mixed precision keeps model in float32."""
        model = torch.nn.Linear(10, 5)
        config = DeviceConfig(
            device="cpu",
            dtype=torch.float16,
            mixed_precision=True,
            autocast_dtype=torch.float16,
        )

        model_result = config.apply_to_model(model)

        # With mixed precision, model should stay in float32
        param = next(model_result.parameters())
        assert param.dtype == torch.float32, "dtype is not valid"

    @pytest.mark.requires_torch
    def test_apply_to_tensor(self):
        """Test applying config to a tensor."""
        tensor = torch.randn(5, 10)
        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)

        result = config.apply_to_tensor(tensor)

        assert str(result.device) == "cpu", "Result must not be empty"
        assert result.dtype == torch.float32, "Result must not be empty"

    @pytest.mark.requires_torch
    def test_apply_to_tensor_dtype_conversion(self):
        """Test tensor dtype conversion."""
        tensor = torch.randn(5, 10, dtype=torch.float32)
        config = DeviceConfig(device="cpu", dtype=torch.float16, mixed_precision=False)

        result = config.apply_to_tensor(tensor)

        assert result.dtype == torch.float16, "Result must not be empty"

    @pytest.mark.requires_torch
    def test_apply_to_model_fallback(self):
        """Test that model placement falls back to CPU on error."""

        class FailingModel(torch.nn.Linear):
            def to(self, *args, **kwargs):
                target = kwargs.get("device") or (args[0] if args else None)
                if isinstance(target, torch.device) and target.type == "cuda":
                    raise RuntimeError("no cuda available")
                return super().to(*args, **kwargs)

        model = FailingModel(2, 2)
        config = DeviceConfig(device="cuda", dtype=torch.float32)
        result = config.apply_to_model(model)
        assert next(result.parameters()).device.type == "cpu", "Result must not be empty"

    @pytest.mark.requires_torch
    def test_apply_to_model_invalid_device(self):
        """Test that invalid device raises ValueError."""
        model = torch.nn.Linear(2, 2)
        config = DeviceConfig(device="not-a-device", dtype=torch.float32)
        with pytest.raises(ValueError, match="invalid device specification"):
            config.apply_to_model(model)


def test_auto_detect_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test auto-detection on CPU-only system."""
    module = _with_stub(monkeypatch, cuda=False)
    cfg = module.DeviceConfig.auto_detect()
    assert cfg.device == "cpu", "device is not valid"
    assert not cfg.mixed_precision, "Condition must be true"


def test_auto_detect_cuda_prefers_bf16(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test auto-detection on CUDA system with bf16 support."""
    module = _with_stub(monkeypatch, cuda=True, bf16=True)
    cfg = module.DeviceConfig.auto_detect()
    assert cfg.device == "cuda", "device is not valid"
    assert cfg.mixed_precision, "Condition must be true"


@pytest.mark.requires_torch
@pytest.mark.parametrize("dtype", ["float16", "float32"])
def test_apply_to_tensor_changes_dtype(dtype: str) -> None:
    """Test that apply_to_tensor changes dtype correctly."""
    cfg = device_strategy.DeviceConfig(device="cpu", dtype=getattr(torch, dtype))
    tensor = torch.ones(2, dtype=torch.float32)
    result = cfg.apply_to_tensor(tensor)
    assert result.dtype == getattr(torch, dtype)
    assert result.device.type == "cpu", "Result must not be empty"


class TestDeviceMapper:
    """Tests for DeviceMapper registry."""

    def test_register_and_get_strategy(self):
        """Test registering and retrieving a strategy."""
        if not _HAS_TORCH:
            pytest.skip("torch not available")

        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        DeviceMapper.register_strategy("test_cpu", config)

        retrieved = DeviceMapper.get_strategy("test_cpu")
        assert retrieved.device == "cpu", "device is not valid"
        assert retrieved.dtype == torch.float32, "dtype is not valid"

    def test_get_nonexistent_strategy_raises(self):
        """Test that getting a nonexistent strategy raises KeyError."""
        with pytest.raises(KeyError, match="not registered"):
            DeviceMapper.get_strategy("nonexistent_strategy")

    def test_register_empty_name_raises(self):
        """Test that registering with empty name raises ValueError."""
        if not _HAS_TORCH:
            pytest.skip("torch not available")

        config = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        with pytest.raises(ValueError, match="must be non-empty"):
            DeviceMapper.register_strategy("", config)

    def test_list_strategies(self):
        """Test listing all registered strategies."""
        if not _HAS_TORCH:
            pytest.skip("torch not available")

        # Clear strategies
        DeviceMapper._STRATEGIES.clear()

        # Register a few strategies
        config1 = DeviceConfig(device="cpu", dtype=torch.float32, mixed_precision=False)
        config2 = DeviceConfig(device="cuda", dtype=torch.float16, mixed_precision=True)

        DeviceMapper.register_strategy("cpu_fp32", config1)
        DeviceMapper.register_strategy("cuda_fp16", config2)

        strategies = DeviceMapper.list_strategies()
        assert "cpu_fp32" in strategies, "Condition must be true"
        assert "cuda_fp16" in strategies, "Condition must be true"
        assert len(strategies) == 2, "Strategies must not be empty"


@pytest.mark.requires_torch
def test_get_device_config_auto_detect():
    """Test get_device_config with auto-detection."""
    config = get_device_config()
    assert config.device in ("cpu", "cuda", "mps") or config.device.startswith("cuda:")


@pytest.mark.requires_torch
def test_get_device_config_explicit():
    """Test get_device_config with explicit parameters."""
    config = get_device_config(device="cpu", dtype=torch.float32, mixed_precision=False)
    assert config.device == "cpu", "device is not valid"
    assert config.dtype == torch.float32, "dtype is not valid"
    assert config.mixed_precision is False, "mixed_precision is not valid"


@pytest.mark.requires_torch
def test_get_device_config_partial():
    """Test get_device_config with partial parameters."""
    config = get_device_config(device="cpu")
    assert config.device == "cpu", "device is not valid"
    assert config.dtype == torch.float32, "dtype is not valid"
    assert config.mixed_precision is False, "mixed_precision is not valid"
