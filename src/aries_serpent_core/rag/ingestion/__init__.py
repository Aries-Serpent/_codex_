"""
RAG Document Ingestion Pipeline

This module provides production-grade document ingestion capabilities:
- Document validation and format detection
- Text preprocessing and normalization
- Configurable chunking strategies
- Batch processing with progress tracking
"""

from .chunker import (
    Chunk,
    Chunker,
    ChunkingConfig,
    ChunkingStrategy,
    chunk_document,
)
from .pipeline import (
    BatchIngestionResult,
    IngestionConfig,
    IngestionPipeline,
    IngestionResult,
)
from .preprocessor import (
    DocumentPreprocessor,
    PreprocessingConfig,
    normalize_text,
    preprocess_text,
)
from .validator import (
    DocumentFormat,
    DocumentValidator,
    ValidationResult,
    validate_document,
)

__all__ = [
    # Validator
    "DocumentValidator",
    "DocumentFormat",
    "ValidationResult",
    "validate_document",
    # Preprocessor
    "DocumentPreprocessor",
    "PreprocessingConfig",
    "preprocess_text",
    "normalize_text",
    # Chunker
    "Chunker",
    "ChunkingStrategy",
    "ChunkingConfig",
    "Chunk",
    "chunk_document",
    # Pipeline
    "IngestionPipeline",
    "IngestionConfig",
    "IngestionResult",
    "BatchIngestionResult",
]
