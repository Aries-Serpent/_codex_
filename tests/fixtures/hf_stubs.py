"""Shared HuggingFace test stubs.

Centralises dummy tokeniser / model objects so that individual test files
do not each redefine the same MagicMock.  Import from here rather than
creating local mocks in each test file.

Pattern P-043: lazy-import patching
------------------------------------
When mocking HF-stack imports that live inside ``run_functional_training``,
patch the **module attribute** (not ``sys.modules``).  Example::

    monkeypatch.setattr(legacy_api, "get_model", lambda *a, **k: _DummyModel())

See: ``src/codex_ml/training/legacy_api.py`` — lazy-import block comment.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Standalone stub objects (re-usable across test files without pytest)
# ---------------------------------------------------------------------------

_DummyTokenizer: MagicMock = MagicMock(name="DummyTokenizer")
_DummyModel: MagicMock = MagicMock(name="DummyModel")

# Preconfigure common attributes that test code inspects
_DummyTokenizer.pad_token_id = 0
_DummyTokenizer.eos_token_id = 1
_DummyTokenizer.model_max_length = 512
_DummyModel.config = MagicMock()
_DummyModel.config.model_type = "gpt2"


# ---------------------------------------------------------------------------
# pytest fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def dummy_tokenizer() -> MagicMock:
    """Return a fresh MagicMock that resembles a HuggingFace tokeniser."""
    tok = MagicMock(name="DummyTokenizer")
    tok.pad_token_id = 0
    tok.eos_token_id = 1
    tok.model_max_length = 512
    return tok


@pytest.fixture()
def dummy_model() -> MagicMock:
    """Return a fresh MagicMock that resembles a HuggingFace model."""
    model = MagicMock(name="DummyModel")
    model.config = MagicMock()
    model.config.model_type = "gpt2"
    return model


@pytest.fixture()
def dummy_load_from_pretrained(dummy_tokenizer, dummy_model, monkeypatch):
    """Patch ``load_from_pretrained`` in legacy_api to return dummy stubs."""
    try:
        from codex_ml.training import legacy_api

        monkeypatch.setattr(
            legacy_api,
            "load_from_pretrained",
            lambda *a, **k: (dummy_model, dummy_tokenizer),
        )
    except ImportError:
        _ = None  # suppressed: no action needed
    return dummy_model, dummy_tokenizer
