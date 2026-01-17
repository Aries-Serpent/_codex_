"""RAG (Retrieval-Augmented Generation) module"""

from .postprocess import OutputProcessor, postprocess_output
from .prompt import PromptConfig, PromptTemplate, TokenizerFn, build_prompt

# Expanded context workflow components (may require optional dependencies)
try:
    from .embeddings import (
        CachedEmbeddingProvider,
        LocalSentenceTransformerProvider,
        OpenAIEmbeddingProvider,
        create_embedding_provider,
    )
    from .indexer import (
        build_index_from_files,
        chunk_text,
        embed_chunks,
        load_index,
        persist_index,
        manage_tenant_indices,
        TenantOperationResult,
        IndexOperation,
    )
    from .retriever import MultiIndexRetriever, Retriever, CachedRetriever, LRUCache
    from .utils import safe_model_load, ProvenanceMetadata
    from .monitoring import RAGMetrics, get_metrics, reset_metrics, MetricDataPoint, MetricsConfig

    _expanded_context_available = True
except ImportError:
    _expanded_context_available = False

# Ingestion pipeline components
try:
    from .ingestion import (
        # Validator
        DocumentValidator,
        DocumentFormat,
        ValidationResult,
        validate_document,
        # Preprocessor
        DocumentPreprocessor,
        PreprocessingConfig,
        preprocess_text,
        normalize_text,
        # Chunker
        Chunker,
        ChunkingStrategy,
        ChunkingConfig,
        Chunk,
        chunk_document,
        # Pipeline
        IngestionPipeline,
        IngestionConfig,
        IngestionResult,
        BatchIngestionResult,
    )
    _ingestion_available = True
except ImportError:
    _ingestion_available = False

__all__ = [
    "build_prompt",
    "PromptTemplate",
    "PromptConfig",
    "TokenizerFn",
    "postprocess_output",
    "OutputProcessor",
]

if _expanded_context_available:
    __all__.extend(
        [
            # Embeddings
            "CachedEmbeddingProvider",
            "LocalSentenceTransformerProvider",
            "OpenAIEmbeddingProvider",
            "create_embedding_provider",
            # Indexer
            "chunk_text",
            "embed_chunks",
            "persist_index",
            "load_index",
            "build_index_from_files",
            "manage_tenant_indices",
            "TenantOperationResult",
            "IndexOperation",
            # Retriever
            "Retriever",
            "MultiIndexRetriever",
            "CachedRetriever",
            "LRUCache",
            # Utils
            "safe_model_load",
            "ProvenanceMetadata",
            # Monitoring
            "RAGMetrics",
            "get_metrics",
            "reset_metrics",
            "MetricDataPoint",
            "MetricsConfig",
        ]
    )

if _ingestion_available:
    __all__.extend(
        [
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
    )
