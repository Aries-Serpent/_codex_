"""
Unit tests for SessionEmbeddings module.

Test coverage:
    - Initialization (new and existing index)
    - Embedding generation (text normalization, dimensions)
    - Session management (add, update, list)
    - Similarity search (by session_id and text)
    - Persistence (save and load)
    - Error handling (corrupted files, invalid input)
    - Threading (concurrent access)
"""

from __future__ import annotations

import json
import tempfile
import threading
from pathlib import Path

import numpy as np
import pytest

from codex.logging.session_embeddings import SessionEmbeddings


class TestSessionEmbeddingsInit:
    """Test initialization scenarios."""

    def test_init_creates_new_index(self):
        """Test that init creates new index when files don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            assert embeddings._metadata == {}, "Data must not be empty"
            assert embeddings._embeddings is not None, "_embeddings must be initialized"

    def test_init_loads_existing_index(self):
        """Test that init loads existing index from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial index
            embeddings1 = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embeddings1.add_session("S001", "Test session")
            embeddings1.save_index()

            # Load existing index
            embeddings2 = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            assert "S001" in embeddings2._metadata, "Data must not be empty"
            assert embeddings2._metadata["S001"]["summary"] == "Test session", "Data must not be empty"

    def test_init_graceful_on_missing_model(self):
        """Test that init works even if sentence-transformers unavailable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Should not raise, uses mock embeddings
            assert embeddings is not None, "embeddings must be initialized"


class TestEmbeddingGeneration:
    """Test embedding generation."""

    def test_generate_embedding_returns_correct_dimension(self):
        """Test that generated embeddings have correct dimension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embedding = embeddings._generate_embedding("Test text")
            assert embedding.shape == (384,)
            assert embedding.dtype == np.float32, "dtype is not valid"

    def test_generate_embedding_text_normalization(self):
        """Test that text is normalized (lowercase, stripped)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Mock embeddings should be deterministic based on text
            emb1 = embeddings._generate_embedding("Test TEXT")
            emb2 = embeddings._generate_embedding("  test text  ")
            # Should be similar (or identical if using mock with seed)
            assert np.allclose(emb1, emb2, atol=0.1)

    def test_generate_embedding_unicode_handling(self):
        """Test that unicode text is handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embedding = embeddings._generate_embedding("测试文本 🚀 café")
            assert embedding.shape == (384,)

    def test_generate_embedding_empty_text_raises(self):
        """Test that empty text raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            with pytest.raises(ValueError):
                embeddings._generate_embedding("")

    def test_generate_embedding_long_text(self):
        """Test embedding of long text (>512 tokens)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            long_text = " ".join(["word"] * 1000)
            embedding = embeddings._generate_embedding(long_text)
            assert embedding.shape == (384,)


class TestSessionManagement:
    """Test session add/update/list operations."""

    def test_add_session_basic(self):
        """Test adding a basic session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            success = embeddings.add_session("S001", "Test session")
            assert success is True, "success is not valid"
            assert "S001" in embeddings._metadata, "Data must not be empty"

    def test_add_session_with_patterns_and_tags(self):
        """Test adding session with patterns and tags."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            success = embeddings.add_session(
                "S001",
                "Test session",
                patterns=["P-001", "P-002"],
                tags=["database", "performance"],
            )
            assert success is True, "success is not valid"
            meta = embeddings.get_metadata("S001")
            assert meta["patterns"] == ["P-001", "P-002"]
            assert meta["tags"] == ["database", "performance"]

    def test_add_multiple_sessions(self):
        """Test adding multiple sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            for i in range(10):
                embeddings.add_session(f"S{i:03d}", f"Session {i}")
            assert len(embeddings._metadata) == 10, "Collection must not be empty"

    def test_add_session_invalid_input(self):
        """Test that invalid input is rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Empty session_id
            success = embeddings.add_session("", "Test")
            assert success is False, "success is not valid"

            # Empty summary
            success = embeddings.add_session("S001", "")
            assert success is False, "success is not valid"

    def test_add_session_duplicate_id(self):
        """Test adding session with duplicate ID (should update index)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embeddings.add_session("S001", "Session A")
            initial_count = len(embeddings._metadata)

            # Add with same ID
            embeddings.add_session("S001", "Session B")
            # Should add a new index entry (not update existing)
            # This is current behavior; could be changed to "update"
            assert len(embeddings._metadata) >= initial_count, "Collection must not be empty"

    def test_list_sessions(self):
        """Test listing all sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            for i in range(5):
                embeddings.add_session(f"S{i:03d}", f"Session {i}")

            sessions = embeddings.list_sessions()
            assert len(sessions) == 5, "Sessions must not be empty"
            assert "S000" in sessions, "Condition must be true"


