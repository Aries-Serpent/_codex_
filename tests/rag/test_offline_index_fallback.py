"""Offline RAG index/retrieval fallback tests."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pytest

pytest.importorskip("faiss")
pytest.importorskip("sklearn")

from aries_serpent_core.rag.indexer import build_index_from_files
from aries_serpent_core.rag.retriever import Retriever


def _make_workspace(name: str) -> Path:
    root = Path(".codex/test-artifacts") / f"{name}-{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _raise_offline(*_args, **_kwargs):
    raise ImportError("offline")


def _force_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deterministically simulate missing/unloadable sentence-transformers.

    Patch the *globals of the function objects this test actually calls* rather
    than a module re-imported via the package attribute. Under the
    ``codex.rag`` -> ``aries_serpent_core.rag`` alias (and other tests that pop
    or reload RAG modules) the package attribute can be a different module
    object than the one ``build_index_from_files``/``Retriever`` close over, so
    ``monkeypatch.setattr(module, ...)`` silently had no effect when the real
    sentence-transformers package and a cached model were installed (hosted CI).
    """
    monkeypatch.setitem(build_index_from_files.__globals__, "embed_chunks", _raise_offline)
    monkeypatch.setitem(Retriever._load_model.__globals__, "SentenceTransformer", None)
    # Belt and braces: even if a SentenceTransformer symbol is consulted, the
    # loader must fail so the TF-IDF fallback path is the only option.
    import sys

    model_utils = sys.modules.get("aries_serpent_core.rag._model_utils")
    if model_utils is not None and hasattr(model_utils, "safe_load_sentence_transformer"):

        def _loader_offline(*_args, **_kwargs):
            raise OSError("offline: model unavailable")

        monkeypatch.setattr(model_utils, "safe_load_sentence_transformer", _loader_offline)


def test_build_index_from_files_falls_back_to_tfidf(monkeypatch: pytest.MonkeyPatch) -> None:
    """Index building should remain available without sentence-transformers."""
    workspace = _make_workspace("offline-build")
    try:
        source = workspace / "python_doc.txt"
        source.write_text(
            "Python makes data pipelines reliable. Python supports semantic search tests.",
            encoding="utf-8",
        )
        _force_offline(monkeypatch)

        index_path = build_index_from_files(
            files=[source],
            index_name="offline-index",
            tenant_id="pytest",
            index_dir=str(workspace / "indices"),
            chunk_size=80,
            overlap=10,
        )

        metadata = json.loads((index_path / "metadata.json").read_text(encoding="utf-8"))
        assert metadata["embedding_provider"] == "TfidfEmbeddingProvider", "Data must not be empty"
        assert metadata["num_vectors"] >= 1, "Value must be greater than zero"
        assert (index_path / "index.faiss").exists(), "Condition must be true"
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_retriever_uses_tfidf_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retriever should query TF-IDF-built indices when transformer deps are absent."""
    workspace = _make_workspace("offline-query")
    try:
        python_doc = workspace / "python_doc.txt"
        garden_doc = workspace / "garden_doc.txt"
        python_doc.write_text(
            "Python functions, decorators, and semantic retrieval belong to software engineering.",
            encoding="utf-8",
        )
        garden_doc.write_text(
            "Tomato plants, compost, and watering schedules belong to home gardening.",
            encoding="utf-8",
        )

        _force_offline(monkeypatch)

        build_index_from_files(
            files=[python_doc, garden_doc],
            index_name="offline-index",
            tenant_id="pytest",
            index_dir=str(workspace / "indices"),
            chunk_size=120,
            overlap=0,
        )

        retriever = Retriever(
            index_dir=str(workspace / "indices"),
            index_name="offline-index",
            tenant_id="pytest",
        )
        results = retriever.query("python semantic retrieval", top_k=2)

        assert retriever.model.__class__.__name__ == "TfidfEmbeddingProvider", "__name__ is not valid"
        assert results, "Result must not be empty"
        assert "Python" in results[0]["text"], "Result must not be empty"
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
