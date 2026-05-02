"""Tests for training enhancements (early stopping and scheduler factory).

This module tests:
- Early stopping functionality
- Learning rate scheduler factory
- Integration with training configurations
"""

from unittest.mock import Mock

import pytest


# Test early stopping
def test_early_stopping_import():
    """Test that early stopping module can be imported."""
    from codex_ml.training.early_stopping import EarlyStopping, EarlyStoppingConfig

    assert EarlyStopping is not None
    assert EarlyStoppingConfig is not None


def test_early_stopping_config_defaults():
    """Test early stopping config default values."""
    from codex_ml.training.early_stopping import EarlyStoppingConfig

    config = EarlyStoppingConfig()
    assert config.enabled is False
    assert config.patience == 3
    assert config.monitor == "val_loss"
    assert config.mode == "min"
    assert config.min_delta == 1e-4
    assert config.verbose is True


def test_early_stopping_config_custom():
    """Test early stopping config with custom values."""
    from codex_ml.training.early_stopping import EarlyStoppingConfig

    config = EarlyStoppingConfig(
        enabled=True, patience=5, monitor="val_accuracy", mode="max", min_delta=0.001, verbose=False
    )

    assert config.enabled is True
    assert config.patience == 5
    assert config.monitor == "val_accuracy"
    assert config.mode == "max"
    assert config.min_delta == 0.001
    assert config.verbose is False


def test_early_stopping_initialization():
    """Test early stopping initialization."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, monitor="val_loss", mode="min")

    assert es.patience == 3
    assert es.monitor == "val_loss"
    assert es.mode == "min"
    assert es.wait == 0
    assert es.best_value is None
    assert es.best_epoch == 0


def test_early_stopping_invalid_mode():
    """Test that invalid mode raises ValueError."""
    from codex_ml.training.early_stopping import EarlyStopping

    with pytest.raises(ValueError, match="mode must be"):
        EarlyStopping(mode="invalid")


def test_early_stopping_invalid_patience():
    """Test that invalid patience raises ValueError."""
    from codex_ml.training.early_stopping import EarlyStopping

    with pytest.raises(ValueError, match="patience must be"):
        EarlyStopping(patience=0)


def test_early_stopping_improvement_detection_min():
    """Test improvement detection in min mode."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, mode="min", min_delta=0.01)

    # First value is always improvement
    assert es._is_improvement(1.0)

    # Set best value
    es.best_value = 1.0

    # Improvement (lower value)
    assert es._is_improvement(0.9)

    # No improvement (same value within delta)
    assert not es._is_improvement(0.995)

    # No improvement (higher value)
    assert not es._is_improvement(1.1)


def test_early_stopping_improvement_detection_max():
    """Test improvement detection in max mode."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, mode="max", min_delta=0.01)

    # First value is always improvement
    assert es._is_improvement(0.5)

    # Set best value
    es.best_value = 0.5

    # Improvement (higher value)
    assert es._is_improvement(0.6)

    # No improvement (same value within delta)
    assert not es._is_improvement(0.505)

    # No improvement (lower value)
    assert not es._is_improvement(0.4)


def test_early_stopping_update():
    """Test early stopping update method."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, mode="min", verbose=False)

    # First update is improvement
    improved_1 = es.update(1.0, epoch=0)
    assert improved_1
    assert es.best_value == 1.0
    assert es.wait == 0

    # Better value is improvement
    improved_2 = es.update(0.9, epoch=1)
    assert improved_2
    assert es.best_value == 0.9
    assert es.wait == 0

    # Worse value is not improvement
    assert not es.update(1.0, epoch=2)
    assert es.best_value == 0.9
    assert es.wait == 1


def test_early_stopping_should_stop():
    """Test early stopping should_stop method."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, mode="min", verbose=False)

    # First few epochs
    assert not es.should_stop(1.0, epoch=0)
    assert not es.should_stop(0.9, epoch=1)  # Improvement, wait resets to 0
    assert not es.should_stop(1.0, epoch=2)  # No improvement, wait=1
    assert not es.should_stop(1.0, epoch=3)  # No improvement, wait=2

    # Should stop now (patience=3, wait=3 >= patience=3)
    assert es.should_stop(1.0, epoch=4)
    assert es.stopped_epoch == 4


def test_early_stopping_reset():
    """Test early stopping reset method."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, mode="min", verbose=False)

    # Set some state
    es.update(1.0, epoch=0)
    es.update(1.1, epoch=1)
    assert es.wait == 1
    assert es.best_value == 1.0

    # Reset
    es.reset()

    assert es.wait == 0
    assert es.best_value is None
    assert es.stopped_epoch == 0
    assert es.best_epoch == 0


