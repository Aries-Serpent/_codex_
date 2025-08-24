"""Configuration dataclasses for the Codex training pipeline."""

from dataclasses import dataclass


@dataclass
class TrainingWeights:
    """Weights controlling relative importance of training stages."""

    alpha: float
    beta: float
    gamma: float


@dataclass
class PretrainingConfig:
    """Settings for the pretraining stage."""

    model_size: str
    context_length: int


@dataclass
class SFTConfig:
    """Settings for supervised fine-tuning."""

    batch_size: int
    learning_rate: float
    epochs: int


@dataclass
class RLHFConfig:
    """Settings for the RLHF stage."""

    algorithm: str
    kl_penalty: float
    ppo_epochs: int


@dataclass
class ValidationThresholds:
    """Metrics expected from the validation step."""

    syntax_ok: float
    logic_ok: float
    security_ok: float
    perf_ok: float
