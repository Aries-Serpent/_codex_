"""
RAG Prompt Assembly Utilities (local-first, offline-capable)

Intent:
- Assemble a structured prompt with clear delimiters for system preamble,
  optional instructions, retrieved context snippets, and the user prompt.
- Respect a token/word budget for context (best-effort if tokenizer not supplied).
- Avoid external dependencies; optionally accept a tokenizer function.

Pattern alignment:
- Sectioned prompts improve steerability for small/medium LLMs.
- Deterministic ordering and trimming preserve reproducibility.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ----------------------------
# Configuration & Defaults
# ----------------------------
CTX_HEADER = "## Context"
INSTR_HEADER = "## Instructions"
PROMPT_HEADER = "## Prompt"

CTX_ITEM_PREFIX = "- "  # bullet prefix for each snippet
SECTION_DIVIDER = "\n---\n"

# Legacy safety delimiters (backward compatibility)
CONTEXT_START = "### RETRIEVED CONTEXT START ###"
CONTEXT_END = "### RETRIEVED CONTEXT END ###"
QUERY_START = "### USER QUERY START ###"
QUERY_END = "### USER QUERY END ###"


# ----------------------------
# Helpers
# ----------------------------
TokenizerFn = Callable[[str], list[int]]


def _count_tokens(text: str, tokenizer: Optional[TokenizerFn]) -> int:
    """
    Count tokens in text using provided tokenizer or simple heuristic.

    Args:
        text: Text to count tokens in
        tokenizer: Optional tokenizer function that returns list of token IDs

    Returns:
        Number of tokens (or words if no tokenizer provided)
    """
    if tokenizer is None:
        # Heuristic: whitespace tokenization
        return len(text.split())
    return len(tokenizer(text))


def _truncate_to_tokens(text: str, max_tokens: int, tokenizer: Optional[TokenizerFn]) -> str:
    """
    Truncate text to fit within token budget.

    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        tokenizer: Optional tokenizer function

    Returns:
        Truncated text
    """
    if max_tokens <= 0:
        return ""

    if tokenizer is None:
        # Simple heuristic truncation by words
        words = text.split()
        if len(words) <= max_tokens:
            return text
        return " ".join(words[:max_tokens]) + "..."

    # Tokenizer-based truncation
    tokens = tokenizer(text)
    if len(tokens) <= max_tokens:
        return text

    # Binary search to find the right truncation point
    # This is approximate since we can't easily detokenize
    # Fall back to word-based with token count validation
    words = text.split()
    low, high = 0, len(words)
    result = ""

    while low <= high:
        mid = (low + high) // 2
        candidate = " ".join(words[:mid])
        token_count = len(tokenizer(candidate))

        if token_count <= max_tokens:
            result = candidate
            low = mid + 1
        else:
            high = mid - 1

    return result + "..." if result != text else result


@dataclass
class PromptConfig:
    """
    Configuration for prompt assembly.

    Attributes:
        max_context_tokens: Maximum tokens for all context snippets combined
        max_snippet_tokens: Maximum tokens per individual snippet
        include_sources: Whether to include source references
        use_legacy_delimiters: Use legacy safety delimiters for backward compatibility
        context_header: Header for context section
        instructions_header: Header for instructions section
        prompt_header: Header for user prompt section
        item_prefix: Prefix for context items (e.g., "- " for bullets)
    """

    max_context_tokens: int = 2048
    max_snippet_tokens: int = 512
    include_sources: bool = True
    use_legacy_delimiters: bool = True
    context_header: str = CTX_HEADER
    instructions_header: str = INSTR_HEADER
    prompt_header: str = PROMPT_HEADER
    item_prefix: str = CTX_ITEM_PREFIX


class PromptTemplate:
    """Template for assembling RAG prompts with configurable sections and token budgets"""

    # Legacy class attributes for backward compatibility
    CONTEXT_START = CONTEXT_START
    CONTEXT_END = CONTEXT_END
    QUERY_START = QUERY_START
    QUERY_END = QUERY_END

    def __init__(
        self,
        config: Optional[PromptConfig] = None,
        tokenizer: Optional[TokenizerFn] = None,
    ):
        """
        Initialize prompt template.

        Args:
            config: Prompt configuration (uses defaults if None)
            tokenizer: Optional tokenizer function for accurate token counting
        """
        self.config = config or PromptConfig()
        self.tokenizer = tokenizer

    def _format_context_snippet(self, doc: dict[str, Any], index: int) -> str:
        """
        Format a single context snippet.

        Args:
            doc: Document with 'content' and optional 'metadata'
            index: 1-based index for numbering

        Returns:
            Formatted snippet string
        """
        content = doc.get("content", "")

        # Truncate content to max snippet tokens
        truncated = _truncate_to_tokens(content, self.config.max_snippet_tokens, self.tokenizer)

        parts = [f"{self.config.item_prefix}Document {index}:"]
        parts.append(f"  {truncated}")

        if self.config.include_sources and "metadata" in doc:
            source_id = doc["metadata"].get("source_id", "unknown")
            parts.append(f"  [Source: {source_id}]")

        return "\n".join(parts)

    def _build_context_section(self, retrieved_docs: Sequence[dict[str, Any]]) -> str:
        """
        Build the context section with token budget management.

        Args:
            retrieved_docs: List of retrieved documents

        Returns:
            Formatted context section
        """
        if not retrieved_docs:
            return ""

        parts = []
        if self.config.use_legacy_delimiters:
            parts.append(CONTEXT_START)
        else:
            parts.append(self.config.context_header)

        parts.append("")

        # Add snippets until token budget exhausted
        total_tokens = 0
        for i, doc in enumerate(retrieved_docs, 1):
            snippet = self._format_context_snippet(doc, i)
            snippet_tokens = _count_tokens(snippet, self.tokenizer)

            if total_tokens + snippet_tokens > self.config.max_context_tokens:
                # Skip if adding would exceed budget
                logger.debug(
                    f"Context budget reached: {total_tokens}/{self.config.max_context_tokens} tokens. "  # noqa: E501
                    f"Skipping remaining {len(retrieved_docs) - i + 1} documents."
                )
                break

            parts.append(snippet)
            parts.append("")
            total_tokens += snippet_tokens

        if self.config.use_legacy_delimiters:
            parts.append(CONTEXT_END)

        return "\n".join(parts)

    def assemble_rag_prompt(
        self,
        query: str,
        retrieved_docs: Sequence[dict[str, Any]],
        system_prompt: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> str:
        """
        Assemble a RAG prompt with safety delimiters and token budgets.

        Args:
            query: User query
            retrieved_docs: List of retrieved documents with 'content' and 'metadata'
            system_prompt: Optional system preamble
            instructions: Optional specific instructions

        Returns:
            Assembled prompt string
        """
        parts = []

        # Add system prompt if provided
        if system_prompt:
            parts.append(system_prompt)
            parts.append("")

        # Add retrieved context section
        context_section = self._build_context_section(retrieved_docs)
        if context_section:
            parts.append(context_section)
            parts.append("")

        # Add instructions if provided
        if instructions:
            if self.config.use_legacy_delimiters:
                parts.append(instructions)
            else:
                parts.append(self.config.instructions_header)
                parts.append(instructions)
            parts.append("")

        # Add user query
        if self.config.use_legacy_delimiters:
            parts.append(QUERY_START)
            parts.append(query)
            parts.append(QUERY_END)
        else:
            parts.append(self.config.prompt_header)
            parts.append(query)

        parts.append("")

        # Add default instruction if not provided
        if not instructions:
            parts.append(
                "Based on the retrieved context above, provide a helpful and accurate response "
                "to the user query. If the context doesn't contain relevant information, "
                "indicate that you don't have enough information to answer."
            )

        return "\n".join(parts)

    @staticmethod
    def assemble_simple_prompt(
        query: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Assemble a simple prompt without RAG context.

        Args:
            query: User query
            system_prompt: Optional system prompt

        Returns:
            Assembled prompt string
        """
        parts = []

        if system_prompt:
            parts.append(system_prompt)
            parts.append("")

        parts.append(query)

        return "\n".join(parts)


