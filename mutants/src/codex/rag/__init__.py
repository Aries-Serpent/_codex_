"""RAG (Retrieval-Augmented Generation) module"""

from .postprocess import OutputProcessor, postprocess_output
from .prompt import PromptConfig, PromptTemplate, TokenizerFn, build_prompt

# Expanded context workflow components (may require optional dependencies)
try:
    from .embeddings import (
        CachedEmbeddingProvider,
        LocalSentenceTransformerProvider,
        OpenAIEmbeddingProvider,
        TfidfEmbeddingProvider,
        create_embedding_provider,
    )
    from .indexer import (
        IndexOperation,
        RAGIndexer,
        TenantOperationResult,
        build_index_from_files,
        chunk_text,
        embed_chunks,
        load_index,
        manage_tenant_indices,
        persist_index,
    )
    from .monitoring import (
        MetricDataPoint,
        MetricsConfig,
        RAGMetrics,
        get_metrics,
        reset_metrics,
    )
    from .retriever import CachedRetriever, LRUCache, MultiIndexRetriever, Retriever
    from .utils import ProvenanceMetadata

    _expanded_context_available = True
except ImportError:
    _expanded_context_available = False

# Ingestion pipeline components
try:
    from .ingestion import (  # Chunker; Preprocessor; Validator; Pipeline
        BatchIngestionResult,
        Chunk,
        Chunker,
        ChunkingConfig,
        ChunkingStrategy,
        DocumentFormat,
        DocumentPreprocessor,
        DocumentValidator,
        IngestionConfig,
        IngestionPipeline,
        IngestionResult,
        PreprocessingConfig,
        ValidationResult,
        chunk_document,
        normalize_text,
        preprocess_text,
        validate_document,
    )

    _ingestion_available = True
except ImportError:
    _ingestion_available = False

__all__ = [
    "OutputProcessor",
    "PromptConfig",
    "PromptTemplate",
    "TokenizerFn",
    "build_prompt",
    "postprocess_output",
]

if _expanded_context_available:
    __all__.extend(
        [
            # Embeddings
            "CachedEmbeddingProvider",
            "LocalSentenceTransformerProvider",
            "OpenAIEmbeddingProvider",
            "TfidfEmbeddingProvider",
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
