"""Deterministic base configuration for Codex training loops."""

from __future__ import annotations

BASE_TRAINING_CONFIG: dict[str, object] = {
    "model_name": "sshleifer/tiny-gpt2",
    "tokenizer_name": "sshleifer/tiny-gpt2",
    "learning_rate": 5e-5,
    "batch_size": 8,
    "epochs": 3,
    "gradient_accumulation_steps": 1,
    "seed": 42,
}

# Backwards compatibility for legacy imports expecting BASE_CONFIG.
BASE_CONFIG: dict[str, object] = dict(BASE_TRAINING_CONFIG)


def get_base_training_config() -> dict[str, object]:
    """Return a shallow copy of :data:`BASE_TRAINING_CONFIG`."""

    return dict(BASE_TRAINING_CONFIG)
