"""Targeted tests for :mod:`codex.training` helpers."""

from __future__ import annotations

import sys
import types

import pytest

# Skip if PyTorch-dependent modules cannot be imported
try:
    from codex.training import (
        _build_safe_ckpt_payload as _build_safe_ckpt_payload,
    )
    from codex.training import (
        _codex_config_hash as _codex_config_hash,
    )
    from codex.training import (
        _safe_perplexity as _safe_perplexity,
    )
    from codex.training import (
        _safe_token_accuracy as _safe_token_accuracy,
    )
    TRAINING_AVAILABLE = True
except (ImportError, AttributeError):
    TRAINING_AVAILABLE = False


@pytest.mark.skipif(not TRAINING_AVAILABLE, reason="Training module requires PyTorch")
def test_safe_token_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    # Stub tokenization dependency pulled in by codex_ml.symbolic_pipeline
    stub_tokenization = types.SimpleNamespace(TokenizerAdapter=type("TokenizerAdapter", (), {}))
    monkeypatch.setitem(sys.modules, "src.tokenization", stub_tokenization)

    from codex.training import _safe_perplexity, _safe_token_accuracy  # noqa: F811

    assert _safe_token_accuracy([1, 2], [1, 3]) == 0.5
    assert _safe_token_accuracy([], []) == 0.0
    assert _safe_perplexity([0.0, 0.0]) >= 1.0


@pytest.mark.skipif(not TRAINING_AVAILABLE, reason="Training module requires PyTorch")
def test_config_hash_stable() -> None:
    from codex.training import _codex_config_hash  # noqa: F811

    cfg = {"a": 1, "b": {"c": 2}}
    first = _codex_config_hash(cfg)
    second = _codex_config_hash(dict(cfg))
    assert first == second


class _Dummy:
    def __init__(self) -> None:
        self._state = {"x": 1}

    def state_dict(self):  # pragma: no cover - simple helper
        return self._state


@pytest.mark.skipif(not TRAINING_AVAILABLE, reason="Training module requires PyTorch")
@pytest.mark.parametrize("extra", [None, {"note": "ok"}])
def test_build_safe_ckpt_payload(extra):
    from codex.training import _build_safe_ckpt_payload  # noqa: F811

    payload = _build_safe_ckpt_payload(_Dummy(), _Dummy(), epoch=3, extra=extra)
    assert payload["meta"].get("saved_at")
    assert payload["model_state_dict"]
