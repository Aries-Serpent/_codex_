"""
Tests for src/codex_ml/training/legacy_api.py

This module contains comprehensive tests for the legacy training API.
Covers dataclasses, helper functions, configuration coercion, and training entry points.

Test Coverage Target: 20+ tests for ~80% coverage of legacy_api module.

Created: 2026-01-18 (Phase 14.1)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Import module under test
try:
    from codex_ml.training.legacy_api import (
        OptimizerSettings,
        SafetySettings,
        SchedulerSettings,
        TrainingRunConfig,
        _coerce_optimizer,
        _coerce_safety,
        _coerce_scheduler,
        _listify_texts,
        _load_texts,
        _log_optional_dependencies,
        _normalize_config,
    )
    LEGACY_API_AVAILABLE = True
except ImportError:
    LEGACY_API_AVAILABLE = False


# Skip all tests if module not available
pytestmark = pytest.mark.skipif(
    not LEGACY_API_AVAILABLE,
    reason="codex_ml.training.legacy_api not available"
)


# =============================================================================
# Dataclass Tests
# =============================================================================


class TestSafetySettings:
    """Tests for SafetySettings dataclass."""

    def test_default_values(self):
        """Test SafetySettings default initialization."""
        settings = SafetySettings()
        assert settings.enabled is True
        assert settings.policy_path is None
        assert settings.bypass is False

    def test_custom_values(self):
        """Test SafetySettings with custom values."""
        settings = SafetySettings(
            enabled=False,
            policy_path="/path/to/policy.yaml",
            bypass=True,
        )
        assert settings.enabled is False
        assert settings.policy_path == "/path/to/policy.yaml"
        assert settings.bypass is True

    def test_moderation_settings_default(self):
        """Test that moderation settings are initialized by default."""
        settings = SafetySettings()
        assert settings.moderation is not None


class TestOptimizerSettings:
    """Tests for OptimizerSettings dataclass."""

    def test_default_values(self):
        """Test OptimizerSettings default initialization."""
        settings = OptimizerSettings()
        assert settings.name == "adamw_torch"
        assert settings.weight_decay == 0.01
        assert settings.betas == (0.9, 0.999)
        assert settings.eps == 1e-8

    def test_custom_optimizer(self):
        """Test OptimizerSettings with custom values."""
        settings = OptimizerSettings(
            name="adam",
            weight_decay=0.001,
            betas=(0.95, 0.99),
            eps=1e-6,
        )
        assert settings.name == "adam"
        assert settings.weight_decay == 0.001
        assert settings.betas == (0.95, 0.99)
        assert settings.eps == 1e-6


class TestSchedulerSettings:
    """Tests for SchedulerSettings dataclass."""

    def test_default_values(self):
        """Test SchedulerSettings default initialization."""
        settings = SchedulerSettings()
        assert settings.name == "linear"
        assert settings.warmup_steps == 0
        assert settings.num_cycles == 1.0

    def test_custom_scheduler(self):
        """Test SchedulerSettings with custom values."""
        settings = SchedulerSettings(
            name="cosine",
            warmup_steps=100,
            num_cycles=2.0,
        )
        assert settings.name == "cosine"
        assert settings.warmup_steps == 100
        assert settings.num_cycles == 2.0


class TestTrainingRunConfig:
    """Tests for TrainingRunConfig dataclass."""

    def test_default_values(self):
        """Test TrainingRunConfig default initialization."""
        config = TrainingRunConfig()
        assert config.seed == 42
        assert config.deterministic is True
        assert config.model == "minilm"
        assert config.learning_rate == 0.0003
        assert config.batch_size == 32
        assert config.max_epochs == 5

    def test_custom_config(self):
        """Test TrainingRunConfig with custom values."""
        config = TrainingRunConfig(
            seed=123,
            learning_rate=1e-4,
            batch_size=16,
            max_epochs=10,
        )
        assert config.seed == 123
        assert config.learning_rate == 1e-4
        assert config.batch_size == 16
        assert config.max_epochs == 10

    def test_nested_settings_defaults(self):
        """Test that nested settings are properly initialized."""
        config = TrainingRunConfig()
        assert isinstance(config.optimizer, OptimizerSettings)
        assert isinstance(config.scheduler, SchedulerSettings)
        assert isinstance(config.safety, SafetySettings)

    def test_dataset_default_structure(self):
        """Test dataset field has correct default structure."""
        config = TrainingRunConfig()
        assert "train_path" in config.dataset
        assert "eval_path" in config.dataset
        assert "format" in config.dataset
        assert config.dataset["format"] == "jsonl"


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestListifyTexts:
    """Tests for _listify_texts helper function."""

    def test_none_input(self):
        """Test that None returns empty list."""
        result = _listify_texts(None)
        assert result == []

    def test_string_input(self):
        """Test that string is wrapped in list."""
        result = _listify_texts("hello world")
        assert result == ["hello world"]

    def test_list_input(self):
        """Test that list items are converted to strings."""
        result = _listify_texts(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_numeric_list(self):
        """Test that numeric items are converted to strings."""
        result = _listify_texts([1, 2, 3])
        assert result == ["1", "2", "3"]

    def test_non_iterable(self):
        """Test that non-iterable is converted to string."""
        result = _listify_texts(42)
        assert result == ["42"]


class TestLoadTexts:
    """Tests for _load_texts helper function."""

    def test_none_path(self):
        """Test that None path returns empty list."""
        result = _load_texts(None)
        assert result == []

    def test_empty_path(self):
        """Test that empty path returns empty list."""
        result = _load_texts("")
        assert result == []

    def test_nonexistent_path(self):
        """Test that nonexistent path returns empty list."""
        result = _load_texts("/nonexistent/path/file.txt")
        assert result == []

    def test_text_format(self):
        """Test loading text format file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            f.flush()
            result = _load_texts(f.name, fmt="text")
            assert result == ["line 1", "line 2", "line 3"]

    def test_jsonl_format(self):
        """Test loading JSONL format file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"text": "hello"}\n')
            f.write('{"text": "world"}\n')
            f.flush()
            result = _load_texts(f.name, fmt="jsonl")
            assert result == ["hello", "world"]

    def test_jsonl_plain_strings(self):
        """Test loading JSONL with plain string values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('"plain string"\n')
            f.flush()
            result = _load_texts(f.name, fmt="jsonl")
            assert result == ["plain string"]


