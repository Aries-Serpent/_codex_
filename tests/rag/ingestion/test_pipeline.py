"""
Tests for Ingestion Pipeline Module.
"""

import pytest
from pathlib import Path
import tempfile
import os

from codex.rag.ingestion.pipeline import (
    IngestionPipeline,
    IngestionConfig,
    IngestionResult,
    BatchIngestionResult,
    IngestionStatus,
)
from codex.rag.ingestion.validator import ValidationConfig
from codex.rag.ingestion.preprocessor import PreprocessingConfig
from codex.rag.ingestion.chunker import ChunkingConfig


class TestIngestionStatus:
    """Tests for IngestionStatus enum."""
    
    def test_status_values(self):
        """Test status enum values."""
        assert IngestionStatus.PENDING.value == "pending"
        assert IngestionStatus.COMPLETED.value == "completed"
        assert IngestionStatus.FAILED.value == "failed"
        assert IngestionStatus.SKIPPED.value == "skipped"


class TestIngestionResult:
    """Tests for IngestionResult dataclass."""
    
    def test_is_success(self):
        """Test is_success property."""
        result = IngestionResult(
            document_id="test",
            status=IngestionStatus.COMPLETED,
        )
        assert result.is_success
        
        result = IngestionResult(
            document_id="test",
            status=IngestionStatus.FAILED,
        )
        assert not result.is_success
    
    def test_chunk_count(self):
        """Test chunk_count property."""
        from codex.rag.ingestion.chunker import Chunk
        
        result = IngestionResult(
            document_id="test",
            status=IngestionStatus.COMPLETED,
            chunks=[
                Chunk(text="a", index=0, start_pos=0, end_pos=1),
                Chunk(text="b", index=1, start_pos=1, end_pos=2),
            ],
        )
        assert result.chunk_count == 2
    
    def test_to_dict(self):
        """Test to_dict method."""
        result = IngestionResult(
            document_id="test",
            status=IngestionStatus.COMPLETED,
            processing_time_seconds=1.5,
            metadata={"key": "value"},
        )
        
        d = result.to_dict()
        assert d["document_id"] == "test"
        assert d["status"] == "completed"
        assert d["processing_time"] == 1.5


class TestBatchIngestionResult:
    """Tests for BatchIngestionResult dataclass."""
    
    def test_success_rate(self):
        """Test success_rate calculation."""
        result = BatchIngestionResult(
            total_documents=10,
            successful=8,
            failed=2,
        )
        assert result.success_rate == 0.8
    
    def test_success_rate_zero_documents(self):
        """Test success_rate with no documents."""
        result = BatchIngestionResult(total_documents=0)
        assert result.success_rate == 0.0
    
    def test_throughput(self):
        """Test throughput calculation."""
        result = BatchIngestionResult(
            total_documents=100,
            total_time_seconds=1.0,  # 1 second = 360000 docs/hour
        )
        assert result.throughput_docs_per_hour == 360000.0
    
    def test_summary(self):
        """Test summary generation."""
        result = BatchIngestionResult(
            total_documents=10,
            successful=8,
            failed=2,
            total_chunks=50,
            total_time_seconds=5.0,
        )
        
        summary = result.summary()
        assert "8/10" in summary
        assert "50 chunks" in summary


