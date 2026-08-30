"""
Shared pytest fixtures for the RAG test suite.

Key fixture: ``rag_mock_model``
-------------------------------
A correctly-configured ``MagicMock`` that satisfies ``safe_model_to_device``'s
internal inspection chain.  ``safe_model_to_device`` calls::

    model.to(device)           -> must return a model (not a fresh MagicMock)
    model.to_empty(device=...) -> same
    model.eval()               -> same

Without these return-value overrides a bare ``MagicMock()`` passes
``model.to(device)`` but the returned *new* MagicMock won't have
``.encode`` / ``.get_sentence_embedding_dimension`` wired up, breaking
any downstream encode call.  This pattern (RP-RAG-MOCK-CHAIN) has
recurred 13+ times across the test suite — centralise it here.

Usage in tests::

    def test_something(rag_mock_model):
        indexer.model = rag_mock_model
        ...

Or in test-class fixtures::

    @pytest.fixture
    def mock_model(self, rag_mock_model):
        return rag_mock_model
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

try:
    import numpy as _np

    _HAS_NUMPY = True
except ImportError:  # pragma: no cover
    _np = None
    _HAS_NUMPY = False


@pytest.fixture()
def rag_mock_model() -> MagicMock:
    """Return a MagicMock SentenceTransformer that satisfies ``safe_model_to_device``.

    The key invariant: every method that ``safe_model_to_device`` may call
    (``to``, ``to_empty``, ``eval``) must return **the same mock object** so
    that attribute access on the *result* of those calls still reaches the
    pre-configured stubs (``encode``, ``get_sentence_embedding_dimension``).

    RP-RAG-MOCK-CHAIN fix (S323 — recurred 13 times in 24 h on 0D_base_).
    """
    mock = MagicMock()
    if _HAS_NUMPY and _np is not None:
        mock.encode.return_value = _np.zeros((3, 384), dtype=_np.float32)
    else:
        mock.encode.return_value = [[0.0] * 384] * 3
    mock.get_sentence_embedding_dimension.return_value = 384
    # Chain: to/to_empty/eval must all return *this* mock, not a new MagicMock.
    mock.to.return_value = mock
    mock.to_empty.return_value = mock
    mock.eval.return_value = mock
    # has_meta_tensors() inspects model.parameters(); make it return an empty iter.
    mock.parameters.return_value = iter([])
    return mock
