"""
RAG Document Ingestion Pipeline

This module provides production-grade document ingestion capabilities:
- Document validation and format detection
- Text preprocessing and normalization
- Configurable chunking strategies
- Batch processing with progress tracking
"""

from .validator import (
    DocumentValidator,
    DocumentFormat,
    ValidationResult,
    validate_document,
)
from .preprocessor import (
    DocumentPreprocessor,
    PreprocessingConfig,
    preprocess_text,
    normalize_text,
)
from .chunker import (
    Chunker,
    ChunkingStrategy,
    ChunkingConfig,
    Chunk,
    chunk_document,
)
from .pipeline import (
    IngestionPipeline,
    IngestionConfig,
    IngestionResult,
    BatchIngestionResult,
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
