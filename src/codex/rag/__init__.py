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
    )
    from .retriever import MultiIndexRetriever, Retriever
    from .utils import safe_model_load

    _expanded_context_available = True
except ImportError:
    _expanded_context_available = False

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
            # Retriever
            "Retriever",
            "MultiIndexRetriever",
            # Utils
            "safe_model_load",
        ]
    )
