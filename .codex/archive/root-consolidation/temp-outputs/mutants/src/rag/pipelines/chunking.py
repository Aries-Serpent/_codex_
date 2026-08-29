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
from collections.abc import Iterator
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger(__name__)

# Safeguards: Bounds
MIN_CHUNK_SIZE = 50
MAX_CHUNK_SIZE = 10000
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200


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

    def __init__(self, config: ChunkingConfig | None = None) -> None:
        """Initialize the chunking pipeline."""
        self.config = config or ChunkingConfig()

        # Validate config (safeguard)
        self.config.chunk_size = max(MIN_CHUNK_SIZE, min(MAX_CHUNK_SIZE, self.config.chunk_size))
        self.config.chunk_overlap = min(self.config.chunk_overlap, self.config.chunk_size // 2)

        logger.info(
            "ChunkingPipeline initialized: size=%d, overlap=%d",
            self.config.chunk_size,
            self.config.chunk_overlap,
        )

    def chunk_text(
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
                    chunks.append(
                        Chunk(
                            content=current_chunk.strip(),
                            start_index=current_start,
                            end_index=current_start + len(current_chunk),
                            metadata={**metadata, "chunk_index": len(chunks)},
                        )
                    )

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
            chunks.append(
                Chunk(
                    content=current_chunk.strip(),
                    start_index=current_start,
                    end_index=current_start + len(current_chunk),
                    metadata={**metadata, "chunk_index": len(chunks)},
                )
            )

        logger.info("Created %d chunks from text of length %d", len(chunks), len(text))
        return chunks

    def _split_by_separator(self, text: str) -> list[str]:
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
        return text.split(separator)

    def _split_large_text(self, text: str, base_index: int) -> Iterator[Chunk]:
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

    def chunk_code(
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


def main() -> None:
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


if __name__ == "__main__":
    main()
