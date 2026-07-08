"""Comprehensive tests for modeling capability.

Tests cover:
- Model factory patterns
- Device/dtype matrix
- PEFT/LoRA integration
- Model card provenance
- Quantization support
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Model Factory Tests ---


class ModelConfig:
    """Model configuration."""

    def __init__(
        self,
        name: str,
        hidden_size: int = 768,
        num_layers: int = 12,
        num_heads: int = 12,
        vocab_size: int = 50257,
    ):
        self.name = name
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.vocab_size = vocab_size

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "num_heads": self.num_heads,
            "vocab_size": self.vocab_size,
        }


class ModelFactory:
    """Factory for creating models."""

    _registry: dict[str, type] = {}

    @classmethod
    def register(cls, name: str, model_cls: type) -> None:
        """Register a model class."""
        cls._registry[name] = model_cls

    @classmethod
    def create(cls, config: ModelConfig) -> Any:
        """Create model from config."""
        if config.name not in cls._registry:
            raise ValueError(f"Unknown model: {config.name}")
        return cls._registry[config.name](config)

    @classmethod
    def list_models(cls) -> list[str]:
        """List registered models."""
        return list(cls._registry.keys())


class TestModelFactory:
    """Tests for model factory."""

    def test_register_model(self):
        """Register model class."""

        class DummyModel:
            def __init__(self, config):
                self.config = config

        ModelFactory.register("dummy", DummyModel)
        assert "dummy" in ModelFactory.list_models(), "Condition must be true"

    def test_create_model(self):
        """Create model from factory."""

        class TestModel:
            def __init__(self, config):
                self.config = config

        ModelFactory.register("test_model", TestModel)
        config = ModelConfig("test_model")
        model = ModelFactory.create(config)
        assert model.config.name == "test_model", "name is not valid"

    def test_unknown_model_raises(self):
        """Unknown model raises error."""
        config = ModelConfig("nonexistent")
        with pytest.raises(ValueError):
            ModelFactory.create(config)


# --- Device/Dtype Matrix Tests ---


class DeviceType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class DtypeType(Enum):
    FLOAT32 = "float32"
    FLOAT16 = "float16"
    BFLOAT16 = "bfloat16"
    INT8 = "int8"


class DeviceDtypeMatrix:
    """Compatibility matrix for device/dtype combinations."""

    COMPATIBLE = {
        DeviceType.CPU: [DtypeType.FLOAT32, DtypeType.FLOAT16, DtypeType.BFLOAT16],
        DeviceType.CUDA: [DtypeType.FLOAT32, DtypeType.FLOAT16, DtypeType.BFLOAT16, DtypeType.INT8],
        DeviceType.MPS: [DtypeType.FLOAT32, DtypeType.FLOAT16],
    }

    @classmethod
    def is_compatible(cls, device: DeviceType, dtype: DtypeType) -> bool:
        """Check if device/dtype combination is compatible."""
        return dtype in cls.COMPATIBLE.get(device, [])

    @classmethod
    def get_supported_dtypes(cls, device: DeviceType) -> list[DtypeType]:
        """Get supported dtypes for device."""
        return cls.COMPATIBLE.get(device, [])


class TestDeviceDtypeMatrix:
    """Tests for device/dtype compatibility."""

    def test_cpu_float32_compatible(self):
        """CPU supports float32."""
        assert DeviceDtypeMatrix.is_compatible(DeviceType.CPU, DtypeType.FLOAT32)

    def test_cuda_int8_compatible(self):
        """CUDA supports int8."""
        assert DeviceDtypeMatrix.is_compatible(DeviceType.CUDA, DtypeType.INT8)

    def test_mps_int8_incompatible(self):
        """MPS does not support int8."""
        assert not DeviceDtypeMatrix.is_compatible(DeviceType.MPS, DtypeType.INT8)

    def test_get_supported_dtypes(self):
        """Get supported dtypes for device."""
        dtypes = DeviceDtypeMatrix.get_supported_dtypes(DeviceType.CUDA)
        assert DtypeType.FLOAT32 in dtypes, "Condition must be true"
        assert DtypeType.INT8 in dtypes, "Condition must be true"


# --- PEFT/LoRA Integration Tests ---


class LoRAConfig:
    """LoRA configuration."""

    def __init__(
        self,
        r: int = 8,
        alpha: int = 16,
        dropout: float = 0.05,
        target_modules: list[str] | None = None,
    ):
        self.r = r
        self.alpha = alpha
        self.dropout = dropout
        self.target_modules = target_modules or ["q_proj", "v_proj"]

    def scaling_factor(self) -> float:
        """Compute LoRA scaling factor."""
        return self.alpha / self.r


class LoRAAdapter:
    """LoRA adapter for models."""

    def __init__(self, config: LoRAConfig):
        self.config = config
        self._enabled = True

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def get_trainable_params(self) -> int:
        """Get count of trainable parameters (simulated)."""
        return self.config.r * len(self.config.target_modules) * 2


class TestLoRAIntegration:
    """Tests for LoRA integration."""

    def test_lora_config(self):
        """Create LoRA config."""
        config = LoRAConfig(r=16, alpha=32)
        assert config.r == 16, "r is not valid"
        assert config.scaling_factor() == 2.0, "Condition must be true"

    def test_lora_adapter(self):
        """Create LoRA adapter."""
        config = LoRAConfig()
        adapter = LoRAAdapter(config)
        assert adapter.is_enabled(), "Condition must be true"

    def test_lora_toggle(self):
        """Toggle LoRA adapter."""
        adapter = LoRAAdapter(LoRAConfig())
        adapter.disable()
        assert not adapter.is_enabled(), "Condition must be true"
        adapter.enable()
        assert adapter.is_enabled(), "Condition must be true"

    @given(st.integers(min_value=1, max_value=64), st.integers(min_value=1, max_value=128))
    @settings(max_examples=20)
    def test_scaling_factor_property(self, r: int, alpha: int):
        """Property: scaling factor is alpha/r."""
        config = LoRAConfig(r=r, alpha=alpha)
        assert config.scaling_factor() == alpha / r, "Condition must be true"


# --- Model Card Provenance Tests ---


class ModelCard:
    """Model card for provenance tracking."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.version: str = "1.0.0"
        self.authors: list[str] = []
        self.license: str = ""
        self.description: str = ""
        self.tags: list[str] = []
        self.metrics: dict[str, float] = {}
        self.training_data: str = ""
        self.checksum: str = ""

    def add_author(self, author: str) -> None:
        self.authors.append(author)

    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)

    def set_metric(self, name: str, value: float) -> None:
        self.metrics[name] = value

    def compute_checksum(self) -> str:
        """Compute card checksum."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model_name,
            "version": self.version,
            "authors": self.authors,
            "license": self.license,
            "description": self.description,
            "tags": self.tags,
            "metrics": self.metrics,
            "training_data": self.training_data,
        }


class TestModelCard:
    """Tests for model card provenance."""

    def test_create_model_card(self):
        """Create model card."""
        card = ModelCard("gpt2")
        assert card.model_name == "gpt2", "model_name is not valid"

    def test_add_metadata(self):
        """Add metadata to card."""
        card = ModelCard("test")
        card.add_author("John Doe")
        card.add_tag("nlp")
        card.set_metric("accuracy", 0.95)
        assert "John Doe" in card.authors, "Condition must be true"
        assert "nlp" in card.tags, "Condition must be true"
        assert card.metrics["accuracy"] == 0.95, "Condition must be true"

    def test_checksum_deterministic(self):
        """Checksum should be deterministic."""
        card = ModelCard("test")
        card.version = "1.0.0"
        h1 = card.compute_checksum()
        h2 = card.compute_checksum()
        assert h1 == h2, "h1 is not valid"


# --- Quantization Tests ---


class QuantizationConfig:
    """Quantization configuration."""

    def __init__(
        self,
        bits: int = 8,
        group_size: int = 128,
        sym: bool = True,
    ):
        self.bits = bits
        self.group_size = group_size
        self.sym = sym

    def compression_ratio(self) -> float:
        """Estimate compression ratio."""
        return 32 / self.bits


class Quantizer:
    """Model quantizer."""

    def __init__(self, config: QuantizationConfig):
        self.config = config

    def quantize_weights(self, weights: list[float]) -> list[int]:
        """Quantize weights (simplified)."""
        max_val = max(abs(w) for w in weights) if weights else 1.0
        scale = (2 ** (self.config.bits - 1) - 1) / max_val
        return [int(w * scale) for w in weights]

    def dequantize_weights(self, quantized: list[int], scale: float) -> list[float]:
        """Dequantize weights."""
        return [q / scale for q in quantized]


class TestQuantization:
    """Tests for quantization."""

    def test_quantization_config(self):
        """Create quantization config."""
        config = QuantizationConfig(bits=4)
        assert config.bits == 4, "bits is not valid"
        assert config.compression_ratio() == 8.0, "Condition must be true"

    def test_quantize_weights(self):
        """Quantize weights."""
        config = QuantizationConfig(bits=8)
        quantizer = Quantizer(config)
        weights = [0.5, -0.3, 0.8, -0.1]
        quantized = quantizer.quantize_weights(weights)
        assert all(isinstance(q, int) for q in quantized)

    @given(st.integers(min_value=2, max_value=16))
    @settings(max_examples=10)
    def test_compression_ratio_property(self, bits: int):
        """Property: compression ratio is 32/bits."""
        config = QuantizationConfig(bits=bits)
        assert config.compression_ratio() == 32 / bits, "Condition must be true"


# --- Model Registry Tests ---


class ModelRegistry:
    """Registry for model management."""

    def __init__(self):
        self.models: dict[str, dict[str, Any]] = {}

    def register(self, name: str, version: str, metadata: dict[str, Any]) -> None:
        """Register model version."""
        key = f"{name}:{version}"
        self.models[key] = {"name": name, "version": version, **metadata}

    def get(self, name: str, version: str | None = None) -> dict[str, Any] | None:
        """Get model by name and version."""
        if version:
            return self.models.get(f"{name}:{version}")
        # Get latest
        matching = [v for k, v in self.models.items() if k.startswith(f"{name}:")]
        return matching[-1] if matching else None

    def list_versions(self, name: str) -> list[str]:
        """List all versions of a model."""
        return [v["version"] for k, v in self.models.items() if v["name"] == name]


class TestModelRegistry:
    """Tests for model registry."""

    def test_register_model(self):
        """Register model version."""
        registry = ModelRegistry()
        registry.register("gpt2", "1.0.0", {"size": "small"})
        model = registry.get("gpt2", "1.0.0")
        assert model is not None, "model must be initialized"
        assert model["size"] == "small", "Condition must be true"

    def test_list_versions(self):
        """List model versions."""
        registry = ModelRegistry()
        registry.register("bert", "1.0.0", {})
        registry.register("bert", "1.1.0", {})
        versions = registry.list_versions("bert")
        assert len(versions) == 2, "Versions must not be empty"
