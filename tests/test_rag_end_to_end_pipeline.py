from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow, pytest.mark.timeout(600)]


def _resolve_model_name(model_name: str) -> str:
    """Ensure model name uses the sentence-transformers namespace."""
    if "/" in model_name:
        return model_name
    return f"sentence-transformers/{model_name}"


@pytest.fixture
def sample_documents(tmp_path: Path) -> Path:
    """Create sample documents for testing."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    documents = [
        ("Machine learning is a subset of artificial intelligence.", "ml.txt"),
        ("Deep learning uses neural networks with multiple layers.", "dl.txt"),
        ("Natural language processing enables computers to understand text.", "nlp.txt"),
    ]

    for content, filename in documents:
        (docs_dir / filename).write_text(content)

    return docs_dir


@pytest.mark.timeout(600)
def test_full_rag_pipeline(sample_documents: Path, tmp_path: Path) -> None:
    """Test the full ingestion → index → query workflow."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files
    from codex.rag.retriever import Retriever

    index_dir = tmp_path / "indices"

    index_path = build_index_from_files(
        files=list(sample_documents.glob("*.txt")),
        index_name="docs",
        tenant_id="tenant",
        index_dir=str(index_dir),
    )

    assert index_path.exists(), "Expected index directory to be created"

    retriever = Retriever(
        index_dir=str(index_dir),
        index_name="docs",
        tenant_id="tenant",
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(tmp_path / "models"),
    )

    results = retriever.query("machine learning", top_k=2)
    assert results, "Expected RAG query to return results"


@pytest.mark.timeout(600)
def test_pipeline_with_metadata(sample_documents: Path, tmp_path: Path) -> None:
    """Verify metadata is persisted alongside the index."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files

    index_dir = tmp_path / "indices"
    index_path = build_index_from_files(
        files=list(sample_documents.glob("*.txt")),
        index_name="docs",
        tenant_id="tenant",
        index_dir=str(index_dir),
    )

    metadata_file = index_path / "metadata.json"
    assert metadata_file.exists(), "Expected metadata.json to be persisted"


@pytest.mark.timeout(600)
def test_index_persistence(sample_documents: Path, tmp_path: Path) -> None:
    """Ensure index files are saved and reloadable."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files

    index_path = build_index_from_files(
        files=list(sample_documents.glob("*.txt")),
        index_name="docs",
        tenant_id="tenant",
        index_dir=str(tmp_path / "indices"),
    )

    assert (index_path / "index.faiss").exists(), "Expected FAISS index file"
    assert (index_path / "chunks.json").exists(), "Expected chunks metadata file"


@pytest.mark.timeout(600)
def test_concurrent_queries(sample_documents: Path, tmp_path: Path) -> None:
    """Validate concurrent queries against a single index."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files
    from codex.rag.retriever import Retriever

    index_dir = tmp_path / "indices"
    build_index_from_files(
        files=list(sample_documents.glob("*.txt")),
        index_name="docs",
        tenant_id="tenant",
        index_dir=str(index_dir),
    )

    retriever = Retriever(
        index_dir=str(index_dir),
        index_name="docs",
        tenant_id="tenant",
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(tmp_path / "models"),
    )

    queries = ["machine learning", "deep learning", "natural language"]

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda q: retriever.query(q, top_k=1), queries))

    assert all(result for result in results), "Expected results for all concurrent queries"


@pytest.mark.timeout(600)
def test_pipeline_error_recovery(tmp_path: Path) -> None:
    """Ensure the pipeline fails gracefully on malformed input files."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    empty_file = docs_dir / "empty.txt"
    empty_file.write_text("")

    with pytest.raises(ValueError):
        build_index_from_files(
            files=[empty_file],
            index_name="empty",
            tenant_id="tenant",
            index_dir=str(tmp_path / "indices"),
        )


@pytest.mark.timeout(600)
def test_large_document_ingestion(tmp_path: Path) -> None:
    """Verify ingestion works with a larger batch of documents."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for i in range(120):
        (docs_dir / f"doc_{i}.txt").write_text(
            f"Document {i} about machine learning and retrieval augmented generation."
        )

    index_path = build_index_from_files(
        files=list(docs_dir.glob("*.txt")),
        index_name="large",
        tenant_id="tenant",
        index_dir=str(tmp_path / "indices"),
    )

    assert index_path.exists(), "Expected large index to be created"


@pytest.mark.timeout(600)
def test_index_update_operations(sample_documents: Path, tmp_path: Path) -> None:
    """Validate index update operations add new documents."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import manage_tenant_indices

    index_dir = tmp_path / "indices"
    tenant_id = "tenant"

    create_result = manage_tenant_indices(
        tenant_id=tenant_id,
        operation="create",
        index_names=["docs"],
        index_dir=str(index_dir),
        files=list(sample_documents.glob("*.txt")),
    )
    assert create_result.success, "Expected initial index creation to succeed"

    extra_doc = sample_documents / "extra.txt"
    extra_doc.write_text("Additional document for update test.")

    update_result = manage_tenant_indices(
        tenant_id=tenant_id,
        operation="update",
        index_names=["docs"],
        index_dir=str(index_dir),
        files=list(sample_documents.glob("*.txt")),
    )

    assert update_result.success, "Expected index update to succeed"


@pytest.mark.timeout(600)
def test_retrieval_relevance(sample_documents: Path, tmp_path: Path) -> None:
    """Verify retrieved results are semantically relevant to the query."""
    pytest.importorskip("sentence_transformers")
    pytest.importorskip("faiss")

    from codex.rag.indexer import build_index_from_files
    from codex.rag.retriever import Retriever

    index_dir = tmp_path / "indices"
    build_index_from_files(
        files=list(sample_documents.glob("*.txt")),
        index_name="docs",
        tenant_id="tenant",
        index_dir=str(index_dir),
    )

    retriever = Retriever(
        index_dir=str(index_dir),
        index_name="docs",
        tenant_id="tenant",
        model_name=_resolve_model_name("all-MiniLM-L6-v2"),
        cache_dir=str(tmp_path / "models"),
    )

    results = retriever.query("artificial intelligence", top_k=3)
    assert any("Machine learning" in result["text"] for result in results), (
        "Expected a machine learning result for AI query"
    )
