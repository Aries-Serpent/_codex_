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
    assert cfg.model_name == "tiny"
    assert cfg.epochs == 2
    assert cfg.grad_accum == 2
    assert cfg.lora is not None and cfg.lora.enable

    restored = TrainingSettings.from_train_config(cfg)
    assert restored.model_name == settings.model_name
    assert restored.epochs == settings.epochs
    assert restored.batch_size == settings.batch_size
    assert restored.grad_accum == settings.grad_accum
    assert restored.lora.enabled
    assert restored.lora.rank == 4
    assert restored.lora.alpha == 32
    assert restored.lora.target_modules == ["q_proj"]


def test_tokenizer_settings_defaults() -> None:
    tokenizer = TokenizerSettings(vocab_size=1024)
    assert tokenizer.model_type == "bpe"
    assert tokenizer.max_length == 1024
