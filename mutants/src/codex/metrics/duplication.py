"""
Duplication Detection and Ratio Calculation

Provides token-based and AST-based duplication detection for Python files
with configurable thresholds and comprehensive reporting.
"""

from __future__ import annotations

import hashlib
import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Configuration defaults
DEFAULT_MIN_LINES = 4  # Minimum lines to consider as duplicate
DEFAULT_MIN_TOKENS = 50  # Minimum tokens to consider as duplicate
TRIVIAL_PATTERNS = [
    r"^import\s+",
    r"^from\s+.*\s+import\s+",
    r"^class\s+\w+\(\):\s*pass\s*$",
    r"^def\s+\w+\(\):\s*pass\s*$",
]
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
class DuplicateBlock:
    """Represents a duplicate code block"""

    hash: str
    lines: tuple[int, int]  # (start_line, end_line)
    occurrences: list[dict[str, Any]]  # list of {file, start, end}
    severity: str = "medium"  # low, medium, high
    clone_type: str = "Type-1"  # Type-1, Type-2, Type-3, Type-4

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "hash": self.hash,
            "lines": list(self.lines),
            "occurrences": self.occurrences,
            "severity": self.severity,
            "clone_type": self.clone_type,
        }


@dataclass
class DuplicationRatio:
    """Represents duplication ratio and related metrics"""

    ratio: float
    total_lines: int
    duplicate_lines: int
    duplicate_blocks: list[DuplicateBlock] = field(default_factory=list)
    files_scanned: int = 0
    files_with_duplicates: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "ratio": self.ratio,
            "total_lines": self.total_lines,
            "duplicate_lines": self.duplicate_lines,
            "duplicate_blocks": [block.to_dict() for block in self.duplicate_blocks],
            "files_scanned": self.files_scanned,
            "files_with_duplicates": self.files_with_duplicates,
        }


