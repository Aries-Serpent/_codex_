"""
Test Retrieval Pipeline
Tests for embedding, FAISS store, and search functionality
"""

import json
import tempfile
from pathlib import Path

import pytest

# Skip if dependencies not available
pytest.importorskip("sentence_transformers")
pytest.importorskip("faiss")

pytestmark = pytest.mark.requires_faiss

from codex.retrieval import (
    FAISSStore,
    RetrievalEngine,
    build_embeddings,
)


@pytest.fixture
def sample_ndjson():
    """Create a temporary NDJSON file with sample documents"""
    docs = [
        {
            "id": "doc1",
            "content": "Machine learning is a subset of AI.",
            "metadata": {"topic": "ml"},
        },
        {
            "id": "doc2",
            "content": "Natural language processing works with text.",
            "metadata": {"topic": "nlp"},
        },
        {
            "id": "doc3",
            "content": "Deep learning uses neural networks.",
            "metadata": {"topic": "dl"},
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
        for doc in docs:
            f.write(json.dumps(doc) + "\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_index_dir():
    """Create a temporary directory for FAISS index"""

    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_build_embeddings(sample_ndjson):
    """Test building embeddings from NDJSON"""
    embeddings, documents = build_embeddings(
        ndjson_path=sample_ndjson,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=2,
    )

    assert embeddings.shape[0] == 3, "Condition must be true"
    assert embeddings.shape[1] == 384, "Condition must be true"
    assert len(documents) == 3, "Documents must not be empty"


def test_faiss_store_create_and_save(sample_ndjson, temp_index_dir):
    """Test creating and saving FAISS index"""
    embeddings, documents = build_embeddings(
        ndjson_path=sample_ndjson,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=2,
    )

    store = FAISSStore(index_dir=temp_index_dir, index_name="test")
    store.create_index(embeddings, documents)

    assert store.index is not None, "index must be initialized"
    assert store.index.ntotal == 3, "ntotal is not valid"

    # Save and verify files exist
    store.save()

    index_path = Path(temp_index_dir) / "test.index"
    docs_path = Path(temp_index_dir) / "test.docs.jsonl"
    meta_path = Path(temp_index_dir) / "test.meta.json"

    assert index_path.exists(), "Condition must be true"
    assert docs_path.exists(), "Condition must be true"
    assert meta_path.exists(), "Condition must be true"


def test_faiss_store_load_and_search(sample_ndjson, temp_index_dir):
    """Test loading FAISS index and searching"""
    # Build and save index
    embeddings, documents = build_embeddings(
        ndjson_path=sample_ndjson,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=2,
    )

    store = FAISSStore(index_dir=temp_index_dir, index_name="test")
    store.create_index(embeddings, documents)
    store.save()

    # Load index
    store2 = FAISSStore(index_dir=temp_index_dir, index_name="test")
    store2.load()

    assert store2.index is not None, "index must be initialized"
    assert len(store2.documents) == 3, "Collection must not be empty"

    # Search
    query_vector = embeddings[0]  # Use first document as query
    results = store2.search(query_vector, top_k=2)

    assert len(results) == 2, "Results must not be empty"
    assert results[0]["document"]["id"] == "doc1", "Result must not be empty"
    assert results[0]["score"] > 0.9, "Value must be greater than zero"


def test_retrieval_engine_search(sample_ndjson, temp_index_dir):
    """Test RetrievalEngine search functionality"""
    # Build index first
    embeddings, documents = build_embeddings(
        ndjson_path=sample_ndjson,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=2,
    )

    store = FAISSStore(index_dir=f"{temp_index_dir}/test-tenant/faiss", index_name="default")
    store.create_index(embeddings, documents)
    store.save()

    # Search using engine
    engine = RetrievalEngine(
        index_base_dir=temp_index_dir,
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    )

    results = engine.search(
        tenant_id="test-tenant",
        query="What is machine learning?",
        top_k=2,
    )

    assert len(results) == 2, "Results must not be empty"
    assert "document_id" in results[0], "Result must not be empty"
    assert "content" in results[0], "Result must not be empty"
    assert "score" in results[0], "Result must not be empty"