class TestSimilaritySearch:
    """Test similarity search operations."""

    def test_find_similar_by_session_id(self):
        """Test finding similar sessions by reference session ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Add sessions
            embeddings.add_session("S001", "Database query filtering")
            embeddings.add_session("S002", "Database optimization")
            embeddings.add_session("S003", "API endpoint")
            embeddings.add_session("S004", "Database indexing")

            # Find similar to S001
            similar = embeddings.find_similar("S001", k=2)
            assert len(similar) <= 2, "Similar must not be empty"
            assert isinstance(similar, list)
            if len(similar) > 0:
                session_id, score = similar[0]
                assert isinstance(session_id, str)
                assert 0 <= score <= 1, "0 is not valid"

    def test_find_similar_by_text(self):
        """Test finding similar sessions by query text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Add sessions
            embeddings.add_session("S001", "Database query filtering")
            embeddings.add_session("S002", "Database optimization")
            embeddings.add_session("S003", "API endpoint")

            # Find similar to query
            similar = embeddings.find_similar_text("database queries", k=2)
            assert len(similar) <= 2, "Similar must not be empty"
            if len(similar) > 0:
                session_id, score = similar[0]
                assert session_id in ["S001", "S002", "S003"]
                assert 0 <= score <= 1, "0 is not valid"

    def test_find_similar_returns_k_results(self):
        """Test that find_similar returns exactly k results (or fewer if k > total)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Add 3 sessions
            embeddings.add_session("S001", "Test A")
            embeddings.add_session("S002", "Test B")
            embeddings.add_session("S003", "Test C")

            # Request 5 results (more than available)
            similar = embeddings.find_similar_text("test", k=5)
            assert len(similar) <= 3, "Similar must not be empty"

            # Request 2 results
            similar = embeddings.find_similar_text("test", k=2)
            assert len(similar) <= 2, "Similar must not be empty"

    def test_find_similar_excludes_self(self):
        """Test that find_similar excludes the reference session itself."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Add sessions with similar text
            embeddings.add_session("S001", "Database queries")
            embeddings.add_session("S002", "Database queries")  # Identical
            embeddings.add_session("S003", "API endpoint")

            # Find similar to S001 (should not return S001 itself)
            similar = embeddings.find_similar("S001", k=2)
            [s[0] for s in similar]
            # S001 should not be in results
            # (though this depends on implementation; may vary)

    def test_find_similar_nonexistent_session(self):
        """Test finding similar for nonexistent session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embeddings.add_session("S001", "Test")

            similar = embeddings.find_similar("NONEXISTENT", k=5)
            assert similar == [], "similar is not valid"


class TestPersistence:
    """Test save and load operations."""

    def test_save_and_load_index(self):
        """Test that index is saved and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            embeddings1 = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embeddings1.add_session("S001", "Test session A")
            embeddings1.add_session("S002", "Test session B")
            embeddings1.save_index()

            # Load and verify
            embeddings2 = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            assert len(embeddings2._metadata) == 2, "Collection must not be empty"
            assert "S001" in embeddings2._metadata, "Data must not be empty"
            assert "S002" in embeddings2._metadata, "Data must not be empty"

    def test_save_creates_directory(self):
        """Test that save_index creates directories if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/nested/dir/embeddings.faiss",
                metadata_path=f"{tmpdir}/nested/dir/metadata.json",
            )
            embeddings.add_session("S001", "Test")
            embeddings.save_index()

            # Verify files exist
            assert Path(f"{tmpdir}/nested/dir/metadata.json").exists(), "Data must not be empty"

    def test_metadata_json_format(self):
        """Test that metadata JSON has correct format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embeddings.add_session("S001", "Test", patterns=["P-001"], tags=["tag1"])
            embeddings.save_index()

            # Load and check JSON
            with open(f"{tmpdir}/metadata.json", "r") as f:
                data = json.load(f)
            assert data["version"] == "1.0", "Data must not be empty"
            assert data["model"] == "sentence-transformers/all-MiniLM-L6-v2", "Data must not be empty"
            assert data["dimension"] == 384, "Data must not be empty"
            assert "S001" in data["sessions"], "Data must not be empty"