class TestIngestionConfig:
    """Tests for IngestionConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = IngestionConfig()
        
        assert config.batch_size == 100
        assert config.max_workers == 4
        assert config.max_retries == 3
        assert config.enable_deduplication is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = IngestionConfig(
            batch_size=50,
            max_workers=8,
            enable_deduplication=False,
        )
        
        assert config.batch_size == 50
        assert config.max_workers == 8
        assert config.enable_deduplication is False


class TestIngestionPipeline:
    """Tests for IngestionPipeline class."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance."""
        return IngestionPipeline()
    
    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is test content for ingestion.\n")
            f.write("It has multiple sentences. And paragraphs.\n\n")
            f.write("This is another paragraph.")
            temp_path = f.name
        yield Path(temp_path)
        os.unlink(temp_path)
    
    @pytest.fixture
    def temp_dir_with_files(self):
        """Create a temporary directory with test files."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test files
        for i in range(3):
            file_path = Path(temp_dir) / f"doc{i}.txt"
            file_path.write_text(f"Document {i} content. Some text here.")
        
        yield Path(temp_dir)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_ingest_text(self, pipeline):
        """Test text ingestion."""
        text = "This is a test document for ingestion."
        result = pipeline.ingest_text(text)
        
        assert result.is_success
        assert result.status == IngestionStatus.COMPLETED
        assert result.chunk_count >= 1
        assert result.processing_time_seconds > 0
    
    def test_ingest_text_with_id(self, pipeline):
        """Test text ingestion with custom ID."""
        result = pipeline.ingest_text(
            "Test content",
            document_id="custom-id",
        )
        
        assert result.document_id == "custom-id"
    
    def test_ingest_text_with_metadata(self, pipeline):
        """Test text ingestion with metadata."""
        result = pipeline.ingest_text(
            "Test content",
            metadata={"source": "test"},
        )
        
        assert result.metadata.get("source") == "test"
    
    def test_ingest_file(self, pipeline, temp_text_file):
        """Test file ingestion."""
        result = pipeline.ingest_file(temp_text_file)
        
        assert result.is_success
        assert result.chunk_count >= 1
        assert result.metadata.get("source_file") == str(temp_text_file)
    
    def test_ingest_file_not_found(self, pipeline):
        """Test ingestion of non-existent file."""
        result = pipeline.ingest_file("/nonexistent/file.txt")
        
        assert not result.is_success
        assert result.status == IngestionStatus.FAILED
        assert "not found" in result.error_message.lower() or "error" in result.error_message.lower()
    
    def test_ingest_files_batch(self, pipeline, temp_dir_with_files):
        """Test batch file ingestion."""
        files = list(temp_dir_with_files.glob("*.txt"))
        result = pipeline.ingest_files(files, parallel=False)
        
        assert result.total_documents == 3
        assert result.successful == 3
        assert result.failed == 0
        assert result.total_chunks >= 3
    
    def test_ingest_files_parallel(self, pipeline, temp_dir_with_files):
        """Test parallel batch file ingestion."""
        files = list(temp_dir_with_files.glob("*.txt"))
        result = pipeline.ingest_files(files, parallel=True)
        
        assert result.total_documents == 3
        assert result.successful == 3
    
    def test_ingest_directory(self, pipeline, temp_dir_with_files):
        """Test directory ingestion."""
        result = pipeline.ingest_directory(temp_dir_with_files, pattern="*.txt")
        
        assert result.total_documents == 3
        assert result.successful >= 1
    
    def test_deduplication(self, pipeline):
        """Test document deduplication."""
        text = "Duplicate document content"
        
        result1 = pipeline.ingest_text(text, document_id="doc1")
        result2 = pipeline.ingest_text(text, document_id="doc2")
        
        assert result1.is_success
        assert result2.status == IngestionStatus.SKIPPED
        assert "duplicate" in result2.error_message.lower()
    
    def test_deduplication_disabled(self):
        """Test with deduplication disabled."""
        config = IngestionConfig(enable_deduplication=False)
        pipeline = IngestionPipeline(config)
        
        text = "Duplicate document content"
        
        result1 = pipeline.ingest_text(text, document_id="doc1")
        result2 = pipeline.ingest_text(text, document_id="doc2")
        
        assert result1.is_success
        assert result2.is_success  # Not skipped
    
    def test_clear_deduplication_cache(self, pipeline):
        """Test clearing deduplication cache."""
        text = "Document to dedupe"
        
        result1 = pipeline.ingest_text(text, document_id="doc1")
        assert result1.is_success
        
        pipeline.clear_deduplication_cache()
        
        result2 = pipeline.ingest_text(text, document_id="doc2")
        assert result2.is_success  # Not skipped after cache clear
    
    def test_skip_validation(self):
        """Test skipping validation."""
        config = IngestionConfig(skip_validation=True)
        pipeline = IngestionPipeline(config)
        
        result = pipeline.ingest_text("Test content")
        
        assert result.is_success
        assert result.validation_result is None
    
    def test_skip_preprocessing(self):
        """Test skipping preprocessing."""
        config = IngestionConfig(skip_preprocessing=True)
        pipeline = IngestionPipeline(config)
        
        result = pipeline.ingest_text("Test   content")
        
        assert result.is_success
        assert result.preprocessing_result is None
    
    def test_skip_chunking(self):
        """Test skipping chunking."""
        config = IngestionConfig(skip_chunking=True)
        pipeline = IngestionPipeline(config)
        
        result = pipeline.ingest_text("Test content")
        
        assert result.is_success
        assert result.chunk_count == 1  # Single chunk for whole doc
    
    def test_get_stats(self, pipeline):
        """Test getting pipeline statistics."""
        stats = pipeline.get_stats()
        
        assert "dedup_cache_size" in stats
        assert "config" in stats
        assert stats["config"]["enable_deduplication"] is True
    
    def test_validation_failure(self):
        """Test handling of validation failure."""
        # Create config that will fail validation
        validation_config = ValidationConfig(max_text_length=10)
        config = IngestionConfig(validation_config=validation_config)
        pipeline = IngestionPipeline(config)
        
        # This text is longer than 10 characters
        result = pipeline.ingest_text("This text is longer than ten characters")
        
        assert not result.is_success
        assert result.status == IngestionStatus.FAILED
        assert result.validation_result is not None
        assert not result.validation_result.is_valid


class TestIngestionPipelineRetry:
    """Tests for retry logic."""
    
    def test_retry_config(self):
        """Test retry configuration."""
        config = IngestionConfig(
            max_retries=5,
            retry_delay_seconds=0.5,
        )
        
        assert config.max_retries == 5
        assert config.retry_delay_seconds == 0.5


class TestIngestionPipelineCallback:
    """Tests for callback functionality."""
    
    def test_document_complete_callback(self):
        """Test on_document_complete callback."""
        callback_data = []
        
        def on_complete(doc_id, result):
            callback_data.append((doc_id, result.is_success))
        
        config = IngestionConfig(on_document_complete=on_complete)
        pipeline = IngestionPipeline(config)
        
        pipeline.ingest_text("Test content", document_id="test-doc")
        
        assert len(callback_data) == 1
        assert callback_data[0][0] == "test-doc"
        assert callback_data[0][1] is True
