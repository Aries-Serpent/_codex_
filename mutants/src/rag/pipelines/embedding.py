"""
Embedding Pipeline - Generate vector embeddings for text.

This module provides embedding functionality for the RAG pipeline.
Uses lazy imports to avoid requiring heavy ML dependencies when not used.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Lazy import of embedding dependencies
- Bounds checking on text length
- Fallback to simple hash-based embeddings
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MAX_TEXT_LENGTH = 100000
DEFAULT_EMBEDDING_DIM = 384
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@dataclass
class EmbeddingConfig:
    """Configuration for the embedding pipeline."""

    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = DEFAULT_EMBEDDING_DIM
    normalize: bool = True
    batch_size: int = 32


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""

    text: str
    embedding: list[float]
    model: str
    dimension: int


class EmbeddingPipeline:
    """
    Pipeline for generating text embeddings.

    Features:
    - Support for sentence-transformers models
    - Fallback to hash-based embeddings for testing
    - Batch processing for efficiency

    Safeguards:
    - Lazy loading of ML dependencies
    - Text length validation
    - Graceful fallback on errors
    """

    def xǁEmbeddingPipelineǁ__init____mutmut_orig(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_1(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = None
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_2(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config and EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_3(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = ""
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_4(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = None

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_5(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = True

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_6(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            None,
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_7(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            None,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_8(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            None
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_9(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_10(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_11(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EmbeddingPipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            )

    def xǁEmbeddingPipelineǁ__init____mutmut_12(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "XXEmbeddingPipeline initialized: model=%s, dim=%dXX",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_13(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "embeddingpipeline initialized: model=%s, dim=%d",
            self.config.model_name,
            self.config.dimension
        )

    def xǁEmbeddingPipelineǁ__init____mutmut_14(self, config: EmbeddingConfig | None = None) -> None:
        """Initialize the embedding pipeline."""
        self.config = config or EmbeddingConfig()
        self._model = None
        self._use_fallback = False

        logger.info(
            "EMBEDDINGPIPELINE INITIALIZED: MODEL=%S, DIM=%D",
            self.config.model_name,
            self.config.dimension
        )
    
    xǁEmbeddingPipelineǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEmbeddingPipelineǁ__init____mutmut_1': xǁEmbeddingPipelineǁ__init____mutmut_1, 
        'xǁEmbeddingPipelineǁ__init____mutmut_2': xǁEmbeddingPipelineǁ__init____mutmut_2, 
        'xǁEmbeddingPipelineǁ__init____mutmut_3': xǁEmbeddingPipelineǁ__init____mutmut_3, 
        'xǁEmbeddingPipelineǁ__init____mutmut_4': xǁEmbeddingPipelineǁ__init____mutmut_4, 
        'xǁEmbeddingPipelineǁ__init____mutmut_5': xǁEmbeddingPipelineǁ__init____mutmut_5, 
        'xǁEmbeddingPipelineǁ__init____mutmut_6': xǁEmbeddingPipelineǁ__init____mutmut_6, 
        'xǁEmbeddingPipelineǁ__init____mutmut_7': xǁEmbeddingPipelineǁ__init____mutmut_7, 
        'xǁEmbeddingPipelineǁ__init____mutmut_8': xǁEmbeddingPipelineǁ__init____mutmut_8, 
        'xǁEmbeddingPipelineǁ__init____mutmut_9': xǁEmbeddingPipelineǁ__init____mutmut_9, 
        'xǁEmbeddingPipelineǁ__init____mutmut_10': xǁEmbeddingPipelineǁ__init____mutmut_10, 
        'xǁEmbeddingPipelineǁ__init____mutmut_11': xǁEmbeddingPipelineǁ__init____mutmut_11, 
        'xǁEmbeddingPipelineǁ__init____mutmut_12': xǁEmbeddingPipelineǁ__init____mutmut_12, 
        'xǁEmbeddingPipelineǁ__init____mutmut_13': xǁEmbeddingPipelineǁ__init____mutmut_13, 
        'xǁEmbeddingPipelineǁ__init____mutmut_14': xǁEmbeddingPipelineǁ__init____mutmut_14
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEmbeddingPipelineǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁEmbeddingPipelineǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁEmbeddingPipelineǁ__init____mutmut_orig)
    xǁEmbeddingPipelineǁ__init____mutmut_orig.__name__ = 'xǁEmbeddingPipelineǁ__init__'

    def xǁEmbeddingPipelineǁ_load_model__mutmut_orig(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_1(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_2(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return False

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_3(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = None
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_4(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(None)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_5(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info(None, self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_6(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", None)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_7(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info(self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_8(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", )
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_9(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("XXLoaded embedding model: %sXX", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_10(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_11(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("LOADED EMBEDDING MODEL: %S", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_12(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return False

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_13(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                None
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_14(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "XXsentence-transformers not installed. Using fallback embeddings. XX"
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_15(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_16(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "SENTENCE-TRANSFORMERS NOT INSTALLED. USING FALLBACK EMBEDDINGS. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_17(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "XXInstall with: pip install sentence-transformersXX"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_18(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_19(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "INSTALL WITH: PIP INSTALL SENTENCE-TRANSFORMERS"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_20(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = None
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_21(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = False
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_22(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return True

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_23(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error(None, e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_24(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", None)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_25(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error(e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_26(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", )
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_27(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("XXFailed to load embedding model: %sXX", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_28(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("failed to load embedding model: %s", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_29(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("FAILED TO LOAD EMBEDDING MODEL: %S", e)
            self._use_fallback = True
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_30(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = None
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_31(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = False
            return False

    def xǁEmbeddingPipelineǁ_load_model__mutmut_32(self) -> bool:
        """Lazy load the embedding model."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded embedding model: %s", self.config.model_name)
            return True

        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using fallback embeddings. "
                "Install with: pip install sentence-transformers"
            )
            self._use_fallback = True
            return False

        except Exception as e:
            logger.error("Failed to load embedding model: %s", e)
            self._use_fallback = True
            return True
    
    xǁEmbeddingPipelineǁ_load_model__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEmbeddingPipelineǁ_load_model__mutmut_1': xǁEmbeddingPipelineǁ_load_model__mutmut_1, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_2': xǁEmbeddingPipelineǁ_load_model__mutmut_2, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_3': xǁEmbeddingPipelineǁ_load_model__mutmut_3, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_4': xǁEmbeddingPipelineǁ_load_model__mutmut_4, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_5': xǁEmbeddingPipelineǁ_load_model__mutmut_5, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_6': xǁEmbeddingPipelineǁ_load_model__mutmut_6, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_7': xǁEmbeddingPipelineǁ_load_model__mutmut_7, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_8': xǁEmbeddingPipelineǁ_load_model__mutmut_8, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_9': xǁEmbeddingPipelineǁ_load_model__mutmut_9, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_10': xǁEmbeddingPipelineǁ_load_model__mutmut_10, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_11': xǁEmbeddingPipelineǁ_load_model__mutmut_11, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_12': xǁEmbeddingPipelineǁ_load_model__mutmut_12, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_13': xǁEmbeddingPipelineǁ_load_model__mutmut_13, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_14': xǁEmbeddingPipelineǁ_load_model__mutmut_14, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_15': xǁEmbeddingPipelineǁ_load_model__mutmut_15, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_16': xǁEmbeddingPipelineǁ_load_model__mutmut_16, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_17': xǁEmbeddingPipelineǁ_load_model__mutmut_17, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_18': xǁEmbeddingPipelineǁ_load_model__mutmut_18, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_19': xǁEmbeddingPipelineǁ_load_model__mutmut_19, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_20': xǁEmbeddingPipelineǁ_load_model__mutmut_20, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_21': xǁEmbeddingPipelineǁ_load_model__mutmut_21, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_22': xǁEmbeddingPipelineǁ_load_model__mutmut_22, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_23': xǁEmbeddingPipelineǁ_load_model__mutmut_23, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_24': xǁEmbeddingPipelineǁ_load_model__mutmut_24, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_25': xǁEmbeddingPipelineǁ_load_model__mutmut_25, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_26': xǁEmbeddingPipelineǁ_load_model__mutmut_26, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_27': xǁEmbeddingPipelineǁ_load_model__mutmut_27, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_28': xǁEmbeddingPipelineǁ_load_model__mutmut_28, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_29': xǁEmbeddingPipelineǁ_load_model__mutmut_29, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_30': xǁEmbeddingPipelineǁ_load_model__mutmut_30, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_31': xǁEmbeddingPipelineǁ_load_model__mutmut_31, 
        'xǁEmbeddingPipelineǁ_load_model__mutmut_32': xǁEmbeddingPipelineǁ_load_model__mutmut_32
    }
    
    def _load_model(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEmbeddingPipelineǁ_load_model__mutmut_orig"), object.__getattribute__(self, "xǁEmbeddingPipelineǁ_load_model__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _load_model.__signature__ = _mutmut_signature(xǁEmbeddingPipelineǁ_load_model__mutmut_orig)
    xǁEmbeddingPipelineǁ_load_model__mutmut_orig.__name__ = 'xǁEmbeddingPipelineǁ_load_model'

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_orig(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_1(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = None

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_2(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(None).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_3(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = None
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_4(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(None, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_5(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, None, 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_6(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), None):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_7(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_8(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_9(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), ):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_10(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(1, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_11(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(None, self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_12(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), None), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_13(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_14(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), ), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_15(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension / 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_16(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 3), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_17(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 3):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_18(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = None
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_19(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(None, 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_20(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], None)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_21(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_22(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], )
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_23(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i - 2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_24(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+3], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_25(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 17)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_26(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append(None)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_27(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) + 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_28(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val * 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_29(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 128.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_30(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 2.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_31(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) <= self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_32(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(None)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_33(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(1.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_34(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = None

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_35(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = None
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_36(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) * 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_37(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(None) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_38(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x / x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_39(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 1.5
            if norm > 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_40(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm >= 0:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_41(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 1:
                embedding = [x / norm for x in embedding]

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_42(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = None

        return embedding

    def xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_43(self, text: str) -> list[float]:
        """Generate a deterministic hash-based embedding for testing."""
        # Create a deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        # Convert hex pairs to float values between -1 and 1
        # Each hex pair (0-255) is normalized: (value / 127.5) - 1.0 maps to [-1, 1]
        for i in range(0, min(len(text_hash), self.config.dimension * 2), 2):
            byte_val = int(text_hash[i:i+2], 16)
            embedding.append((byte_val / 127.5) - 1.0)

        # Pad to full dimension
        while len(embedding) < self.config.dimension:
            embedding.append(0.0)

        # Truncate if needed
        embedding = embedding[:self.config.dimension]

        # Normalize if configured
        if self.config.normalize:
            norm = sum(x * x for x in embedding) ** 0.5
            if norm > 0:
                embedding = [x * norm for x in embedding]

        return embedding
    
    xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_1': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_1, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_2': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_2, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_3': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_3, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_4': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_4, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_5': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_5, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_6': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_6, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_7': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_7, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_8': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_8, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_9': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_9, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_10': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_10, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_11': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_11, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_12': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_12, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_13': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_13, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_14': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_14, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_15': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_15, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_16': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_16, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_17': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_17, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_18': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_18, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_19': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_19, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_20': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_20, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_21': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_21, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_22': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_22, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_23': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_23, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_24': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_24, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_25': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_25, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_26': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_26, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_27': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_27, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_28': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_28, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_29': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_29, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_30': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_30, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_31': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_31, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_32': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_32, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_33': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_33, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_34': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_34, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_35': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_35, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_36': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_36, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_37': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_37, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_38': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_38, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_39': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_39, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_40': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_40, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_41': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_41, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_42': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_42, 
        'xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_43': xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_43
    }
    
    def _fallback_embedding(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_orig"), object.__getattribute__(self, "xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _fallback_embedding.__signature__ = _mutmut_signature(xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_orig)
    xǁEmbeddingPipelineǁ_fallback_embedding__mutmut_orig.__name__ = 'xǁEmbeddingPipelineǁ_fallback_embedding'

    def xǁEmbeddingPipelineǁembed_text__mutmut_orig(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_1(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text and not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_2(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_3(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_4(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text=None,
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_5(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=None,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_6(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model=None,
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_7(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=None,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_8(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_9(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_10(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_11(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_12(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="XXXX",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_13(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] / self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_14(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[1.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_15(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="XXnoneXX",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_16(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="NONE",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_17(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) >= MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_18(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(None, len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_19(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", None, MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_20(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), None)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_21(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_22(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_23(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), )
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_24(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("XXText truncated: %d > %dXX", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_25(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_26(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("TEXT TRUNCATED: %D > %D", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_27(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = None

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_28(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_29(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback and self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_30(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is not None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_31(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = None
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_32(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(None)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_33(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = None
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_34(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "XXfallback-hashXX"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_35(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "FALLBACK-HASH"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_36(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = None
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_37(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = None
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_38(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    None, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_39(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=None
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_40(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_41(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_42(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = None
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_43(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = None
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_44(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error(None, e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_45(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", None)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_46(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error(e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_47(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", )
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_48(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("XXEmbedding failed, using fallback: %sXX", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_49(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_50(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("EMBEDDING FAILED, USING FALLBACK: %S", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_51(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = None
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_52(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(None)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_53(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = None

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_54(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "XXfallback-hashXX"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_55(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "FALLBACK-HASH"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_56(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=None,  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_57(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=None,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_58(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=None,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_59(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=None,
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_60(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_61(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            model=model_name,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_62(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            dimension=len(embedding),
        )

    def xǁEmbeddingPipelineǁembed_text__mutmut_63(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:100],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            )

    def xǁEmbeddingPipelineǁembed_text__mutmut_64(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResult with the embedding vector.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            return EmbeddingResult(
                text="",
                embedding=[0.0] * self.config.dimension,
                model="none",
                dimension=self.config.dimension,
            )

        # Truncate if too long (safeguard)
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning("Text truncated: %d > %d", len(text), MAX_TEXT_LENGTH)
            text = text[:MAX_TEXT_LENGTH]

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        # Generate embedding
        if self._use_fallback or self._model is None:
            embedding = self._fallback_embedding(text)
            model_name = "fallback-hash"
        else:
            try:
                normalize = self.config.normalize
                raw_embedding = self._model.encode(
                    text, normalize_embeddings=normalize
                )
                embedding = raw_embedding.tolist()
                model_name = self.config.model_name
            except Exception as e:
                logger.error("Embedding failed, using fallback: %s", e)
                embedding = self._fallback_embedding(text)
                model_name = "fallback-hash"

        return EmbeddingResult(
            text=text[:101],  # Truncate for storage
            embedding=embedding,
            model=model_name,
            dimension=len(embedding),
        )
    
    xǁEmbeddingPipelineǁembed_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEmbeddingPipelineǁembed_text__mutmut_1': xǁEmbeddingPipelineǁembed_text__mutmut_1, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_2': xǁEmbeddingPipelineǁembed_text__mutmut_2, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_3': xǁEmbeddingPipelineǁembed_text__mutmut_3, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_4': xǁEmbeddingPipelineǁembed_text__mutmut_4, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_5': xǁEmbeddingPipelineǁembed_text__mutmut_5, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_6': xǁEmbeddingPipelineǁembed_text__mutmut_6, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_7': xǁEmbeddingPipelineǁembed_text__mutmut_7, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_8': xǁEmbeddingPipelineǁembed_text__mutmut_8, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_9': xǁEmbeddingPipelineǁembed_text__mutmut_9, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_10': xǁEmbeddingPipelineǁembed_text__mutmut_10, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_11': xǁEmbeddingPipelineǁembed_text__mutmut_11, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_12': xǁEmbeddingPipelineǁembed_text__mutmut_12, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_13': xǁEmbeddingPipelineǁembed_text__mutmut_13, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_14': xǁEmbeddingPipelineǁembed_text__mutmut_14, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_15': xǁEmbeddingPipelineǁembed_text__mutmut_15, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_16': xǁEmbeddingPipelineǁembed_text__mutmut_16, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_17': xǁEmbeddingPipelineǁembed_text__mutmut_17, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_18': xǁEmbeddingPipelineǁembed_text__mutmut_18, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_19': xǁEmbeddingPipelineǁembed_text__mutmut_19, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_20': xǁEmbeddingPipelineǁembed_text__mutmut_20, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_21': xǁEmbeddingPipelineǁembed_text__mutmut_21, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_22': xǁEmbeddingPipelineǁembed_text__mutmut_22, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_23': xǁEmbeddingPipelineǁembed_text__mutmut_23, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_24': xǁEmbeddingPipelineǁembed_text__mutmut_24, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_25': xǁEmbeddingPipelineǁembed_text__mutmut_25, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_26': xǁEmbeddingPipelineǁembed_text__mutmut_26, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_27': xǁEmbeddingPipelineǁembed_text__mutmut_27, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_28': xǁEmbeddingPipelineǁembed_text__mutmut_28, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_29': xǁEmbeddingPipelineǁembed_text__mutmut_29, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_30': xǁEmbeddingPipelineǁembed_text__mutmut_30, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_31': xǁEmbeddingPipelineǁembed_text__mutmut_31, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_32': xǁEmbeddingPipelineǁembed_text__mutmut_32, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_33': xǁEmbeddingPipelineǁembed_text__mutmut_33, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_34': xǁEmbeddingPipelineǁembed_text__mutmut_34, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_35': xǁEmbeddingPipelineǁembed_text__mutmut_35, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_36': xǁEmbeddingPipelineǁembed_text__mutmut_36, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_37': xǁEmbeddingPipelineǁembed_text__mutmut_37, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_38': xǁEmbeddingPipelineǁembed_text__mutmut_38, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_39': xǁEmbeddingPipelineǁembed_text__mutmut_39, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_40': xǁEmbeddingPipelineǁembed_text__mutmut_40, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_41': xǁEmbeddingPipelineǁembed_text__mutmut_41, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_42': xǁEmbeddingPipelineǁembed_text__mutmut_42, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_43': xǁEmbeddingPipelineǁembed_text__mutmut_43, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_44': xǁEmbeddingPipelineǁembed_text__mutmut_44, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_45': xǁEmbeddingPipelineǁembed_text__mutmut_45, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_46': xǁEmbeddingPipelineǁembed_text__mutmut_46, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_47': xǁEmbeddingPipelineǁembed_text__mutmut_47, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_48': xǁEmbeddingPipelineǁembed_text__mutmut_48, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_49': xǁEmbeddingPipelineǁembed_text__mutmut_49, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_50': xǁEmbeddingPipelineǁembed_text__mutmut_50, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_51': xǁEmbeddingPipelineǁembed_text__mutmut_51, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_52': xǁEmbeddingPipelineǁembed_text__mutmut_52, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_53': xǁEmbeddingPipelineǁembed_text__mutmut_53, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_54': xǁEmbeddingPipelineǁembed_text__mutmut_54, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_55': xǁEmbeddingPipelineǁembed_text__mutmut_55, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_56': xǁEmbeddingPipelineǁembed_text__mutmut_56, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_57': xǁEmbeddingPipelineǁembed_text__mutmut_57, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_58': xǁEmbeddingPipelineǁembed_text__mutmut_58, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_59': xǁEmbeddingPipelineǁembed_text__mutmut_59, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_60': xǁEmbeddingPipelineǁembed_text__mutmut_60, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_61': xǁEmbeddingPipelineǁembed_text__mutmut_61, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_62': xǁEmbeddingPipelineǁembed_text__mutmut_62, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_63': xǁEmbeddingPipelineǁembed_text__mutmut_63, 
        'xǁEmbeddingPipelineǁembed_text__mutmut_64': xǁEmbeddingPipelineǁembed_text__mutmut_64
    }
    
    def embed_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEmbeddingPipelineǁembed_text__mutmut_orig"), object.__getattribute__(self, "xǁEmbeddingPipelineǁembed_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    embed_text.__signature__ = _mutmut_signature(xǁEmbeddingPipelineǁembed_text__mutmut_orig)
    xǁEmbeddingPipelineǁembed_text__mutmut_orig.__name__ = 'xǁEmbeddingPipelineǁembed_text'

    def xǁEmbeddingPipelineǁembed_texts__mutmut_orig(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_1(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_2(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_3(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = None

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_4(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback and self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_5(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is not None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_6(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(None)
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_7(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(None))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_8(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = None
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_9(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = None

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_10(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    None,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_11(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=None,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_12(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=None,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_13(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=None,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_14(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_15(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_16(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_17(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_18(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=True,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_19(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(None, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_20(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, None):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_21(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_22(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, ):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_23(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(None)

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_24(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=None,
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_25(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=None,
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_26(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=None,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_27(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=None,
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_28(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_29(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_30(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_31(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_32(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:101],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_33(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error(None, e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_34(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", None)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_35(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error(e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_36(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", )
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_37(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("XXBatch embedding failed, using fallback: %sXX", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_38(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_39(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("BATCH EMBEDDING FAILED, USING FALLBACK: %S", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_40(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(None)

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_41(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(None))

        logger.info("Embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_42(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info(None, len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_43(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", None)
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_44(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info(len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_45(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("Embedded %d texts", )
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_46(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("XXEmbedded %d textsXX", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_47(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("embedded %d texts", len(results))
        return results

    def xǁEmbeddingPipelineǁembed_texts__mutmut_48(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of EmbeddingResults.
        """
        if not texts:
            return []

        # Load model if not using fallback
        if not self._use_fallback:
            self._load_model()

        results = []

        if self._use_fallback or self._model is None:
            # Use fallback for each text
            for text in texts:
                results.append(self.embed_text(text))
        else:
            try:
                # Batch encode
                truncated_texts = [t[:MAX_TEXT_LENGTH] for t in texts]
                embeddings = self._model.encode(
                    truncated_texts,
                    normalize_embeddings=self.config.normalize,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )

                for text, embedding in zip(texts, embeddings):
                    results.append(EmbeddingResult(
                        text=text[:100],
                        embedding=embedding.tolist(),
                        model=self.config.model_name,
                        dimension=len(embedding),
                    ))

            except Exception as e:
                logger.error("Batch embedding failed, using fallback: %s", e)
                for text in texts:
                    results.append(self.embed_text(text))

        logger.info("EMBEDDED %D TEXTS", len(results))
        return results
    
    xǁEmbeddingPipelineǁembed_texts__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁEmbeddingPipelineǁembed_texts__mutmut_1': xǁEmbeddingPipelineǁembed_texts__mutmut_1, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_2': xǁEmbeddingPipelineǁembed_texts__mutmut_2, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_3': xǁEmbeddingPipelineǁembed_texts__mutmut_3, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_4': xǁEmbeddingPipelineǁembed_texts__mutmut_4, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_5': xǁEmbeddingPipelineǁembed_texts__mutmut_5, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_6': xǁEmbeddingPipelineǁembed_texts__mutmut_6, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_7': xǁEmbeddingPipelineǁembed_texts__mutmut_7, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_8': xǁEmbeddingPipelineǁembed_texts__mutmut_8, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_9': xǁEmbeddingPipelineǁembed_texts__mutmut_9, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_10': xǁEmbeddingPipelineǁembed_texts__mutmut_10, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_11': xǁEmbeddingPipelineǁembed_texts__mutmut_11, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_12': xǁEmbeddingPipelineǁembed_texts__mutmut_12, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_13': xǁEmbeddingPipelineǁembed_texts__mutmut_13, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_14': xǁEmbeddingPipelineǁembed_texts__mutmut_14, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_15': xǁEmbeddingPipelineǁembed_texts__mutmut_15, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_16': xǁEmbeddingPipelineǁembed_texts__mutmut_16, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_17': xǁEmbeddingPipelineǁembed_texts__mutmut_17, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_18': xǁEmbeddingPipelineǁembed_texts__mutmut_18, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_19': xǁEmbeddingPipelineǁembed_texts__mutmut_19, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_20': xǁEmbeddingPipelineǁembed_texts__mutmut_20, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_21': xǁEmbeddingPipelineǁembed_texts__mutmut_21, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_22': xǁEmbeddingPipelineǁembed_texts__mutmut_22, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_23': xǁEmbeddingPipelineǁembed_texts__mutmut_23, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_24': xǁEmbeddingPipelineǁembed_texts__mutmut_24, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_25': xǁEmbeddingPipelineǁembed_texts__mutmut_25, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_26': xǁEmbeddingPipelineǁembed_texts__mutmut_26, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_27': xǁEmbeddingPipelineǁembed_texts__mutmut_27, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_28': xǁEmbeddingPipelineǁembed_texts__mutmut_28, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_29': xǁEmbeddingPipelineǁembed_texts__mutmut_29, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_30': xǁEmbeddingPipelineǁembed_texts__mutmut_30, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_31': xǁEmbeddingPipelineǁembed_texts__mutmut_31, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_32': xǁEmbeddingPipelineǁembed_texts__mutmut_32, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_33': xǁEmbeddingPipelineǁembed_texts__mutmut_33, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_34': xǁEmbeddingPipelineǁembed_texts__mutmut_34, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_35': xǁEmbeddingPipelineǁembed_texts__mutmut_35, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_36': xǁEmbeddingPipelineǁembed_texts__mutmut_36, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_37': xǁEmbeddingPipelineǁembed_texts__mutmut_37, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_38': xǁEmbeddingPipelineǁembed_texts__mutmut_38, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_39': xǁEmbeddingPipelineǁembed_texts__mutmut_39, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_40': xǁEmbeddingPipelineǁembed_texts__mutmut_40, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_41': xǁEmbeddingPipelineǁembed_texts__mutmut_41, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_42': xǁEmbeddingPipelineǁembed_texts__mutmut_42, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_43': xǁEmbeddingPipelineǁembed_texts__mutmut_43, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_44': xǁEmbeddingPipelineǁembed_texts__mutmut_44, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_45': xǁEmbeddingPipelineǁembed_texts__mutmut_45, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_46': xǁEmbeddingPipelineǁembed_texts__mutmut_46, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_47': xǁEmbeddingPipelineǁembed_texts__mutmut_47, 
        'xǁEmbeddingPipelineǁembed_texts__mutmut_48': xǁEmbeddingPipelineǁembed_texts__mutmut_48
    }
    
    def embed_texts(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁEmbeddingPipelineǁembed_texts__mutmut_orig"), object.__getattribute__(self, "xǁEmbeddingPipelineǁembed_texts__mutmut_mutants"), args, kwargs, self)
        return result 
    
    embed_texts.__signature__ = _mutmut_signature(xǁEmbeddingPipelineǁembed_texts__mutmut_orig)
    xǁEmbeddingPipelineǁembed_texts__mutmut_orig.__name__ = 'xǁEmbeddingPipelineǁembed_texts'

    def get_dimension(self) -> int:
        """Return the embedding dimension."""
        return self.config.dimension


def x_main__mutmut_orig() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_1() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=None)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_2() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = None

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_3() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = None
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_4() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text(None)
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_5() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("XXHello worldXX")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_6() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_7() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("HELLO WORLD")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_8() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(None)
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_9() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(None)

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_10() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:6]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_11() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = None
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_12() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["XXFirst textXX", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_13() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["first text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_14() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["FIRST TEXT", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_15() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "XXSecond textXX", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_16() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_17() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "SECOND TEXT", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_18() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "XXThird textXX"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_19() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_20() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "THIRD TEXT"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_21() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = None
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_22() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(None)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_23() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(None)
    for r in results:
        print(f"  - {r.text}: dim={r.dimension}")


def x_main__mutmut_24() -> None:
    """Test the embedding pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = EmbeddingPipeline()

    # Test single embedding
    result = pipeline.embed_text("Hello world")
    print(f"Single embedding: dim={result.dimension}, model={result.model}")
    print(f"  First 5 values: {result.embedding[:5]}")

    # Test batch embedding
    texts = ["First text", "Second text", "Third text"]
    results = pipeline.embed_texts(texts)
    print(f"\nBatch embedding: {len(results)} results")
    for r in results:
        print(None)

x_main__mutmut_mutants : ClassVar[MutantDict] = {
'x_main__mutmut_1': x_main__mutmut_1, 
    'x_main__mutmut_2': x_main__mutmut_2, 
    'x_main__mutmut_3': x_main__mutmut_3, 
    'x_main__mutmut_4': x_main__mutmut_4, 
    'x_main__mutmut_5': x_main__mutmut_5, 
    'x_main__mutmut_6': x_main__mutmut_6, 
    'x_main__mutmut_7': x_main__mutmut_7, 
    'x_main__mutmut_8': x_main__mutmut_8, 
    'x_main__mutmut_9': x_main__mutmut_9, 
    'x_main__mutmut_10': x_main__mutmut_10, 
    'x_main__mutmut_11': x_main__mutmut_11, 
    'x_main__mutmut_12': x_main__mutmut_12, 
    'x_main__mutmut_13': x_main__mutmut_13, 
    'x_main__mutmut_14': x_main__mutmut_14, 
    'x_main__mutmut_15': x_main__mutmut_15, 
    'x_main__mutmut_16': x_main__mutmut_16, 
    'x_main__mutmut_17': x_main__mutmut_17, 
    'x_main__mutmut_18': x_main__mutmut_18, 
    'x_main__mutmut_19': x_main__mutmut_19, 
    'x_main__mutmut_20': x_main__mutmut_20, 
    'x_main__mutmut_21': x_main__mutmut_21, 
    'x_main__mutmut_22': x_main__mutmut_22, 
    'x_main__mutmut_23': x_main__mutmut_23, 
    'x_main__mutmut_24': x_main__mutmut_24
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":
    main()
