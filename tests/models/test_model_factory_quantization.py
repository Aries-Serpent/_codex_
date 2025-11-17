"""Tests for optional quantization support in :mod:`codex_ml.models.factory`."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from codex_ml.models import factory


def _dummy_builder(record: dict[str, Any]):
    def _builder(**kwargs: Any) -> SimpleNamespace:
        record.update(kwargs)
        return SimpleNamespace(**kwargs)

    return _builder


def test_quantization_string_mode_sets_flags() -> None:
    """String shorthands enable the expected loader flags."""

    recorded: dict[str, Any] = {}
    factory.create_model(
        _dummy_builder(recorded),
        config={"quantization": "8bit"},
    )

    assert recorded["load_in_8bit"] is True


def test_quantization_mapping_uses_bitsandbytes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mappings are converted into :class:`BitsAndBytesConfig` when available."""

    recorded: dict[str, Any] = {}

    class FakeBitsAndBytesConfig:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

    monkeypatch.setattr(factory, "BitsAndBytesConfig", FakeBitsAndBytesConfig)

    factory.create_model(
        _dummy_builder(recorded),
        config={
            "quantization": {
                "mode": "4bit",
                "bnb_4bit_compute_dtype": "float16",
                "bnb_4bit_use_double_quant": True,
            }
        },
    )

    assert recorded["load_in_4bit"] is True
    config_obj = recorded["quantization_config"]
    assert isinstance(config_obj, FakeBitsAndBytesConfig)
    assert config_obj.kwargs["bnb_4bit_compute_dtype"] == "float16"
    assert config_obj.kwargs["bnb_4bit_use_double_quant"] is True


def test_quantization_mapping_requires_bitsandbytes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Informative error when advanced settings used without transformers extras."""

    recorded: dict[str, Any] = {}
    monkeypatch.setattr(factory, "BitsAndBytesConfig", None)

    with pytest.raises(RuntimeError):
        factory.create_model(
            _dummy_builder(recorded),
            config={"quantization": {"bnb_4bit_compute_dtype": "float16"}},
        )
