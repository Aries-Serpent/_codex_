"""
Tests for codex.metrics.duplication module.

This module contains tests for duplication detection and ratio calculation.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestDuplicateBlock:
    """Tests for DuplicateBlock dataclass."""

    def test_default_values(self):
        """Test DuplicateBlock default values."""
        from codex.metrics.duplication import DuplicateBlock
        
        block = DuplicateBlock(
            hash="abc123",
            lines=(1, 10),
            occurrences=[{"file": "test.py", "start": 1, "end": 10}]
        )
        
        assert block.hash == "abc123"
        assert block.lines == (1, 10)
        assert len(block.occurrences) == 1
        assert block.severity == "medium"
        assert block.clone_type == "Type-1"

    def test_custom_values(self):
        """Test DuplicateBlock with custom values."""
        from codex.metrics.duplication import DuplicateBlock
        
        block = DuplicateBlock(
            hash="xyz789",
            lines=(5, 20),
            occurrences=[
                {"file": "a.py", "start": 5, "end": 20},
                {"file": "b.py", "start": 10, "end": 25}
            ],
            severity="high",
            clone_type="Type-2"
        )
        
        assert block.severity == "high"
        assert block.clone_type == "Type-2"
        assert len(block.occurrences) == 2

    def test_to_dict(self):
        """Test DuplicateBlock serialization."""
        from codex.metrics.duplication import DuplicateBlock
        
        block = DuplicateBlock(
            hash="abc123",
            lines=(1, 10),
            occurrences=[{"file": "test.py", "start": 1, "end": 10}],
            severity="low",
            clone_type="Type-3"
        )
        
        result = block.to_dict()
        
        assert result["hash"] == "abc123"
        assert result["lines"] == [1, 10]  # Converted to list
        assert result["occurrences"] == [{"file": "test.py", "start": 1, "end": 10}]
        assert result["severity"] == "low"
        assert result["clone_type"] == "Type-3"


class TestDuplicationRatio:
    """Tests for DuplicationRatio dataclass."""

    def test_default_values(self):
        """Test DuplicationRatio default values."""
        from codex.metrics.duplication import DuplicationRatio
        
        ratio = DuplicationRatio(
            ratio=0.15,
            total_lines=1000,
            duplicate_lines=150
        )
        
        assert ratio.ratio == 0.15
        assert ratio.total_lines == 1000
        assert ratio.duplicate_lines == 150
        assert ratio.duplicate_blocks == []
        assert ratio.files_scanned == 0
        assert ratio.files_with_duplicates == 0

    def test_custom_values(self):
        """Test DuplicationRatio with custom values."""
        from codex.metrics.duplication import DuplicationRatio, DuplicateBlock
        
        blocks = [
            DuplicateBlock(hash="a", lines=(1, 5), occurrences=[]),
            DuplicateBlock(hash="b", lines=(10, 15), occurrences=[])
        ]
        
        ratio = DuplicationRatio(
            ratio=0.25,
            total_lines=500,
            duplicate_lines=125,
            duplicate_blocks=blocks,
            files_scanned=10,
            files_with_duplicates=3
        )
        
        assert ratio.files_scanned == 10
        assert ratio.files_with_duplicates == 3
        assert len(ratio.duplicate_blocks) == 2

    def test_to_dict(self):
        """Test DuplicationRatio serialization."""
        from codex.metrics.duplication import DuplicationRatio
        
        ratio = DuplicationRatio(
            ratio=0.1,
            total_lines=100,
            duplicate_lines=10,
            files_scanned=5,
            files_with_duplicates=2
        )
        
        result = ratio.to_dict()
        
        assert result["ratio"] == 0.1
        assert result["total_lines"] == 100
        assert result["duplicate_lines"] == 10
        assert result["duplicate_blocks"] == []
        assert result["files_scanned"] == 5
        assert result["files_with_duplicates"] == 2


class TestDuplicationDetector:
    """Tests for DuplicationDetector class."""

    def test_init_defaults(self):
        """Test DuplicationDetector initialization with defaults."""
        from codex.metrics.duplication import (
            DuplicationDetector, 
            DEFAULT_MIN_LINES, 
            DEFAULT_MIN_TOKENS
        )
        
        detector = DuplicationDetector()
        
        assert detector.min_lines == DEFAULT_MIN_LINES
        assert detector.min_tokens == DEFAULT_MIN_TOKENS
        assert detector.ignore_trivial is True

    def test_init_custom(self):
        """Test DuplicationDetector with custom parameters."""
        from codex.metrics.duplication import DuplicationDetector
        
        detector = DuplicationDetector(
            min_lines=10,
            min_tokens=100,
            ignore_trivial=False
        )
        
        assert detector.min_lines == 10
        assert detector.min_tokens == 100
        assert detector.ignore_trivial is False

    @patch('codex.metrics.duplication.subprocess.run')
    def test_detect_with_pylint_not_found(self, mock_run):
        """Test handling when pylint is not found."""
        from codex.metrics.duplication import DuplicationDetector
        
        mock_run.side_effect = FileNotFoundError("pylint not found")
        
        detector = DuplicationDetector()
        result = detector.detect_with_pylint(Path("/tmp"))
        
        assert result == []

    @patch('codex.metrics.duplication.subprocess.run')
    def test_detect_with_pylint_timeout(self, mock_run):
        """Test handling when pylint times out."""
        import subprocess
        from codex.metrics.duplication import DuplicationDetector
        
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pylint", timeout=300)
        
        detector = DuplicationDetector()
        result = detector.detect_with_pylint(Path("/tmp"))
        
        assert result == []

    @patch('codex.metrics.duplication.subprocess.run')
    def test_detect_with_pylint_error(self, mock_run):
        """Test handling when pylint has an error."""
        from codex.metrics.duplication import DuplicationDetector
        
        mock_run.side_effect = Exception("Some error")
        
        detector = DuplicationDetector()
        result = detector.detect_with_pylint(Path("/tmp"))
        
        assert result == []


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_default_min_lines(self):
        """Test DEFAULT_MIN_LINES constant."""
        from codex.metrics.duplication import DEFAULT_MIN_LINES
        
        assert DEFAULT_MIN_LINES == 4

    def test_default_min_tokens(self):
        """Test DEFAULT_MIN_TOKENS constant."""
        from codex.metrics.duplication import DEFAULT_MIN_TOKENS
        
        assert DEFAULT_MIN_TOKENS == 50

    def test_trivial_patterns(self):
        """Test TRIVIAL_PATTERNS constant."""
        from codex.metrics.duplication import TRIVIAL_PATTERNS
        
        assert isinstance(TRIVIAL_PATTERNS, list)
        assert len(TRIVIAL_PATTERNS) > 0
        # Check first pattern
        assert r"^import\s+" in TRIVIAL_PATTERNS

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.metrics.duplication import logger
        
        assert logger is not None
        assert logger.name == "codex.metrics.duplication"
