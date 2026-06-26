"""Comprehensive tests for configuration schema validation.

Tests cover:
- Schema enforcement for all config types
- Config hashing for reproducibility
- Drift detection against baselines
- Defaults coverage testing
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")
pytest.importorskip("pydantic", reason="pydantic required for config validation")

# Ensure real torch is in sys.modules if available; only mock if torch is not installed
try:
    __import__("torch")  # populate sys.modules["torch"] with real torch if available
except ImportError:
    sys.modules["torch"] = MagicMock()

from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    ValidationError,
)


# Local config schema implementation for testing without torch dependency
class LoraConfig(BaseModel):
    """Subset of LoRA hyper-parameters."""

    model_config = ConfigDict(extra="forbid")

    enable: bool = False
    r: PositiveInt = Field(default=8, description="LoRA rank")
    lora_alpha: PositiveInt = Field(default=16, description="LoRA alpha scaling")
    lora_dropout: float = Field(default=0.05, ge=0.0, le=1.0)
    task_type: str = Field(default="CAUSAL_LM")
    target_modules: list[str] | None = Field(default=None)


class TrainConfig(BaseModel):
    """Training configuration schema."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    config_version: int = Field(default=1, ge=1)
    model_name: str = Field(default="tiny", description="Model identifier")
    learning_rate: float = Field(default=1e-3, gt=0.0)
    batch_size: PositiveInt = Field(default=8, description="Training batch size")
    epochs: PositiveInt = Field(default=1)
    max_samples: PositiveInt = Field(default=32)
    data_path: str | None = Field(default=None)
    seed: int = Field(default=42, description="Random seed")
    device: str = Field(default="cpu", description="Training device")
    dtype: str = Field(default="float32", description="Torch dtype")
    grad_accum: PositiveInt = Field(default=1, description="Gradient accumulation steps")
    lora: LoraConfig | None = Field(default=None)
    eval_split: float | None = Field(default=None, ge=0.0, le=1.0)
    checkpoint_keep: PositiveInt = Field(default=1)
    bf16_require_capability: bool = Field(default=False)
    dataset_cast_policy: str | None = Field(default=None)


class LoraSettings:
    """Dataclass wrapper for LoraConfig."""

    def __init__(
        self,
        enabled: bool = False,
        rank: int = 8,
        alpha: int = 16,
        dropout: float = 0.05,
        task_type: str = "CAUSAL_LM",
        target_modules: list[str] | None = None,
    ):
        self.enabled = enabled
        self.rank = rank
        self.alpha = alpha
        self.dropout = dropout
        self.task_type = task_type
        self.target_modules = target_modules

    def to_payload(self) -> dict[str, Any]:
        if not self.enabled:
            return {"enable": False}
        payload: dict[str, Any] = {
            "enable": True,
            "r": int(self.rank),
            "lora_alpha": int(self.alpha),
            "lora_dropout": float(self.dropout),
            "task_type": self.task_type,
        }
        if self.target_modules is not None:
            payload["target_modules"] = list(self.target_modules)
        return payload


class TrainingSettings:
    """Minimal training configuration."""

    def __init__(
        self,
        model_name: str,
        epochs: int = 1,
        batch_size: int = 8,
        learning_rate: float = 1e-3,
        use_amp: bool = False,
        seed: int = 42,
        device: str = "cpu",
        dtype: str = "float32",
        grad_accum: int = 1,
        lora: LoraSettings | None = None,
    ):
        self.model_name = model_name
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.use_amp = use_amp
        self.seed = seed
        self.device = device
        self.dtype = dtype
        self.grad_accum = grad_accum
        self.lora = lora or LoraSettings()

    def to_train_config(self) -> TrainConfig:
        payload = {
            "model_name": self.model_name,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "seed": self.seed,
            "device": self.device,
            "dtype": self.dtype,
            "grad_accum": self.grad_accum,
        }
        if self.lora.enabled:
            payload["lora"] = self.lora.to_payload()
        return TrainConfig.model_validate(payload)

    @classmethod
    def from_train_config(cls, cfg: TrainConfig) -> "TrainingSettings":
        return cls(
            model_name=cfg.model_name,
            epochs=cfg.epochs,
            batch_size=cfg.batch_size,
            learning_rate=cfg.learning_rate,
            seed=cfg.seed,
            device=cfg.device,
            dtype=cfg.dtype,
            grad_accum=cfg.grad_accum,
        )


def validate_config_dict(cfg: dict) -> TrainConfig:
    """Validate config from dictionary."""
    if "training" in cfg and isinstance(cfg["training"], dict):
        return TrainConfig.model_validate(cfg["training"])
    return TrainConfig.model_validate(cfg)


