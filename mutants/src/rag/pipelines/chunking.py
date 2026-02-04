"""
Chunking Pipeline - Split documents into semantic chunks.

This module provides text chunking functionality for the RAG pipeline.

Author: Copilot Agent
Generated: 2025-12-24

Safeguards:
- Input validation on text and parameters
- Bounds checking on chunk sizes
- Defensive error handling
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Iterator

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MIN_CHUNK_SIZE = 50
MAX_CHUNK_SIZE = 10000
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200
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
class Chunk:
    """A text chunk with metadata."""

    content: str
    start_index: int
    end_index: int
    metadata: dict = field(default_factory=dict)

    @property
    def length(self) -> int:
        """Return the length of the chunk content."""
        return len(self.content)


@dataclass
class ChunkingConfig:
    """Configuration for the chunking pipeline."""

    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_OVERLAP
    separator: str = "\n\n"
    keep_separator: bool = True


class ChunkingPipeline:
    """
    Pipeline for splitting text into semantic chunks.

    Features:
    - Configurable chunk size and overlap
    - Separator-aware splitting
    - Metadata preservation

    Safeguards:
    - Input validation on text and parameters
    - Bounds checking on chunk sizes
    """

    def xǁChunkingPipelineǁ__init____mutmut_orig(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_1(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = None

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_2(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config and ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_3(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = None
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_4(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            None,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_5(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            None
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_6(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_7(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_8(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(None, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_9(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, None)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_10(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_11(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, )
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_12(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = None

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_13(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            None,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_14(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            None
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_15(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_16(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_17(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size / 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_18(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 3
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_19(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            None,
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_20(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            None,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_21(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            None
        )

    def xǁChunkingPipelineǁ__init____mutmut_22(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_23(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_24(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            )

    def xǁChunkingPipelineǁ__init____mutmut_25(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "XXChunkingPipeline initialized: size=%d, overlap=%dXX",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_26(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "chunkingpipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap
        )

    def xǁChunkingPipelineǁ__init____mutmut_27(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(
            MIN_CHUNK_SIZE,
            min(MAX_CHUNK_SIZE, self.config.chunk_size)
        )
        self.config.chunk_overlap = min(
            self.config.chunk_overlap,
            self.config.chunk_size // 2
        )

        logger.info(
            "CHUNKINGPIPELINE INITIALIZED: SIZE=%D, OVERLAP=%D",
            self.config.chunk_size,
            self.config.chunk_overlap
        )
    
    xǁChunkingPipelineǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChunkingPipelineǁ__init____mutmut_1': xǁChunkingPipelineǁ__init____mutmut_1, 
        'xǁChunkingPipelineǁ__init____mutmut_2': xǁChunkingPipelineǁ__init____mutmut_2, 
        'xǁChunkingPipelineǁ__init____mutmut_3': xǁChunkingPipelineǁ__init____mutmut_3, 
        'xǁChunkingPipelineǁ__init____mutmut_4': xǁChunkingPipelineǁ__init____mutmut_4, 
        'xǁChunkingPipelineǁ__init____mutmut_5': xǁChunkingPipelineǁ__init____mutmut_5, 
        'xǁChunkingPipelineǁ__init____mutmut_6': xǁChunkingPipelineǁ__init____mutmut_6, 
        'xǁChunkingPipelineǁ__init____mutmut_7': xǁChunkingPipelineǁ__init____mutmut_7, 
        'xǁChunkingPipelineǁ__init____mutmut_8': xǁChunkingPipelineǁ__init____mutmut_8, 
        'xǁChunkingPipelineǁ__init____mutmut_9': xǁChunkingPipelineǁ__init____mutmut_9, 
        'xǁChunkingPipelineǁ__init____mutmut_10': xǁChunkingPipelineǁ__init____mutmut_10, 
        'xǁChunkingPipelineǁ__init____mutmut_11': xǁChunkingPipelineǁ__init____mutmut_11, 
        'xǁChunkingPipelineǁ__init____mutmut_12': xǁChunkingPipelineǁ__init____mutmut_12, 
        'xǁChunkingPipelineǁ__init____mutmut_13': xǁChunkingPipelineǁ__init____mutmut_13, 
        'xǁChunkingPipelineǁ__init____mutmut_14': xǁChunkingPipelineǁ__init____mutmut_14, 
        'xǁChunkingPipelineǁ__init____mutmut_15': xǁChunkingPipelineǁ__init____mutmut_15, 
        'xǁChunkingPipelineǁ__init____mutmut_16': xǁChunkingPipelineǁ__init____mutmut_16, 
        'xǁChunkingPipelineǁ__init____mutmut_17': xǁChunkingPipelineǁ__init____mutmut_17, 
        'xǁChunkingPipelineǁ__init____mutmut_18': xǁChunkingPipelineǁ__init____mutmut_18, 
        'xǁChunkingPipelineǁ__init____mutmut_19': xǁChunkingPipelineǁ__init____mutmut_19, 
        'xǁChunkingPipelineǁ__init____mutmut_20': xǁChunkingPipelineǁ__init____mutmut_20, 
        'xǁChunkingPipelineǁ__init____mutmut_21': xǁChunkingPipelineǁ__init____mutmut_21, 
        'xǁChunkingPipelineǁ__init____mutmut_22': xǁChunkingPipelineǁ__init____mutmut_22, 
        'xǁChunkingPipelineǁ__init____mutmut_23': xǁChunkingPipelineǁ__init____mutmut_23, 
        'xǁChunkingPipelineǁ__init____mutmut_24': xǁChunkingPipelineǁ__init____mutmut_24, 
        'xǁChunkingPipelineǁ__init____mutmut_25': xǁChunkingPipelineǁ__init____mutmut_25, 
        'xǁChunkingPipelineǁ__init____mutmut_26': xǁChunkingPipelineǁ__init____mutmut_26, 
        'xǁChunkingPipelineǁ__init____mutmut_27': xǁChunkingPipelineǁ__init____mutmut_27
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChunkingPipelineǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁChunkingPipelineǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁChunkingPipelineǁ__init____mutmut_orig)
    xǁChunkingPipelineǁ__init____mutmut_orig.__name__ = 'xǁChunkingPipelineǁ__init__'

    def xǁChunkingPipelineǁchunk_text__mutmut_orig(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_1(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text and not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_2(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_3(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_4(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning(None)
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_5(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("XXEmpty or invalid text providedXX")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_6(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_7(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("EMPTY OR INVALID TEXT PROVIDED")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_8(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = None
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_9(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata and {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_10(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = None

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_11(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = None

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_12(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(None)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_13(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = None
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_14(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = "XXXX"
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_15(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = None

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_16(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 1

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_17(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) - len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_18(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) < self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_19(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk = split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_20(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk -= split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_21(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(None)

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_22(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=None,
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_23(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=None,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_24(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=None,
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_25(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata=None,
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_26(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_27(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_28(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_29(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_30(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start - len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_31(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "XXchunk_indexXX": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_32(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "CHUNK_INDEX": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_33(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) >= self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_34(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = None
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_35(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(None)
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_36(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(None, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_37(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, None))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_38(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_39(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, ))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_40(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = None
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_41(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "XXchunk_indexXX": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_42(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "CHUNK_INDEX": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_43(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(None)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_44(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = None
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_45(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = "XXXX"
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_46(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = None
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_47(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[+1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_48(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-2].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_49(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 1
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_50(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start = len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_51(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start -= len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_52(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = None

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_53(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(None)

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_54(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=None,
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_55(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=None,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_56(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=None,
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_57(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata=None,
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_58(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_59(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_60(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_61(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_62(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start - len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_63(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "XXchunk_indexXX": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_64(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "CHUNK_INDEX": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_65(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info(None, len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_66(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", None, len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_67(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), None)
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_68(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info(len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_69(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_70(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("Created %d chunks from text of length %d", len(chunks), )
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_71(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("XXCreated %d chunks from text of length %dXX", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_72(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def xǁChunkingPipelineǁchunk_text__mutmut_73(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk.
            metadata: Optional metadata to attach to chunks.

        Returns:
            List of Chunk objects.
        """
        # Input validation (safeguard)
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided")
            return []

        metadata = metadata or {}
        chunks: list[Chunk] = []

        # Split by separator first
        splits = self._split_by_separator(text)

        # Merge small splits, split large ones
        current_chunk = ""
        current_start = 0

        for split in splits:
            if len(current_chunk) + len(split) <= self.config.chunk_size:
                current_chunk += split
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(Chunk(
                        content=current_chunk.strip(),
                        start_index=current_start,
                        end_index=current_start + len(current_chunk),
                        metadata={**metadata, "chunk_index": len(chunks)},
                    ))

                # Handle large splits
                if len(split) > self.config.chunk_size:
                    # Split into smaller chunks with overlap
                    sub_chunks = list(self._split_large_text(split, current_start))
                    for sub_chunk in sub_chunks:
                        sub_chunk.metadata = {**metadata, "chunk_index": len(chunks)}
                        chunks.append(sub_chunk)
                    current_chunk = ""
                    current_start = chunks[-1].end_index if chunks else 0
                else:
                    current_start += len(current_chunk)
                    current_chunk = split

        # Add final chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                content=current_chunk.strip(),
                start_index=current_start,
                end_index=current_start + len(current_chunk),
                metadata={**metadata, "chunk_index": len(chunks)},
            ))

        logger.info("CREATED %D CHUNKS FROM TEXT OF LENGTH %D", len(chunks), len(text))
        return chunks
    
    xǁChunkingPipelineǁchunk_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChunkingPipelineǁchunk_text__mutmut_1': xǁChunkingPipelineǁchunk_text__mutmut_1, 
        'xǁChunkingPipelineǁchunk_text__mutmut_2': xǁChunkingPipelineǁchunk_text__mutmut_2, 
        'xǁChunkingPipelineǁchunk_text__mutmut_3': xǁChunkingPipelineǁchunk_text__mutmut_3, 
        'xǁChunkingPipelineǁchunk_text__mutmut_4': xǁChunkingPipelineǁchunk_text__mutmut_4, 
        'xǁChunkingPipelineǁchunk_text__mutmut_5': xǁChunkingPipelineǁchunk_text__mutmut_5, 
        'xǁChunkingPipelineǁchunk_text__mutmut_6': xǁChunkingPipelineǁchunk_text__mutmut_6, 
        'xǁChunkingPipelineǁchunk_text__mutmut_7': xǁChunkingPipelineǁchunk_text__mutmut_7, 
        'xǁChunkingPipelineǁchunk_text__mutmut_8': xǁChunkingPipelineǁchunk_text__mutmut_8, 
        'xǁChunkingPipelineǁchunk_text__mutmut_9': xǁChunkingPipelineǁchunk_text__mutmut_9, 
        'xǁChunkingPipelineǁchunk_text__mutmut_10': xǁChunkingPipelineǁchunk_text__mutmut_10, 
        'xǁChunkingPipelineǁchunk_text__mutmut_11': xǁChunkingPipelineǁchunk_text__mutmut_11, 
        'xǁChunkingPipelineǁchunk_text__mutmut_12': xǁChunkingPipelineǁchunk_text__mutmut_12, 
        'xǁChunkingPipelineǁchunk_text__mutmut_13': xǁChunkingPipelineǁchunk_text__mutmut_13, 
        'xǁChunkingPipelineǁchunk_text__mutmut_14': xǁChunkingPipelineǁchunk_text__mutmut_14, 
        'xǁChunkingPipelineǁchunk_text__mutmut_15': xǁChunkingPipelineǁchunk_text__mutmut_15, 
        'xǁChunkingPipelineǁchunk_text__mutmut_16': xǁChunkingPipelineǁchunk_text__mutmut_16, 
        'xǁChunkingPipelineǁchunk_text__mutmut_17': xǁChunkingPipelineǁchunk_text__mutmut_17, 
        'xǁChunkingPipelineǁchunk_text__mutmut_18': xǁChunkingPipelineǁchunk_text__mutmut_18, 
        'xǁChunkingPipelineǁchunk_text__mutmut_19': xǁChunkingPipelineǁchunk_text__mutmut_19, 
        'xǁChunkingPipelineǁchunk_text__mutmut_20': xǁChunkingPipelineǁchunk_text__mutmut_20, 
        'xǁChunkingPipelineǁchunk_text__mutmut_21': xǁChunkingPipelineǁchunk_text__mutmut_21, 
        'xǁChunkingPipelineǁchunk_text__mutmut_22': xǁChunkingPipelineǁchunk_text__mutmut_22, 
        'xǁChunkingPipelineǁchunk_text__mutmut_23': xǁChunkingPipelineǁchunk_text__mutmut_23, 
        'xǁChunkingPipelineǁchunk_text__mutmut_24': xǁChunkingPipelineǁchunk_text__mutmut_24, 
        'xǁChunkingPipelineǁchunk_text__mutmut_25': xǁChunkingPipelineǁchunk_text__mutmut_25, 
        'xǁChunkingPipelineǁchunk_text__mutmut_26': xǁChunkingPipelineǁchunk_text__mutmut_26, 
        'xǁChunkingPipelineǁchunk_text__mutmut_27': xǁChunkingPipelineǁchunk_text__mutmut_27, 
        'xǁChunkingPipelineǁchunk_text__mutmut_28': xǁChunkingPipelineǁchunk_text__mutmut_28, 
        'xǁChunkingPipelineǁchunk_text__mutmut_29': xǁChunkingPipelineǁchunk_text__mutmut_29, 
        'xǁChunkingPipelineǁchunk_text__mutmut_30': xǁChunkingPipelineǁchunk_text__mutmut_30, 
        'xǁChunkingPipelineǁchunk_text__mutmut_31': xǁChunkingPipelineǁchunk_text__mutmut_31, 
        'xǁChunkingPipelineǁchunk_text__mutmut_32': xǁChunkingPipelineǁchunk_text__mutmut_32, 
        'xǁChunkingPipelineǁchunk_text__mutmut_33': xǁChunkingPipelineǁchunk_text__mutmut_33, 
        'xǁChunkingPipelineǁchunk_text__mutmut_34': xǁChunkingPipelineǁchunk_text__mutmut_34, 
        'xǁChunkingPipelineǁchunk_text__mutmut_35': xǁChunkingPipelineǁchunk_text__mutmut_35, 
        'xǁChunkingPipelineǁchunk_text__mutmut_36': xǁChunkingPipelineǁchunk_text__mutmut_36, 
        'xǁChunkingPipelineǁchunk_text__mutmut_37': xǁChunkingPipelineǁchunk_text__mutmut_37, 
        'xǁChunkingPipelineǁchunk_text__mutmut_38': xǁChunkingPipelineǁchunk_text__mutmut_38, 
        'xǁChunkingPipelineǁchunk_text__mutmut_39': xǁChunkingPipelineǁchunk_text__mutmut_39, 
        'xǁChunkingPipelineǁchunk_text__mutmut_40': xǁChunkingPipelineǁchunk_text__mutmut_40, 
        'xǁChunkingPipelineǁchunk_text__mutmut_41': xǁChunkingPipelineǁchunk_text__mutmut_41, 
        'xǁChunkingPipelineǁchunk_text__mutmut_42': xǁChunkingPipelineǁchunk_text__mutmut_42, 
        'xǁChunkingPipelineǁchunk_text__mutmut_43': xǁChunkingPipelineǁchunk_text__mutmut_43, 
        'xǁChunkingPipelineǁchunk_text__mutmut_44': xǁChunkingPipelineǁchunk_text__mutmut_44, 
        'xǁChunkingPipelineǁchunk_text__mutmut_45': xǁChunkingPipelineǁchunk_text__mutmut_45, 
        'xǁChunkingPipelineǁchunk_text__mutmut_46': xǁChunkingPipelineǁchunk_text__mutmut_46, 
        'xǁChunkingPipelineǁchunk_text__mutmut_47': xǁChunkingPipelineǁchunk_text__mutmut_47, 
        'xǁChunkingPipelineǁchunk_text__mutmut_48': xǁChunkingPipelineǁchunk_text__mutmut_48, 
        'xǁChunkingPipelineǁchunk_text__mutmut_49': xǁChunkingPipelineǁchunk_text__mutmut_49, 
        'xǁChunkingPipelineǁchunk_text__mutmut_50': xǁChunkingPipelineǁchunk_text__mutmut_50, 
        'xǁChunkingPipelineǁchunk_text__mutmut_51': xǁChunkingPipelineǁchunk_text__mutmut_51, 
        'xǁChunkingPipelineǁchunk_text__mutmut_52': xǁChunkingPipelineǁchunk_text__mutmut_52, 
        'xǁChunkingPipelineǁchunk_text__mutmut_53': xǁChunkingPipelineǁchunk_text__mutmut_53, 
        'xǁChunkingPipelineǁchunk_text__mutmut_54': xǁChunkingPipelineǁchunk_text__mutmut_54, 
        'xǁChunkingPipelineǁchunk_text__mutmut_55': xǁChunkingPipelineǁchunk_text__mutmut_55, 
        'xǁChunkingPipelineǁchunk_text__mutmut_56': xǁChunkingPipelineǁchunk_text__mutmut_56, 
        'xǁChunkingPipelineǁchunk_text__mutmut_57': xǁChunkingPipelineǁchunk_text__mutmut_57, 
        'xǁChunkingPipelineǁchunk_text__mutmut_58': xǁChunkingPipelineǁchunk_text__mutmut_58, 
        'xǁChunkingPipelineǁchunk_text__mutmut_59': xǁChunkingPipelineǁchunk_text__mutmut_59, 
        'xǁChunkingPipelineǁchunk_text__mutmut_60': xǁChunkingPipelineǁchunk_text__mutmut_60, 
        'xǁChunkingPipelineǁchunk_text__mutmut_61': xǁChunkingPipelineǁchunk_text__mutmut_61, 
        'xǁChunkingPipelineǁchunk_text__mutmut_62': xǁChunkingPipelineǁchunk_text__mutmut_62, 
        'xǁChunkingPipelineǁchunk_text__mutmut_63': xǁChunkingPipelineǁchunk_text__mutmut_63, 
        'xǁChunkingPipelineǁchunk_text__mutmut_64': xǁChunkingPipelineǁchunk_text__mutmut_64, 
        'xǁChunkingPipelineǁchunk_text__mutmut_65': xǁChunkingPipelineǁchunk_text__mutmut_65, 
        'xǁChunkingPipelineǁchunk_text__mutmut_66': xǁChunkingPipelineǁchunk_text__mutmut_66, 
        'xǁChunkingPipelineǁchunk_text__mutmut_67': xǁChunkingPipelineǁchunk_text__mutmut_67, 
        'xǁChunkingPipelineǁchunk_text__mutmut_68': xǁChunkingPipelineǁchunk_text__mutmut_68, 
        'xǁChunkingPipelineǁchunk_text__mutmut_69': xǁChunkingPipelineǁchunk_text__mutmut_69, 
        'xǁChunkingPipelineǁchunk_text__mutmut_70': xǁChunkingPipelineǁchunk_text__mutmut_70, 
        'xǁChunkingPipelineǁchunk_text__mutmut_71': xǁChunkingPipelineǁchunk_text__mutmut_71, 
        'xǁChunkingPipelineǁchunk_text__mutmut_72': xǁChunkingPipelineǁchunk_text__mutmut_72, 
        'xǁChunkingPipelineǁchunk_text__mutmut_73': xǁChunkingPipelineǁchunk_text__mutmut_73
    }
    
    def chunk_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChunkingPipelineǁchunk_text__mutmut_orig"), object.__getattribute__(self, "xǁChunkingPipelineǁchunk_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    chunk_text.__signature__ = _mutmut_signature(xǁChunkingPipelineǁchunk_text__mutmut_orig)
    xǁChunkingPipelineǁchunk_text__mutmut_orig.__name__ = 'xǁChunkingPipelineǁchunk_text'

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_orig(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_1(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = None

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_2(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = None
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_3(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(None, text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_4(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", None)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_5(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_6(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", )
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_7(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.rsplit(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_8(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(None)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_9(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = None
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_10(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(None, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_11(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, None, 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_12(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), None):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_13(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_14(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_15(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), ):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_16(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(1, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_17(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 3):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_18(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = None
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_19(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i - 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_20(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 2 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_21(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 <= len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_22(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part = parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_23(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part -= parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_24(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i - 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_25(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 2]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_26(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(None)
            return result
        else:
            return text.split(separator)

    def xǁChunkingPipelineǁ_split_by_separator__mutmut_27(self, text: str) -> list[str]:
        """Split text by configured separator."""
        separator = self.config.separator

        if self.config.keep_separator:
            # Keep separator attached to preceding chunk
            parts = re.split(f"({re.escape(separator)})", text)
            result = []
            for i in range(0, len(parts), 2):
                part = parts[i]
                if i + 1 < len(parts):
                    part += parts[i + 1]
                if part:
                    result.append(part)
            return result
        else:
            return text.split(None)
    
    xǁChunkingPipelineǁ_split_by_separator__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChunkingPipelineǁ_split_by_separator__mutmut_1': xǁChunkingPipelineǁ_split_by_separator__mutmut_1, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_2': xǁChunkingPipelineǁ_split_by_separator__mutmut_2, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_3': xǁChunkingPipelineǁ_split_by_separator__mutmut_3, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_4': xǁChunkingPipelineǁ_split_by_separator__mutmut_4, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_5': xǁChunkingPipelineǁ_split_by_separator__mutmut_5, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_6': xǁChunkingPipelineǁ_split_by_separator__mutmut_6, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_7': xǁChunkingPipelineǁ_split_by_separator__mutmut_7, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_8': xǁChunkingPipelineǁ_split_by_separator__mutmut_8, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_9': xǁChunkingPipelineǁ_split_by_separator__mutmut_9, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_10': xǁChunkingPipelineǁ_split_by_separator__mutmut_10, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_11': xǁChunkingPipelineǁ_split_by_separator__mutmut_11, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_12': xǁChunkingPipelineǁ_split_by_separator__mutmut_12, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_13': xǁChunkingPipelineǁ_split_by_separator__mutmut_13, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_14': xǁChunkingPipelineǁ_split_by_separator__mutmut_14, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_15': xǁChunkingPipelineǁ_split_by_separator__mutmut_15, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_16': xǁChunkingPipelineǁ_split_by_separator__mutmut_16, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_17': xǁChunkingPipelineǁ_split_by_separator__mutmut_17, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_18': xǁChunkingPipelineǁ_split_by_separator__mutmut_18, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_19': xǁChunkingPipelineǁ_split_by_separator__mutmut_19, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_20': xǁChunkingPipelineǁ_split_by_separator__mutmut_20, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_21': xǁChunkingPipelineǁ_split_by_separator__mutmut_21, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_22': xǁChunkingPipelineǁ_split_by_separator__mutmut_22, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_23': xǁChunkingPipelineǁ_split_by_separator__mutmut_23, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_24': xǁChunkingPipelineǁ_split_by_separator__mutmut_24, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_25': xǁChunkingPipelineǁ_split_by_separator__mutmut_25, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_26': xǁChunkingPipelineǁ_split_by_separator__mutmut_26, 
        'xǁChunkingPipelineǁ_split_by_separator__mutmut_27': xǁChunkingPipelineǁ_split_by_separator__mutmut_27
    }
    
    def _split_by_separator(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChunkingPipelineǁ_split_by_separator__mutmut_orig"), object.__getattribute__(self, "xǁChunkingPipelineǁ_split_by_separator__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _split_by_separator.__signature__ = _mutmut_signature(xǁChunkingPipelineǁ_split_by_separator__mutmut_orig)
    xǁChunkingPipelineǁ_split_by_separator__mutmut_orig.__name__ = 'xǁChunkingPipelineǁ_split_by_separator'

    def xǁChunkingPipelineǁ_split_large_text__mutmut_orig(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_1(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = None
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_2(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = None
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_3(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = None

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_4(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size + overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_5(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(None, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_6(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, None, step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_7(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), None):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_8(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_9(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_10(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), ):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_11(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(1, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_12(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = None
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_13(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(None, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_14(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, None)
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_15(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_16(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, )
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_17(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i - chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_18(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = None

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_19(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=None,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_20(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=None,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_21(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=None,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_22(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_23(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_24(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_25(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index - i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_26(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index - chunk_end,
            )

            if chunk_end == len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_27(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end != len(text):
                break

    def xǁChunkingPipelineǁ_split_large_text__mutmut_28(self, text: str, base_index: int) -> Iterator[Chunk]:
        """Split large text into overlapping chunks."""
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        step = chunk_size - overlap

        for i in range(0, len(text), step):
            chunk_end = min(i + chunk_size, len(text))
            chunk_content = text[i:chunk_end]

            yield Chunk(
                content=chunk_content,
                start_index=base_index + i,
                end_index=base_index + chunk_end,
            )

            if chunk_end == len(text):
                return
    
    xǁChunkingPipelineǁ_split_large_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChunkingPipelineǁ_split_large_text__mutmut_1': xǁChunkingPipelineǁ_split_large_text__mutmut_1, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_2': xǁChunkingPipelineǁ_split_large_text__mutmut_2, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_3': xǁChunkingPipelineǁ_split_large_text__mutmut_3, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_4': xǁChunkingPipelineǁ_split_large_text__mutmut_4, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_5': xǁChunkingPipelineǁ_split_large_text__mutmut_5, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_6': xǁChunkingPipelineǁ_split_large_text__mutmut_6, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_7': xǁChunkingPipelineǁ_split_large_text__mutmut_7, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_8': xǁChunkingPipelineǁ_split_large_text__mutmut_8, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_9': xǁChunkingPipelineǁ_split_large_text__mutmut_9, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_10': xǁChunkingPipelineǁ_split_large_text__mutmut_10, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_11': xǁChunkingPipelineǁ_split_large_text__mutmut_11, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_12': xǁChunkingPipelineǁ_split_large_text__mutmut_12, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_13': xǁChunkingPipelineǁ_split_large_text__mutmut_13, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_14': xǁChunkingPipelineǁ_split_large_text__mutmut_14, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_15': xǁChunkingPipelineǁ_split_large_text__mutmut_15, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_16': xǁChunkingPipelineǁ_split_large_text__mutmut_16, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_17': xǁChunkingPipelineǁ_split_large_text__mutmut_17, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_18': xǁChunkingPipelineǁ_split_large_text__mutmut_18, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_19': xǁChunkingPipelineǁ_split_large_text__mutmut_19, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_20': xǁChunkingPipelineǁ_split_large_text__mutmut_20, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_21': xǁChunkingPipelineǁ_split_large_text__mutmut_21, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_22': xǁChunkingPipelineǁ_split_large_text__mutmut_22, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_23': xǁChunkingPipelineǁ_split_large_text__mutmut_23, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_24': xǁChunkingPipelineǁ_split_large_text__mutmut_24, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_25': xǁChunkingPipelineǁ_split_large_text__mutmut_25, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_26': xǁChunkingPipelineǁ_split_large_text__mutmut_26, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_27': xǁChunkingPipelineǁ_split_large_text__mutmut_27, 
        'xǁChunkingPipelineǁ_split_large_text__mutmut_28': xǁChunkingPipelineǁ_split_large_text__mutmut_28
    }
    
    def _split_large_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChunkingPipelineǁ_split_large_text__mutmut_orig"), object.__getattribute__(self, "xǁChunkingPipelineǁ_split_large_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _split_large_text.__signature__ = _mutmut_signature(xǁChunkingPipelineǁ_split_large_text__mutmut_orig)
    xǁChunkingPipelineǁ_split_large_text__mutmut_orig.__name__ = 'xǁChunkingPipelineǁ_split_large_text'

    def xǁChunkingPipelineǁchunk_code__mutmut_orig(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_1(
        self,
        code: str,
        language: str = "XXpythonXX",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_2(
        self,
        code: str,
        language: str = "PYTHON",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_3(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = None
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_4(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata and {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_5(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = None

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_6(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["XXlanguageXX"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_7(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["LANGUAGE"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_8(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = None
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_9(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = None  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_10(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "XX\n\nXX"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_11(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = None

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_12(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(None, metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_13(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, None)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_14(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(metadata)

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_15(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, )

        self.config.separator = original_separator
        return chunks

    def xǁChunkingPipelineǁchunk_code__mutmut_16(
        self,
        code: str,
        language: str = "python",
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split code into chunks with language-aware boundaries.

        Args:
            code: The source code to chunk.
            language: The programming language.
            metadata: Optional metadata.

        Returns:
            List of Chunk objects.
        """
        metadata = metadata or {}
        metadata["language"] = language

        # Note: Previous implementation assigned language-specific separators
        # but never used them. The actual separation logic uses self.config.separator
        # which is temporarily overridden below for code chunking.

        original_separator = self.config.separator
        self.config.separator = "\n\n"  # Use simple separator for code

        # Split on code boundaries
        chunks = self.chunk_text(code, metadata)

        self.config.separator = None
        return chunks
    
    xǁChunkingPipelineǁchunk_code__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁChunkingPipelineǁchunk_code__mutmut_1': xǁChunkingPipelineǁchunk_code__mutmut_1, 
        'xǁChunkingPipelineǁchunk_code__mutmut_2': xǁChunkingPipelineǁchunk_code__mutmut_2, 
        'xǁChunkingPipelineǁchunk_code__mutmut_3': xǁChunkingPipelineǁchunk_code__mutmut_3, 
        'xǁChunkingPipelineǁchunk_code__mutmut_4': xǁChunkingPipelineǁchunk_code__mutmut_4, 
        'xǁChunkingPipelineǁchunk_code__mutmut_5': xǁChunkingPipelineǁchunk_code__mutmut_5, 
        'xǁChunkingPipelineǁchunk_code__mutmut_6': xǁChunkingPipelineǁchunk_code__mutmut_6, 
        'xǁChunkingPipelineǁchunk_code__mutmut_7': xǁChunkingPipelineǁchunk_code__mutmut_7, 
        'xǁChunkingPipelineǁchunk_code__mutmut_8': xǁChunkingPipelineǁchunk_code__mutmut_8, 
        'xǁChunkingPipelineǁchunk_code__mutmut_9': xǁChunkingPipelineǁchunk_code__mutmut_9, 
        'xǁChunkingPipelineǁchunk_code__mutmut_10': xǁChunkingPipelineǁchunk_code__mutmut_10, 
        'xǁChunkingPipelineǁchunk_code__mutmut_11': xǁChunkingPipelineǁchunk_code__mutmut_11, 
        'xǁChunkingPipelineǁchunk_code__mutmut_12': xǁChunkingPipelineǁchunk_code__mutmut_12, 
        'xǁChunkingPipelineǁchunk_code__mutmut_13': xǁChunkingPipelineǁchunk_code__mutmut_13, 
        'xǁChunkingPipelineǁchunk_code__mutmut_14': xǁChunkingPipelineǁchunk_code__mutmut_14, 
        'xǁChunkingPipelineǁchunk_code__mutmut_15': xǁChunkingPipelineǁchunk_code__mutmut_15, 
        'xǁChunkingPipelineǁchunk_code__mutmut_16': xǁChunkingPipelineǁchunk_code__mutmut_16
    }
    
    def chunk_code(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁChunkingPipelineǁchunk_code__mutmut_orig"), object.__getattribute__(self, "xǁChunkingPipelineǁchunk_code__mutmut_mutants"), args, kwargs, self)
        return result 
    
    chunk_code.__signature__ = _mutmut_signature(xǁChunkingPipelineǁchunk_code__mutmut_orig)
    xǁChunkingPipelineǁchunk_code__mutmut_orig.__name__ = 'xǁChunkingPipelineǁchunk_code'


def x_main__mutmut_orig() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_1() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=None)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_2() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = None

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_3() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = None

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_4() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = None

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_5() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(None, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_6() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, None)

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_7() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text({"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_8() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, )

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_9() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"XXsourceXX": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_10() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"SOURCE": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_11() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "XXtestXX"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_12() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "TEST"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_13() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(None)
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_14() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(None)
        print(f"    Preview: {chunk.content[:50]}...")


def x_main__mutmut_15() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(None)


def x_main__mutmut_16() -> None:
    """Test the chunking pipeline."""
    logging.basicConfig(level=logging.INFO)

    pipeline = ChunkingPipeline()

    sample_text = """
# Introduction

This is a sample document for testing the chunking pipeline.
It contains multiple paragraphs and sections.

## Section 1

This section contains information about topic A.
It spans multiple lines and includes details.

## Section 2

This section covers topic B with different content.
The chunking pipeline should handle this properly.
"""

    chunks = pipeline.chunk_text(sample_text, {"source": "test"})

    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"  [{chunk.start_index}:{chunk.end_index}] ({chunk.length} chars)")
        print(f"    Preview: {chunk.content[:51]}...")

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
    'x_main__mutmut_16': x_main__mutmut_16
}

def main(*args, **kwargs):
    result = _mutmut_trampoline(x_main__mutmut_orig, x_main__mutmut_mutants, args, kwargs)
    return result 

main.__signature__ = _mutmut_signature(x_main__mutmut_orig)
x_main__mutmut_orig.__name__ = 'x_main'


if __name__ == "__main__":
    main()
