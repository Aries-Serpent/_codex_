"""
Semantic Deduplicator

Removes semantically redundant statements from context using
fingerprint-based matching and configurable similarity thresholds.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from .fingerprint import Fingerprint, StatementFingerprinter
from .normalizer import ContextNormalizer


@dataclass
class DeduplicationResult:
    """Result of deduplication operation."""

    original_count: int
    deduplicated_count: int
    removed_count: int
    unique_statements: list[str]
    duplicates_found: list[tuple[str, str]]  # (duplicate, original)
    compression_ratio: float

    @property
    def reduction_percentage(self) -> float:
        """Percentage of statements removed."""
        if self.original_count == 0:
            return 0.0
        return (self.removed_count / self.original_count) * 100


@dataclass
class StatementEntry:
    """Entry in the deduplication index."""

    text: str
    fingerprint: Fingerprint
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: int = 0
    source: str = ""
    preserved_signals: dict = field(default_factory=dict)


class SemanticDeduplicator:
    """
    Remove semantically redundant statements from context.

    Uses fingerprint-based matching with configurable thresholds
    to identify and remove duplicates while preserving key signals.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        preserve_first: bool = True,
        max_entries: int = 10000,
    ):
        """
        Initialize deduplicator.

        Args:
            similarity_threshold: Minimum similarity to consider duplicate (0.0-1.0)
            preserve_first: Keep first occurrence (True) or last (False)
            max_entries: Maximum entries in index before cleanup
        """
        self.similarity_threshold = similarity_threshold
        self.preserve_first = preserve_first
        self.max_entries = max_entries

        self.fingerprinter = StatementFingerprinter()
        self.normalizer = ContextNormalizer()

        # Index of seen statements
        self._index: dict[str, StatementEntry] = {}  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def deduplicate(
        self, statements: list[str], preserve_signals: bool = True
    ) -> DeduplicationResult:
        """
        Deduplicate a list of statements.

        Args:
            statements: list of text statements
            preserve_signals: Extract and preserve key signals from removed duplicates

        Returns:
            DeduplicationResult with unique statements and metrics
        """
        unique = []
        duplicates = []

        for stmt in statements:
            if not stmt or not stmt.strip():
                continue

            # Generate fingerprint
            fp = self.fingerprinter.fingerprint(stmt)

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)  # type: ignore[arg-type]
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,  # type: ignore[arg-type]
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def is_duplicate(self, statement: str) -> tuple[bool, Optional[str]]:
        """
        Check if statement is a duplicate of existing entry.

        Args:
            statement: Text to check

        Returns:
            tuple of (is_duplicate, original_text_if_duplicate)
        """
        fp = self.fingerprinter.fingerprint(statement)
        return self._check_duplicate(fp)

    def add_statement(self, statement: str, priority: int = 0, source: str = "") -> bool:
        """
        Add statement to index if not duplicate.

        Args:
            statement: Text to add
            priority: Priority level for pruning decisions
            source: Source identifier

        Returns:
            True if added (not duplicate), False if duplicate
        """
        fp = self.fingerprinter.fingerprint(statement)
        is_dup, _ = self._check_duplicate(fp)

        if not is_dup:
            signals = self.normalizer.extract_key_signals(statement)
            entry = StatementEntry(
                text=statement,
                fingerprint=fp,
                priority=priority,
                source=source,
                preserved_signals=signals,
            )
            self._index[fp.exact_hash] = entry

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def clear(self):
        """Clear all indexed entries."""
        self._index.clear()
        self._semantic_index.clear()

    def _check_duplicate(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(fp, entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def _add_to_index(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def _merge_signals(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def _cleanup_oldest(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: x[1].timestamp)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]
