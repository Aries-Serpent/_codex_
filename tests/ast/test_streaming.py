"""Tests for streaming parser."""

import pytest

from codex.ast.streaming import StreamingParser


class TestStreamingParser:
    """Test streaming parser functionality."""

    def test_parse_small_file(self, tmp_path):
        """Test parsing small file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        parser = StreamingParser()
        nodes = list(parser.parse_file(str(test_file)))

        assert len(nodes) > 0, "Nodes must not be empty"

    def test_parse_large_file(self, tmp_path):
        """Test parsing large file."""
        test_file = tmp_path / "large.py"

        # Generate large file
        code = "\n".join([f"def func_{i}():\n    pass" for i in range(1000)])
        test_file.write_text(code)

        parser = StreamingParser(chunk_size=1024)  # Small chunks
        nodes = list(parser.parse_file(str(test_file)))

        # Count FunctionDef nodes specifically, not just total nodes
        # (parser might also yield Module or other container nodes)
        # Note: StandardizedASTNode uses .type (NodeType enum), not .node_type
        from codex.ast.node import NodeType

        function_nodes = [n for n in nodes if n.type == NodeType.FUNCTION]
        assert len(function_nodes) >= 1000, "Function_nodes must not be empty"

    def test_parse_directory(self, tmp_path):
        """Test parsing directory of files."""
        # Create test files
        (tmp_path / "file1.py").write_text("def func1(): pass")
        (tmp_path / "file2.py").write_text("def func2(): pass")

        parser = StreamingParser()
        results = list(parser.parse_directory(str(tmp_path)))

        assert len(results) >= 2, "Results must not be empty"

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file raises error."""
        parser = StreamingParser()

        with pytest.raises(FileNotFoundError):
            list(parser.parse_file("nonexistent.py"))
