"""
Test Peft Utils

Test module for peft utils.
"""

from __future__ import annotations

import importlib

import pytest

from src.models.peft_utils import summarize_peft


def test_summarize_peft_graceful_without_peft() -> None:
    res = summarize_peft(object())
    assert isinstance(res, dict)
    assert "peft" in res or "base_model_type" in res


@pytest.mark.skipif(importlib.util.find_spec("peft") is None, reason="peft not installed")
def test_summarize_peft_with_dummy_model() -> None:
    class Dummy:
        pass

    res = summarize_peft(Dummy())
    assert isinstance(res, dict)
