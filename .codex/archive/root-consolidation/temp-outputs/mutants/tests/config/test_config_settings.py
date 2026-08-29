"""
Test Config Settings

Test module for config settings.
"""

from codex_ml.config_schema import LoraSettings, TokenizerSettings, TrainingSettings


def test_training_settings_round_trip() -> None:
    settings = TrainingSettings(
        model_name="tiny",
        epochs=2,
        batch_size=4,
        learning_rate=1e-4,
        grad_accum=2,
        lora=LoraSettings(enabled=True, rank=4, alpha=32, target_modules=("q_proj",)),
    )
    cfg = settings.to_train_config()
    assert cfg.model_name == "tiny", "model_name is not valid"
    assert cfg.epochs == 2, "epochs is not valid"
    assert cfg.grad_accum == 2, "grad_accum is not valid"
    assert cfg.lora is not None and cfg.lora.enable, "lora must be initialized"

    restored = TrainingSettings.from_train_config(cfg)
    assert restored.model_name == settings.model_name, "model_name is not valid"
    assert restored.epochs == settings.epochs, "epochs is not valid"
    assert restored.batch_size == settings.batch_size, "batch_size is not valid"
    assert restored.grad_accum == settings.grad_accum, "grad_accum is not valid"
    assert restored.lora.enabled, "rest is not valid"
    assert restored.lora.rank == 4, "rank is not valid"
    assert restored.lora.alpha == 32, "alpha is not valid"
    assert restored.lora.target_modules == ["q_proj"], "target_modules is not valid"


def test_tokenizer_settings_defaults() -> None:
    tokenizer = TokenizerSettings(vocab_size=1024)
    assert tokenizer.model_type == "bpe", "model_type is not valid"
    assert tokenizer.max_length == 1024, "Length must be greater than zero"