def build_prompt(
    query: str,
    retrieved_docs: Optional[list[dict[str, Any]]] = None,
    system_prompt: Optional[str] = None,
    use_rag: bool = True,
    config: Optional[PromptConfig] = None,
    tokenizer: Optional[TokenizerFn] = None,
) -> str:
    """
    Build a prompt for inference (convenience function).

    Args:
        query: User query
        retrieved_docs: Optional list of retrieved documents
        system_prompt: Optional system prompt
        use_rag: Whether to use RAG template
        config: Optional prompt configuration
        tokenizer: Optional tokenizer for token counting

    Returns:
        Assembled prompt string
    """
    if use_rag and retrieved_docs:
        template = PromptTemplate(config=config, tokenizer=tokenizer)
        prompt = template.assemble_rag_prompt(
            query=query,
            retrieved_docs=retrieved_docs,
            system_prompt=system_prompt,
        )
    else:
        prompt = PromptTemplate.assemble_simple_prompt(
            query=query,
            system_prompt=system_prompt,
        )

    logger.debug(f"Built prompt with length: {len(prompt)}")
    return prompt


__all__ = [
    "CTX_ITEM_PREFIX",
    "CONTEXT_END",
    "CONTEXT_START",
    "INSTR_HEADER",
    "PROMPT_HEADER",
    "QUERY_END",
    "QUERY_START",
    "SECTION_DIVIDER",
    "PromptConfig",
    "PromptTemplate",
    "build_prompt",
]
