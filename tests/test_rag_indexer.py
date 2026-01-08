"""
Tests for RAG Indexer Module
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

# Skip tests if dependencies not available
pytest.importorskip("sentence_transformers")
pytest.importorskip("faiss")

from codex.rag.indexer import (
    build_index_from_files,
    chunk_text,
    embed_chunks,
    load_index,
    persist_index,
)


class TestChunkText:
    """Tests for chunk_text function"""

    def test_basic_chunking(self):
        """Test basic text chunking"""
        text = "This is a test. " * 100  # ~1600 chars
        chunks = chunk_text(text, chunk_size=500, overlap=50)

        assert len(chunks) > 0
        assert all(len(chunk[2]) <= 500 for chunk in chunks)
        assert all(isinstance(chunk, tuple) for chunk in chunks)
        assert all(len(chunk) == 3 for chunk in chunks)

    def test_empty_text(self):
        """Test chunking empty text"""
        chunks = chunk_text("", chunk_size=100, overlap=10)
        assert len(chunks) == 0

    def test_small_text(self):
        """Test chunking text smaller than chunk_size"""
        text = "Small text"
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0][2] == text

    def test_overlap(self):
        """Test that chunks have proper overlap"""
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=200, overlap=50)

        assert len(chunks) > 1
        # Check positions show overlap
        for i in range(len(chunks) - 1):
            current_end = chunks[i][1]
            next_start = chunks[i + 1][0]
            # Overlap should be approximately 50 chars
            assert current_end - next_start >= 40  # Allow some variance

    def test_invalid_params(self):
        """Test invalid parameters"""
        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=0)

        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=100, overlap=-1)

        with pytest.raises(ValueError):
            chunk_text("test", chunk_size=100, overlap=100)


class TestEmbedChunks:
    """Tests for embed_chunks function"""

    def test_basic_embedding(self):
        """Test basic embedding generation"""
        text = "This is a test sentence. " * 10
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        embeddings = embed_chunks(chunks)

        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == len(chunks)
        assert embeddings.shape[1] > 0  # Has embedding dimension

    def test_empty_chunks(self):
        """Test embedding empty chunks"""
        embeddings = embed_chunks([])
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 0

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

        assert len(embeddings) == 2
        assert embeddings.shape[1] == 384  # Expected dimension for this model


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

            assert index_path.exists()
            assert (index_path / "index.faiss").exists()
            assert (index_path / "chunks.json").exists()
            assert (index_path / "metadata.json").exists()

            # Load index
            loaded_index, loaded_chunks, loaded_metadata = load_index(
                index_name="test_index",
                tenant_id="test_tenant",
                index_dir=tmpdir,
            )

            assert loaded_index is not None
            assert loaded_index.ntotal == 3
            assert len(loaded_chunks) == 3
            assert loaded_metadata["test"] == "metadata"
            assert loaded_metadata["index_name"] == "test_index"

    def test_load_nonexistent_index(self):
        """Test loading non-existent index"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                load_index(
                    index_name="nonexistent",
                    tenant_id="test",
                    index_dir=tmpdir,
                )

    def test_persist_empty_embeddings(self):
        """Test persisting empty embeddings raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
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

            assert index_path.exists()
            assert (index_path / "index.faiss").exists()

            # Load and verify
            loaded_index, chunks, metadata = load_index(
                index_name="test_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            assert loaded_index.ntotal > 0
            assert len(chunks) > 0
            assert metadata["total_files"] == 3
            assert metadata["total_chunks"] > 0

    def test_build_from_empty_list(self):
        """Test building index from empty file list"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
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

            assert index_path.exists()
            loaded_index, _, _ = load_index(
                index_name="test",
                tenant_id="test",
                index_dir=str(index_dir),
            )
            assert loaded_index.ntotal > 0


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
            assert index_path.exists()

            # Load and inspect
            index, chunks, metadata = load_index(
                index_name="test_corpus",
                tenant_id="test",
                index_dir=str(index_dir),
            )

            assert index.ntotal > 0
            assert len(chunks) > 0
            assert all("text" in chunk for chunk in chunks)
            assert metadata["total_files"] == 3