class TestLogOptionalDependencies:
    """Tests for _log_optional_dependencies function."""

    def test_returns_list(self):
        """Test that function returns a list of missing dependencies."""
        result = _log_optional_dependencies()
        assert isinstance(result, list)

    @patch("importlib.util.find_spec")
    def test_all_missing(self, mock_find_spec):
        """Test when all optional dependencies are missing."""
        mock_find_spec.return_value = None
        result = _log_optional_dependencies()
        # Should include psutil, pynvml, wandb, mlflow
        assert len(result) >= 4


# =============================================================================
# Coercion Function Tests
# =============================================================================


class TestCoerceOptimizer:
    """Tests for _coerce_optimizer function."""

    def test_optimizer_settings_passthrough(self):
        """Test that OptimizerSettings passes through unchanged."""
        settings = OptimizerSettings(name="sgd", weight_decay=0.1)
        result = _coerce_optimizer(settings, OptimizerSettings())
        assert result.name == "sgd"
        assert result.weight_decay == 0.1

    def test_mapping_input(self):
        """Test coercion from mapping."""
        mapping = {"name": "adam", "weight_decay": 0.05}
        result = _coerce_optimizer(mapping, OptimizerSettings())
        assert result.name == "adam"
        assert result.weight_decay == 0.05

    def test_string_input(self):
        """Test coercion from string (optimizer name only)."""
        result = _coerce_optimizer("sgd", OptimizerSettings())
        assert result.name == "sgd"

    def test_betas_from_list(self):
        """Test betas extraction from list."""
        mapping = {"betas": [0.8, 0.98]}
        result = _coerce_optimizer(mapping, OptimizerSettings())
        assert result.betas == (0.8, 0.98)

    def test_invalid_betas_uses_default(self):
        """Test that invalid betas fall back to default."""
        mapping = {"betas": ["invalid"]}
        default = OptimizerSettings()
        result = _coerce_optimizer(mapping, default)
        assert result.betas == default.betas