def validate_config(path_or_dict) -> TrainConfig:
    """Validate config from path or dict."""
    if isinstance(path_or_dict, dict):
        return validate_config_dict(path_or_dict)
    import yaml

    with open(path_or_dict) as f:
        data = yaml.safe_load(f) or {}
    return validate_config_dict(data)


# --- Schema Enforcement Tests ---


class TestSchemaEnforcement:
    """Tests for strict schema validation."""

    def test_train_config_rejects_unknown_fields(self):
        """Config should reject unknown fields (extra='forbid')."""
        with pytest.raises(ValidationError):
            TrainConfig(unknown_field="value")

    def test_lora_config_rejects_unknown_fields(self):
        """LoRA config should reject unknown fields."""
        with pytest.raises(ValidationError):
            LoraConfig(unknown_lora_field=123)

    def test_learning_rate_must_be_positive(self):
        """Learning rate must be greater than zero."""
        with pytest.raises(ValidationError):
            TrainConfig(learning_rate=0.0)
        with pytest.raises(ValidationError):
            TrainConfig(learning_rate=-1e-5)

    def test_batch_size_must_be_positive_int(self):
        """Batch size must be positive integer."""
        with pytest.raises(ValidationError):
            TrainConfig(batch_size=0)
        with pytest.raises(ValidationError):
            TrainConfig(batch_size=-1)

    def test_epochs_must_be_positive_int(self):
        """Epochs must be positive integer."""
        with pytest.raises(ValidationError):
            TrainConfig(epochs=0)

    def test_lora_dropout_bounded_zero_one(self):
        """LoRA dropout must be in [0, 1]."""
        with pytest.raises(ValidationError):
            LoraConfig(lora_dropout=-0.1)
        with pytest.raises(ValidationError):
            LoraConfig(lora_dropout=1.1)

    def test_eval_split_bounded_zero_one(self):
        """Eval split must be in [0, 1]."""
        with pytest.raises(ValidationError):
            TrainConfig(eval_split=-0.1)
        with pytest.raises(ValidationError):
            TrainConfig(eval_split=1.1)

    def test_valid_config_passes(self):
        """Valid configuration should pass validation."""
        cfg = TrainConfig(
            model_name="gpt2",
            learning_rate=1e-4,
            batch_size=16,
            epochs=3,
            seed=123,
        )
        assert cfg.model_name == "gpt2", "model_name is not valid"
        assert cfg.learning_rate == 1e-4, "learning_rate is not valid"


# --- Config Hashing Tests ---


def compute_config_hash(cfg: TrainConfig) -> str:
    """Compute deterministic hash of config for reproducibility."""
    data = cfg.model_dump(mode="json")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class TestConfigHashing:
    """Tests for config hashing reproducibility."""

    def test_identical_configs_same_hash(self):
        """Identical configs should produce same hash."""
        cfg1 = TrainConfig(model_name="test", learning_rate=1e-3, seed=42)
        cfg2 = TrainConfig(model_name="test", learning_rate=1e-3, seed=42)
        assert compute_config_hash(cfg1) == compute_config_hash(cfg2), "Condition must be true"

    def test_different_configs_different_hash(self):
        """Different configs should produce different hashes."""
        cfg1 = TrainConfig(model_name="test", seed=42)
        cfg2 = TrainConfig(model_name="test", seed=43)
        assert compute_config_hash(cfg1) != compute_config_hash(cfg2), "Condition must be true"

    def test_hash_deterministic_across_serialization(self):
        """Hash should be consistent across serialization."""
        cfg = TrainConfig(model_name="model", learning_rate=2e-5)
        h1 = compute_config_hash(cfg)
        # Re-create from dict
        cfg2 = TrainConfig.model_validate(cfg.model_dump())
        h2 = compute_config_hash(cfg2)
        assert h1 == h2, "h1 is not valid"

    @given(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L", "N"))),
        st.floats(min_value=1e-10, max_value=1.0, allow_nan=False),
        st.integers(min_value=1, max_value=1000),
    )
    @settings(max_examples=50)
    def test_hash_property_deterministic(self, name: str, lr: float, seed: int):
        """Property: config hash is deterministic for any valid config."""
        cfg = TrainConfig(model_name=name or "default", learning_rate=lr, seed=seed)
        h1 = compute_config_hash(cfg)
        h2 = compute_config_hash(cfg)
        assert h1 == h2, "h1 is not valid"


# --- Drift Detection Tests ---


