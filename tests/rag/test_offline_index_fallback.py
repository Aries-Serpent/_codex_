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


def test_build_index_from_files_falls_back_to_tfidf(monkeypatch: pytest.MonkeyPatch) -> None:
    """Index building should remain available without sentence-transformers."""
    from aries_serpent_core.rag import indexer as indexer_module

    workspace = _make_workspace("offline-build")
    try:
        source = workspace / "python_doc.txt"
        source.write_text(
            "Python makes data pipelines reliable. Python supports semantic search tests.",
            encoding="utf-8",
        )
        monkeypatch.setattr(indexer_module, "embed_chunks", lambda *_args, **_kwargs: (_ for _ in ()).throw(ImportError("offline")))  # noqa: E501

        index_path = build_index_from_files(
            files=[source],
            index_name="offline-index",
            tenant_id="pytest",
            index_dir=str(workspace / "indices"),
            chunk_size=80,
            overlap=10,
        )

        metadata = json.loads((index_path / "metadata.json").read_text(encoding="utf-8"))
        assert metadata["embedding_provider"] == "TfidfEmbeddingProvider"
        assert metadata["num_vectors"] >= 1
        assert (index_path / "index.faiss").exists()
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_retriever_uses_tfidf_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retriever should query TF-IDF-built indices when transformer deps are absent."""
    from aries_serpent_core.rag import indexer as indexer_module
    from aries_serpent_core.rag import retriever as retriever_module

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

        monkeypatch.setattr(indexer_module, "embed_chunks", lambda *_args, **_kwargs: (_ for _ in ()).throw(ImportError("offline")))  # noqa: E501
        monkeypatch.setattr(retriever_module, "SentenceTransformer", None)

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

        assert retriever.model.__class__.__name__ == "TfidfEmbeddingProvider"
        assert results
        assert "Python" in results[0]["text"]
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
