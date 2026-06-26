"""
Tests for RAG Indexer Module
"""

import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

# Conditional imports for RAG dependencies - safely handled at test runtime
try:
    from codex.rag.indexer import (
        build_index_from_files,
        chunk_text,
        embed_chunks,
        load_index,
        persist_index,
    )

    RAG_INDEXER_AVAILABLE = True
except ImportError:
    RAG_INDEXER_AVAILABLE = False

# Check if sentence_transformers is available
try:
    if importlib.util.find_spec("sentence_transformers") is None:
        raise ImportError
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not RAG_INDEXER_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE,
    reason="RAG indexer dependencies (sentence_transformers, faiss) not installed",
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


class TestChunkText:
    """Tests for chunk_text function"""

    def test_basic_chunking(self):
        """Test basic text chunking"""
        text = "This is a test. " * 100  # ~1600 chars
        chunks = chunk_text(text, chunk_size=500, overlap=50)

        assert len(chunks) > 0, "Chunks must not be empty"
        assert all(len(chunk[2]) <= 500 for chunk in chunks), "Collection must not be empty"
        assert all(isinstance(chunk, tuple) for chunk in chunks)
        assert all(len(chunk) == 3 for chunk in chunks), "Chunk must not be empty"

    def test_empty_text(self):
        """Test chunking empty text"""
        chunks = chunk_text("", chunk_size=100, overlap=10)
        assert len(chunks) == 0, "Chunks must not be empty"

    def test_small_text(self):
        """Test chunking text smaller than chunk_size"""
        text = "Small text"
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1, "Chunks must not be empty"
        assert chunks[0][2] == text, "Condition must be true"

    def test_overlap(self):
        """Test that chunks have proper overlap"""
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=200, overlap=50)

        assert len(chunks) > 1, "Chunks must not be empty"
        # Check positions show overlap
        for i in range(len(chunks) - 1):
            current_end = chunks[i][1]
            next_start = chunks[i + 1][0]
            # Overlap should be approximately 50 chars
            assert current_end - next_start >= 40, "next_start must be greater than zero"

    def test_invalid_params(self):
        """Test invalid parameters"""
        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=0)

        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=100, overlap=-1)

        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=100, overlap=100)


@_skip_real_st_models
class TestEmbedChunks:
    """Tests for embed_chunks function"""

    def test_basic_embedding(self):
        """Test basic embedding generation"""
        text = "This is a test sentence. " * 10
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        embeddings = embed_chunks(chunks)

        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == len(chunks), "Embeddings must not be empty"
        assert embeddings.shape[1] > 0, "Value must be greater than zero"

    def test_empty_chunks(self):
        """Test embedding empty chunks"""
        embeddings = embed_chunks([])
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 0, "Embeddings must not be empty"

    def test_custom_model_profile(self):
        """Test with custom model profile"""
        chunks = [
            (0, 10, "Test text"),
            (10, 20, "More text"),
        ]
        model_profile = {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "cache_dir": None,
        }
        embeddings = embed_chunks(chunks, model_profile=model_profile)

        assert len(embeddings) == 2, "Embeddings must not be empty"
        assert embeddings.shape[1] == 384, "Condition must be true"


class TestPersistAndLoadIndex:
    """Tests for persist_index and load_index functions"""

    def test_persist_and_load(self):
        """Test persisting and loading an index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test data
            chunks = [
                (0, 10, "First chunk of text"),
                (10, 20, "Second chunk of text"),
                (20, 30, "Third chunk of text"),
            ]
            embeddings = np.random.randn(3, 384).astype(np.float32)

            # Persist index
            index_path = persist_index(
                index_name="test_index",
                embeddings=embeddings,
                chunks=chunks,
                metadata={"test": "metadata"},
                tenant_id="test_tenant",
                index_dir=tmpdir,
            )

            assert index_path.exists(), "Condition must be true"
            assert (index_path / "index.faiss").exists(), "Condition must be true"
            assert (index_path / "chunks.json").exists(), "Condition must be true"
            assert (index_path / "metadata.json").exists(), "Data must not be empty"

            # Load index
            loaded_index, loaded_chunks, loaded_metadata = load_index(
                index_name="test_index",
                tenant_id="test_tenant",
                index_dir=tmpdir,
            )

            assert loaded_index is not None, "loaded_index must be initialized"
            assert loaded_index.ntotal == 3, "ntotal is not valid"
            assert len(loaded_chunks) == 3, "Loaded_chunks must not be empty"
            assert loaded_metadata["test"] == "metadata", "Data must not be empty"
            assert loaded_metadata["index_name"] == "test_index", "Data must not be empty"

    def test_load_nonexistent_index(self):
        """Test loading non-existent index"""
        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(FileNotFoundError):
            load_index(
                index_name="nonexistent",
                tenant_id="test",
                index_dir=tmpdir,
            )

    def test_persist_empty_embeddings(self):
        """Test persisting empty embeddings raises error"""
        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ValueError):
            persist_index(
                index_name="test",
                embeddings=np.array([]),
                chunks=[],
                tenant_id="test",
                index_dir=tmpdir,
            )

    def test_persist_mismatched_data(self):
        """Test persisting with mismatched embeddings and chunks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = np.random.randn(3, 384).astype(np.float32)
            chunks = [(0, 10, "Only one chunk")]

            with pytest.raises(ValueError):
                persist_index(
                    index_name="test",
                    embeddings=embeddings,
                    chunks=chunks,
                    tenant_id="test",
                    index_dir=tmpdir,
                )