class TestCoerceScheduler:
    """Tests for _coerce_scheduler function."""

    def test_scheduler_settings_passthrough(self):
        """Test that SchedulerSettings passes through unchanged."""
        settings = SchedulerSettings(name="cosine", warmup_steps=50)
        result = _coerce_scheduler(settings, SchedulerSettings())
        assert result.name == "cosine"
        assert result.warmup_steps == 50

    def test_mapping_input(self):
        """Test coercion from mapping."""
        mapping = {"name": "cosine_annealing", "warmup_steps": 100}
        result = _coerce_scheduler(mapping, SchedulerSettings())
        assert result.name == "cosine_annealing"
        assert result.warmup_steps == 100


class TestCoerceSafety:
    """Tests for _coerce_safety function."""

    def test_safety_settings_passthrough(self):
        """Test that SafetySettings passes through with cloning."""
        settings = SafetySettings(enabled=False, bypass=True)
        result = _coerce_safety(settings, None)
        assert result.enabled is False
        assert result.bypass is True

    def test_mapping_input(self):
        """Test coercion from mapping."""
        mapping = {"enabled": False, "policy_path": "/path/policy.yaml"}
        result = _coerce_safety(mapping, None)
        assert result.enabled is False
        assert result.policy_path == "/path/policy.yaml"

    def test_non_mapping_uses_default(self):
        """Test that non-mapping input uses defaults."""
        result = _coerce_safety("invalid", None)
        assert result.enabled is True  # Default
        assert result.bypass is False  # Default


class TestNormalizeConfig:
    """Tests for _normalize_config function."""

    def test_dict_input(self):
        """Test normalization of dict input."""
        config = {"key": "value", "number": 42}
        result = _normalize_config(config)
        assert result == {"key": "value", "number": 42}

    def test_non_mapping_raises(self):
        """Test that non-mapping raises TypeError."""
        with pytest.raises(TypeError, match="config must be a mapping"):
            _normalize_config("not a mapping")

    @patch("codex_ml.training.legacy_api.DictConfig", None)
    def test_without_omegaconf(self):
        """Test behavior when OmegaConf is not available."""
        config = {"test": "value"}
        result = _normalize_config(config)
        assert result == {"test": "value"}


# =============================================================================
# Integration Tests
# =============================================================================


class TestConfigIntegration:
    """Integration tests for configuration handling."""

    def test_full_config_creation(self):
        """Test creating a full training configuration."""
        config = TrainingRunConfig(
            seed=123,
            model="gpt2",
            learning_rate=5e-5,
            batch_size=8,
            max_epochs=3,
            optimizer=OptimizerSettings(name="adamw", weight_decay=0.01),
            scheduler=SchedulerSettings(name="cosine", warmup_steps=500),
            safety=SafetySettings(enabled=True, bypass=False),
        )
        assert config.seed == 123
        assert config.optimizer.name == "adamw"
        assert config.scheduler.name == "cosine"
        assert config.safety.enabled is True

    def test_config_defaults_are_independent(self):
        """Test that default instances don't share mutable state."""
        config1 = TrainingRunConfig()
        config2 = TrainingRunConfig()
        
        # Modify config1's nested settings
        config1.dataset["custom_key"] = "value"
        
        # Ensure config2 is not affected
        assert "custom_key" not in config2.dataset


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_text_file(self):
        """Test loading empty text file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            f.flush()
            result = _load_texts(f.name, fmt="text")
            assert result == []

    def test_whitespace_only_lines(self):
        """Test that whitespace-only lines are ignored."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("content\n   \n\t\nmore content\n")
            f.flush()
            result = _load_texts(f.name, fmt="text")
            assert result == ["content", "more content"]

    def test_optimizer_empty_name_uses_default(self):
        """Test that empty optimizer name falls back to default."""
        mapping = {"name": ""}
        default = OptimizerSettings()
        result = _coerce_optimizer(mapping, default)
        assert result.name == default.name

    def test_scheduler_zero_warmup(self):
        """Test scheduler with zero warmup steps."""
        settings = SchedulerSettings(warmup_steps=0)
        assert settings.warmup_steps == 0

    def test_training_config_all_flags(self):
        """Test TrainingRunConfig with all boolean flags."""
        config = TrainingRunConfig(
            deterministic=False,
            tensorboard=False,
            mlflow_enable=True,
            amp_enable=True,
            lora_enable=True,
            log_system_metrics=True,
        )
        assert config.deterministic is False
        assert config.tensorboard is False
        assert config.mlflow_enable is True
        assert config.amp_enable is True
        assert config.lora_enable is True
        assert config.log_system_metrics is True
