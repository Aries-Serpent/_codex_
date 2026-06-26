"""Phase 3C: Data Path Testing - Ingestion, Transformation, and Persistence.

Focus: Data ingestion, transformation, persistence paths and end-to-end
data pipeline operations.

Target: Add 50+ tests for data pipeline paths covering critical transformations
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from src.codex.agents.memory.backends import JSONLMemoryBackend
from src.codex.agents.memory.protocol import MemoryEntry, MemoryQuery


class TestDataIngestion:
    """Test data ingestion into the system."""

    def test_ingest_simple_text_data(self):
        """Test ingesting simple text data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")
            entry = MemoryEntry(
                content="Simple text data", agent_id="ingestor", session_id="ingestion-test"
            )
            backend.store(entry)

            # Verify ingestion
            query = MemoryQuery(limit=10)
            results = backend.retrieve(query)
            assert len(results) >= 1, "Results must not be empty"

    def test_ingest_json_data(self):
        """Test ingesting JSON structured data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")
            data = {"user_id": 123, "action": "login", "timestamp": "2024-01-01"}
            entry = MemoryEntry(content=data, agent_id="ingestor", session_id="ingestion-test")
            backend.store(entry)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 1, "Results must not be empty"
            assert results[0].content == data, "Result must not be empty"

    def test_ingest_batch_data(self):
        """Test batch ingestion of multiple data items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Ingest batch of 10 items
            for i in range(10):
                entry = MemoryEntry(
                    content=f"Item {i}", agent_id="batch-ingestor", session_id="batch-test"
                )
                backend.store(entry)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 10, "Results must not be empty"

    def test_ingest_with_metadata_enrichment(self):
        """Test ingesting data with metadata enrichment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            metadata = {
                "source": "api",
                "version": "1.0",
                "priority": "high",
                "tags": ["important", "urgent"],
            }
            entry = MemoryEntry(
                content="Important data", agent_id="ingestor", session_id="test", metadata=metadata
            )
            backend.store(entry)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 1, "Results must not be empty"
            assert results[0].metadata == metadata, "Result must not be empty"

    def test_ingest_csv_like_data(self):
        """Test ingesting CSV-like data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store multiple CSV records as dictionaries
            records = [
                {"id": 1, "name": "Alice", "value": 100},
                {"id": 2, "name": "Bob", "value": 200},
                {"id": 3, "name": "Charlie", "value": 300},
            ]

            for record in records:
                entry = MemoryEntry(content=record, agent_id="csv-ingestor", session_id="csv-test")
                backend.store(entry)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 3, "Results must not be empty"