class TestDriftDetection:
    """Tests for detecting config drift from baselines."""

    def setup_method(self):
        """Set up baseline config for drift detection."""
        self.baseline = TrainConfig(
            model_name="baseline_model",
            learning_rate=1e-4,
            batch_size=32,
            epochs=10,
            seed=42,
        )

    def compute_drift(self, current: TrainConfig) -> dict[str, Any]:
        """Compute drift from baseline."""
        baseline_data = self.baseline.model_dump()
        current_data = current.model_dump()
        drift = {}
        for key in baseline_data:
            if baseline_data[key] != current_data[key]:
                drift[key] = {
                    "baseline": baseline_data[key],
                    "current": current_data[key],
                }
        return drift

    def test_no_drift_identical_config(self):
        """No drift when config matches baseline."""
        current = TrainConfig(
            model_name="baseline_model",
            learning_rate=1e-4,
            batch_size=32,
            epochs=10,
            seed=42,
        )
        drift = self.compute_drift(current)
        assert len(drift) == 0, "Drift must not be empty"

    def test_detect_learning_rate_drift(self):
        """Detect learning rate drift."""
        current = TrainConfig(
            model_name="baseline_model",
            learning_rate=2e-4,  # changed
            batch_size=32,
            epochs=10,
            seed=42,
        )
        drift = self.compute_drift(current)
        assert "learning_rate" in drift, "Condition must be true"
        assert drift["learning_rate"]["baseline"] == 1e-4, "Condition must be true"
        assert drift["learning_rate"]["current"] == 2e-4, "Condition must be true"

    def test_detect_multiple_drifts(self):
        """Detect multiple parameter drifts."""
        current = TrainConfig(
            model_name="different_model",  # changed
            learning_rate=5e-5,  # changed
            batch_size=32,
            epochs=20,  # changed
            seed=42,
        )
        drift = self.compute_drift(current)
        assert len(drift) == 3, "Drift must not be empty"
        assert "model_name" in drift, "Condition must be true"
        assert "learning_rate" in drift, "Condition must be true"
        assert "epochs" in drift, "Condition must be true"


# --- Defaults Coverage Tests ---


class TestDefaultsCoverage:
    """Tests ensuring all defaults are properly set and tested."""

    def test_all_defaults_present(self):
        """All fields should have sensible defaults."""
        cfg = TrainConfig()
        assert cfg.model_name == "tiny", "model_name is not valid"
        assert cfg.learning_rate == 1e-3, "learning_rate is not valid"
        assert cfg.batch_size == 8, "batch_size is not valid"
        assert cfg.epochs == 1, "epochs is not valid"
        assert cfg.max_samples == 32, "max_samples is not valid"
        assert cfg.seed == 42, "seed is not valid"
        assert cfg.device == "cpu", "device is not valid"
        assert cfg.dtype == "float32", "dtype is not valid"
        assert cfg.grad_accum == 1, "grad_accum is not valid"
        assert cfg.lora is None, "lora is not valid"
        assert cfg.eval_split is None, "eval_split is not valid"
        assert cfg.checkpoint_keep == 1, "checkpoint_keep is not valid"
        assert cfg.bf16_require_capability is False, "bf16_require_capability is not valid"
        assert cfg.dataset_cast_policy is None, "Data must not be empty"
        assert cfg.config_version == 1, "config_version is not valid"

    def test_lora_defaults(self):
        """LoRA config defaults should be sensible."""
        lora = LoraConfig()
        assert lora.enable is False, "enable is not valid"
        assert lora.r == 8, "r is not valid"
        assert lora.lora_alpha == 16, "lora_alpha is not valid"
        assert lora.lora_dropout == 0.05, "lora_dropout is not valid"
        assert lora.task_type == "CAUSAL_LM", "task_type is not valid"
        assert lora.target_modules is None, "target_modules is not valid"

    def test_training_settings_defaults(self):
        """TrainingSettings defaults should match expected values."""
        settings = TrainingSettings(model_name="test")
        assert settings.epochs == 1, "epochs is not valid"
        assert settings.batch_size == 8, "batch_size is not valid"
        assert settings.learning_rate == 1e-3, "learning_rate is not valid"
        assert settings.use_amp is False, "use_amp is not valid"
        assert settings.seed == 42, "seed is not valid"
        assert settings.device == "cpu", "device is not valid"
        assert settings.dtype == "float32", "dtype is not valid"
        assert settings.grad_accum == 1, "grad_accum is not valid"


# --- YAML Loading Tests ---


class TestYamlLoading:
    """Tests for YAML config loading."""

    def test_load_valid_yaml(self):
        """Load valid YAML config file."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
            f.write("""
