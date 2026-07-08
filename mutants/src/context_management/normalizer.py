"""
Context Normalizer

Normalizes text for consistent processing:
- Lowercase conversion
- Whitespace compaction
- Punctuation standardization
- Unicode normalization
"""

import logging
import re
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)


class ContextNormalizer:
    """
    Normalize text for consistent fingerprinting and deduplication.

    Applies:
    - Unicode NFC normalization
    - Lowercase conversion (optional)
    - Whitespace compaction
    - Punctuation standardization
    """

    # Patterns for normalization
    MULTI_SPACE = re.compile(r"\s+")
    MULTI_NEWLINE = re.compile(r"\n{3,}")
    TRAILING_SPACE = re.compile(r"[ \t]+$", re.MULTILINE)
    LEADING_SPACE = re.compile(r"^[ \t]+", re.MULTILINE)

    def __init__(
        self,
        lowercase: bool = True,
        compact_whitespace: bool = True,
        normalize_unicode: bool = True,
        strip_ansi: bool = True,
        max_consecutive_newlines: int = 2,
    ):
        """
        Initialize normalizer with configuration.

        Args:
            lowercase: Convert to lowercase
            compact_whitespace: Collapse multiple spaces to single
            normalize_unicode: Apply NFC normalization
            strip_ansi: Remove ANSI escape sequences
            max_consecutive_newlines: Maximum allowed consecutive newlines
        """
        self.lowercase = lowercase
        self.compact_whitespace = compact_whitespace
        self.normalize_unicode = normalize_unicode
        self.strip_ansi = strip_ansi
        self.max_consecutive_newlines = max_consecutive_newlines

        # ANSI escape pattern
        self._ansi_pattern = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")

    def normalize(self, text: str) -> str:
        """
        Apply all configured normalizations to text.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text string
        """
        if not text:
            return ""

        result = text

        # Unicode normalization first
        if self.normalize_unicode:
            result = unicodedata.normalize("NFC", result)

        # Strip ANSI codes
        if self.strip_ansi:
            result = self._ansi_pattern.sub("", result)

        # Lowercase
        if self.lowercase:
            result = result.lower()

        # Whitespace compaction
        if self.compact_whitespace:
            result = self._compact_whitespace(result)

        return result.strip()

    def _compact_whitespace(self, text: str) -> str:
        """Compact whitespace while preserving structure."""
        # Remove trailing spaces from lines
        text = self.TRAILING_SPACE.sub("", text)

        # Compact multiple spaces to single
        text = self.MULTI_SPACE.sub(" ", text)

        # Limit consecutive newlines
        replacement = "\n" * self.max_consecutive_newlines
        return self.MULTI_NEWLINE.sub(replacement, text)

    def normalize_for_fingerprint(self, text: str) -> str:
        """
        Aggressive normalization for fingerprinting.

        Removes all formatting, converts to lowercase, strips punctuation
        except for semantic markers.
        """
        result = self.normalize(text)

        # Remove most punctuation but keep semantic markers
        result = re.sub(r"[^\w\s\.\?\!]", "", result)

        # Compact all whitespace to single space
        result = re.sub(r"\s+", " ", result)

        return result.strip()

    def extract_key_signals(self, text: str) -> dict:
        """
        Extract key signals from text that should be preserved.

        Returns dict with:
        - errors: Error messages found
        - file_paths: File paths found
        - test_names: Test names found
        - correlation_ids: Request/trace IDs found
        """
        signals: dict[str, list[Any]] = {
            "errors": [],
            "file_paths": [],
            "test_names": [],
            "correlation_ids": [],
        }

        # Error patterns
        error_patterns = [
            r"(?:error|exception|failed|failure):\s*(.+?)(?:\n|$)",
            r"(?:assert(?:ion)?error|typeerror|valueerror):\s*(.+?)(?:\n|$)",
        ]
        for pattern in error_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals["errors"].extend(matches)

        # File paths
        path_pattern = r"(?:[a-zA-Z]:\\|/)?(?:[\w.-]+[/\\])+[\w.-]+\.(?:py|js|ts|yaml|yml|json|md)"
        signals["file_paths"] = re.findall(path_pattern, text)

        # Test names
        test_pattern = r"test_[\w]+|Test[\w]+"
        signals["test_names"] = re.findall(test_pattern, text)

        # Correlation IDs
        id_patterns = [
            r"x-request-id[:\s]+([a-f0-9-]+)",
            r"ghRequestId[:\s]+([a-f0-9-]+)",
            r"correlation[_-]?id[:\s]+([a-f0-9-]+)",
            r"trace[_-]?id[:\s]+([a-f0-9-]+)",
        ]
        for pattern in id_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            signals["correlation_ids"].extend(matches)

        return signals