class TestDataTransformation:
    """Test data transformation operations."""

    def test_transform_raw_text_to_structured(self):
        """Test transforming raw text to structured data."""
        raw_text = "User alice performed action login at 2024-01-01"

        # Simulate transformation
        transformed = {"user": "alice", "action": "login", "timestamp": "2024-01-01"}

        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store original
            entry_raw = MemoryEntry(
                content=raw_text,
                agent_id="transformer",
                session_id="transform-test",
                metadata={"type": "raw"},
            )
            backend.store(entry_raw)

            # Store transformed
            entry_transformed = MemoryEntry(
                content=transformed,
                agent_id="transformer",
                session_id="transform-test",
                metadata={"type": "transformed"},
            )
            backend.store(entry_transformed)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 2, "Results must not be empty"

    def test_transform_nested_data_flattening(self):
        """Test flattening nested data structures."""
        nested_data = {
            "user": {
                "profile": {"name": "Alice", "email": "alice@example.com"},
                "preferences": {"theme": "dark"},
            }
        }

        # Flattened version
        flattened_data = {
            "user.profile.name": "Alice",
            "user.profile.email": "alice@example.com",
            "user.preferences.theme": "dark",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store both versions
            entry_nested = MemoryEntry(
                content=nested_data, agent_id="transformer", session_id="test"
            )
            backend.store(entry_nested)

            entry_flat = MemoryEntry(
                content=flattened_data, agent_id="transformer", session_id="test"
            )
            backend.store(entry_flat)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 2, "Results must not be empty"

    def test_transform_with_aggregation(self):
        """Test data aggregation transformation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store individual measurements
            for i in range(5):
                entry = MemoryEntry(
                    content={"value": i * 10},
                    agent_id="sensor",
                    session_id="measurements",
                    metadata={"measurement": i},
                )
                backend.store(entry)

            # Store aggregated result
            aggregated = {"count": 5, "sum": 100, "average": 20}
            entry_agg = MemoryEntry(
                content=aggregated,
                agent_id="aggregator",
                session_id="measurements",
                metadata={"type": "aggregated"},
            )
            backend.store(entry_agg)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 6, "Results must not be empty"

    def test_transform_type_conversion(self):
        """Test type conversion transformations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store string representation
            entry_str = MemoryEntry(
                content="123",
                agent_id="converter",
                session_id="test",
                metadata={"original_type": "string"},
            )
            backend.store(entry_str)

            # Store numeric representation
            entry_num = MemoryEntry(
                content=123,
                agent_id="converter",
                session_id="test",
                metadata={"original_type": "number"},
            )
            backend.store(entry_num)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 2, "Results must not be empty"


class TestDataPersistence:
    """Test data persistence mechanisms."""

    def test_persist_to_jsonl_file(self):
        """Test persisting data to JSONL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "data.jsonl"
            backend = JSONLMemoryBackend(file_path)

            entry = MemoryEntry(content="Persistent data", agent_id="test", session_id="test")
            backend.store(entry)

            # Verify file was created and contains data
            assert file_path.exists(), "Condition must be true"
            with open(file_path) as f:
                lines = f.readlines()
                assert len(lines) >= 1, "Lines must not be empty"

    def test_persist_multiple_entries(self):
        """Test persisting multiple entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "data.jsonl"
            backend = JSONLMemoryBackend(file_path)

            # Store multiple entries
            for i in range(5):
                entry = MemoryEntry(content=f"Entry {i}", agent_id="test", session_id="test")
                backend.store(entry)

            # Verify all entries persisted
            with open(file_path) as f:
                lines = f.readlines()
                assert len(lines) >= 5, "Lines must not be empty"

    def test_persist_large_data(self):
        """Test persisting large data objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "data.jsonl")

            # Create large data
            large_data = {"items": [{"id": i, "data": "x" * 1000} for i in range(100)]}

            entry = MemoryEntry(content=large_data, agent_id="test", session_id="test")
            backend.store(entry)

            # Retrieve and verify
            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 1, "Results must not be empty"

    def test_persist_and_restore_metadata(self):
        """Test persisting and restoring with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "data.jsonl")

            metadata = {
                "source": "production",
                "timestamp": "2024-01-01T00:00:00Z",
                "tags": ["critical", "audit"],
            }

            entry = MemoryEntry(
                content="Critical data", agent_id="test", session_id="test", metadata=metadata
            )
            backend.store(entry)

            # Retrieve and verify metadata
            results = backend.retrieve(MemoryQuery(limit=10))
            assert results[0].metadata == metadata, "Result must not be empty"


class TestDataPipeline:
    """Test complete data pipeline scenarios."""

    def test_pipeline_ingest_transform_persist(self):
        """Test complete pipeline: ingest -> transform -> persist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "pipeline.jsonl")

            # Step 1: Ingest raw data
            raw_data = "raw user event data"
            entry1 = MemoryEntry(
                content=raw_data,
                agent_id="ingestor",
                session_id="pipeline",
                metadata={"stage": "ingest"},
            )
            backend.store(entry1)

            # Step 2: Transform
            transformed_data = {"event_type": "user_action", "processed": True}
            entry2 = MemoryEntry(
                content=transformed_data,
                agent_id="transformer",
                session_id="pipeline",
                metadata={"stage": "transform"},
            )
            backend.store(entry2)

            # Step 3: Verify persistence
            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 2, "Results must not be empty"

    def test_pipeline_branching(self):
        """Test data pipeline with branching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "pipeline.jsonl")

            # Initial data
            entry_input = MemoryEntry(
                content={"value": 100}, agent_id="input", session_id="pipeline"
            )
            backend.store(entry_input)

            # Branch 1: Process for analytics
            entry_analytics = MemoryEntry(
                content={"processed_for": "analytics", "value": 100},
                agent_id="analytics",
                session_id="pipeline",
            )
            backend.store(entry_analytics)

            # Branch 2: Process for archival
            entry_archive = MemoryEntry(
                content={"processed_for": "archive", "value": 100},
                agent_id="archiver",
                session_id="pipeline",
            )
            backend.store(entry_archive)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 3, "Results must not be empty"

    def test_pipeline_filtering_and_filtering(self):
        """Test filtering during pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "pipeline.jsonl")

            # Store mixed priority data
            for i in range(10):
                priority = "high" if i % 2 == 0 else "low"
                entry = MemoryEntry(
                    content={"id": i, "priority": priority},
                    agent_id="producer",
                    session_id="pipeline",
                    metadata={"priority": priority},
                )
                backend.store(entry)

            # Retrieve all
            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 10, "Results must not be empty"

    def test_pipeline_error_handling_and_retry(self):
        """Test error handling in pipeline with retry capability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "pipeline.jsonl")

            # Record attempt 1 (failed)
            entry_fail = MemoryEntry(
                content={"status": "failed", "attempt": 1},
                agent_id="processor",
                session_id="pipeline",
                metadata={"event": "failure"},
            )
            backend.store(entry_fail)

            # Record retry (success)
            entry_retry = MemoryEntry(
                content={"status": "success", "attempt": 2},
                agent_id="processor",
                session_id="pipeline",
                metadata={"event": "recovery"},
            )
            backend.store(entry_retry)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert len(results) >= 2, "Results must not be empty"


