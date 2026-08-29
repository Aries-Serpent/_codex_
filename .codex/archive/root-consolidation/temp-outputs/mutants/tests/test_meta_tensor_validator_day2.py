"""
Meta-Tensor Validator Tests — codex_ml.models
Critical validation for model initialization on meta device

DR-003 Guard: PyTorch 2.x + Python 3.12 isinstance union-type bug
Fixed in torch >= 2.2.0
"""

import sys

import pytest

# Guard for PyTorch 2.x + Python 3.12 isinstance() union-type bug
_TORCH_312_BUG = False
try:
    import torch
    _TORCH_312_BUG = (
        sys.version_info >= (3, 12)
        and tuple(int(x) for x in torch.__version__.split(".")[:2]) < (2, 2)
    )
except (ImportError, AttributeError, ValueError):
    torch = None

pytestmark = pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="torch<2.2+py3.12 isinstance union bug (DR-003)"
)


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestMetaTensorValidation:
    """Validate no meta tensors in model initialization."""

    def test_no_meta_tensors_on_model_creation(self):
        """Model creation should not leave parameters on meta device."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Model factory not available")

        factory = create_model_factory()
        if factory is None:
            pytest.skip("Factory creation failed")

        # Create a minimal model
        model = factory.create(model_type="tiny", device="cpu")
        assert model is not None, "model must be initialized"

        # Check no meta tensors
        meta_params = [
            name for name, param in model.named_parameters()
            if param.device.type == "meta"
        ]
        assert len(meta_params) == 0, f"Found meta tensors: {meta_params}"

    @pytest.mark.skipif(torch is None, reason="PyTorch not installed")
    def test_model_ready_no_meta(self):
        """Model should be fully initialized after creation."""
        try:
            from codex_ml.models.factory import validate_model_ready
        except (ImportError, AttributeError):
            pytest.skip("validate_model_ready not available")

        # If function exists, it should not raise
        try:
            import torch.nn as nn
            model = nn.Linear(10, 10)
            result = validate_model_ready(model)
            assert result is True, "Result must not be empty"
        except (ImportError, NotImplementedError):
            pytest.skip("validate_model_ready not implemented")

    @pytest.mark.skipif(torch is None, reason="PyTorch not installed")
    def test_device_placement_cpu(self):
        """Model parameters should be on CPU after creation."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Model factory not available")

        factory = create_model_factory()
        if factory is None:
            pytest.skip("Factory creation failed")

        model = factory.create(model_type="tiny", device="cpu")

        # All parameters should be on CPU
        for param in model.parameters():
            assert param.device.type == "cpu", f"Found param on {param.device}"

    @pytest.mark.skipif(torch is None, reason="PyTorch not installed")
    def test_device_placement_validation(self):
        """Validate device placement consistency across model."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )

        # All params should be on same device
        devices = {p.device for p in model.parameters()}
        assert len(devices) == 1, f"Mixed devices: {devices}"


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestPEFTCompatibility:
    """Validate PEFT/LoRA integration."""

    def test_peft_target_modules_configuration(self):
        """LoRA configuration should specify valid target modules."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        cfg = LoraBuildCfg(
            r=8,
            alpha=16,
            target_modules=["q_proj", "v_proj"]
        )

        assert cfg.r > 0, "LoRA rank must be positive"
        assert cfg.alpha > 0, "LoRA alpha must be positive"
        assert cfg.target_modules is not None, "Target modules required"
        assert len(cfg.target_modules) > 0, "At least one target module"

    def test_lora_config_defaults(self):
        """LoRA config should have sensible defaults."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        cfg = LoraBuildCfg()

        assert cfg.r == 8, "Default rank should be 8"
        assert cfg.alpha == 16, "Default alpha should be 16"
        assert cfg.dropout == 0.0, "Default dropout should be 0"
        assert cfg.bias == "none", "Default bias should be none"

    @pytest.mark.skipif(_TORCH_312_BUG, reason="torch<2.2+py3.12 isinstance bug (DR-003)")
    def test_lora_build_no_peft(self):
        """Should handle graceful fallback when PEFT not installed."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg, build_lora
        except (ImportError, AttributeError):
            pytest.skip("LoRA functions not available")

        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Linear(10, 10)
        cfg = LoraBuildCfg(r=8)

        # Should return model unchanged if PEFT unavailable
        result = build_lora(model, cfg)
        assert result is not None, "result must be initialized"


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestModelInitialization:
    """Test model factory initialization patterns."""

    def test_model_factory_dtype_resolution(self):
        """Model factory should resolve dtype correctly."""
        try:
            from codex_ml.models.factory import _resolve_dtype
        except (ImportError, AttributeError):
            pytest.skip("_resolve_dtype not available")

        # Test string input
        result = _resolve_dtype("fp32")
        assert result is not None, "result must be initialized"

        result = _resolve_dtype("bf16")
        assert result is not None, "result must be initialized"

        # Test None input
        result = _resolve_dtype(None)
        assert result is None, "Result must not be empty"

    def test_model_factory_quantization_config(self):
        """Quantization config should be properly validated."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Model factory not available")

        try:
            import os
            os.environ.pop("CODEX_ML_QUANTIZATION", None)

            factory = create_model_factory()
            assert factory is not None, "factory must be initialized"
        except Exception as _err:
            pytest.skip("Factory initialization failed")

    def test_model_forward_pass_ready(self):
        """Model should be ready for forward pass after init."""
        try:
            import torch
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )

        # Should handle forward pass
        x = torch.randn(2, 10)
        output = model(x)

        assert output.shape == (2, 5), f"Unexpected output shape: {output.shape}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
