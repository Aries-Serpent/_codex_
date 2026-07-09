"""
Document Ingestion Pipeline Module

Provides end-to-end document ingestion with:
- Batch processing with progress tracking
- Error recovery and retry logic
- Parallel processing support
- Pipeline status reporting
"""

import hashlib
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

from .chunker import (
    Chunk,
    Chunker,
    ChunkingConfig,
)
from .preprocessor import (
    DocumentPreprocessor,
    PreprocessingConfig,
    PreprocessingResult,
)
from .validator import (
    DocumentValidator,
    ValidationConfig,
    ValidationResult,
)


class IngestionStatus(Enum):
    """Status of ingestion operation."""

    PENDING = "pending"
    VALIDATING = "validating"
    PREPROCESSING = "preprocessing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class IngestionConfig:
    """Configuration for ingestion pipeline."""

    # Validation
    validation_config: ValidationConfig = field(default_factory=ValidationConfig)
    skip_validation: bool = False

    # Preprocessing
    preprocessing_config: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    skip_preprocessing: bool = False

    # Chunking
    chunking_config: ChunkingConfig = field(default_factory=ChunkingConfig)
    skip_chunking: bool = False

    # Batch processing
    batch_size: int = 100
    max_workers: int = 4

    # Error handling
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    continue_on_error: bool = True

    # Deduplication
    enable_deduplication: bool = True

    # Callbacks
    on_document_complete: Optional[Callable[[str, "IngestionResult"], None]] = None
    on_batch_complete: Optional[Callable[[int, list["IngestionResult"]], None]] = None