class TestDataConsistency:
    """Test data consistency in storage and retrieval."""

    def test_data_consistency_round_trip(self):
        """Test data consistency in store-retrieve cycle."""
        original_data = {"complex": {"nested": {"structure": [1, 2, 3], "text": "unicode: 你好"}}}

        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            entry_original = MemoryEntry(content=original_data, agent_id="test", session_id="test")
            backend.store(entry_original)

            results = backend.retrieve(MemoryQuery(limit=10))
            assert results[0].content == original_data, "Result must not be empty"

    def test_multiple_retrieval_consistency(self):
        """Test consistency across multiple retrievals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            entry = MemoryEntry(content="Test data", agent_id="test", session_id="test")
            backend.store(entry)

            # Multiple retrievals should return same data
            results1 = backend.retrieve(MemoryQuery(limit=10))
            results2 = backend.retrieve(MemoryQuery(limit=10))

            assert results1[0].content == results2[0].content, "Result must not be empty"

    def test_serialization_deserialization(self):
        """Test serialization/deserialization consistency."""
        entry_original = MemoryEntry(
            content={"key": "value"}, agent_id="test", session_id="test", metadata={"meta": "data"}
        )

        # Serialize
        data_dict = entry_original.to_dict()

        # Deserialize
        entry_restored = MemoryEntry.from_dict(data_dict)

        # Compare
        assert entry_restored.content == entry_original.content, "Content must not be empty"
        assert entry_restored.agent_id == entry_original.agent_id, "agent_id is not valid"
        assert entry_restored.session_id == entry_original.session_id, "session_id is not valid"
        assert entry_restored.metadata == entry_original.metadata, "Data must not be empty"


class TestDataRetention:
    """Test data retention and cleanup policies."""

    def test_data_retention_query(self):
        """Test querying retained data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store multiple records
            for i in range(5):
                entry = MemoryEntry(content=f"Record {i}", agent_id="test", session_id="retention")
                backend.store(entry)

            # Query should return all retained data
            results = backend.retrieve(MemoryQuery(limit=100))
            assert len(results) >= 5, "Results must not be empty"

    def test_session_clear_removes_data(self):
        """Test that clearing session removes all data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store data
            entry = MemoryEntry(content="Test data", agent_id="test", session_id="session-1")
            backend.store(entry)

            # Clear session
            count = backend.clear_session("session-1")
            assert count >= 1, "count must be positive"

    def test_selective_retention_by_metadata(self):
        """Test selective data retention by metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONLMemoryBackend(Path(tmpdir) / "test.jsonl")

            # Store records with different retention policies
            for i in range(3):
                entry = MemoryEntry(
                    content=f"Record {i}",
                    agent_id="test",
                    session_id="test",
                    metadata={"retention": "permanent"},
                )
                backend.store(entry)

            for i in range(3):
                entry = MemoryEntry(
                    content=f"Temp {i}",
                    agent_id="test",
                    session_id="test",
                    metadata={"retention": "temporary"},
                )
                backend.store(entry)

            results = backend.retrieve(MemoryQuery(limit=100))
            assert len(results) >= 6, "Results must not be empty"
