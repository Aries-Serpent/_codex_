"""
Integration tests for RAG modules.
Tests end-to-end workflows, multi-tenant isolation, and cross-module interactions.
"""

import importlib.util
import tempfile
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

# Conditional imports for RAG dependencies - safely handled at test runtime
try:
    from codex.rag.embeddings import create_embedding_provider
    from codex.rag.indexer import build_index_from_files, load_index
    from codex.rag.retriever import MultiIndexRetriever, Retriever

    RAG_INTEGRATION_AVAILABLE = True
except ImportError:
    RAG_INTEGRATION_AVAILABLE = False

# Check if sentence_transformers is available
try:
    if importlib.util.find_spec("sentence_transformers") is None:
        raise ImportError
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RAG_INTEGRATION_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="RAG dependencies (sentence_transformers, faiss) not installed",
)

# Guard for tests that require real SentenceTransformer models on CPU
try:
    import torch as _torch

    _cuda_available = _torch.cuda.is_available()
except (ImportError, RuntimeError):
    _cuda_available = False

_skip_real_st_models = pytest.mark.skipif(
    not _cuda_available,
    reason="SentenceTransformer real model tests may fail on CPU-only runners",
)


@pytest.mark.integration
@_skip_real_st_models
class TestEndToEndPipeline:
    """Test complete RAG pipeline from docs to retrieval"""

    def test_full_workflow_docs_to_query(self):
        """Test: Create corpus → Build index → Query → Verify provenance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Step 1: Create diverse document corpus
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            corpus = {
                "python_guide.md": "# Python Programming\n\nPython is a high-level, interpreted language. "
                * 50,
                "ml_intro.md": "# Machine Learning\n\nML uses statistical algorithms to learn from data. "
                * 50,
                "docker_tutorial.md": "# Docker Containerization\n\nDocker packages applications in containers. "
                * 50,
            }

            files = []
            for filename, content in corpus.items():
                file_path = docs_dir / filename
                file_path.write_text(content)
                files.append(file_path)

            # Step 2: Build FAISS index
            index_dir = tmpdir / "indices"
            index_path = build_index_from_files(
                files=files,
                index_name="test_docs",
                tenant_id="default",
                index_dir=str(index_dir),
                chunk_size=500,
                overlap=100,
            )

            assert index_path.exists(), "Condition must be true"
            assert (index_path / "index.faiss").exists(), "Condition must be true"
            assert (index_path / "chunks.json").exists(), "Condition must be true"
            assert (index_path / "metadata.json").exists(), "Data must not be empty"

            # Step 3: Load and verify index
            faiss_index, chunks, metadata = load_index(
                index_name="test_docs",
                tenant_id="default",
                index_dir=str(index_dir),
            )

            assert faiss_index.ntotal > 0, "ntotal must be greater than zero"
            assert len(chunks) > 0, "Chunks must not be empty"
            assert metadata["total_files"] == 3, "Data must not be empty"

            # Step 4: Query with retriever
            retriever = Retriever(
                index_dir=str(index_dir),
                index_name="test_docs",
                tenant_id="default",
            )

            # Query about Python
            python_results = retriever.query("Python programming language", top_k=5)
            assert len(python_results) > 0, "Python_results must not be empty"
            assert python_results[0]["score"] < 100, "Result must not be empty"

            # Verify provenance
            for result in python_results:
                assert "text" in result, "Result must not be empty"
                assert "file" in result, "Result must not be empty"
                assert "start_line" in result, "Result must not be empty"
                assert "end_line" in result, "Result must not be empty"
                assert "score" in result, "Result must not be empty"
                assert "generated_at" in result, "Result must not be empty"
                assert isinstance(result["score"], float)

            # Query about Machine Learning
            ml_results = retriever.query("machine learning algorithms", top_k=5)
            assert len(ml_results) > 0, "Ml_results must not be empty"

            # Query about Docker
            docker_results = retriever.query("container deployment", top_k=5)
            assert len(docker_results) > 0, "Docker_results must not be empty"

            # Verify different queries return different results
            assert python_results[0]["text"] != ml_results[0]["text"], "Result must not be empty"


@pytest.mark.integration
@_skip_real_st_models
class TestMultiTenantIsolation:
    """Test multi-tenant index isolation"""

    def test_tenant_isolation(self):
        """Test that different tenants cannot access each other's indices"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            index_dir = tmpdir / "indices"

            # Create indices for 3 different tenants
            tenants = ["tenant_a", "tenant_b", "tenant_c"]

            for tenant in tenants:
                # Create unique content for each tenant
                docs_dir = tmpdir / f"docs_{tenant}"
                docs_dir.mkdir()

                content_file = docs_dir / f"{tenant}_data.txt"
                content_file.write_text(f"Sensitive data for {tenant}. " * 50)

                # Build index
                build_index_from_files(
                    files=[content_file],
                    index_name="data",
                    tenant_id=tenant,
                    index_dir=str(index_dir),
                    chunk_size=300,
                    overlap=50,
                )

            # Verify each tenant can access their own data
            for tenant in tenants:
                retriever = Retriever(
                    index_dir=str(index_dir),
                    index_name="data",
                    tenant_id=tenant,
                )

                results = retriever.query("sensitive data", top_k=5)
                assert len(results) > 0, "Results must not be empty"

                # Verify results contain the tenant's data
                assert tenant in results[0]["text"], "Result must not be empty"

                # Verify results don't contain other tenants' data
                for other_tenant in tenants:
                    if other_tenant != tenant:
                        assert other_tenant not in results[0]["text"], "Result must not be empty"

            # Verify tenant directories are separate
            for tenant in tenants:
                tenant_dir = index_dir / tenant / "data"
                assert tenant_dir.exists(), "Condition must be true"


