"""Configuration dataclasses for the Codex training pipeline."""

from dataclasses import dataclass


@dataclass
class TrainingWeights:
    alpha: float
    beta: float
    gamma: float


@dataclass
class PretrainingConfig:
    model_size: str
    context_length: int


@dataclass
class SFTConfig:
    batch_size: int
    learning_rate: float
    epochs: int


@dataclass
class RLHFConfig:
    algorithm: str
    kl_penalty: float
    ppo_epochs: int


@dataclass
class ValidationThresholds:
    syntax_ok: float
    logic_ok: float
    security_ok: float
    perf_ok: float

