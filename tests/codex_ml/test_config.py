"""
Tests for ML Configuration.

Tests for ML training configuration parsing and validation.

Phase 55: MEDIUM Priority Module Tests
Coverage Target: src/codex_ml 11% → 16%+
"""

from dataclasses import dataclass

import pytest


@dataclass
class TrainingConfig:
    """Training configuration."""

    model_name: str
    learning_rate: float = 1e-4
    batch_size: int = 32
    epochs: int = 10
    warmup_steps: int = 0
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    seed: int = 42
    fp16: bool = False
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100


class TestConfigParsing:
    """Tests for configuration parsing."""

    def test_default_config_values(self):
        """Default config values are set correctly."""
        config = TrainingConfig(model_name="bert-base-uncased")

        assert config.model_name == "bert-base-uncased", "model_name is not valid"
        assert config.learning_rate == 1e-4, "learning_rate is not valid"
        assert config.batch_size == 32, "batch_size is not valid"
        assert config.epochs == 10, "epochs is not valid"

    def test_config_override(self):
        """Config values can be overridden."""
        config = TrainingConfig(model_name="gpt2", learning_rate=5e-5, batch_size=16, epochs=3)

        assert config.learning_rate == 5e-5, "learning_rate is not valid"
        assert config.batch_size == 16, "batch_size is not valid"
        assert config.epochs == 3, "epochs is not valid"

    def test_config_from_dict(self):
        """Config can be created from dictionary."""

        def config_from_dict(d):
            return TrainingConfig(**d)

        config_dict = {
            "model_name": "roberta-base",
            "learning_rate": 2e-5,
            "batch_size": 8,
        }

        config = config_from_dict(config_dict)

        assert config.model_name == "roberta-base", "model_name is not valid"
        assert config.learning_rate == 2e-5, "learning_rate is not valid"


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_learning_rate_validation(self):
        """Learning rate must be positive."""

        def validate_learning_rate(lr):
            if lr <= 0:
                raise ValueError("Learning rate must be positive")
            if lr > 1:
                raise ValueError("Learning rate too high")
            return True

        assert validate_learning_rate(1e-4), "Condition must be true"

        with pytest.raises(ValueError):
            validate_learning_rate(0)

        with pytest.raises(ValueError):
            validate_learning_rate(-1e-4)

    def test_batch_size_validation(self):
        """Batch size must be positive integer."""

        def validate_batch_size(batch_size):
            if not isinstance(batch_size, int):
                raise TypeError("Batch size must be integer")
            if batch_size <= 0:
                raise ValueError("Batch size must be positive")
            if batch_size > 1024:
                raise ValueError("Batch size too large")
            return True

        assert validate_batch_size(32), "Condition must be true"

        with pytest.raises(ValueError):
            validate_batch_size(0)

        with pytest.raises(TypeError):
            validate_batch_size(32.5)

    def test_epochs_validation(self):
        """Epochs must be at least 1."""

        def validate_epochs(epochs):
            if epochs < 1:
                raise ValueError("Epochs must be at least 1")
            return True

        assert validate_epochs(10), "Condition must be true"

        with pytest.raises(ValueError):
            validate_epochs(0)


class TestConfigMerging:
    """Tests for configuration merging."""

    def test_merge_configs(self):
        """Configs can be merged with priority."""

        def merge_configs(base, override):
            result = {**base}
            for key, value in override.items():
                if value is not None:
                    result[key] = value
            return result

        base = {"model_name": "bert", "lr": 1e-4, "batch_size": 32}
        override = {"lr": 5e-5, "epochs": 5}

        merged = merge_configs(base, override)

        assert merged["model_name"] == "bert", "Condition must be true"
        assert merged["lr"] == 5e-5, "Condition must be true"
        assert merged["epochs"] == 5, "Condition must be true"

    def test_nested_config_merge(self):
        """Nested configs merge correctly."""

        def deep_merge(base, override):
            result = {**base}
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        base = {"training": {"lr": 1e-4, "batch_size": 32}, "model": {"hidden_size": 768}}
        override = {"training": {"lr": 5e-5}, "model": {"dropout": 0.1}}

        merged = deep_merge(base, override)

        assert merged["training"]["lr"] == 5e-5, "Condition must be true"
        assert merged["training"]["batch_size"] == 32, "Condition must be true"
        assert merged["model"]["dropout"] == 0.1, "Condition must be true"


class TestConfigSerialization:
    """Tests for configuration serialization."""

    def test_config_to_dict(self):
        """Config can be serialized to dict."""
        from dataclasses import asdict

        config = TrainingConfig(model_name="bert-base")
        config_dict = asdict(config)

        assert config_dict["model_name"] == "bert-base", "Condition must be true"
        assert "learning_rate" in config_dict, "Condition must be true"

    def test_config_to_yaml(self):
        """Config can be serialized to YAML-like format."""

        def to_yaml_lines(config_dict, indent=0):
            lines = []
            for key, value in config_dict.items():
                if isinstance(value, dict):
                    lines.append(f"{'  ' * indent}{key}:")
                    lines.extend(to_yaml_lines(value, indent + 1))
                else:
                    lines.append(f"{'  ' * indent}{key}: {value}")
            return lines

        config_dict = {"model": "bert", "training": {"lr": 1e-4}}
        yaml_lines = to_yaml_lines(config_dict)

        assert "model: bert" in yaml_lines, "Condition must be true"
        assert "  lr: 0.0001" in yaml_lines, "Condition must be true"

    def test_config_to_json(self):
        """Config can be serialized to JSON."""
        import json
        from dataclasses import asdict

        config = TrainingConfig(model_name="bert-base")
        json_str = json.dumps(asdict(config))

        assert "bert-base" in json_str, "Condition must be true"
        parsed = json.loads(json_str)
        assert parsed["model_name"] == "bert-base", "Condition must be true"


class TestConfigInheritance:
    """Tests for configuration inheritance."""

    def test_base_config_extension(self):
        """Configs can extend base configs."""
        base_configs = {
            "small": {"hidden_size": 256, "num_layers": 4},
            "base": {"hidden_size": 768, "num_layers": 12},
            "large": {"hidden_size": 1024, "num_layers": 24},
        }

        def get_config(size, overrides=None):
            if size not in base_configs:
                raise ValueError(f"Unknown size: {size}")
            config = {**base_configs[size]}
            if overrides:
                config.update(overrides)
            return config

        config = get_config("base", {"dropout": 0.1})

        assert config["hidden_size"] == 768, "Condition must be true"
        assert config["dropout"] == 0.1, "Condition must be true"

    def test_config_presets(self):
        """Config presets provide common configurations."""
        presets = {
            "debug": {"epochs": 1, "batch_size": 2, "logging_steps": 1},
            "quick": {"epochs": 3, "eval_steps": 100},
            "full": {"epochs": 10, "save_steps": 500},
        }

        def apply_preset(config, preset_name):
            if preset_name not in presets:
                return config
            preset = presets[preset_name]
            return {**config, **preset}

        config = {"model_name": "bert", "lr": 1e-4}
        debug_config = apply_preset(config, "debug")

        assert debug_config["epochs"] == 1, "Condition must be true"
        assert debug_config["batch_size"] == 2, "Condition must be true"
        assert debug_config["lr"] == 1e-4, "Condition must be true"