@dataclass
class IngestionResult:
    """Result of ingesting a single document."""

    document_id: str
    status: IngestionStatus
    chunks: list[Chunk] = field(default_factory=list)
    validation_result: Optional[ValidationResult] = None
    preprocessing_result: Optional[PreprocessingResult] = None
    error_message: str = ""
    processing_time_seconds: float = 0.0
    retries: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if ingestion was successful."""
        return self.status == IngestionStatus.COMPLETED

    @property
    def chunk_count(self) -> int:
        """Get number of chunks generated."""
        return len(self.chunks)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "status": self.status.value,
            "chunk_count": self.chunk_count,
            "error_message": self.error_message,
            "processing_time": self.processing_time_seconds,
            "retries": self.retries,
            "metadata": self.metadata,
        }


@dataclass
class BatchIngestionResult:
    """Result of batch ingestion operation."""

    total_documents: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_chunks: int = 0
    total_time_seconds: float = 0.0
    results: list[IngestionResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_documents == 0:
            return 0.0
        return self.successful / self.total_documents

    @property
    def throughput_docs_per_hour(self) -> float:
        """Calculate documents processed per hour."""
        if self.total_time_seconds == 0:
            return 0.0
        seconds_per_hour = 3600
        return (self.total_documents / self.total_time_seconds) * seconds_per_hour

    def summary(self) -> str:
        """Generate summary string."""
        return (
            f"Ingestion complete: {self.successful}/{self.total_documents} successful "
            f"({self.success_rate:.1%}), {self.total_chunks} chunks generated, "
            f"{self.total_time_seconds:.2f}s ({self.throughput_docs_per_hour:.0f} docs/hour)"
        )


class IngestionPipeline:
    """
    Production-grade document ingestion pipeline.

    Features:
    - Configurable validation, preprocessing, and chunking
    - Batch processing with parallel execution
    - Error recovery and retry logic
    - Progress tracking and reporting
    - Deduplication support

    Example:
        pipeline = IngestionPipeline()

        # Single document
        result = pipeline.ingest_text("Document content here...")

        # Batch processing
        batch_result = pipeline.ingest_files(["/path/to/doc1.txt", "/path/to/doc2.md"])
        logger.info(batch_result.summary())
    """

    def __init__(self, config: Optional[IngestionConfig] = None):
        """Initialize pipeline with configuration."""
        self.config = config or IngestionConfig()

        # Initialize components
        self.validator = DocumentValidator(self.config.validation_config)
        self.preprocessor = DocumentPreprocessor(self.config.preprocessing_config)
        self.chunker = Chunker(self.config.chunking_config)

        # Deduplication cache
        self._seen_hashes: set[str] = set()

    def ingest_text(
        self,
        text: str,
        document_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> IngestionResult:
        """
        Ingest a single text document.

        Args:
            text: Document text content
            document_id: Optional document identifier
            metadata: Optional metadata to attach

        Returns:
            IngestionResult with processing status and chunks
        """
        start_time = time.time()

        # Generate document ID if not provided
        if document_id is None:
            document_id = hashlib.sha256(text.encode()).hexdigest()[:16]

        result = IngestionResult(
            document_id=document_id,
            status=IngestionStatus.PENDING,
            metadata=metadata or {},
        )

        try:
            # Validation
            result.status = IngestionStatus.VALIDATING
            if not self.config.skip_validation:
                validation = self.validator.validate_text(text)
                result.validation_result = validation

                if not validation.is_valid:
                    result.status = IngestionStatus.FAILED
                    result.error_message = "; ".join(validation.errors)
                    return result

            # Deduplication check
            if self.config.enable_deduplication:
                content_hash = hashlib.sha256(text.encode()).hexdigest()
                if content_hash in self._seen_hashes:
                    result.status = IngestionStatus.SKIPPED
                    result.error_message = "Duplicate document"
                    return result
                self._seen_hashes.add(content_hash)

            # Preprocessing
            result.status = IngestionStatus.PREPROCESSING
            processed_text = text
            if not self.config.skip_preprocessing:
                preprocessing = self.preprocessor.preprocess(text)
                result.preprocessing_result = preprocessing
                processed_text = preprocessing.text

            # Chunking
            result.status = IngestionStatus.CHUNKING
            if not self.config.skip_chunking:
                chunks = self.chunker.chunk(processed_text)
                result.chunks = chunks
            else:
                # Create single chunk for entire document
                result.chunks = [
                    Chunk(
                        text=processed_text,
                        index=0,
                        start_pos=0,
                        end_pos=len(processed_text),
                    )
                ]

            result.status = IngestionStatus.COMPLETED

        except (ValueError, TypeError, RuntimeError) as e:
            result.status = IngestionStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Ingestion failed for {document_id}: <ERROR_TYPE>")

        finally:
            result.processing_time_seconds = time.time() - start_time

        # Trigger callback if configured
        if self.config.on_document_complete:
            self.config.on_document_complete(result.document_id, result)

        return result

    def ingest_file(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        """
        Ingest a single file.

        Args:
            file_path: Path to document file
            document_id: Optional document identifier
            metadata: Optional metadata to attach

        Returns:
            IngestionResult with processing status and chunks
        """
        path = Path(file_path)

        # Use filename as document ID if not provided
        if document_id is None:
            document_id = path.stem

        result = IngestionResult(
            document_id=document_id,
            status=IngestionStatus.PENDING,
            metadata=metadata or {},
        )
        result.metadata["source_file"] = str(path)

        start_time = time.time()

        try:
            # Validate file
            result.status = IngestionStatus.VALIDATING
            if not self.config.skip_validation:
                validation = self.validator.validate_file(path)
                result.validation_result = validation

                if not validation.is_valid:
                    result.status = IngestionStatus.FAILED
                    result.error_message = "; ".join(validation.errors)
                    return result

            # Read file content
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(path, encoding="latin-1") as f:
                    text = f.read()

            # Deduplication check
            if self.config.enable_deduplication:
                content_hash = hashlib.sha256(text.encode()).hexdigest()
                if content_hash in self._seen_hashes:
                    result.status = IngestionStatus.SKIPPED
                    result.error_message = "Duplicate document"
                    return result
                self._seen_hashes.add(content_hash)

            # Preprocessing
            result.status = IngestionStatus.PREPROCESSING
            processed_text = text
            if not self.config.skip_preprocessing:
                preprocessing = self.preprocessor.preprocess(text)
                result.preprocessing_result = preprocessing
                processed_text = preprocessing.text

            # Chunking
            result.status = IngestionStatus.CHUNKING
            if not self.config.skip_chunking:
                chunks = self.chunker.chunk(processed_text)
                result.chunks = chunks
            else:
                result.chunks = [
                    Chunk(
                        text=processed_text,
                        index=0,
                        start_pos=0,
                        end_pos=len(processed_text),
                    )
                ]

            result.status = IngestionStatus.COMPLETED

        except Exception as e:
            result.status = IngestionStatus.FAILED
            result.error_message = str(e)
            logger.error(f"Ingestion failed for {path}: <ERROR_TYPE>")

        finally:
            result.processing_time_seconds = time.time() - start_time

        return result

    def ingest_files(
        self,
        file_paths: Sequence[str | Path],
        parallel: bool = True,
    ) -> BatchIngestionResult:
        """
        Ingest multiple files.

        Args:
            file_paths: List of file paths to ingest
            parallel: Whether to use parallel processing

        Returns:
            BatchIngestionResult with aggregate statistics
        """
        start_time = time.time()

        batch_result = BatchIngestionResult(
            total_documents=len(file_paths),
        )

        if parallel and len(file_paths) > 1:
            self._process_parallel(file_paths, batch_result)
        else:
            self._process_sequential(file_paths, batch_result)

        batch_result.total_time_seconds = time.time() - start_time
        logger.info(batch_result.summary())

        return batch_result

    def _process_parallel(
        self,
        file_paths: Sequence[str | Path],
        batch_result: BatchIngestionResult,
    ) -> None:
        """Process files in parallel using ThreadPoolExecutor."""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {executor.submit(self._ingest_with_retry, path): path for path in file_paths}

            for future in as_completed(futures):
                path = futures[future]
                try:
                    result = future.result()
                    self._update_batch_result(batch_result, result)
                except Exception as e:
                    self._handle_ingestion_error(batch_result, path, e)

    def _process_sequential(
        self,
        file_paths: Sequence[str | Path],
        batch_result: BatchIngestionResult,
    ) -> None:
        """Process files sequentially."""
        for path in file_paths:
            try:
                result = self._ingest_with_retry(path)
                self._update_batch_result(batch_result, result)
            except Exception as e:
                if not self.config.continue_on_error:
                    raise
                self._handle_ingestion_error(batch_result, path, e)

    def _handle_ingestion_error(
        self,
        batch_result: BatchIngestionResult,
        path: str | Path,
        error: Exception,
    ) -> None:
        """Handle ingestion error and update batch result."""
        error_msg = f"Failed to process {path}: {error}"
        batch_result.errors.append(error_msg)
        batch_result.failed += 1
        logger.error(error_msg)

    def ingest_directory(
        self,
        directory: str | Path,
        pattern: str = "*",
        recursive: bool = True,
    ) -> BatchIngestionResult:
        """
        Ingest all matching files from a directory.

        Args:
            directory: Directory path
            pattern: Glob pattern for file matching
            recursive: Whether to search recursively

        Returns:
            BatchIngestionResult with aggregate statistics
        """
        dir_path = Path(directory)

        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        # Find matching files
        files = list(dir_path.rglob(pattern)) if recursive else list(dir_path.glob(pattern))

        # Filter to files only
        files = [f for f in files if f.is_file()]

        logger.info(f"Found {len(files)} files matching '{pattern}' in {directory}")

        return self.ingest_files(files)

    def _ingest_with_retry(self, file_path: str | Path) -> IngestionResult:
        """Ingest file with retry logic."""
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = self.ingest_file(file_path)
                result.retries = attempt

                if result.is_success or result.status == IngestionStatus.SKIPPED:
                    return result

                # Validation failures should not be retried
                if result.status == IngestionStatus.FAILED and result.validation_result:
                    return result

            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay_seconds * (attempt + 1))

        # All retries failed
        return IngestionResult(
            document_id=str(file_path),
            status=IngestionStatus.FAILED,
            error_message=str(last_error) if last_error else "Max retries exceeded",
            retries=self.config.max_retries,
        )

    def _update_batch_result(
        self,
        batch: BatchIngestionResult,
        result: IngestionResult,
    ) -> None:
        """Update batch result with individual result."""
        batch.results.append(result)

        if result.is_success:
            batch.successful += 1
            batch.total_chunks += result.chunk_count
        elif result.status == IngestionStatus.SKIPPED:
            batch.skipped += 1
        else:
            batch.failed += 1
            if result.error_message:
                batch.errors.append(f"{result.document_id}: {result.error_message}")

        # Trigger callback if configured
        if self.config.on_document_complete:
            self.config.on_document_complete(result.document_id, result)

    def clear_deduplication_cache(self) -> None:
        """Clear the deduplication cache."""
        self._seen_hashes.clear()
        logger.debug("Cleared deduplication cache")

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "dedup_cache_size": len(self._seen_hashes),
            "config": {
                "batch_size": self.config.batch_size,
                "max_workers": self.config.max_workers,
                "max_retries": self.config.max_retries,
                "enable_deduplication": self.config.enable_deduplication,
            },
        }
