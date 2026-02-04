"""
Semantic Deduplicator

Removes semantically redundant statements from context using
fingerprint-based matching and configurable similarity thresholds.
"""

from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from .fingerprint import StatementFingerprinter, Fingerprint
from .normalizer import ContextNormalizer
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
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    source: str = ""
    preserved_signals: dict = field(default_factory=dict)


class SemanticDeduplicator:
    """
    Remove semantically redundant statements from context.

    Uses fingerprint-based matching with configurable thresholds
    to identify and remove duplicates while preserving key signals.
    """

    def xǁSemanticDeduplicatorǁ__init____mutmut_orig(
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

    def xǁSemanticDeduplicatorǁ__init____mutmut_1(
        self,
        similarity_threshold: float = 1.85,
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

    def xǁSemanticDeduplicatorǁ__init____mutmut_2(
        self,
        similarity_threshold: float = 0.85,
        preserve_first: bool = False,
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

    def xǁSemanticDeduplicatorǁ__init____mutmut_3(
        self,
        similarity_threshold: float = 0.85,
        preserve_first: bool = True,
        max_entries: int = 10001,
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

    def xǁSemanticDeduplicatorǁ__init____mutmut_4(
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
        self.similarity_threshold = None
        self.preserve_first = preserve_first
        self.max_entries = max_entries

        self.fingerprinter = StatementFingerprinter()
        self.normalizer = ContextNormalizer()

        # Index of seen statements
        self._index: dict[str, StatementEntry] = {}  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def xǁSemanticDeduplicatorǁ__init____mutmut_5(
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
        self.preserve_first = None
        self.max_entries = max_entries

        self.fingerprinter = StatementFingerprinter()
        self.normalizer = ContextNormalizer()

        # Index of seen statements
        self._index: dict[str, StatementEntry] = {}  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def xǁSemanticDeduplicatorǁ__init____mutmut_6(
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
        self.max_entries = None

        self.fingerprinter = StatementFingerprinter()
        self.normalizer = ContextNormalizer()

        # Index of seen statements
        self._index: dict[str, StatementEntry] = {}  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def xǁSemanticDeduplicatorǁ__init____mutmut_7(
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

        self.fingerprinter = None
        self.normalizer = ContextNormalizer()

        # Index of seen statements
        self._index: dict[str, StatementEntry] = {}  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def xǁSemanticDeduplicatorǁ__init____mutmut_8(
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
        self.normalizer = None

        # Index of seen statements
        self._index: dict[str, StatementEntry] = {}  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def xǁSemanticDeduplicatorǁ__init____mutmut_9(
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
        self._index: dict[str, StatementEntry] = None  # exact_hash -> entry
        self._semantic_index: dict[str, list[str]] = {}  # semantic_hash -> [exact_hashes]

    def xǁSemanticDeduplicatorǁ__init____mutmut_10(
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
        self._semantic_index: dict[str, list[str]] = None  # semantic_hash -> [exact_hashes]
    
    xǁSemanticDeduplicatorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁ__init____mutmut_1': xǁSemanticDeduplicatorǁ__init____mutmut_1, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_2': xǁSemanticDeduplicatorǁ__init____mutmut_2, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_3': xǁSemanticDeduplicatorǁ__init____mutmut_3, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_4': xǁSemanticDeduplicatorǁ__init____mutmut_4, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_5': xǁSemanticDeduplicatorǁ__init____mutmut_5, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_6': xǁSemanticDeduplicatorǁ__init____mutmut_6, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_7': xǁSemanticDeduplicatorǁ__init____mutmut_7, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_8': xǁSemanticDeduplicatorǁ__init____mutmut_8, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_9': xǁSemanticDeduplicatorǁ__init____mutmut_9, 
        'xǁSemanticDeduplicatorǁ__init____mutmut_10': xǁSemanticDeduplicatorǁ__init____mutmut_10
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁ__init____mutmut_orig)
    xǁSemanticDeduplicatorǁ__init____mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁ__init__'

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_orig(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_1(
        self, statements: list[str], preserve_signals: bool = False
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_2(
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
        unique = None
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_3(
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
        duplicates = None

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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_4(
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
            if not stmt and not stmt.strip():
                continue

            # Generate fingerprint
            fp = self.fingerprinter.fingerprint(stmt)

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_5(
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
            if stmt or not stmt.strip():
                continue

            # Generate fingerprint
            fp = self.fingerprinter.fingerprint(stmt)

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_6(
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
            if not stmt or stmt.strip():
                continue

            # Generate fingerprint
            fp = self.fingerprinter.fingerprint(stmt)

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_7(
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
                break

            # Generate fingerprint
            fp = self.fingerprinter.fingerprint(stmt)

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_8(
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
            fp = None

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_9(
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
            fp = self.fingerprinter.fingerprint(None)

            # Check for duplicates
            is_dup, original = self._check_duplicate(fp)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_10(
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
            is_dup, original = None

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_11(
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
            is_dup, original = self._check_duplicate(None)

            if is_dup:
                duplicates.append((stmt, original))
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_12(
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
                duplicates.append(None)
                if preserve_signals:
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_13(
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
                    self._merge_signals(None, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_14(
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
                    self._merge_signals(stmt, None)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_15(
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
                    self._merge_signals(original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_16(
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
                    self._merge_signals(stmt, )
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_17(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(None)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_18(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(None, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_19(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, None)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_20(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_21(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, )

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_22(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = None
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_23(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = None

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_24(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=None,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_25(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=None,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_26(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=None,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_27(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=None,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_28(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=None,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_29(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=None,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_30(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_31(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            removed_count=original_count - dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_32(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_33(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count - dedup_count,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_34(
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
                    self._merge_signals(stmt, original)
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
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_35(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_36(
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
                    self._merge_signals(stmt, original)
            else:
                unique.append(stmt)
                self._add_to_index(stmt, fp)

        original_count = len(statements)
        dedup_count = len(unique)

        return DeduplicationResult(
            original_count=original_count,
            deduplicated_count=dedup_count,
            removed_count=original_count + dedup_count,
            unique_statements=unique,
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_37(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count * original_count if original_count > 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_38(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count >= 0 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_39(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 1 else 1.0,
        )

    def xǁSemanticDeduplicatorǁdeduplicate__mutmut_40(
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
                    self._merge_signals(stmt, original)
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
            duplicates_found=duplicates,
            compression_ratio=dedup_count / original_count if original_count > 0 else 2.0,
        )
    
    xǁSemanticDeduplicatorǁdeduplicate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁdeduplicate__mutmut_1': xǁSemanticDeduplicatorǁdeduplicate__mutmut_1, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_2': xǁSemanticDeduplicatorǁdeduplicate__mutmut_2, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_3': xǁSemanticDeduplicatorǁdeduplicate__mutmut_3, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_4': xǁSemanticDeduplicatorǁdeduplicate__mutmut_4, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_5': xǁSemanticDeduplicatorǁdeduplicate__mutmut_5, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_6': xǁSemanticDeduplicatorǁdeduplicate__mutmut_6, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_7': xǁSemanticDeduplicatorǁdeduplicate__mutmut_7, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_8': xǁSemanticDeduplicatorǁdeduplicate__mutmut_8, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_9': xǁSemanticDeduplicatorǁdeduplicate__mutmut_9, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_10': xǁSemanticDeduplicatorǁdeduplicate__mutmut_10, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_11': xǁSemanticDeduplicatorǁdeduplicate__mutmut_11, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_12': xǁSemanticDeduplicatorǁdeduplicate__mutmut_12, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_13': xǁSemanticDeduplicatorǁdeduplicate__mutmut_13, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_14': xǁSemanticDeduplicatorǁdeduplicate__mutmut_14, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_15': xǁSemanticDeduplicatorǁdeduplicate__mutmut_15, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_16': xǁSemanticDeduplicatorǁdeduplicate__mutmut_16, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_17': xǁSemanticDeduplicatorǁdeduplicate__mutmut_17, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_18': xǁSemanticDeduplicatorǁdeduplicate__mutmut_18, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_19': xǁSemanticDeduplicatorǁdeduplicate__mutmut_19, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_20': xǁSemanticDeduplicatorǁdeduplicate__mutmut_20, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_21': xǁSemanticDeduplicatorǁdeduplicate__mutmut_21, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_22': xǁSemanticDeduplicatorǁdeduplicate__mutmut_22, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_23': xǁSemanticDeduplicatorǁdeduplicate__mutmut_23, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_24': xǁSemanticDeduplicatorǁdeduplicate__mutmut_24, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_25': xǁSemanticDeduplicatorǁdeduplicate__mutmut_25, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_26': xǁSemanticDeduplicatorǁdeduplicate__mutmut_26, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_27': xǁSemanticDeduplicatorǁdeduplicate__mutmut_27, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_28': xǁSemanticDeduplicatorǁdeduplicate__mutmut_28, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_29': xǁSemanticDeduplicatorǁdeduplicate__mutmut_29, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_30': xǁSemanticDeduplicatorǁdeduplicate__mutmut_30, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_31': xǁSemanticDeduplicatorǁdeduplicate__mutmut_31, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_32': xǁSemanticDeduplicatorǁdeduplicate__mutmut_32, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_33': xǁSemanticDeduplicatorǁdeduplicate__mutmut_33, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_34': xǁSemanticDeduplicatorǁdeduplicate__mutmut_34, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_35': xǁSemanticDeduplicatorǁdeduplicate__mutmut_35, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_36': xǁSemanticDeduplicatorǁdeduplicate__mutmut_36, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_37': xǁSemanticDeduplicatorǁdeduplicate__mutmut_37, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_38': xǁSemanticDeduplicatorǁdeduplicate__mutmut_38, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_39': xǁSemanticDeduplicatorǁdeduplicate__mutmut_39, 
        'xǁSemanticDeduplicatorǁdeduplicate__mutmut_40': xǁSemanticDeduplicatorǁdeduplicate__mutmut_40
    }
    
    def deduplicate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁdeduplicate__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁdeduplicate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    deduplicate.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁdeduplicate__mutmut_orig)
    xǁSemanticDeduplicatorǁdeduplicate__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁdeduplicate'

    def xǁSemanticDeduplicatorǁis_duplicate__mutmut_orig(self, statement: str) -> tuple[bool, Optional[str]]:
        """
        Check if statement is a duplicate of existing entry.

        Args:
            statement: Text to check

        Returns:
            tuple of (is_duplicate, original_text_if_duplicate)
        """
        fp = self.fingerprinter.fingerprint(statement)
        return self._check_duplicate(fp)

    def xǁSemanticDeduplicatorǁis_duplicate__mutmut_1(self, statement: str) -> tuple[bool, Optional[str]]:
        """
        Check if statement is a duplicate of existing entry.

        Args:
            statement: Text to check

        Returns:
            tuple of (is_duplicate, original_text_if_duplicate)
        """
        fp = None
        return self._check_duplicate(fp)

    def xǁSemanticDeduplicatorǁis_duplicate__mutmut_2(self, statement: str) -> tuple[bool, Optional[str]]:
        """
        Check if statement is a duplicate of existing entry.

        Args:
            statement: Text to check

        Returns:
            tuple of (is_duplicate, original_text_if_duplicate)
        """
        fp = self.fingerprinter.fingerprint(None)
        return self._check_duplicate(fp)

    def xǁSemanticDeduplicatorǁis_duplicate__mutmut_3(self, statement: str) -> tuple[bool, Optional[str]]:
        """
        Check if statement is a duplicate of existing entry.

        Args:
            statement: Text to check

        Returns:
            tuple of (is_duplicate, original_text_if_duplicate)
        """
        fp = self.fingerprinter.fingerprint(statement)
        return self._check_duplicate(None)
    
    xǁSemanticDeduplicatorǁis_duplicate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁis_duplicate__mutmut_1': xǁSemanticDeduplicatorǁis_duplicate__mutmut_1, 
        'xǁSemanticDeduplicatorǁis_duplicate__mutmut_2': xǁSemanticDeduplicatorǁis_duplicate__mutmut_2, 
        'xǁSemanticDeduplicatorǁis_duplicate__mutmut_3': xǁSemanticDeduplicatorǁis_duplicate__mutmut_3
    }
    
    def is_duplicate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁis_duplicate__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁis_duplicate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    is_duplicate.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁis_duplicate__mutmut_orig)
    xǁSemanticDeduplicatorǁis_duplicate__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁis_duplicate'

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_orig(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_1(self, statement: str, priority: int = 1, source: str = "") -> bool:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_2(self, statement: str, priority: int = 0, source: str = "XXXX") -> bool:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_3(self, statement: str, priority: int = 0, source: str = "") -> bool:
        """
        Add statement to index if not duplicate.

        Args:
            statement: Text to add
            priority: Priority level for pruning decisions
            source: Source identifier

        Returns:
            True if added (not duplicate), False if duplicate
        """
        fp = None
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_4(self, statement: str, priority: int = 0, source: str = "") -> bool:
        """
        Add statement to index if not duplicate.

        Args:
            statement: Text to add
            priority: Priority level for pruning decisions
            source: Source identifier

        Returns:
            True if added (not duplicate), False if duplicate
        """
        fp = self.fingerprinter.fingerprint(None)
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_5(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
        is_dup, _ = None

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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_6(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
        is_dup, _ = self._check_duplicate(None)

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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_7(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

        if is_dup:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_8(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
            signals = None
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_9(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
            signals = self.normalizer.extract_key_signals(None)
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_10(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
            entry = None
            self._index[fp.exact_hash] = entry

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_11(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                text=None,
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_12(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                fingerprint=None,
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_13(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                priority=None,
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_14(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                source=None,
                preserved_signals=signals,
            )
            self._index[fp.exact_hash] = entry

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_15(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                preserved_signals=None,
            )
            self._index[fp.exact_hash] = entry

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_16(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_17(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_18(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_19(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                preserved_signals=signals,
            )
            self._index[fp.exact_hash] = entry

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_20(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                )
            self._index[fp.exact_hash] = entry

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_21(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
            self._index[fp.exact_hash] = None

            # Add to semantic index
            if fp.semantic_hash not in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_22(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
            if fp.semantic_hash in self._semantic_index:
                self._semantic_index[fp.semantic_hash] = []
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_23(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
                self._semantic_index[fp.semantic_hash] = None
            self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_24(self, statement: str, priority: int = 0, source: str = "") -> bool:
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
            self._semantic_index[fp.semantic_hash].append(None)

            return True

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_25(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

            return False

        return False

    def xǁSemanticDeduplicatorǁadd_statement__mutmut_26(self, statement: str, priority: int = 0, source: str = "") -> bool:
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

        return True
    
    xǁSemanticDeduplicatorǁadd_statement__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁadd_statement__mutmut_1': xǁSemanticDeduplicatorǁadd_statement__mutmut_1, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_2': xǁSemanticDeduplicatorǁadd_statement__mutmut_2, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_3': xǁSemanticDeduplicatorǁadd_statement__mutmut_3, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_4': xǁSemanticDeduplicatorǁadd_statement__mutmut_4, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_5': xǁSemanticDeduplicatorǁadd_statement__mutmut_5, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_6': xǁSemanticDeduplicatorǁadd_statement__mutmut_6, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_7': xǁSemanticDeduplicatorǁadd_statement__mutmut_7, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_8': xǁSemanticDeduplicatorǁadd_statement__mutmut_8, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_9': xǁSemanticDeduplicatorǁadd_statement__mutmut_9, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_10': xǁSemanticDeduplicatorǁadd_statement__mutmut_10, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_11': xǁSemanticDeduplicatorǁadd_statement__mutmut_11, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_12': xǁSemanticDeduplicatorǁadd_statement__mutmut_12, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_13': xǁSemanticDeduplicatorǁadd_statement__mutmut_13, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_14': xǁSemanticDeduplicatorǁadd_statement__mutmut_14, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_15': xǁSemanticDeduplicatorǁadd_statement__mutmut_15, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_16': xǁSemanticDeduplicatorǁadd_statement__mutmut_16, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_17': xǁSemanticDeduplicatorǁadd_statement__mutmut_17, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_18': xǁSemanticDeduplicatorǁadd_statement__mutmut_18, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_19': xǁSemanticDeduplicatorǁadd_statement__mutmut_19, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_20': xǁSemanticDeduplicatorǁadd_statement__mutmut_20, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_21': xǁSemanticDeduplicatorǁadd_statement__mutmut_21, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_22': xǁSemanticDeduplicatorǁadd_statement__mutmut_22, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_23': xǁSemanticDeduplicatorǁadd_statement__mutmut_23, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_24': xǁSemanticDeduplicatorǁadd_statement__mutmut_24, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_25': xǁSemanticDeduplicatorǁadd_statement__mutmut_25, 
        'xǁSemanticDeduplicatorǁadd_statement__mutmut_26': xǁSemanticDeduplicatorǁadd_statement__mutmut_26
    }
    
    def add_statement(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁadd_statement__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁadd_statement__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_statement.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁadd_statement__mutmut_orig)
    xǁSemanticDeduplicatorǁadd_statement__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁadd_statement'

    def clear(self):
        """Clear all indexed entries."""
        self._index.clear()
        self._semantic_index.clear()

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_orig(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
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

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_1(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash not in self._index:
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

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_2(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return False, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(fp, entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_3(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash not in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(fp, entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_4(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash not in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(fp, entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_5(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = None
                    similarity = self.fingerprinter.similarity(fp, entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_6(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = None
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_7(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(None, entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_8(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(fp, None)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_9(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(entry.fingerprint)
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_10(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
        """Check if fingerprint matches any existing entry."""
        # Exact match
        if fp.exact_hash in self._index:
            return True, self._index[fp.exact_hash].text

        # Semantic match
        if fp.semantic_hash in self._semantic_index:
            for exact_hash in self._semantic_index[fp.semantic_hash]:
                if exact_hash in self._index:
                    entry = self._index[exact_hash]
                    similarity = self.fingerprinter.similarity(fp, )
                    if similarity >= self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_11(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
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
                    if similarity > self.similarity_threshold:
                        return True, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_12(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
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
                        return False, entry.text

        return False, None

    def xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_13(self, fp: Fingerprint) -> tuple[bool, Optional[str]]:
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

        return True, None
    
    xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_1': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_1, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_2': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_2, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_3': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_3, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_4': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_4, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_5': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_5, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_6': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_6, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_7': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_7, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_8': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_8, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_9': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_9, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_10': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_10, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_11': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_11, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_12': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_12, 
        'xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_13': xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_13
    }
    
    def _check_duplicate(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _check_duplicate.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_orig)
    xǁSemanticDeduplicatorǁ_check_duplicate__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁ_check_duplicate'

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_orig(self, text: str, fp: Fingerprint):
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

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_1(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = None
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_2(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(None)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_3(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = None

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_4(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=None, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_5(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=None, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_6(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=None)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_7(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_8(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_9(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, )

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_10(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = None

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_11(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_12(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = None
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_13(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(None)

        # Cleanup if over limit
        if len(self._index) > self.max_entries:
            self._cleanup_oldest()

    def xǁSemanticDeduplicatorǁ_add_to_index__mutmut_14(self, text: str, fp: Fingerprint):
        """Add entry to indices."""
        signals = self.normalizer.extract_key_signals(text)
        entry = StatementEntry(text=text, fingerprint=fp, preserved_signals=signals)

        self._index[fp.exact_hash] = entry

        if fp.semantic_hash not in self._semantic_index:
            self._semantic_index[fp.semantic_hash] = []
        self._semantic_index[fp.semantic_hash].append(fp.exact_hash)

        # Cleanup if over limit
        if len(self._index) >= self.max_entries:
            self._cleanup_oldest()
    
    xǁSemanticDeduplicatorǁ_add_to_index__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_1': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_1, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_2': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_2, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_3': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_3, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_4': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_4, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_5': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_5, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_6': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_6, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_7': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_7, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_8': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_8, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_9': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_9, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_10': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_10, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_11': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_11, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_12': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_12, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_13': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_13, 
        'xǁSemanticDeduplicatorǁ_add_to_index__mutmut_14': xǁSemanticDeduplicatorǁ_add_to_index__mutmut_14
    }
    
    def _add_to_index(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_add_to_index__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_add_to_index__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _add_to_index.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁ_add_to_index__mutmut_orig)
    xǁSemanticDeduplicatorǁ_add_to_index__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁ_add_to_index'

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_orig(self, duplicate: str, original: str):
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

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_1(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = None

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_2(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(None)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_3(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = None
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_4(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(None)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_5(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash not in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_6(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = None
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_7(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key not in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_8(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = None
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_9(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(None)
                    existing.update(values)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_10(self, duplicate: str, original: str):
        """Merge signals from duplicate into original entry."""
        dup_signals = self.normalizer.extract_key_signals(duplicate)

        # Find original entry
        fp = self.fingerprinter.fingerprint(original)
        if fp.exact_hash in self._index:
            entry = self._index[fp.exact_hash]
            for key, values in dup_signals.items():
                if key in entry.preserved_signals:
                    existing = set(entry.preserved_signals[key])
                    existing.update(None)
                    entry.preserved_signals[key] = list(existing)

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_11(self, duplicate: str, original: str):
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
                    entry.preserved_signals[key] = None

    def xǁSemanticDeduplicatorǁ_merge_signals__mutmut_12(self, duplicate: str, original: str):
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
                    entry.preserved_signals[key] = list(None)
    
    xǁSemanticDeduplicatorǁ_merge_signals__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_1': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_1, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_2': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_2, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_3': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_3, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_4': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_4, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_5': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_5, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_6': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_6, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_7': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_7, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_8': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_8, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_9': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_9, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_10': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_10, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_11': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_11, 
        'xǁSemanticDeduplicatorǁ_merge_signals__mutmut_12': xǁSemanticDeduplicatorǁ_merge_signals__mutmut_12
    }
    
    def _merge_signals(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_merge_signals__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_merge_signals__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _merge_signals.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁ_merge_signals__mutmut_orig)
    xǁSemanticDeduplicatorǁ_merge_signals__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁ_merge_signals'

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_orig(self):
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

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_1(self):
        """Remove oldest entries when over limit."""
        if len(self._index) < self.max_entries:
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

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_2(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = None

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_3(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(None, key=lambda x: x[1].timestamp)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_4(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=None)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_5(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(key=lambda x: x[1].timestamp)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_6(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), )

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_7(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: None)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_8(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: x[2].timestamp)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_9(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: x[1].timestamp)

        remove_count = None
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_10(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: x[1].timestamp)

        remove_count = len(entries) / 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_11(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: x[1].timestamp)

        remove_count = len(entries) // 11
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = entry.fingerprint.semantic_hash
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_12(self):
        """Remove oldest entries when over limit."""
        if len(self._index) <= self.max_entries:
            return

        # Sort by timestamp and remove oldest 10%
        entries = sorted(self._index.items(), key=lambda x: x[1].timestamp)

        remove_count = len(entries) // 10
        for exact_hash, entry in entries[:remove_count]:
            del self._index[exact_hash]
            # Clean semantic index
            sem_hash = None
            if sem_hash in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_13(self):
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
            if sem_hash not in self._semantic_index:
                self._semantic_index[sem_hash] = [
                    h for h in self._semantic_index[sem_hash] if h != exact_hash
                ]

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_14(self):
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
                self._semantic_index[sem_hash] = None

    def xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_15(self):
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
                    h for h in self._semantic_index[sem_hash] if h == exact_hash
                ]
    
    xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_1': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_1, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_2': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_2, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_3': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_3, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_4': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_4, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_5': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_5, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_6': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_6, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_7': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_7, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_8': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_8, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_9': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_9, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_10': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_10, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_11': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_11, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_12': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_12, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_13': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_13, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_14': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_14, 
        'xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_15': xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_15
    }
    
    def _cleanup_oldest(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _cleanup_oldest.__signature__ = _mutmut_signature(xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_orig)
    xǁSemanticDeduplicatorǁ_cleanup_oldest__mutmut_orig.__name__ = 'xǁSemanticDeduplicatorǁ_cleanup_oldest'
