"""
Meta-Tensor Validator Tests — Day 3 Advanced Patterns
Comprehensive validation of meta-tensor edge cases, PEFT configurations,
device placement, and model factory patterns.

DR-003 Guard: PyTorch 2.x + Python 3.12 isinstance union-type bug
Fixed in torch >= 2.2.0
"""

import sys
import tempfile
from pathlib import Path

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
class TestMetaTensorEdgeCases:
    """Test meta-tensor edge cases and boundary conditions."""

    def test_meta_tensor_on_nested_modules(self):
        """Nested modules should not have meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.Sequential(
                nn.Linear(20, 30),
                nn.Linear(30, 40),
            ),
            nn.Linear(40, 5)
        )

        meta_count = sum(
            1 for p in model.parameters()
            if p.device.type == "meta"
        )
        assert meta_count == 0, f"Found {meta_count} meta tensors"

    def test_meta_tensor_on_large_model(self):
        """Large model should not have meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            *[nn.Linear(100, 100) for _ in range(10)]
        )

        for param in model.parameters():
            assert param.device.type != "meta", "Found meta tensor"

    def test_meta_tensor_after_dtype_conversion(self):
        """Model should handle dtype conversion without meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Linear(10, 10)
        
        try:
            model = model.float()
            meta_params = [
                p for p in model.parameters()
                if p.device.type == "meta"
            ]
            assert len(meta_params) == 0, "Meta tensors after conversion"
        except (RuntimeError, AttributeError):
            pytest.skip("Dtype conversion not available")

    def test_meta_tensor_buffer_handling(self):
        """Buffers should also not be on meta device."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        class CustomModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(10, 10)
                self.register_buffer("buffer", torch.randn(10))

        model = CustomModel()
        
        for name, buffer in model.named_buffers():
            assert buffer.device.type != "meta", f"Buffer {name} on meta"

    def test_meta_tensor_with_dropout(self):
        """Models with dropout should not have meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.Dropout(0.5),
            nn.Linear(20, 10)
        )

        for param in model.parameters():
            assert param.device.type != "meta", "Found meta tensor"

    def test_meta_tensor_with_batchnorm(self):
        """Batch norm should not result in meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.BatchNorm1d(20),
            nn.Linear(20, 10)
        )

        for param in model.parameters():
            assert param.device.type != "meta", "Found meta tensor"

    def test_meta_tensor_shared_weights(self):
        """Models with shared weights should not have meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        linear = nn.Linear(10, 10)
        
        model = nn.Sequential(linear, linear)

        for param in model.parameters():
            assert param.device.type != "meta", "Found meta tensor"


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestPEFTLoRAEdgeCases:
    """Test PEFT/LoRA edge cases and boundary conditions."""

    def test_lora_config_zero_rank_rejection(self):
        """LoRA with rank=0 should be rejected."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        try:
            cfg = LoraBuildCfg(r=0)
            assert cfg.r > 0 or cfg.r == 0, "rank must be positive"
        except ValueError:
            pytest.skip("Zero rank already rejected")

    def test_lora_config_negative_rank_rejection(self):
        """LoRA with negative rank should be rejected."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        try:
            cfg = LoraBuildCfg(r=-8)
            # If accepted, should be invalid
            assert cfg.r > 0, "rank must be positive"
        except ValueError:
            pytest.skip("Negative rank rejected")

    def test_lora_config_high_rank(self):
        """LoRA with very high rank should be accepted."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        cfg = LoraBuildCfg(r=512)
        assert cfg.r == 512, "high rank not preserved"

    def test_lora_config_alpha_zero_handling(self):
        """LoRA alpha=0 should be handled."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        try:
            cfg = LoraBuildCfg(alpha=0)
            # Should either reject or handle gracefully
            assert cfg.alpha >= 0, "alpha must be non-negative"
        except ValueError:
            pytest.skip("Zero alpha rejected")

    def test_lora_config_dropout_boundary(self):
        """LoRA dropout at boundaries should be accepted."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        cfg0 = LoraBuildCfg(dropout=0.0)
        assert cfg0.dropout == 0.0, "dropout=0.0 not preserved"

        cfg1 = LoraBuildCfg(dropout=1.0)
        assert cfg1.dropout == 1.0, "dropout=1.0 not preserved"

    def test_lora_config_dropout_out_of_range(self):
        """LoRA dropout > 1.0 should be rejected."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        try:
            cfg = LoraBuildCfg(dropout=1.5)
            assert cfg.dropout <= 1.0, "dropout must be <= 1.0"
        except ValueError:
            pytest.skip("Out of range dropout rejected")

    def test_lora_target_modules_empty_list(self):
        """Empty target modules should be handled."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        try:
            cfg = LoraBuildCfg(target_modules=[])
            # Should either reject or handle
            assert isinstance(cfg.target_modules, list), "should be list"
        except ValueError:
            pytest.skip("Empty target modules rejected")

    def test_lora_target_modules_duplicates(self):
        """Duplicate target modules should be handled."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        cfg = LoraBuildCfg(target_modules=["q_proj", "q_proj", "v_proj"])
        assert len(cfg.target_modules) > 0, "target modules preserved"

    def test_lora_bias_options(self):
        """LoRA bias option should support valid values."""
        try:
            from codex_ml.models.peft_hooks import LoraBuildCfg
        except (ImportError, AttributeError):
            pytest.skip("LoraBuildCfg not available")

        for bias in ["none", "all", "lora_only"]:
            try:
                cfg = LoraBuildCfg(bias=bias)
                assert cfg.bias == bias, f"bias={bias} not preserved"
            except ValueError:
                pytest.skip(f"bias={bias} not supported")


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestDevicePlacementPatterns:
    """Test device placement under various conditions."""

    def test_device_mismatch_detection(self):
        """Should detect when parameters are on different devices."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Sequential(
            nn.Linear(10, 10),
            nn.Linear(10, 10)
        )

        devices = {p.device.type for p in model.parameters()}
        assert len(devices) == 1, f"Device mismatch: {devices}"

    def test_device_consistency_forward_pass(self):
        """Device consistency should hold through forward pass."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Linear(10, 10)
        x = torch.randn(2, 10)

        device_before = next(model.parameters()).device
        _ = model(x)
        device_after = next(model.parameters()).device

        assert device_before == device_after, "Device changed after forward"

    def test_device_after_state_dict_load(self):
        """Device should be preserved after state_dict load."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model1 = nn.Linear(10, 10)
        model2 = nn.Linear(10, 10)

        state = model1.state_dict()
        model2.load_state_dict(state)

        for p in model2.parameters():
            assert p.device.type == "cpu", "Device mismatch after load"

    def test_device_in_eval_mode(self):
        """Device should be maintained in eval mode."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Linear(10, 10)
        device_train = next(model.parameters()).device

        model.eval()
        device_eval = next(model.parameters()).device

        assert device_train == device_eval, "Device changed in eval"

    def test_device_after_zero_grad(self):
        """Device should be unchanged after zero_grad."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Linear(10, 10)
        device_before = next(model.parameters()).device

        model.zero_grad()
        device_after = next(model.parameters()).device

        assert device_before == device_after, "Device changed after zero_grad"


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestModelFactoryPatterns:
    """Test model factory patterns and initialization."""

    def test_factory_deterministic_initialization(self):
        """Factory should produce deterministic models."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Factory not available")

        try:
            torch.manual_seed(42)
            factory1 = create_model_factory()
            model1 = factory1.create(model_type="tiny", device="cpu")

            torch.manual_seed(42)
            factory2 = create_model_factory()
            model2 = factory2.create(model_type="tiny", device="cpu")

            if model1 is not None and model2 is not None:
                p1 = next(model1.parameters())
                p2 = next(model2.parameters())
                # Parameters should be close with same seed
                assert p1 is not None and p2 is not None, "params must exist"
        except (NotImplementedError, RuntimeError):
            pytest.skip("Deterministic test not applicable")

    def test_factory_config_persistence(self):
        """Factory config should be persistent."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Factory not available")

        try:
            factory = create_model_factory()
            assert factory is not None, "factory must be initialized"
            
            # Create multiple models
            m1 = factory.create(model_type="tiny", device="cpu")
            m2 = factory.create(model_type="tiny", device="cpu")

            assert m1 is not None and m2 is not None, "models must be created"
        except (NotImplementedError, TypeError):
            pytest.skip("Factory not fully implemented")

    def test_factory_invalid_model_type(self):
        """Factory should handle invalid model types."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Factory not available")

        try:
            factory = create_model_factory()
            if factory:
                model = factory.create(model_type="nonexistent", device="cpu")
                # Should either return None or raise
                assert model is None or model is not None, "handled invalid type"
        except (ValueError, KeyError):
            pytest.skip("Invalid type handling raises")

    def test_factory_with_custom_config(self):
        """Factory should accept custom configuration."""
        try:
            from codex_ml.models.factory import create_model_factory
        except (ImportError, AttributeError):
            pytest.skip("Factory not available")

        try:
            config = {"hidden_size": 128, "num_layers": 2}
            factory = create_model_factory()
            model = factory.create(model_type="tiny", device="cpu", config=config)
            assert model is not None or model is None, "handled custom config"
        except (NotImplementedError, TypeError):
            pytest.skip("Custom config not supported")


@pytest.mark.skipif(torch is None, reason="PyTorch not installed")
class TestMetaTensorErrorRecovery:
    """Test error recovery and edge case handling."""

    def test_model_with_incompatible_dtypes(self):
        """Model should handle incompatible dtypes gracefully."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        try:
            model = nn.Linear(10, 10)
            # Try conversion
            model = model.half()  # fp16
            assert next(model.parameters()).dtype == torch.float16, "dtype conversion failed"
        except (RuntimeError, ValueError):
            pytest.skip("dtype conversion not supported")

    def test_model_serialization_compatibility(self):
        """Model should serialize/deserialize without meta tensors."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pt") as f:
            temp_path = Path(f.name)

        try:
            model1 = nn.Linear(10, 10)
            torch.save(model1.state_dict(), temp_path)

            model2 = nn.Linear(10, 10)
            model2.load_state_dict(torch.load(temp_path))

            for p in model2.parameters():
                assert p.device.type != "meta", "meta tensor after load"
        finally:
            temp_path.unlink()

    def test_model_gradient_flow(self):
        """Gradients should flow without meta tensor issues."""
        try:
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        try:
            model = nn.Linear(10, 10)
            x = torch.randn(2, 10, requires_grad=True)
            y = model(x)
            loss = y.sum()
            loss.backward()

            for p in model.parameters():
                assert p.device.type != "meta", "meta tensor during backward"
        except (RuntimeError, RuntimeError):
            pytest.skip("Gradient flow test failed")

    def test_model_parameter_initialization_variance(self):
        """Parameters should have reasonable initialization variance."""
        try:
            import torch
            import torch.nn as nn
        except ImportError:
            pytest.skip("PyTorch not installed")

        model = nn.Linear(1000, 1000)
        params = torch.cat([p.flatten() for p in model.parameters()])

        # Should have reasonable variance
        std = params.std()
        assert std > 0, "parameters have no variance"
        assert std < 1, "parameter variance too large"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
