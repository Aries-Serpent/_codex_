from __future__ import annotations

import pytest

from codex_ml.config_schema import validate_config


def test_validate_config_invalid() -> None:
    bad_cfg = {"train": {"batch_size": 1, "lr": 0.1}, "tokenizer": {"vocab_size": 64}}
    with pytest.raises(ValueError):
        validate_config(bad_cfg)
