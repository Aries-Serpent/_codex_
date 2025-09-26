"""Deterministic base configuration for Codex training loops."""

BASE_CONFIG: dict[str, object] = {
    "model_name": "sshleifer/tiny-gpt2",
    "tokenizer_name": "sshleifer/tiny-gpt2",
    "learning_rate": 5e-5,
    "batch_size": 8,
    "epochs": 3,
    "gradient_accumulation_steps": 1,
    "seed": 42,
}