class DuplicationDetector:
    """Duplication detection engine with multiple strategies"""

    def xǁDuplicationDetectorǁ__init____mutmut_orig(
        self,
        min_lines: int = DEFAULT_MIN_LINES,
        min_tokens: int = DEFAULT_MIN_TOKENS,
        ignore_trivial: bool = True,
    ):
        """
        Initialize duplication detector

        Args:
            min_lines: Minimum lines to consider as duplicate
            min_tokens: Minimum tokens to consider as duplicate
            ignore_trivial: Whether to ignore trivial code patterns
        """
        self.min_lines = min_lines
        self.min_tokens = min_tokens
        self.ignore_trivial = ignore_trivial

    def xǁDuplicationDetectorǁ__init____mutmut_1(
        self,
        min_lines: int = DEFAULT_MIN_LINES,
        min_tokens: int = DEFAULT_MIN_TOKENS,
        ignore_trivial: bool = False,
    ):
        """
        Initialize duplication detector

        Args:
            min_lines: Minimum lines to consider as duplicate
            min_tokens: Minimum tokens to consider as duplicate
            ignore_trivial: Whether to ignore trivial code patterns
        """
        self.min_lines = min_lines
        self.min_tokens = min_tokens
        self.ignore_trivial = ignore_trivial

    def xǁDuplicationDetectorǁ__init____mutmut_2(
        self,
        min_lines: int = DEFAULT_MIN_LINES,
        min_tokens: int = DEFAULT_MIN_TOKENS,
        ignore_trivial: bool = True,
    ):
        """
        Initialize duplication detector

        Args:
            min_lines: Minimum lines to consider as duplicate
            min_tokens: Minimum tokens to consider as duplicate
            ignore_trivial: Whether to ignore trivial code patterns
        """
        self.min_lines = None
        self.min_tokens = min_tokens
        self.ignore_trivial = ignore_trivial

    def xǁDuplicationDetectorǁ__init____mutmut_3(
        self,
        min_lines: int = DEFAULT_MIN_LINES,
        min_tokens: int = DEFAULT_MIN_TOKENS,
        ignore_trivial: bool = True,
    ):
        """
        Initialize duplication detector

        Args:
            min_lines: Minimum lines to consider as duplicate
            min_tokens: Minimum tokens to consider as duplicate
            ignore_trivial: Whether to ignore trivial code patterns
        """
        self.min_lines = min_lines
        self.min_tokens = None
        self.ignore_trivial = ignore_trivial

    def xǁDuplicationDetectorǁ__init____mutmut_4(
        self,
        min_lines: int = DEFAULT_MIN_LINES,
        min_tokens: int = DEFAULT_MIN_TOKENS,
        ignore_trivial: bool = True,
    ):
        """
        Initialize duplication detector

        Args:
            min_lines: Minimum lines to consider as duplicate
            min_tokens: Minimum tokens to consider as duplicate
            ignore_trivial: Whether to ignore trivial code patterns
        """
        self.min_lines = min_lines
        self.min_tokens = min_tokens
        self.ignore_trivial = None
    
    xǁDuplicationDetectorǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDuplicationDetectorǁ__init____mutmut_1': xǁDuplicationDetectorǁ__init____mutmut_1, 
        'xǁDuplicationDetectorǁ__init____mutmut_2': xǁDuplicationDetectorǁ__init____mutmut_2, 
        'xǁDuplicationDetectorǁ__init____mutmut_3': xǁDuplicationDetectorǁ__init____mutmut_3, 
        'xǁDuplicationDetectorǁ__init____mutmut_4': xǁDuplicationDetectorǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDuplicationDetectorǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDuplicationDetectorǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDuplicationDetectorǁ__init____mutmut_orig)
    xǁDuplicationDetectorǁ__init____mutmut_orig.__name__ = 'xǁDuplicationDetectorǁ__init__'

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_orig(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_1(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = None

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_2(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines and self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_3(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = None

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_4(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "XXpylintXX",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_5(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "PYLINT",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_6(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "XX--disable=allXX",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_7(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--DISABLE=ALL",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_8(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "XX--enable=duplicate-codeXX",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_9(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--ENABLE=DUPLICATE-CODE",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_10(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "XX--output-format=jsonXX",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_11(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--OUTPUT-FORMAT=JSON",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_12(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(None),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_13(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = None

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_14(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                None,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_15(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=None,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_16(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=None,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_17(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=None,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_18(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_19(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_20(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_21(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_22(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=False,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_23(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_24(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=301,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_25(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = None
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_26(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(None, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_27(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, None)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_28(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_29(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, )
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_30(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(None)
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_31(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(None, exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_32(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=None)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_33(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_34(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", )
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_35(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=False)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_36(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning(None)
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_37(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("XXpylint not found. Install with: pip install pylintXX")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_38(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_39(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("PYLINT NOT FOUND. INSTALL WITH: PIP INSTALL PYLINT")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_40(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(None)
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_41(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(None)
            logger.error(f"Error running pylint: {e}")
            return []

    def xǁDuplicationDetectorǁdetect_with_pylint__mutmut_42(
        self, directory: Path, min_similarity_lines: Optional[int] = None
    ) -> list[DuplicateBlock]:
        """
        Detect duplicates using pylint's duplicate-code checker

        Args:
            directory: Directory to scan for duplicates
            min_similarity_lines: Minimum lines for pylint (defaults to self.min_lines)

        Returns:
            list of duplicate blocks found
        """
        min_lines = min_similarity_lines or self.min_lines

        try:
            # Run pylint with duplicate-code checker
            cmd = [
                "pylint",
                "--disable=all",
                "--enable=duplicate-code",
                f"--min-similarity-lines={min_lines}",
                "--output-format=json",
                str(directory),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse pylint JSON output
            duplicates = self._parse_pylint_output(result.stdout, result.stderr)
            return duplicates

        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.error(None)
            return []
    
    xǁDuplicationDetectorǁdetect_with_pylint__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_1': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_1, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_2': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_2, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_3': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_3, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_4': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_4, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_5': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_5, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_6': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_6, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_7': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_7, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_8': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_8, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_9': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_9, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_10': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_10, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_11': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_11, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_12': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_12, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_13': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_13, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_14': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_14, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_15': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_15, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_16': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_16, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_17': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_17, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_18': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_18, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_19': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_19, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_20': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_20, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_21': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_21, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_22': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_22, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_23': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_23, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_24': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_24, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_25': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_25, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_26': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_26, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_27': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_27, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_28': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_28, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_29': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_29, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_30': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_30, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_31': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_31, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_32': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_32, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_33': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_33, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_34': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_34, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_35': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_35, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_36': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_36, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_37': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_37, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_38': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_38, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_39': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_39, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_40': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_40, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_41': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_41, 
        'xǁDuplicationDetectorǁdetect_with_pylint__mutmut_42': xǁDuplicationDetectorǁdetect_with_pylint__mutmut_42
    }
    
    def detect_with_pylint(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDuplicationDetectorǁdetect_with_pylint__mutmut_orig"), object.__getattribute__(self, "xǁDuplicationDetectorǁdetect_with_pylint__mutmut_mutants"), args, kwargs, self)
        return result 
    
    detect_with_pylint.__signature__ = _mutmut_signature(xǁDuplicationDetectorǁdetect_with_pylint__mutmut_orig)
    xǁDuplicationDetectorǁdetect_with_pylint__mutmut_orig.__name__ = 'xǁDuplicationDetectorǁdetect_with_pylint'

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_orig(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "Similar lines in" in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_1(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = None

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "Similar lines in" in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_2(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "XXSimilar lines inXX" in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_3(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "similar lines in" in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_4(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "SIMILAR LINES IN" in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_5(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "Similar lines in" not in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_6(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "Similar lines in" in stderr:
            blocks = None
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_7(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "Similar lines in" in stderr:
            blocks = self._parse_pylint_stderr(None)
            duplicates.extend(blocks)

        return duplicates

    def xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_8(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint JSON output to extract duplicates

        Args:
            stdout: pylint stdout
            stderr: pylint stderr

        Returns:
            list of duplicate blocks
        """
        duplicates = []

        # pylint duplicate-code messages appear in stderr, not JSON output
        # Parse stderr for duplicate code reports
        if "Similar lines in" in stderr:
            blocks = self._parse_pylint_stderr(stderr)
            duplicates.extend(None)

        return duplicates
    
    xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_1': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_1, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_2': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_2, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_3': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_3, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_4': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_4, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_5': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_5, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_6': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_6, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_7': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_7, 
        'xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_8': xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_8
    }
    
    def _parse_pylint_output(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_orig"), object.__getattribute__(self, "xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _parse_pylint_output.__signature__ = _mutmut_signature(xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_orig)
    xǁDuplicationDetectorǁ_parse_pylint_output__mutmut_orig.__name__ = 'xǁDuplicationDetectorǁ_parse_pylint_output'

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_orig(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_1(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = None
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_2(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = None

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_3(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split(None)

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_4(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("XX\nXX")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_5(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = None
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_6(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 1
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_7(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i <= len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_8(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = None

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_9(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "XXSimilar lines inXX" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_10(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_11(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "SIMILAR LINES IN" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_12(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" not in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_13(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = None
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_14(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(None, line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_15(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", None)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_16(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_17(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", )
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_18(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"XXSimilar lines in (\d+) filesXX", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_19(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_20(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"SIMILAR LINES IN (\d+) FILES", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_21(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(None)
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_22(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(None))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_23(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(2))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_24(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = None

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_25(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i = 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_26(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i -= 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_27(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 2
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_28(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) or lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_29(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i <= len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_30(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith(None):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_31(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("XX==XX"):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_32(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = None
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_33(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = None
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_34(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(None)
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_35(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[3:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_36(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split("XX:XX")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_37(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) > 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_38(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 3:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_39(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = None
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_40(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(None)
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_41(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = "XX:XX".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_42(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:+1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_43(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-2])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_44(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = None

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_45(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(None)

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_46(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[+1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_47(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-2])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_48(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = None

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_49(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines + 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_50(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line - self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_51(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 2

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_52(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                None
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_53(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "XXfileXX": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_54(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "FILE": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_55(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "XXstartXX": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_56(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "START": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_57(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "XXendXX": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_58(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "END": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_59(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i = 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_60(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i -= 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_61(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 2

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_62(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = None
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_63(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[1]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_64(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['XXfileXX']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_65(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['FILE']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_66(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[1]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_67(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['XXstartXX']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_68(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['START']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_69(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = None

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_70(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            None, usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_71(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=None
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_72(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_73(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_74(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=True
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_75(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = None
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_76(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=None,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_77(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=None,
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_78(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=None,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_79(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=None,
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_80(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type=None,  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_81(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_82(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_83(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_84(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_85(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_86(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[1]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_87(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["XXstartXX"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_88(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["START"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_89(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[1]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_90(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["XXendXX"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_91(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["END"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_92(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(None),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_93(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="XXType-1XX",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_94(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_95(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="TYPE-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_96(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(None)

            i += 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_97(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i = 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_98(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i -= 1

        return blocks

    def xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_99(self, stderr: str) -> list[DuplicateBlock]:
        """
        Parse pylint stderr for duplicate code messages

        Format:
        ************* Module <module>
        Similar lines in 2 files
        ==<file1>:<start>
        ==<file2>:<start>
        <code snippet>

        Args:
            stderr: pylint stderr output

        Returns:
            list of duplicate blocks
        """
        blocks = []
        lines = stderr.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for "Similar lines in N files"
            if "Similar lines in" in line:
                match = re.search(r"Similar lines in (\d+) files", line)
                if match:
                    int(match.group(1))
                    occurrences = []

                    # Parse file locations
                    i += 1
                    while i < len(lines) and lines[i].startswith("=="):
                        file_line = lines[i]
                        # Format: ==<file>:<start_line>
                        parts = file_line[2:].split(":")
                        if len(parts) >= 2:
                            filepath = ":".join(parts[:-1])
                            start_line = int(parts[-1])

                            # Estimate end line (will be refined later)
                            end_line = start_line + self.min_lines - 1

                            occurrences.append(
                                {
                                    "file": filepath,
                                    "start": start_line,
                                    "end": end_line,
                                }
                            )
                        i += 1

                    if occurrences:
                        # Create hash from first occurrence
                        hash_str = f"{occurrences[0]['file']}:{occurrences[0]['start']}"
                        # nosec B324 - MD5 used for deduplication hashing, not security
                        block_hash = hashlib.md5(
                            hash_str.encode(), usedforsecurity=False
                        ).hexdigest()

                        block = DuplicateBlock(
                            hash=block_hash,
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 2

        return blocks
    
    xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_1': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_1, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_2': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_2, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_3': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_3, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_4': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_4, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_5': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_5, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_6': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_6, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_7': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_7, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_8': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_8, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_9': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_9, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_10': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_10, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_11': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_11, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_12': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_12, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_13': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_13, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_14': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_14, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_15': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_15, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_16': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_16, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_17': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_17, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_18': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_18, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_19': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_19, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_20': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_20, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_21': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_21, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_22': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_22, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_23': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_23, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_24': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_24, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_25': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_25, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_26': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_26, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_27': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_27, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_28': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_28, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_29': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_29, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_30': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_30, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_31': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_31, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_32': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_32, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_33': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_33, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_34': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_34, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_35': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_35, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_36': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_36, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_37': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_37, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_38': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_38, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_39': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_39, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_40': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_40, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_41': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_41, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_42': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_42, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_43': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_43, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_44': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_44, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_45': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_45, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_46': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_46, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_47': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_47, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_48': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_48, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_49': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_49, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_50': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_50, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_51': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_51, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_52': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_52, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_53': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_53, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_54': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_54, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_55': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_55, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_56': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_56, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_57': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_57, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_58': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_58, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_59': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_59, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_60': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_60, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_61': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_61, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_62': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_62, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_63': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_63, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_64': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_64, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_65': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_65, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_66': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_66, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_67': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_67, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_68': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_68, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_69': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_69, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_70': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_70, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_71': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_71, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_72': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_72, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_73': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_73, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_74': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_74, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_75': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_75, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_76': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_76, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_77': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_77, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_78': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_78, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_79': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_79, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_80': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_80, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_81': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_81, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_82': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_82, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_83': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_83, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_84': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_84, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_85': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_85, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_86': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_86, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_87': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_87, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_88': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_88, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_89': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_89, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_90': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_90, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_91': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_91, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_92': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_92, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_93': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_93, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_94': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_94, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_95': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_95, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_96': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_96, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_97': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_97, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_98': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_98, 
        'xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_99': xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_99
    }
    
    def _parse_pylint_stderr(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_orig"), object.__getattribute__(self, "xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _parse_pylint_stderr.__signature__ = _mutmut_signature(xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_orig)
    xǁDuplicationDetectorǁ_parse_pylint_stderr__mutmut_orig.__name__ = 'xǁDuplicationDetectorǁ_parse_pylint_stderr'

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_orig(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_1(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences > 5:
            return "high"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_2(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 6:
            return "high"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_3(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "XXhighXX"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_4(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "HIGH"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_5(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences > 3:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_6(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences >= 4:
            return "medium"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_7(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences >= 3:
            return "XXmediumXX"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_8(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences >= 3:
            return "MEDIUM"
        else:
            return "low"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_9(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "XXlowXX"

    def xǁDuplicationDetectorǁ_determine_severity__mutmut_10(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        elif num_occurrences >= 3:
            return "medium"
        else:
            return "LOW"
    
    xǁDuplicationDetectorǁ_determine_severity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDuplicationDetectorǁ_determine_severity__mutmut_1': xǁDuplicationDetectorǁ_determine_severity__mutmut_1, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_2': xǁDuplicationDetectorǁ_determine_severity__mutmut_2, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_3': xǁDuplicationDetectorǁ_determine_severity__mutmut_3, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_4': xǁDuplicationDetectorǁ_determine_severity__mutmut_4, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_5': xǁDuplicationDetectorǁ_determine_severity__mutmut_5, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_6': xǁDuplicationDetectorǁ_determine_severity__mutmut_6, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_7': xǁDuplicationDetectorǁ_determine_severity__mutmut_7, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_8': xǁDuplicationDetectorǁ_determine_severity__mutmut_8, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_9': xǁDuplicationDetectorǁ_determine_severity__mutmut_9, 
        'xǁDuplicationDetectorǁ_determine_severity__mutmut_10': xǁDuplicationDetectorǁ_determine_severity__mutmut_10
    }
    
    def _determine_severity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDuplicationDetectorǁ_determine_severity__mutmut_orig"), object.__getattribute__(self, "xǁDuplicationDetectorǁ_determine_severity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _determine_severity.__signature__ = _mutmut_signature(xǁDuplicationDetectorǁ_determine_severity__mutmut_orig)
    xǁDuplicationDetectorǁ_determine_severity__mutmut_orig.__name__ = 'xǁDuplicationDetectorǁ_determine_severity'

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_orig(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, code):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_1(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, code):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_2(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return True

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, code):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_3(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = None
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, code):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_4(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(None, code):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_5(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, None):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_6(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(code):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_7(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, ):
                return True

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_8(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, code):
                return False

        return False

    def xǁDuplicationDetectorǁ_is_trivial__mutmut_9(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        for pattern in TRIVIAL_PATTERNS:
            if re.match(pattern, code):
                return True

        return True
    
    xǁDuplicationDetectorǁ_is_trivial__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDuplicationDetectorǁ_is_trivial__mutmut_1': xǁDuplicationDetectorǁ_is_trivial__mutmut_1, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_2': xǁDuplicationDetectorǁ_is_trivial__mutmut_2, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_3': xǁDuplicationDetectorǁ_is_trivial__mutmut_3, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_4': xǁDuplicationDetectorǁ_is_trivial__mutmut_4, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_5': xǁDuplicationDetectorǁ_is_trivial__mutmut_5, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_6': xǁDuplicationDetectorǁ_is_trivial__mutmut_6, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_7': xǁDuplicationDetectorǁ_is_trivial__mutmut_7, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_8': xǁDuplicationDetectorǁ_is_trivial__mutmut_8, 
        'xǁDuplicationDetectorǁ_is_trivial__mutmut_9': xǁDuplicationDetectorǁ_is_trivial__mutmut_9
    }
    
    def _is_trivial(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDuplicationDetectorǁ_is_trivial__mutmut_orig"), object.__getattribute__(self, "xǁDuplicationDetectorǁ_is_trivial__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _is_trivial.__signature__ = _mutmut_signature(xǁDuplicationDetectorǁ_is_trivial__mutmut_orig)
    xǁDuplicationDetectorǁ_is_trivial__mutmut_orig.__name__ = 'xǁDuplicationDetectorǁ_is_trivial'


def x_detect_duplicates__mutmut_orig(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        min_lines=min_lines,
        ignore_trivial=ignore_trivial,
    )

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_1(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = False,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        min_lines=min_lines,
        ignore_trivial=ignore_trivial,
    )

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_2(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = None

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_3(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        min_lines=None,
        ignore_trivial=ignore_trivial,
    )

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_4(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        min_lines=min_lines,
        ignore_trivial=None,
    )

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_5(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        ignore_trivial=ignore_trivial,
    )

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_6(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        min_lines=min_lines,
        )

    return detector.detect_with_pylint(directory)


def x_detect_duplicates__mutmut_7(
    directory: Path,
    min_lines: int = DEFAULT_MIN_LINES,
    ignore_trivial: bool = True,
) -> list[DuplicateBlock]:
    """
    Convenience function to detect duplicates in a directory

    Args:
        directory: Directory to scan
        min_lines: Minimum lines to consider as duplicate
        ignore_trivial: Whether to ignore trivial patterns

    Returns:
        list of duplicate blocks found
    """
    detector = DuplicationDetector(
        min_lines=min_lines,
        ignore_trivial=ignore_trivial,
    )

    return detector.detect_with_pylint(None)

x_detect_duplicates__mutmut_mutants : ClassVar[MutantDict] = {
'x_detect_duplicates__mutmut_1': x_detect_duplicates__mutmut_1, 
    'x_detect_duplicates__mutmut_2': x_detect_duplicates__mutmut_2, 
    'x_detect_duplicates__mutmut_3': x_detect_duplicates__mutmut_3, 
    'x_detect_duplicates__mutmut_4': x_detect_duplicates__mutmut_4, 
    'x_detect_duplicates__mutmut_5': x_detect_duplicates__mutmut_5, 
    'x_detect_duplicates__mutmut_6': x_detect_duplicates__mutmut_6, 
    'x_detect_duplicates__mutmut_7': x_detect_duplicates__mutmut_7
}

def detect_duplicates(*args, **kwargs):
    result = _mutmut_trampoline(x_detect_duplicates__mutmut_orig, x_detect_duplicates__mutmut_mutants, args, kwargs)
    return result 

detect_duplicates.__signature__ = _mutmut_signature(x_detect_duplicates__mutmut_orig)
x_detect_duplicates__mutmut_orig.__name__ = 'x_detect_duplicates'


def x_calculate_duplication_ratio__mutmut_orig(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_1(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = None

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_2(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = None
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_3(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["XXfileXX"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_4(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["FILE"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_5(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = None
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_6(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["XXstartXX"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_7(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["START"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_8(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = None

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_9(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["XXendXX"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_10(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["END"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_11(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(None, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_12(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, None):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_13(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_14(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, ):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_15(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end - 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_16(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 2):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_17(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add(None)

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_18(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = None
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_19(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = None

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_20(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines * total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_21(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines >= 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_22(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 1 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_23(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 1.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_24(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = None

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_25(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=None,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_26(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=None,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_27(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=None,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_28(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=None,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_29(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=None,
    )


def x_calculate_duplication_ratio__mutmut_30(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_31(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_32(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_blocks=duplicates,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_33(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        files_with_duplicates=files_with_duplicates,
    )


def x_calculate_duplication_ratio__mutmut_34(
    duplicates: list[DuplicateBlock],
    total_lines: int,
) -> DuplicationRatio:
    """
    Calculate duplication ratio from duplicate blocks

    Args:
        duplicates: list of duplicate blocks
        total_lines: Total lines in codebase

    Returns:
        DuplicationRatio object with calculated metrics
    """
    # Use set to handle overlapping duplicates
    duplicate_lines_set: set[tuple[str, int]] = set()

    for block in duplicates:
        for occurrence in block.occurrences:
            filepath = occurrence["file"]
            start = occurrence["start"]
            end = occurrence["end"]

            # Add each line to the set (file, line_number)
            for line_num in range(start, end + 1):
                duplicate_lines_set.add((filepath, line_num))

    duplicate_lines = len(duplicate_lines_set)
    ratio = duplicate_lines / total_lines if total_lines > 0 else 0.0

    # Count files with duplicates
    files_with_duplicates = len({occ["file"] for block in duplicates for occ in block.occurrences})

    return DuplicationRatio(
        ratio=ratio,
        total_lines=total_lines,
        duplicate_lines=duplicate_lines,
        duplicate_blocks=duplicates,
        )

x_calculate_duplication_ratio__mutmut_mutants : ClassVar[MutantDict] = {
'x_calculate_duplication_ratio__mutmut_1': x_calculate_duplication_ratio__mutmut_1, 
    'x_calculate_duplication_ratio__mutmut_2': x_calculate_duplication_ratio__mutmut_2, 
    'x_calculate_duplication_ratio__mutmut_3': x_calculate_duplication_ratio__mutmut_3, 
    'x_calculate_duplication_ratio__mutmut_4': x_calculate_duplication_ratio__mutmut_4, 
    'x_calculate_duplication_ratio__mutmut_5': x_calculate_duplication_ratio__mutmut_5, 
    'x_calculate_duplication_ratio__mutmut_6': x_calculate_duplication_ratio__mutmut_6, 
    'x_calculate_duplication_ratio__mutmut_7': x_calculate_duplication_ratio__mutmut_7, 
    'x_calculate_duplication_ratio__mutmut_8': x_calculate_duplication_ratio__mutmut_8, 
    'x_calculate_duplication_ratio__mutmut_9': x_calculate_duplication_ratio__mutmut_9, 
    'x_calculate_duplication_ratio__mutmut_10': x_calculate_duplication_ratio__mutmut_10, 
    'x_calculate_duplication_ratio__mutmut_11': x_calculate_duplication_ratio__mutmut_11, 
    'x_calculate_duplication_ratio__mutmut_12': x_calculate_duplication_ratio__mutmut_12, 
    'x_calculate_duplication_ratio__mutmut_13': x_calculate_duplication_ratio__mutmut_13, 
    'x_calculate_duplication_ratio__mutmut_14': x_calculate_duplication_ratio__mutmut_14, 
    'x_calculate_duplication_ratio__mutmut_15': x_calculate_duplication_ratio__mutmut_15, 
    'x_calculate_duplication_ratio__mutmut_16': x_calculate_duplication_ratio__mutmut_16, 
    'x_calculate_duplication_ratio__mutmut_17': x_calculate_duplication_ratio__mutmut_17, 
    'x_calculate_duplication_ratio__mutmut_18': x_calculate_duplication_ratio__mutmut_18, 
    'x_calculate_duplication_ratio__mutmut_19': x_calculate_duplication_ratio__mutmut_19, 
    'x_calculate_duplication_ratio__mutmut_20': x_calculate_duplication_ratio__mutmut_20, 
    'x_calculate_duplication_ratio__mutmut_21': x_calculate_duplication_ratio__mutmut_21, 
    'x_calculate_duplication_ratio__mutmut_22': x_calculate_duplication_ratio__mutmut_22, 
    'x_calculate_duplication_ratio__mutmut_23': x_calculate_duplication_ratio__mutmut_23, 
    'x_calculate_duplication_ratio__mutmut_24': x_calculate_duplication_ratio__mutmut_24, 
    'x_calculate_duplication_ratio__mutmut_25': x_calculate_duplication_ratio__mutmut_25, 
    'x_calculate_duplication_ratio__mutmut_26': x_calculate_duplication_ratio__mutmut_26, 
    'x_calculate_duplication_ratio__mutmut_27': x_calculate_duplication_ratio__mutmut_27, 
    'x_calculate_duplication_ratio__mutmut_28': x_calculate_duplication_ratio__mutmut_28, 
    'x_calculate_duplication_ratio__mutmut_29': x_calculate_duplication_ratio__mutmut_29, 
    'x_calculate_duplication_ratio__mutmut_30': x_calculate_duplication_ratio__mutmut_30, 
    'x_calculate_duplication_ratio__mutmut_31': x_calculate_duplication_ratio__mutmut_31, 
    'x_calculate_duplication_ratio__mutmut_32': x_calculate_duplication_ratio__mutmut_32, 
    'x_calculate_duplication_ratio__mutmut_33': x_calculate_duplication_ratio__mutmut_33, 
    'x_calculate_duplication_ratio__mutmut_34': x_calculate_duplication_ratio__mutmut_34
}

def calculate_duplication_ratio(*args, **kwargs):
    result = _mutmut_trampoline(x_calculate_duplication_ratio__mutmut_orig, x_calculate_duplication_ratio__mutmut_mutants, args, kwargs)
    return result 

calculate_duplication_ratio.__signature__ = _mutmut_signature(x_calculate_duplication_ratio__mutmut_orig)
x_calculate_duplication_ratio__mutmut_orig.__name__ = 'x_calculate_duplication_ratio'
