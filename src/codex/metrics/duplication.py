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
]


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

    def __init__(
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

    def detect_with_pylint(
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
            return self._parse_pylint_output(result.stdout, result.stderr)

        except FileNotFoundError as e:
            type(e).__name__
            logger.debug("FileNotFoundError: <ERROR_TYPE>")
            logger.warning("FileNotFoundError: <ERROR_TYPE>", exc_info=True)
            logger.warning("pylint not found. Install with: pip install pylint")
            return []
        except subprocess.TimeoutExpired:
            logger.error(f"pylint timed out scanning {directory}")
            return []
        except (ValueError, TypeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.error("Error running pylint: <ERROR_TYPE>")
            return []

    def _parse_pylint_output(self, stdout: str, stderr: str) -> list[DuplicateBlock]:
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

    def _parse_pylint_stderr(self, stderr: str) -> list[DuplicateBlock]:
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
                            lines=(occurrences[0]["start"], occurrences[0]["end"]),  # type: ignore[arg-type]
                            occurrences=occurrences,
                            severity=self._determine_severity(len(occurrences)),
                            clone_type="Type-1",  # pylint finds exact matches
                        )
                        blocks.append(block)

            i += 1

        return blocks

    def _determine_severity(self, num_occurrences: int) -> str:
        """Determine severity based on number of occurrences"""
        if num_occurrences >= 5:
            return "high"
        if num_occurrences >= 3:
            return "medium"
        return "low"

    def _is_trivial(self, code: str) -> bool:
        """Check if code matches trivial patterns"""
        if not self.ignore_trivial:
            return False

        code = code.strip()
        return any(re.match(pattern, code) for pattern in TRIVIAL_PATTERNS)


def detect_duplicates(
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


def calculate_duplication_ratio(
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