model_name: test_model
learning_rate: 0.0001
batch_size: 16
epochs: 5
seed: 123
""")
            f.flush()
            cfg = validate_config(f.name)
            assert cfg.model_name == "test_model", "model_name is not valid"
            assert cfg.learning_rate == 0.0001, "learning_rate is not valid"
            assert cfg.batch_size == 16, "batch_size is not valid"
            Path(f.name).unlink()

    def test_load_nested_training_yaml(self):
        """Load YAML with nested training section."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
            f.write("""
training:
  model_name: nested_model
  learning_rate: 0.00005
  batch_size: 32
""")
            f.flush()
            cfg = validate_config(f.name)
            assert cfg.model_name == "nested_model", "model_name is not valid"
            assert cfg.learning_rate == 5e-5, "learning_rate is not valid"
            Path(f.name).unlink()

    def test_load_dict_config(self):
        """Load config from dictionary."""
        data = {"model_name": "dict_model", "learning_rate": 1e-4}
        cfg = validate_config_dict(data)
        assert cfg.model_name == "dict_model", "model_name is not valid"


# --- Conversion Tests ---


class TestConfigConversion:
    """Tests for config conversion between formats."""

    def test_lora_settings_to_payload(self):
        """LoraSettings should convert to LoraConfig payload."""
        settings = LoraSettings(enabled=True, rank=16, alpha=32, dropout=0.1)
        payload = settings.to_payload()
        assert payload["enable"] is True, "Condition must be true"
        assert payload["r"] == 16, "Condition must be true"
        assert payload["lora_alpha"] == 32, "Condition must be true"
        assert payload["lora_dropout"] == 0.1, "Condition must be true"

    def test_lora_settings_disabled(self):
        """Disabled LoraSettings should only have enable=False."""
        settings = LoraSettings(enabled=False)
        payload = settings.to_payload()
        assert payload == {"enable": False}, "payload is not valid"

    def test_training_settings_to_train_config(self):
        """TrainingSettings should convert to TrainConfig."""
        settings = TrainingSettings(
            model_name="conv_test",
            epochs=5,
            batch_size=16,
            learning_rate=2e-4,
        )
        cfg = settings.to_train_config()
        assert isinstance(cfg, TrainConfig)
        assert cfg.model_name == "conv_test", "model_name is not valid"
        assert cfg.epochs == 5, "epochs is not valid"

    def test_round_trip_conversion(self):
        """TrainConfig -> TrainingSettings -> TrainConfig should be consistent."""
        original = TrainConfig(
            model_name="roundtrip",
            learning_rate=1e-4,
            batch_size=32,
            epochs=10,
            seed=99,
        )
        settings = TrainingSettings.from_train_config(original)
        restored = settings.to_train_config()
        assert restored.model_name == original.model_name, "model_name is not valid"
        assert restored.learning_rate == original.learning_rate, "learning_rate is not valid"
        assert restored.batch_size == original.batch_size, "batch_size is not valid"
        assert restored.seed == original.seed, "seed is not valid"


# --- Property-Based Tests ---


class TestPropertyBasedConfig:
    """Property-based tests for configuration robustness."""

    @given(
        st.integers(min_value=1, max_value=100),
        st.integers(min_value=1, max_value=10000),
        st.floats(min_value=1e-10, max_value=1.0, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_valid_ranges_accepted(self, epochs: int, batch: int, lr: float):
        """Property: valid parameter ranges should always be accepted."""
        cfg = TrainConfig(epochs=epochs, batch_size=batch, learning_rate=lr)
        assert cfg.epochs == epochs, "epochs is not valid"
        assert cfg.batch_size == batch, "batch_size is not valid"
        assert cfg.learning_rate == lr, "learning_rate is not valid"

    @given(st.integers(min_value=0, max_value=1000000))
    @settings(max_examples=30)
    def test_seed_accepted_any_int(self, seed: int):
        """Property: any integer seed should be accepted."""
        cfg = TrainConfig(seed=seed)
        assert cfg.seed == seed, "seed is not valid"

    @given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    @settings(max_examples=30)
    def test_eval_split_valid_range(self, split: float):
        """Property: eval_split in [0, 1] should be accepted."""
        cfg = TrainConfig(eval_split=split)
        assert cfg.eval_split == split, "eval_split is not valid"

    @given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    @settings(max_examples=30)
    def test_lora_dropout_valid_range(self, dropout: float):
        """Property: lora_dropout in [0, 1] should be accepted."""
        lora = LoraConfig(lora_dropout=dropout)
        assert lora.lora_dropout == dropout, "lora_dropout is not valid"
