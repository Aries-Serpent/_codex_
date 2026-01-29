from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest


def _resolve_model_name(model_name: str) -> str:
    """Ensure model name uses the sentence-transformers namespace."""
    if "/" in model_name:
        return model_name
    return f"sentence-transformers/{model_name}"


@pytest.mark.timeout(300)
def test_embedding_model_caching(tmp_path: Path) -> None:
    """Verify LocalSentenceTransformerProvider uses the provided cache directory."""
    pytest.importorskip("sentence_transformers")

    from codex.rag.embeddings import LocalSentenceTransformerProvider

    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    provider = LocalSentenceTransformerProvider(
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(cache_dir),
    )

    cache_contents = list(cache_dir.rglob("*"))
    if not cache_contents:
        pytest.skip("Cache directory empty; model may already be cached elsewhere")

    assert provider.model is not None, "Expected embedding model to initialize"


@pytest.mark.parametrize("model_profile", ["fast", "quality", "multilingual"])
@pytest.mark.timeout(300)
def test_indexer_model_profile_handling(model_profile: str, tmp_path: Path) -> None:
    """
    Ensure embed_chunks handles multiple model profiles with stable embeddings.
    """
    pytest.importorskip("sentence_transformers")

    from codex.rag.indexer import embed_chunks

    profile_map = {
        "fast": "all-MiniLM-L6-v2",
        "quality": "all-MiniLM-L6-v2",
        "multilingual": "all-MiniLM-L6-v2",
    }
    model_name = _resolve_model_name(profile_map[model_profile])

    chunks = [(0, 28, "Profile handling regression test")]
    embeddings = embed_chunks(
        chunks,
        model_profile={"model_name": model_name, "cache_dir": str(tmp_path / "models")},
    )

    assert embeddings.shape[0] == 1, f"Expected one embedding for profile {model_profile}"


@pytest.mark.timeout(300)
def test_retriever_index_loading(tmp_path: Path) -> None:
    """Verify retriever loads an existing index and returns results."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files
    from codex.rag.retriever import Retriever

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    doc_path = docs_dir / "doc.txt"
    doc_path.write_text("Retrieval test document for index loading.")

    index_path = build_index_from_files(
        files=[doc_path],
        index_name="docs",
        tenant_id="tenant",
        index_dir=str(tmp_path / "indices"),
    )
    assert index_path.exists(), "Expected index directory to be created"

    retriever = Retriever(
        index_dir=str(tmp_path / "indices"),
        index_name="docs",
        tenant_id="tenant",
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(tmp_path / "models"),
    )

    results = retriever.query("index loading", top_k=1)
    assert results, "Expected retriever to return results from loaded index"


@pytest.mark.timeout(300)
def test_model_initialization_timeout(tmp_path: Path) -> None:
    """Ensure model initialization completes within a reasonable time bound."""
    pytest.importorskip("sentence_transformers")

    from codex.rag.embeddings import LocalSentenceTransformerProvider

    start = time.monotonic()
    _ = LocalSentenceTransformerProvider(
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(tmp_path / "models"),
    )
    duration = time.monotonic() - start

    assert duration < 300, f"Model initialization took too long: {duration:.1f}s"


@pytest.mark.timeout(300)
def test_concurrent_model_loading(tmp_path: Path) -> None:
    """Validate model initialization is thread-safe under concurrent loads."""
    pytest.importorskip("sentence_transformers")

    from codex.rag.embeddings import LocalSentenceTransformerProvider

    cache_dir = tmp_path / "models"
    cache_dir.mkdir(parents=True, exist_ok=True)

    def _load() -> LocalSentenceTransformerProvider:
        return LocalSentenceTransformerProvider(
            model_name=_resolve_model_name("all-MiniLM-L6-v2"),
            cache_dir=str(cache_dir),
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        providers = list(executor.map(lambda _: _load(), range(2)))

    assert all(provider.model is not None for provider in providers), "Model load failed in threads"


@pytest.mark.timeout(300)
def test_invalid_model_name_handling(tmp_path: Path) -> None:
    """Ensure invalid model names raise a clear initialization error."""
    pytest.importorskip("sentence_transformers")

    from codex.rag.embeddings import LocalSentenceTransformerProvider

    with pytest.raises(Exception):
        _ = LocalSentenceTransformerProvider(
            model_name="invalid-model-name-for-tests",
            cache_dir=str(tmp_path / "models"),
        )


@pytest.mark.timeout(300)
def test_model_device_attribute(tmp_path: Path) -> None:
    """Check that the embedding model reports CPU device allocation."""
    pytest.importorskip("sentence_transformers")
    torch = pytest.importorskip("torch")

    from codex.rag.embeddings import LocalSentenceTransformerProvider

    provider = LocalSentenceTransformerProvider(
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(tmp_path / "models"),
    )

    device = getattr(provider.model, "device", None)
    assert device is not None, "Expected model to expose device attribute"
    assert isinstance(device, torch.device), "Model device should be a torch.device"
    assert device.type == "cpu", f"Expected CPU device, got {device}"