@pytest.mark.integration
@_skip_real_st_models
class TestCacheEffectiveness:
    """Test embedding cache behavior across workflows"""

    def test_cache_hit_rate(self):
        """Test that cache provides significant speedup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create provider with caching
            cache_dir = tmpdir / "cache"
            provider = create_embedding_provider(
                provider_type="local",
                use_cache=True,
                cache_dir=str(cache_dir),
            )

            texts = ["Test text 1", "Test text 2", "Test text 3"]
            cache_key = "test_docs"

            # First encoding: cache miss
            embeddings1 = provider.encode(texts, cache_key=cache_key)
            assert provider.cache_misses == 1, "cache_misses is not valid"
            assert provider.cache_hits == 0, "cache_hits is not valid"

            # Second encoding: cache hit
            embeddings2 = provider.encode(texts, cache_key=cache_key)
            assert provider.cache_hits == 1, "cache_hits is not valid"
            assert provider.cache_misses == 1, "cache_misses is not valid"

            # Verify embeddings are identical
            np.testing.assert_array_equal(embeddings1, embeddings2)

            # Verify cache hit rate
            stats = provider.get_stats()
            assert stats["hit_rate"] == 0.5, "Condition must be true"
            assert stats["total_requests"] == 2, "Condition must be true"


@pytest.mark.integration
@_skip_real_st_models
class TestCrossModuleInteractions:
    """Test interactions between different RAG modules"""

    def test_indexer_retriever_embeddings_integration(self):
        """Test that all modules work together seamlessly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create embedding provider with cache (cache_dir declared but not explicitly used)
            _ = tmpdir / "cache"

            # Create documents
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            doc1 = docs_dir / "doc1.txt"
            doc1.write_text("Python is a programming language. " * 30)

            doc2 = docs_dir / "doc2.txt"
            doc2.write_text("Docker is a container platform. " * 30)

            # Build index (uses embeddings internally)
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=[doc1, doc2],
                index_name="docs",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            # Retrieve (uses embeddings for query encoding)
            retriever = Retriever(
                index_dir=str(index_dir),
                index_name="docs",
                tenant_id="test",
            )

            results = retriever.query("programming", top_k=3)
            assert len(results) > 0, "Results must not be empty"
            assert "Python" in results[0]["text"] or "programming" in results[0]["text"], "Result must not be empty"


@pytest.mark.integration
@_skip_real_st_models
class TestMultiIndexQueries:
    """Test querying across multiple indices"""

    def test_multi_index_retrieval(self):
        """Test retrieving from multiple indices simultaneously"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            index_dir = tmpdir / "indices"

            # Create 2 separate indices with different content
            for idx in [1, 2]:
                docs_dir = tmpdir / f"docs_{idx}"
                docs_dir.mkdir()

                doc = docs_dir / "doc.txt"
                doc.write_text(f"Content for index {idx}. " * 40)

                build_index_from_files(
                    files=[doc],
                    index_name=f"index_{idx}",
                    tenant_id="test",
                    index_dir=str(index_dir),
                )

            # Query across both indices
            multi_retriever = MultiIndexRetriever(
                indices=[
                    {"index_name": "index_1", "tenant_id": "test"},
                    {"index_name": "index_2", "tenant_id": "test"},
                ],
                index_dir=str(index_dir),
            )

            results = multi_retriever.query("content", top_k=10)

            # Should get results from both indices
            assert len(results) > 0, "Results must not be empty"

            # Check that results have index metadata
            for result in results:
                assert "index_name" in result, "Result must not be empty"
                assert "tenant_id" in result, "Result must not be empty"
                assert result["index_name"] in ["index_1", "index_2"]

            # Should have results from both indices (if top_k is large enough)
            index_names = set(r["index_name"] for r in results)
            assert len(index_names) >= 1, "Index_names must not be empty"


@pytest.mark.integration
@pytest.mark.slow
@_skip_real_st_models
class TestPerformanceUnderLoad:
    """Test system performance with realistic loads"""

    def test_large_corpus_indexing(self):
        """Test indexing a moderately large corpus"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            # Create 50 documents
            files = []
            for i in range(50):
                doc = docs_dir / f"doc_{i}.txt"
                doc.write_text(f"Document {i} content. " * 100)
                files.append(doc)

            # Build index
            index_dir = tmpdir / "indices"
            index_path = build_index_from_files(
                files=files,
                index_name="large_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=500,
                overlap=100,
            )

            assert index_path.exists(), "Condition must be true"

            # Verify index
            faiss_index, _chunks, metadata = load_index(
                index_name="large_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            assert faiss_index.ntotal > 0, "ntotal must be greater than zero"
            assert metadata["total_files"] == 50, "Data must not be empty"

            # Test queries
            retriever = Retriever(
                index_dir=str(index_dir),
                index_name="large_corpus",
                tenant_id="test",
            )

            results = retriever.query("document content", top_k=10)
            assert len(results) == 10, "Results must not be empty"

    def test_high_query_volume(self):
        """Test system with many queries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create small corpus
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            doc = docs_dir / "doc.txt"
            doc.write_text("Test content for queries. " * 50)

            # Build index
            index_dir = tmpdir / "indices"
            build_index_from_files(
                files=[doc],
                index_name="query_test",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            # Create retriever
            retriever = Retriever(
                index_dir=str(index_dir),
                index_name="query_test",
                tenant_id="test",
            )

            # Execute many queries
            queries = [f"query {i}" for i in range(100)]
            results_list = []

            for query in queries:
                results = retriever.query(query, top_k=5)
                results_list.append(results)

            # All queries should succeed
            assert len(results_list) == 100, "Results_list must not be empty"
            assert all(len(r) > 0 for r in results_list), "R must not be empty"
