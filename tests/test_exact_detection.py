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

        content = "print('hello world')\n"
        file1.write_text(content)
        file2.write_text(content)

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find one duplicate group with 2 files
        assert len(groups) == 1
        assert len(groups[0].member_files) == 2
        assert groups[0].type == "exact-file"
        assert groups[0].confidence == "high"


def test_exact_detector_ignores_different_files():
    """Test that different files are not grouped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create two different files
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        file1.write_text("print('hello')\n")
        file2.write_text("print('world')\n")

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find no duplicates
        assert len(groups) == 0


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
        assert len(groups) == 0


def test_exact_detector_language_detection():
    """Test that file language is correctly detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create identical Python files
        file1 = root / "file1.py"
        file2 = root / "file2.py"

        content = "print('test')\n"
        file1.write_text(content)
        file2.write_text(content)

        # Run detector
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should detect as Python
        assert len(groups) == 1
        assert groups[0].language == "python"


def test_exact_detector_handles_empty_directory():
    """Test that empty directory is handled gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Run detector on empty directory
        from tools.dupinv.exact_detector import ExactDetector

        detector = ExactDetector(root)
        groups = detector.scan()

        # Should find no duplicates
        assert len(groups) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