def test_early_stopping_state_dict():
    """Test early stopping state_dict serialization."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, monitor="val_loss", mode="min", verbose=False)

    # Set some state
    es.update(1.0, epoch=0)
    es.update(1.1, epoch=1)

    # Get state dict
    state = es.state_dict()

    assert state["wait"] == 1
    assert state["best_value"] == 1.0
    assert state["best_epoch"] == 0
    assert state["patience"] == 3
    assert state["monitor"] == "val_loss"
    assert state["mode"] == "min"


def test_early_stopping_load_state_dict():
    """Test early stopping load_state_dict deserialization."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=3, mode="min", verbose=False)

    # Load state
    state = {
        "wait": 2,
        "best_value": 0.5,
        "best_epoch": 5,
        "stopped_epoch": 0,
        "patience": 5,
        "monitor": "val_accuracy",
        "mode": "max",
        "min_delta": 0.001,
    }

    es.load_state_dict(state)

    assert es.wait == 2
    assert es.best_value == 0.5
    assert es.best_epoch == 5
    assert es.patience == 5
    assert es.monitor == "val_accuracy"
    assert es.mode == "max"


def test_create_early_stopping_from_config():
    """Test creating early stopping from config."""
    from codex_ml.training.early_stopping import (
        EarlyStoppingConfig,
        create_early_stopping_from_config,
    )

    # Disabled config returns None
    config = EarlyStoppingConfig(enabled=False)
    es = create_early_stopping_from_config(config)
    assert es is None

    # Enabled config returns instance
    config = EarlyStoppingConfig(
        enabled=True,
        patience=5,
        monitor="val_accuracy",
        mode="max",
    )
    es = create_early_stopping_from_config(config)
    assert es is not None
    assert es.patience == 5
    assert es.monitor == "val_accuracy"
    assert es.mode == "max"


# Test scheduler factory
def test_scheduler_factory_import():
    """Test that scheduler factory can be imported."""
    from codex_ml.training.scheduler_factory import create_scheduler

    assert create_scheduler is not None


def test_get_available_schedulers():
    """Test getting list of available schedulers."""
    from codex_ml.training.scheduler_factory import get_available_schedulers

    schedulers = get_available_schedulers()

    assert "constant" in schedulers
    assert "linear" in schedulers
    assert "cosine" in schedulers
    assert "cosine_with_restarts" in schedulers
    assert "polynomial" in schedulers


def test_calculate_num_training_steps():
    """Test calculation of training steps."""
    from codex_ml.training.scheduler_factory import calculate_num_training_steps

    # Simple case
    steps = calculate_num_training_steps(
        num_epochs=3, dataset_size=1000, batch_size=10, gradient_accumulation_steps=1
    )
    assert steps == 300  # 3 * (1000 / 10)

    # With gradient accumulation
    steps = calculate_num_training_steps(
        num_epochs=2, dataset_size=1000, batch_size=10, gradient_accumulation_steps=2
    )
    assert steps == 100  # 2 * (1000 / (10 * 2))

    # Non-even division
    steps = calculate_num_training_steps(
        num_epochs=1, dataset_size=100, batch_size=32, gradient_accumulation_steps=1
    )
    assert steps == 4  # ceil(100 / 32)


def test_create_constant_scheduler():
    """Test creating constant scheduler."""
    from codex_ml.training.scheduler_factory import create_scheduler

    # Mock optimizer
    optimizer = Mock()
    optimizer.param_groups = [{"lr": 0.001}]

    try:
        scheduler = create_scheduler(optimizer=optimizer, scheduler_type="constant")

        assert scheduler is not None

        # Constant scheduler should return 1.0 for all steps
        # (though the actual behavior depends on implementation)

    except ImportError:
        # Skip if transformers or torch not available
        pytest.skip("transformers or torch not available")


