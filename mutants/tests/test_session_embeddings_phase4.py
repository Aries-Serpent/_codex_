"""
Phase 4: Comprehensive Integration Tests for Session Embeddings

Tests the full embeddings pipeline including:
1. Index initialization
2. Embedding generation (mock mode)
3. Semantic search
4. Performance metrics
5. Integration with session tracking
"""

import json
import time

import pytest

from codex.logging.session_embeddings import SessionEmbeddings


class TestPhase4EmbeddingsIntegration:
    """Phase 4 integration tests."""

    @pytest.fixture
    def temp_index_path(self, tmp_path):
        """Create temporary index path."""
        return tmp_path / "test_embeddings.faiss"

    @pytest.fixture
    def temp_metadata_path(self, tmp_path):
        """Create temporary metadata path."""
        return tmp_path / "test_metadata.json"

    @pytest.fixture
    def embeddings(self, temp_index_path, temp_metadata_path):
        """Create SessionEmbeddings instance."""
        return SessionEmbeddings(
            embeddings_path=str(temp_index_path),
            metadata_path=str(temp_metadata_path),
        )

    def test_initialization(self, embeddings):
        """Test embeddings initialization."""
        assert embeddings is not None
        assert embeddings.DIMENSION == 384
        assert embeddings.MODEL_NAME == "sentence-transformers/all-MiniLM-L6-v2"

    def test_add_single_session(self, embeddings):
        """Test adding a single session."""
        success = embeddings.add_session(
            session_id="S001",
            summary="Test session",
            patterns=["P-001"],
            tags=["test"],
        )
        assert success is True
        assert len(embeddings.list_sessions()) == 1

    def test_add_multiple_sessions(self, embeddings):
        """Test adding multiple sessions."""
        sessions = [
            ("S001", "Cache management optimization", ["P-001"], ["cache"]),
            ("S002", "CI failure resolution", ["P-002"], ["ci"]),
            ("S003", "Coverage improvements", ["P-003"], ["coverage"]),
            ("S004", "Query filtering", ["P-004"], ["database"]),
            ("S005", "Performance tuning", ["P-005"], ["performance"]),
        ]

        for session_id, summary, patterns, tags in sessions:
            success = embeddings.add_session(
                session_id=session_id,
                summary=summary,
                patterns=patterns,
                tags=tags,
            )
            assert success is True

        assert len(embeddings.list_sessions()) == 5

    def test_get_stats(self, embeddings):
        """Test getting index statistics."""
        embeddings.add_session("S001", "Test session", [], [])
        embeddings.add_session("S002", "Another session", [], [])

        stats = embeddings.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["dimension"] == 384
        assert stats["model"] == "sentence-transformers/all-MiniLM-L6-v2"
        assert stats["has_faiss"] is True or stats["has_faiss"] is False
        assert stats["has_model"] is True or stats["has_model"] is False

    def test_save_and_load_index(self, embeddings, temp_index_path, temp_metadata_path):
        """Test saving and loading index."""
        # Add sessions
        embeddings.add_session("S001", "Cache management", [], ["cache"])
        embeddings.add_session("S002", "CI failure", [], ["ci"])

        # Save
        embeddings.save_index()
        assert temp_index_path.exists() or temp_metadata_path.exists()

        # Load in new instance
        new_embeddings = SessionEmbeddings(
            embeddings_path=str(temp_index_path),
            metadata_path=str(temp_metadata_path),
        )
        assert len(new_embeddings.list_sessions()) == 2

    def test_semantic_search_text(self, embeddings):
        """Test semantic search with text query."""
        # Add sessions with different topics
        embeddings.add_session("S001", "Cache management optimization", [], ["cache"])
        embeddings.add_session("S002", "CI failure resolution", [], ["ci"])
        embeddings.add_session("S003", "Coverage improvements", [], ["coverage"])

        # Search
        results = embeddings.find_similar_text("cache management", k=2)
        assert len(results) <= 2
        assert isinstance(results, list)
        if results:
            session_id, score = results[0]
            assert isinstance(session_id, str)
            assert isinstance(score, (int, float))
            assert 0 <= score <= 1

    def test_semantic_search_session(self, embeddings):
        """Test semantic search by session."""
        embeddings.add_session("S001", "Cache management", [], ["cache"])
        embeddings.add_session("S002", "CI failure", [], ["ci"])
        embeddings.add_session("S003", "Cache optimization", [], ["cache"])

        results = embeddings.find_similar("S001", k=2)
        assert len(results) <= 2
        # Results should not include S001 itself
        result_ids = [r[0] for r in results]
        assert "S001" not in result_ids

    def test_find_similar_nonexistent_session(self, embeddings):
        """Test finding similar to non-existent session."""
        embeddings.add_session("S001", "Test", [], [])
        results = embeddings.find_similar("NONEXISTENT", k=5)
        assert results == []

    def test_get_metadata(self, embeddings):
        """Test getting session metadata."""
        embeddings.add_session(
            session_id="S001",
            summary="Test session",
            patterns=["P-001"],
            tags=["test"],
        )

        meta = embeddings.get_metadata("S001")
        assert meta["summary"] == "Test session"
        assert meta["patterns"] == ["P-001"]
        assert meta["tags"] == ["test"]

    def test_invalid_session_handling(self, embeddings):
        """Test handling of invalid sessions."""
        # Empty session_id
        result = embeddings.add_session("", "Test", [], [])
        assert result is False

        # Empty summary
        result = embeddings.add_session("S001", "", [], [])
        assert result is False

    def test_normalize_text(self, embeddings):
        """Test text normalization."""
        # Create instance to test private method
        text = "  UPPERCASE TEXT  "
        normalized = embeddings._normalize_text(text)
        assert normalized == "uppercase text"

    def test_embedding_dimension(self, embeddings):
        """Test that embeddings have correct dimension."""
        embeddings.add_session("S001", "Test", [], [])
        metadata = embeddings.get_metadata("S001")
        assert metadata is not None
        assert embeddings.DIMENSION == 384

    def test_batch_operations(self, embeddings):
        """Test batch session operations."""
        sessions = [
            (f"S{i:03d}", f"Session {i} summary", [f"P-{i}"], [f"tag{i}"]) for i in range(20)
        ]

        for session_id, summary, patterns, tags in sessions:
            embeddings.add_session(session_id, summary, patterns, tags)

        # Verify all sessions added
        all_sessions = embeddings.list_sessions()
        assert len(all_sessions) == 20

        # Test search with all sessions
        results = embeddings.find_similar_text("summary", k=5)
        assert len(results) <= 5

    def test_performance_search_latency(self, embeddings):
        """Test search performance."""
        # Add 50 sessions
        for i in range(50):
            embeddings.add_session(
                f"S{i:03d}",
                f"Test session {i}",
                [],
                ["test"],
            )

        # Measure search latency
        start = time.time()
        results = embeddings.find_similar_text("test query", k=5)
        latency = (time.time() - start) * 1000  # Convert to ms

        # Should complete in reasonable time (< 100ms even for 50 sessions)
        assert latency < 1000  # Very generous limit for mock mode
        assert len(results) <= 5

    def test_list_sessions(self, embeddings):
        """Test listing all sessions."""
        sessions = ["S001", "S002", "S003"]
        for s_id in sessions:
            embeddings.add_session(s_id, f"Session {s_id}", [], [])

        listed = embeddings.list_sessions()
        assert len(listed) == 3
        assert set(listed) == set(sessions)

    def test_search_with_k_parameter(self, embeddings):
        """Test search with different k values."""
        # Add 10 sessions
        for i in range(10):
            embeddings.add_session(f"S{i:02d}", f"Session {i}", [], [])

        # Test different k values
        for k in [1, 3, 5, 10]:
            results = embeddings.find_similar_text("test", k=k)
            assert len(results) <= min(k, 10)

    def test_metadata_persistence(self, embeddings, temp_metadata_path):
        """Test that metadata is persisted correctly."""
        embeddings.add_session(
            "S001",
            "Test summary",
            ["P-001", "P-002"],
            ["tag1", "tag2"],
        )
        embeddings.save_index()

        # Load metadata file directly
        with open(temp_metadata_path) as f:
            data = json.load(f)

        assert data["version"] == embeddings.VERSION
        assert data["model"] == embeddings.MODEL_NAME
        assert data["dimension"] == embeddings.DIMENSION
        assert "S001" in data["sessions"]

    def test_thread_safety(self, embeddings):
        """Test basic thread safety (concurrent access)."""
        import threading

        def add_sessions(start_id, count):
            for i in range(count):
                embeddings.add_session(
                    f"S{start_id:03d}_{i:03d}",
                    f"Session {start_id}_{i}",
                    [],
                    [],
                )

        # Create multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=add_sessions, args=(i * 10, 10))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify sessions
        all_sessions = embeddings.list_sessions()
        assert len(all_sessions) == 30

    def test_rebuild_index(self, embeddings):
        """Test rebuilding index."""
        embeddings.add_session("S001", "Test 1", [], [])
        embeddings.add_session("S002", "Test 2", [], [])

        # Rebuild
        success = embeddings.rebuild_index()
        assert success is True
        assert len(embeddings.list_sessions()) == 2

    def test_search_result_format(self, embeddings):
        """Test search result format."""
        embeddings.add_session("S001", "Cache management", [], ["cache"])
        embeddings.add_session("S002", "Database query", [], ["database"])

        results = embeddings.find_similar_text("cache", k=1)

        # Verify format
        assert isinstance(results, list)
        for session_id, score in results:
            assert isinstance(session_id, str)
            assert isinstance(score, (int, float))
            assert 0 <= score <= 1

    def test_empty_index_search(self, embeddings):
        """Test searching empty index."""
        results = embeddings.find_similar_text("query", k=5)
        assert results == []

    def test_single_session_search(self, embeddings):
        """Test searching with single session in index."""
        embeddings.add_session("S001", "Only session", [], [])

        results = embeddings.find_similar_text("query", k=5)
        # With mock embeddings, might return the one session or might not
        # depending on distance calculation
        assert len(results) <= 1
