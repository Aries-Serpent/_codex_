"""
Statement Fingerprinter

Generates stable fingerprints for statements to enable deduplication.
Uses multiple hashing strategies for different similarity thresholds.
"""

import hashlib
import re
from dataclasses import dataclass


@dataclass
class Fingerprint:
    """Represents a statement fingerprint with multiple hash levels."""

    exact_hash: str  # SHA-256 of exact normalized text
    semantic_hash: str  # Hash of semantic tokens only
    structure_hash: str  # Hash of structural pattern
    ngram_hashes: list[str]  # Hashes of n-gram shingles
    token_count: int

    def matches(self, other: "Fingerprint", threshold: float = 0.8) -> bool:
        """Check if fingerprints match at given similarity threshold."""
        if threshold >= 1.0:
            return self.exact_hash == other.exact_hash
        if threshold >= 0.9:
            return self.semantic_hash == other.semantic_hash
        if threshold >= 0.7:
            return self.structure_hash == other.structure_hash
        # Jaccard similarity of n-grams
        return self._ngram_similarity(other) >= threshold

    def _ngram_similarity(self, other: "Fingerprint") -> float:
        """Calculate Jaccard similarity of n-gram hashes."""
        set_a = set(self.ngram_hashes)
        set_b = set(other.ngram_hashes)
        if not set_a and not set_b:
            return 1.0
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0


class StatementFingerprinter:
    """
    Generate fingerprints for text statements.

    Supports multiple fingerprinting strategies:
    - Exact: SHA-256 of normalized text
    - Semantic: Hash of meaningful tokens only
    - Structural: Hash of text structure pattern
    - N-gram: Shingle-based for fuzzy matching
    """

    # Stop words to filter for semantic hashing
    STOP_WORDS = frozenset(
        [
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "need",
            "dare",
            "ought",
            "used",
            "to",
            "of",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "from",
            "as",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "again",
            "further",
            "then",
            "once",
            "and",
            "but",
            "or",
            "nor",
            "so",
            "yet",
            "both",
            "either",
            "neither",
            "not",
            "only",
            "own",
            "same",
            "than",
            "too",
            "very",
            "just",
        ]
    )

    def __init__(self, ngram_size: int = 3, min_token_length: int = 2, use_stemming: bool = False):
        """
        Initialize fingerprinter.

        Args:
            ngram_size: Size of n-grams for shingle hashing
            min_token_length: Minimum token length to consider
            use_stemming: Whether to apply basic stemming
        """
        self.ngram_size = ngram_size
        self.min_token_length = min_token_length
        self.use_stemming = use_stemming

    def fingerprint(self, text: str) -> Fingerprint:
        """
        Generate fingerprint for text.

        Args:
            text: Input text to fingerprint

        Returns:
            Fingerprint object with multiple hash levels
        """
        # Normalize text
        normalized = self._normalize(text)
        tokens = self._tokenize(normalized)

        # Generate different hash types
        exact_hash = self._hash_exact(normalized)
        semantic_hash = self._hash_semantic(tokens)
        structure_hash = self._hash_structure(text)
        ngram_hashes = self._hash_ngrams(tokens)

        return Fingerprint(
            exact_hash=exact_hash,
            semantic_hash=semantic_hash,
            structure_hash=structure_hash,
            ngram_hashes=ngram_hashes,
            token_count=len(tokens),
        )

    def _normalize(self, text: str) -> str:
        """Basic normalization for fingerprinting."""
        text = text.lower().strip()
        return re.sub(r"\s+", " ", text)

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words."""
        tokens = re.findall(r"\b\w+\b", text)
        return [t for t in tokens if len(t) >= self.min_token_length]

    def _hash_exact(self, text: str) -> str:
        """Generate exact hash of normalized text."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def _hash_semantic(self, tokens: list[str]) -> str:
        """Generate hash of semantic tokens (stop words removed)."""
        semantic_tokens = [t for t in tokens if t not in self.STOP_WORDS]
        if self.use_stemming:
            semantic_tokens = [self._simple_stem(t) for t in semantic_tokens]
        content = " ".join(sorted(semantic_tokens))
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _hash_structure(self, text: str) -> str:
        """
        Generate hash of text structure pattern.

        Converts text to pattern like:
        - W = word
        - N = number
        - P = punctuation
        - S = space
        """
        pattern = []
        for char in text[:500]:  # Limit to first 500 chars
            if char.isalpha():
                pattern.append("W")
            elif char.isdigit():
                pattern.append("N")
            elif char.isspace():
                pattern.append("S")
            else:
                pattern.append("P")

        # Collapse runs
        collapsed = re.sub(r"(.)\1+", r"\1", "".join(pattern))
        return hashlib.sha256(collapsed.encode("utf-8")).hexdigest()[:16]

    def _hash_ngrams(self, tokens: list[str]) -> list[str]:
        """Generate hashes for n-gram shingles."""
        if len(tokens) < self.ngram_size:
            return [self._hash_exact(" ".join(tokens))]

        hashes = []
        for i in range(len(tokens) - self.ngram_size + 1):
            ngram = " ".join(tokens[i : i + self.ngram_size])
            h = hashlib.sha256(ngram.encode("utf-8")).hexdigest()[:8]
            hashes.append(h)

        return hashes

    def _simple_stem(self, word: str) -> str:
        """Apply simple suffix stripping."""
        suffixes = ["ing", "ed", "ly", "es", "s", "er", "est"]
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[: -len(suffix)]
        return word

    def similarity(self, fp1: Fingerprint, fp2: Fingerprint) -> float:
        """
        Calculate similarity between two fingerprints.

        Returns value between 0.0 (no match) and 1.0 (exact match).
        """
        if fp1.exact_hash == fp2.exact_hash:
            return 1.0
        if fp1.semantic_hash == fp2.semantic_hash:
            return 0.95
        if fp1.structure_hash == fp2.structure_hash:
            return 0.85
        return fp1._ngram_similarity(fp2)