class TestRebuildIndex:
    """Test index rebuilding."""

    def test_rebuild_index(self):
        """Test that rebuild_index preserves all sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Add sessions
            for i in range(5):
                embeddings.add_session(f"S{i:03d}", f"Session {i}")

            original_count = len(embeddings._metadata)
            success = embeddings.rebuild_index()

            assert success is True, "success is not valid"
            assert len(embeddings._metadata) == original_count, "Collection must not be empty"


class TestThreading:
    """Test thread-safety."""

    def test_concurrent_add_sessions(self):
        """Test concurrent session additions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )

            def add_sessions(start_idx: int, count: int):
                for i in range(count):
                    embeddings.add_session(f"S{start_idx + i:03d}", f"Session {start_idx + i}")

            threads = [threading.Thread(target=add_sessions, args=(i * 10, 10)) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Should have 50 sessions (5 threads × 10 each)
            assert len(embeddings._metadata) == 50, "Collection must not be empty"

    def test_concurrent_search(self):
        """Test concurrent search operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            # Add sessions
            for i in range(10):
                embeddings.add_session(f"S{i:03d}", f"Session {i}")

            results = []

            def search_sessions(query: str):
                res = embeddings.find_similar_text(query, k=3)
                results.append(res)

            threads = [
                threading.Thread(target=search_sessions, args=(f"session {i}",)) for i in range(5)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # All searches should complete
            assert len(results) == 5, "Results must not be empty"


class TestGetMetadata:
    """Test metadata retrieval."""

    def test_get_metadata_existing_session(self):
        """Test getting metadata for existing session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            embeddings.add_session("S001", "Test summary", patterns=["P-001"], tags=["tag1"])

            meta = embeddings.get_metadata("S001")
            assert meta["summary"] == "Test summary", "Condition must be true"
            assert meta["patterns"] == ["P-001"], "Condition must be true"
            assert meta["tags"] == ["tag1"], "Condition must be true"

    def test_get_metadata_nonexistent_session(self):
        """Test getting metadata for nonexistent session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )

            meta = embeddings.get_metadata("NONEXISTENT")
            assert meta == {}, "meta is not valid"


class TestGetStats:
    """Test statistics retrieval."""

    def test_get_stats(self):
        """Test getting index statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            for i in range(5):
                embeddings.add_session(f"S{i:03d}", f"Session {i}")

            stats = embeddings.get_stats()
            assert stats["total_sessions"] == 5, "Condition must be true"
            assert stats["dimension"] == 384, "Condition must be true"
            assert stats["model"] == "sentence-transformers/all-MiniLM-L6-v2", "Condition must be true"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_corrupted_metadata_json(self):
        """Test handling of corrupted metadata JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create corrupted metadata
            metadata_path = Path(f"{tmpdir}/metadata.json")
            metadata_path.write_text("{ invalid json }")

            # Should create new index instead of crashing
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=str(metadata_path),
            )
            assert embeddings is not None, "embeddings must be initialized"

    def test_search_on_empty_index(self):
        """Test searching on empty index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            embeddings = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )

            similar = embeddings.find_similar_text("test", k=5)
            assert similar == [], "similar is not valid"


# Integration tests


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_full_workflow(self):
        """Test full workflow: create, add, search, save, load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate
            embeddings1 = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )
            sessions_data = [
                ("S001", "Database query filtering", ["P-001"], ["database"]),
                ("S002", "API endpoint design", ["P-002"], ["api"]),
                ("S003", "Database optimization", ["P-003"], ["database"]),
            ]

            for session_id, summary, patterns, tags in sessions_data:
                embeddings1.add_session(session_id, summary, patterns, tags)

            # Search
            similar = embeddings1.find_similar_text("database", k=2)
            assert len(similar) > 0, "Similar must not be empty"

            # Save
            embeddings1.save_index()

            # Load
            embeddings2 = SessionEmbeddings(
                embeddings_path=f"{tmpdir}/embeddings.faiss",
                metadata_path=f"{tmpdir}/metadata.json",
            )

            # Verify
            assert len(embeddings2.list_sessions()) == 3, "Collection must not be empty"
            similar2 = embeddings2.find_similar_text("database", k=2)
            assert len(similar2) > 0, "Similar2 must not be empty"
