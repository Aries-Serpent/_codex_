"""Tests for RAG model initialization patterns and default device allocation.

Focuses on CPU-default SentenceTransformer initialization after PR #3020 changes.
"""

from __future__ import annotations

import os
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import pytest

np = pytest.importorskip("numpy")

from codex.rag.embeddings import LocalSentenceTransformerProvider  # noqa: E402
from codex.rag.indexer import embed_chunks  # noqa: E402
from codex.rag.retriever import Retriever  # noqa: E402


@dataclass
class SentenceTransformerSpy:
    """Capture SentenceTransformer initialization for validation."""

    calls: List[Tuple[str, dict]]
    instances: List[object]


@pytest.fixture()
def sentence_transformer_spy(monkeypatch: pytest.MonkeyPatch) -> SentenceTransformerSpy:
    """Install a fake sentence_transformers module that records init kwargs."""
    calls: List[Tuple[str, dict]] = []
    instances: List[object] = []

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
    """Local provider should explicitly set device='cpu' to prevent meta tensors."""
    cache_dir = tmp_path / "rag_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    LocalSentenceTransformerProvider(cache_dir=str(cache_dir))
    assert sentence_transformer_spy.calls
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu"


@pytest.mark.timeout(30)
def test_local_provider_sets_device_cpu(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Local provider should explicitly set device='cpu' to prevent meta tensor issues."""
    LocalSentenceTransformerProvider()
    assert sentence_transformer_spy.calls
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu"


@pytest.mark.timeout(30)
def test_local_provider_calls_eval(sentence_transformer_spy: SentenceTransformerSpy) -> None:
    """Local provider should call eval on the loaded model."""
    LocalSentenceTransformerProvider()
    assert sentence_transformer_spy.instances
    assert sentence_transformer_spy.instances[0].eval_called is True


@pytest.mark.timeout(30)
def test_embed_chunks_uses_default_device_allocation(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Indexer embed_chunks should explicitly set device='cpu' to prevent meta tensors."""
    chunks = [(0, 10, "hello"), (11, 20, "world")]
    embed_chunks(chunks, model_profile={"model_name": "fake-model", "cache_dir": "cache"})
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu"


@pytest.mark.timeout(30)
def test_embed_chunks_passes_cache_folder(
    sentence_transformer_spy: SentenceTransformerSpy,
) -> None:
    """Indexer embed_chunks should pass cache_dir as cache_folder."""
    chunks = [(0, 10, "hello")]
    embed_chunks(chunks, model_profile={"cache_dir": "custom-cache"})
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("cache_folder") == "custom-cache"


@pytest.mark.timeout(30)
def test_retriever_load_model_uses_default_device_allocation(
    sentence_transformer_spy: SentenceTransformerSpy,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Retriever model initialization should explicitly set device='cpu' to prevent meta tensors."""
    monkeypatch.setattr(Retriever, "_load_index", lambda self: None)
    Retriever(index_dir=str(tmp_path))
    _, kwargs = sentence_transformer_spy.calls[0]
    assert kwargs.get("device") == "cpu"


@pytest.mark.timeout(30)
def test_retriever_load_model_calls_eval(
    sentence_transformer_spy: SentenceTransformerSpy,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Retriever should call eval on the loaded SentenceTransformer."""
    monkeypatch.setattr(Retriever, "_load_index", lambda self: None)
    Retriever(index_dir=str(tmp_path))
    assert sentence_transformer_spy.instances
    assert sentence_transformer_spy.instances[0].eval_called is True