@_skip_real_st_models
class TestBuildIndexFromFiles:
    """Tests for build_index_from_files function"""

    def test_build_from_sample_files(self):
        """Test building index from sample files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create sample corpus
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            files = []
            for i in range(3):
                file_path = docs_dir / f"doc{i}.txt"
                with open(file_path, "w") as f:
                    f.write(f"Document {i} content. " * 50)
                files.append(file_path)

            # Build index
            index_dir = tmpdir / "indices"
            index_path = build_index_from_files(
                files=files,
                index_name="test_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=200,
                overlap=50,
            )

            assert index_path.exists(), "Condition must be true"
            assert (index_path / "index.faiss").exists(), "Condition must be true"

            # Load and verify
            loaded_index, chunks, metadata = load_index(
                index_name="test_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            assert loaded_index.ntotal > 0, "ntotal must be greater than zero"
            assert len(chunks) > 0, "Chunks must not be empty"
            assert metadata["total_files"] == 3, "Data must not be empty"
            assert metadata["total_chunks"] > 0, "Value must be greater than zero"

    def test_build_from_empty_list(self):
        """Test building index from empty file list"""
        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ValueError):
            build_index_from_files(
                files=[],
                index_name="test",
                tenant_id="test",
                index_dir=tmpdir,
            )

    def test_build_with_nonexistent_file(self):
        """Test building index with non-existent file (should skip)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create one valid file
            valid_file = tmpdir / "valid.txt"
            with open(valid_file, "w") as f:
                f.write("Valid content. " * 100)

            # Include non-existent file
            files = [valid_file, tmpdir / "nonexistent.txt"]

            # Should skip non-existent and process valid
            index_dir = tmpdir / "indices"
            index_path = build_index_from_files(
                files=files,
                index_name="test",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            assert index_path.exists(), "Condition must be true"
            loaded_index, _, _ = load_index(
                index_name="test",
                tenant_id="test",
                index_dir=str(index_dir),
            )
            assert loaded_index.ntotal > 0, "ntotal must be greater than zero"


@_skip_real_st_models
class TestEndToEnd:
    """End-to-end integration tests"""

    def test_full_workflow(self):
        """Test complete workflow: create corpus, build index, query"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create sample corpus with different topics
            docs_dir = tmpdir / "docs"
            docs_dir.mkdir()

            corpus = [
                ("python.txt", "Python is a programming language. " * 30),
                (
                    "machine_learning.txt",
                    "Machine learning uses algorithms and data. " * 30,
                ),
                ("cooking.txt", "Cooking involves recipes and ingredients. " * 30),
            ]

            files = []
            for filename, content in corpus:
                file_path = docs_dir / filename
                with open(file_path, "w") as f:
                    f.write(content)
                files.append(file_path)

            # Build index
            index_dir = tmpdir / "indices"
            index_path = build_index_from_files(
                files=files,
                index_name="test_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
                chunk_size=500,
                overlap=100,
            )

            # Verify index was created
            assert index_path.exists(), "Condition must be true"

            # Load and inspect
            index, chunks, metadata = load_index(
                index_name="test_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            assert index.ntotal > 0, "ntotal must be greater than zero"
            assert len(chunks) > 0, "Chunks must not be empty"
            assert all("text" in chunk for chunk in chunks), "Condition must be true"
            assert metadata["total_files"] == 3, "Data must not be empty"


class TestIndexerEdgeCases:
    """Additional edge case tests for indexer"""

    def test_chunk_text_with_various_delimiters(self):
        """Test chunking with different sentence delimiters"""
        text = "First sentence.\nSecond sentence! Third sentence? Fourth sentence. "
        chunks = chunk_text(text, chunk_size=30, overlap=10)

        assert len(chunks) > 0, "Chunks must not be empty"

    def test_chunk_text_with_no_delimiters(self):
        """Test chunking text with no sentence delimiters"""
        text = "a" * 500
        chunks = chunk_text(text, chunk_size=100, overlap=20)

        assert len(chunks) > 0, "Chunks must not be empty"

    def test_persist_index_with_extensive_metadata(self):
        """Test persisting index with rich metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            chunks = [(0, 10, "Test")]
            embeddings = np.random.randn(1, 384).astype(np.float32)

            metadata = {
                "source": "test_source",
                "version": "1.0",
                "tags": ["test", "sample"],
            }

            _ = persist_index(
                index_name="rich_meta",
                embeddings=embeddings,
                chunks=chunks,
                metadata=metadata,
                tenant_id="test",
                index_dir=tmpdir,
            )

            _, _, loaded_meta = load_index(
                index_name="rich_meta",
                tenant_id="test",
                index_dir=tmpdir,
            )

            assert loaded_meta["source"] == "test_source", "Condition must be true"
            assert loaded_meta["version"] == "1.0", "Condition must be true"

    def test_load_index_with_missing_chunks_file(self):
        """Test loading index when chunks.json is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            chunks = [(0, 10, "Test")]
            embeddings = np.random.randn(1, 384).astype(np.float32)

            index_path = persist_index(
                index_name="partial",
                embeddings=embeddings,
                chunks=chunks,
                tenant_id="test",
                index_dir=tmpdir,
            )

            chunks_file = index_path / "chunks.json"
            chunks_file.unlink()

            index, loaded_chunks, _ = load_index(
                index_name="partial",
                tenant_id="test",
                index_dir=tmpdir,
            )

            assert index is not None, "index must be initialized"
            assert len(loaded_chunks) == 0, "Loaded_chunks must not be empty"


class TestManageTenantIndices:
    """Tests for manage_tenant_indices function"""

    def test_invalid_operation(self):
        """Test with invalid operation"""
        pytest.importorskip("codex.rag.indexer", reason="manage_tenant_indices not available")
        from codex.rag.indexer import manage_tenant_indices

        with tempfile.TemporaryDirectory() as tmpdir:
            result = manage_tenant_indices(
                tenant_id="test", operation="invalid_op", index_names=["idx1"], index_dir=tmpdir
            )
            assert not result.success, "Result must not be empty"
            assert "Invalid operation" in result.message, "Result must not be empty"

    def test_create_missing_files(self):
        """Test CREATE operation without files parameter"""
        pytest.importorskip("codex.rag.indexer", reason="manage_tenant_indices not available")
        from codex.rag.indexer import manage_tenant_indices

        with tempfile.TemporaryDirectory() as tmpdir:
            result = manage_tenant_indices(
                tenant_id="test", operation="create", index_names=["idx1"], index_dir=tmpdir
            )
            assert not result.success, "Result must not be empty"
            assert "requires 'files' parameter" in result.message, "Result must not be empty"

    def test_list_empty(self):
        """Test LIST operation with no indices"""
        pytest.importorskip("codex.rag.indexer", reason="manage_tenant_indices not available")
        from codex.rag.indexer import manage_tenant_indices

        with tempfile.TemporaryDirectory() as tmpdir:
            result = manage_tenant_indices(
                tenant_id="test", operation="list", index_names=[], index_dir=tmpdir
            )
            assert result.success, "Result must not be empty"
            assert len(result.index_names) == 0, "Collection must not be empty"

    def test_delete_nonexistent(self):
        """Test DELETE operation on non-existent index"""
        pytest.importorskip("codex.rag.indexer", reason="manage_tenant_indices not available")
        from codex.rag.indexer import manage_tenant_indices

        with tempfile.TemporaryDirectory() as tmpdir:
            result = manage_tenant_indices(
                tenant_id="test", operation="delete", index_names=["nonexistent"], index_dir=tmpdir
            )
            assert not result.success, "Result must not be empty"

    def test_merge_missing_param(self):
        """Test MERGE operation without merge_name"""
        pytest.importorskip("codex.rag.indexer", reason="manage_tenant_indices not available")
        from codex.rag.indexer import manage_tenant_indices

        with tempfile.TemporaryDirectory() as tmpdir:
            result = manage_tenant_indices(
                tenant_id="test", operation="merge", index_names=["idx1", "idx2"], index_dir=tmpdir
            )
            assert not result.success, "Result must not be empty"
            assert "requires 'merge_name' parameter" in result.message, "Result must not be empty"

    def test_update_missing_files(self):
        """Test UPDATE operation without files parameter"""
        pytest.importorskip("codex.rag.indexer", reason="manage_tenant_indices not available")
        from codex.rag.indexer import manage_tenant_indices

        with tempfile.TemporaryDirectory() as tmpdir:
            result = manage_tenant_indices(
                tenant_id="test", operation="update", index_names=["idx1"], index_dir=tmpdir
            )
            assert not result.success, "Result must not be empty"
            assert "requires 'files' parameter" in result.message, "Result must not be empty"


@_skip_real_st_models
class TestEmbedChunksErrorPaths:
    """Error path tests for embed_chunks function"""

    def test_embed_chunks_empty_returns_empty_array(self):
        """Test embed_chunks with empty chunks returns empty array"""
        embeddings = embed_chunks([])
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 0, "Embeddings must not be empty"

    def test_embed_chunks_import_error_coverage(self):
        """
        Test to exercise ImportError path in embed_chunks.
        Note: We can't easily test ImportError without breaking the module,
        but we document that lines 87-92 handle ImportError gracefully.
        This test verifies embed_chunks works when dependencies ARE available.
        """
        chunks = [(0, 10, "Test text for embedding")]
        embeddings = embed_chunks(chunks)
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 1, "Embeddings must not be empty"
        assert embeddings.shape[1] > 0, "Value must be greater than zero"


class TestLoadIndexErrorPaths:
    """Error path tests for load_index function"""

    def test_load_index_file_not_found(self):
        """Test load_index with non-existent index directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to load non-existent index
            with pytest.raises(FileNotFoundError, match="Index not found"):
                load_index(
                    index_name="nonexistent",
                    tenant_id="test",
                    index_dir=tmpdir,
                )

    def test_load_index_missing_faiss_file(self):
        """Test load_index when FAISS file is missing (line 247)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create index directory structure but without FAISS file
            index_path = tmpdir / "test" / "test_index"
            index_path.mkdir(parents=True)

            # Create metadata files but not index.faiss
            with open(index_path / "chunks.json", "w") as f:
                json.dump([], f)
            with open(index_path / "metadata.json", "w") as f:
                json.dump({}, f)

            # Should raise FileNotFoundError for missing FAISS file
            with pytest.raises(FileNotFoundError, match="FAISS index file not found"):
                load_index(
                    index_name="test_index",
                    tenant_id="test",
                    index_dir=tmpdir,
                )

    def test_load_index_corrupted_metadata_json(self):
        """Test load_index with corrupted metadata.json (line 266)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid index first
            chunks = [(0, 10, "Test")]
            embeddings = np.random.randn(1, 384).astype(np.float32)

            index_path = persist_index(
                index_name="test",
                embeddings=embeddings,
                chunks=chunks,
                tenant_id="test",
                index_dir=tmpdir,
            )

            # Corrupt the metadata.json
            metadata_file = index_path / "metadata.json"
            with open(metadata_file, "w") as f:
                f.write("{invalid json content")

            # Should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                load_index(
                    index_name="test",
                    tenant_id="test",
                    index_dir=tmpdir,
                )

    def test_load_index_corrupted_chunks_json(self):
        """Test load_index with corrupted chunks.json"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid index first
            chunks = [(0, 10, "Test")]
            embeddings = np.random.randn(1, 384).astype(np.float32)

            index_path = persist_index(
                index_name="test",
                embeddings=embeddings,
                chunks=chunks,
                tenant_id="test",
                index_dir=tmpdir,
            )

            # Corrupt the chunks.json
            chunks_file = index_path / "chunks.json"
            with open(chunks_file, "w") as f:
                f.write("{invalid json")

            # Should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                load_index(
                    index_name="test",
                    tenant_id="test",
                    index_dir=tmpdir,
                )

    def test_load_index_corrupted_faiss_index(self):
        """Test load_index with corrupted FAISS index file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create index directory structure
            index_path = tmpdir / "test" / "test_index"
            index_path.mkdir(parents=True)

            # Create a corrupted FAISS file
            faiss_file = index_path / "index.faiss"
            with open(faiss_file, "wb") as f:
                f.write(b"corrupted data")

            # Create valid JSON files
            with open(index_path / "chunks.json", "w") as f:
                json.dump([], f)
            with open(index_path / "metadata.json", "w") as f:
                json.dump({}, f)

            # Should raise exception when reading corrupted FAISS index
            with pytest.raises(Exception):  # FAISS will raise various exceptions
                load_index(
                    index_name="test_index",
                    tenant_id="test",
                    index_dir=tmpdir,
                )

    def test_load_index_missing_metadata_file(self):
        """Test load_index when metadata.json is missing (should use empty dict)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid index first
            chunks = [(0, 10, "Test")]
            embeddings = np.random.randn(1, 384).astype(np.float32)

            index_path = persist_index(
                index_name="test",
                embeddings=embeddings,
                chunks=chunks,
                tenant_id="test",
                index_dir=tmpdir,
            )

            # Remove metadata.json
            metadata_file = index_path / "metadata.json"
            metadata_file.unlink()

            # Should load successfully with empty metadata
            index, loaded_chunks, metadata = load_index(
                index_name="test",
                tenant_id="test",
                index_dir=tmpdir,
            )

            assert index is not None, "index must be initialized"
            assert len(loaded_chunks) == 1, "Loaded_chunks must not be empty"
            assert metadata == {}, "Data must not be empty"
