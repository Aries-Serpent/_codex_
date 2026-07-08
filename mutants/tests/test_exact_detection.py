"""Tests for exact duplicate detection."""

import tempfile
from pathlib import Path

import pytest


def test_exact_detector_finds_identical_files():
    """Test that identical files are detected as duplicates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two identical files
        file1 = root / "file1.py"
        file2 = root / "subdir" / "file2.py"
        file2.parent.mkdir()

        content = "logger.info('hello world')\n"
        file1.write_text(content)
        file2.write_text(content)

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find one duplicate group with 2 files
        assert len(groups) == 1, "Groups must not be empty"
        assert len(groups[0].member_files) == 2, "Collection must not be empty"
        assert groups[0].type == "exact-file", "type is not valid"
        assert groups[0].confidence == "high", "confidence is not valid"


def test_exact_detector_ignores_different_files():
    """Test that different files are not grouped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two different files
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        file1.write_text("logger.info('hello')\n")
        file2.write_text("logger.info('world')\n")

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find no duplicates
        assert len(groups) == 0, "Groups must not be empty"


def test_exact_detector_respects_exclusions():
    """Test that excluded patterns are respected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create files in excluded directory
        excluded_dir = root / "node_modules"
        excluded_dir.mkdir()
        file1 = excluded_dir / "file1.js"
        file2 = excluded_dir / "file2.js"

        content = "console.log('test');\n"
        file1.write_text(content)
        file2.write_text(content)

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find no duplicates (excluded)
        assert len(groups) == 0, "Groups must not be empty"


def test_exact_detector_language_detection():
    """Test that file language is correctly detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create identical Python files
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        content = "logger.info('test')\n"
        file1.write_text(content)
        file2.write_text(content)

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should detect as Python
        assert len(groups) == 1, "Groups must not be empty"
        assert groups[0].language == "python", "language is not valid"


def test_exact_detector_handles_empty_directory():
    """Test that empty directory is handled gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Run detector on empty directory
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find no duplicates
        assert len(groups) == 0, "Groups must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
