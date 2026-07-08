"""
Test Codex Model Dtype

Test module for codex model dtype.
"""

import pytest

torch = pytest.importorskip("torch")

from codex_ml.codex_model import ModelConfig, build_codex_model


def test_build_codex_model_accepts_torch_dtype():
    config = ModelConfig(base_model_path=None, dtype=torch.float16, device="cpu")
    model = build_codex_model(config)
    assert next(model.parameters()).dtype == torch.float16, "dtype is not valid"


def test_build_codex_model_accepts_string_dtype():
    config = ModelConfig(base_model_path=None, dtype="float32", device="cpu")
    model = build_codex_model(config)
    assert next(model.parameters()).dtype == torch.float32, "dtype is not valid"


def test_build_codex_model_rejects_invalid_dtype():
    config = ModelConfig(base_model_path=None, dtype="not-a-dtype", device="cpu")
    with pytest.raises(ValueError):
        build_codex_model(config)