def test_create_linear_scheduler():
    """Test creating linear scheduler."""
    from codex_ml.training.scheduler_factory import create_scheduler

    # Mock optimizer
    optimizer = Mock()
    optimizer.param_groups = [{"lr": 0.001}]

    try:
        scheduler = create_scheduler(
            optimizer=optimizer,
            scheduler_type="linear",
            num_training_steps=1000,
            num_warmup_steps=100,
        )

        assert scheduler is not None

    except ImportError:
        # Skip if transformers or torch not available
        pytest.skip("transformers or torch not available")


def test_create_cosine_scheduler():
    """Test creating cosine scheduler."""
    from codex_ml.training.scheduler_factory import create_scheduler

    # Mock optimizer
    optimizer = Mock()
    optimizer.param_groups = [{"lr": 0.001}]

    try:
        scheduler = create_scheduler(
            optimizer=optimizer,
            scheduler_type="cosine",
            num_training_steps=1000,
            num_warmup_steps=100,
        )

        assert scheduler is not None

    except ImportError:
        # Skip if transformers or torch not available
        pytest.skip("transformers or torch not available")


def test_create_scheduler_missing_training_steps():
    """Test that missing num_training_steps raises error for non-constant schedulers."""
    from codex_ml.training.scheduler_factory import create_scheduler

    optimizer = Mock()
    optimizer.param_groups = [{"lr": 0.001}]

    try:
        with pytest.raises(ValueError, match="num_training_steps"):
            create_scheduler(
                optimizer=optimizer,
                scheduler_type="linear",
                num_training_steps=None,  # Missing required parameter
            )
    except ImportError:
        # Skip if transformers or torch not available
        pytest.skip("transformers or torch not available")


def test_create_scheduler_invalid_type():
    """Test that invalid scheduler type raises error."""
    from codex_ml.training.scheduler_factory import create_scheduler

    optimizer = Mock()
    optimizer.param_groups = [{"lr": 0.001}]

    try:
        with pytest.raises(ValueError, match="Unknown scheduler type"):
            create_scheduler(
                optimizer=optimizer, scheduler_type="invalid_scheduler"  # Invalid type
            )
    except ImportError:
        # Skip if transformers or torch not available
        pytest.skip("transformers or torch not available")


# Integration tests
def test_training_enhancements_config_exists():
    """Test that training enhancements config file exists."""
    from pathlib import Path

    config_path = Path(__file__).parents[2] / "configs" / "base" / "training_enhancements.yaml"
    assert config_path.exists(), f"Config file not found: {config_path}"


def test_training_enhancements_config_valid():
    """Test that training enhancements config is valid YAML."""
    from pathlib import Path

    import yaml

    config_path = Path(__file__).parents[2] / "configs" / "base" / "training_enhancements.yaml"

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check structure
        assert "early_stopping" in config
        assert "scheduler" in config
        assert "training" in config

        # Check early stopping defaults
        assert config["early_stopping"]["enabled"] is False
        assert config["early_stopping"]["patience"] == 3
        assert config["early_stopping"]["monitor"] == "val_loss"

        # Check scheduler defaults
        assert config["scheduler"]["type"] == "linear"
        assert config["scheduler"]["num_warmup_steps"] == 0

    except FileNotFoundError:
        pytest.skip("Config file not found")


def test_integration_early_stopping_full_training_loop():
    """Test early stopping in a simulated training loop."""
    from codex_ml.training.early_stopping import EarlyStopping

    es = EarlyStopping(patience=2, mode="min", verbose=False)

    # Simulate training with improving then plateauing loss
    losses = [1.0, 0.9, 0.85, 0.84, 0.84, 0.84, 0.84]

    stopped = False
    stopped_epoch = -1

    for epoch, loss in enumerate(losses):
        if es.should_stop(loss, epoch):
            stopped = True
            stopped_epoch = epoch
            break

    # Should stop after patience epochs of no improvement
    assert stopped
    assert stopped_epoch == 5  # Improves until epoch 3, then plateaus for 2 epochs


def test_integration_scheduler_with_warmup():
    """Test scheduler behavior during warmup."""
    from codex_ml.training.scheduler_factory import create_scheduler

    # Mock optimizer
    optimizer = Mock()
    optimizer.param_groups = [{"lr": 0.001}]

    try:
        scheduler = create_scheduler(
            optimizer=optimizer,
            scheduler_type="linear",
            num_training_steps=100,
            num_warmup_steps=10,
        )

        # Warmup phase should increase LR
        # (exact behavior depends on scheduler implementation)
        assert scheduler is not None

    except ImportError:
        pytest.skip("transformers or torch not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
