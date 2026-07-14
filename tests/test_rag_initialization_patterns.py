"""Tests for RAG model initialization patterns and default device allocation.

Focuses on CPU-default SentenceTransformer initialization after PR #3020 changes.
"""

from __future__ import annotations

import os
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from codex.rag.embeddings import LocalSentenceTransformerProvider
from codex.rag.indexer import embed_chunks
from codex.rag.retriever import Retriever


@dataclass
class SentenceTransformerSpy:
    """Capture SentenceTransformer initialization for validation."""

    calls: list[tuple[str, dict]]
    instances: list[object]


@pytest.fixture()
def sentence_transformer_spy(monkeypatch: pytest.MonkeyPatch) -> SentenceTransformerSpy:
    """Install a fake sentence_transformers module that records init kwargs."""
    calls: list[tuple[str, dict]] = []
    instances: list[object] = []

    class FakeSentenceTransformer:
        def __init__(self, model_name: str, **kwargs):
            self.model_name = model_name
            self.kwargs = kwargs
            self.eval_called = False
            calls.append((model_name, kwargs))
            instances.append(self)

        def encode(self, texts, **kwargs):
            return np.zeros((len(texts), 3))

        def get_sentence_embedding_dimension(self) -> int:
            return 3

        def eval(self):
            self.eval_called = True
            return self

        def to(self, device):
            """Mock .to() method for device placement."""
            return self

        def to_empty(self, device):
            """Mock .to_empty() method for meta tensor handling."""
            return self

    fake_module = types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    # Also patch the module-level SentenceTransformer variable in retriever module
    from codex.rag import retriever as retriever_module

    monkeypatch.setattr(retriever_module, "SentenceTransformer", FakeSentenceTransformer)
    return SentenceTransformerSpy(calls=calls, instances=instances)


@pytest.fixture(autouse=True)
def reset_env_vars() -> None:
    """Reset environment variables to avoid test interference."""
    os.environ.pop("HF_TOKEN", None)


@pytest.mark.timeout(30)
def test_local_provider_uses_default_device_allocation(
    sentence_transformer_spy: SentenceTransformerSpy,
    tmp_path: Path,
) -> None:
    """Local provider should use device='cpu' for direct CPU initialization."""
    cache_dir = tmp_path / "rag_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    LocalSentenceTransformerProvider(cache_dir=str(cache_dir))
    assert sentence_transformer_spy.calls, "sentence_transf is not valid"
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu", "Condition must be true"


@pytest.mark.timeout(30)
def test_local_provider_uses_device_none_pattern(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Local provider should use device='cpu' for direct CPU initialization."""
    LocalSentenceTransformerProvider()
    assert sentence_transformer_spy.calls, "sentence_transf is not valid"
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu", "Condition must be true"


@pytest.mark.timeout(30)
def test_local_provider_calls_eval(sentence_transformer_spy: SentenceTransformerSpy) -> None:
    """Local provider should call eval on the loaded model."""
    LocalSentenceTransformerProvider()
    assert sentence_transformer_spy.instances, "sentence_transf is not valid"
    assert sentence_transformer_spy.instances[0].eval_called is True, "eval_called is not valid"


@pytest.mark.timeout(30)
def test_embed_chunks_uses_default_device_allocation(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Indexer embed_chunks should use device='cpu' for direct CPU initialization."""
    chunks = [(0, 10, "hello"), (11, 20, "world")]
    embed_chunks(chunks, model_profile={"model_name": "fake-model", "cache_dir": "cache"})
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu", "Condition must be true"


@pytest.mark.timeout(30)
def test_embed_chunks_passes_cache_folder(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Indexer embed_chunks should pass cache_dir as cache_folder."""
    chunks = [(0, 10, "hello")]
    embed_chunks(chunks, model_profile={"cache_dir": "custom-cache"})
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("cache_folder") == "custom-cache", "Condition must be true"


@pytest.mark.timeout(30)
def test_retriever_load_model_uses_default_device_allocation(
    sentence_transformer_spy: SentenceTransformerSpy,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Retriever model initialization should use device='cpu' for direct CPU initialization."""
    monkeypatch.setattr(Retriever, "_load_index", lambda self: None)
    Retriever(index_dir=str(tmp_path))
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu", "Condition must be true"


@pytest.mark.timeout(30)
def test_retriever_load_model_calls_eval(
    sentence_transformer_spy: SentenceTransformerSpy,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Retriever should call eval on the loaded SentenceTransformer."""
    monkeypatch.setattr(Retriever, "_load_index", lambda self: None)
    Retriever(index_dir=str(tmp_path))
    assert sentence_transformer_spy.instances, "sentence_transf is not valid"
    assert sentence_transformer_spy.instances[0].eval_called is True, "eval_called is not valid"
