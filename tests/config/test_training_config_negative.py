import pytest
from codex_ml.config import TrainingConfig


def test_training_config_invalid_epochs():
    with pytest.raises(ValueError):
        TrainingConfig(max_epochs=-1)


def test_training_config_invalid_batch_size():
    with pytest.raises(ValueError):
        TrainingConfig(batch_size=0)


def test_training_config_invalid_seed():
    with pytest.raises(ValueError):
        TrainingConfig(seed=-5)
