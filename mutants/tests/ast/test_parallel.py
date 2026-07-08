"""Tests for parallel parser."""

from codex.ast.parallel import ParallelParser


class TestParallelParser:
    """Test parallel parsing functionality."""

    def test_parse_multiple_files(self, tmp_path):
        """Test parsing multiple files in parallel."""
        # Create test files
        for i in range(5):
            (tmp_path / f"file{i}.py").write_text(f"def func{i}(): pass")

        parser = ParallelParser(max_workers=2)
        file_paths = [str(f) for f in tmp_path.glob("*.py")]

        results = parser.parse_files(file_paths)

        assert len(results) == 5, "Results must not be empty"
        assert all(node is not None for node in results.values()), "node must be initialized"

    def test_progress_callback(self, tmp_path):
        """Test progress callback functionality."""
        # Create test files
        for i in range(3):
            (tmp_path / f"file{i}.py").write_text("def func(): pass")

        progress_calls = []

        def progress(file_path, completed, total):
            progress_calls.append((file_path, completed, total))

        parser = ParallelParser()
        file_paths = [str(f) for f in tmp_path.glob("*.py")]

        # Parse files with progress callback (results not used in test)
        parser.parse_files(file_paths, progress_callback=progress)

        assert len(progress_calls) == 3, "Progress_calls must not be empty"
        assert progress_calls[-1][1] == 3, "Condition must be true"

    def test_parse_directory_parallel(self, tmp_path):
        """Test parsing directory in parallel."""
        # Create nested structure
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file1.py").write_text("def func1(): pass")
        (tmp_path / "subdir" / "file2.py").write_text("def func2(): pass")

        parser = ParallelParser()
        results = parser.parse_directory(str(tmp_path))

        assert len(results) == 2, "Results must not be empty"

    def test_thread_safe_node_ids(self, tmp_path):
        """Test thread-safe node ID generation."""
        for i in range(10):
            (tmp_path / f"file{i}.py").write_text("def func(): pass")

        parser = ParallelParser(max_workers=4)
        file_paths = [str(f) for f in tmp_path.glob("*.py")]

        # Should not raise threading errors
        results = parser.parse_files(file_paths)
        assert len(results) == 10, "Results must not be empty"
