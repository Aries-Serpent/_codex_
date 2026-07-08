"""
Tests for the AST CLI tool.

Tests cover all commands (parse, stats, query) across all supported languages
(Python, YAML, JSON, SQL) with various edge cases and error scenarios.
"""

import json

import pytest

from codex.cli.ast_cli import get_adapter, main


class TestGetAdapter:
    """Tests for the get_adapter function."""

    def test_python_adapter(self):
        """Test getting Python adapter."""
        adapter = get_adapter("python")
        assert adapter is not None, "adapter must be initialized"
        assert adapter.__class__.__name__ == "PythonASTAdapter", "__name__ is not valid"

    def test_yaml_adapter(self):
        """Test getting YAML adapter."""
        adapter = get_adapter("yaml")
        assert adapter is not None, "adapter must be initialized"
        assert adapter.__class__.__name__ == "YAMLASTAdapter", "__name__ is not valid"

    def test_json_adapter(self):
        """Test getting JSON adapter."""
        adapter = get_adapter("json")
        assert adapter is not None, "adapter must be initialized"
        assert adapter.__class__.__name__ == "JSONASTAdapter", "__name__ is not valid"

    def test_sql_adapter(self):
        """Test getting SQL adapter."""
        adapter = get_adapter("sql")
        assert adapter is not None, "adapter must be initialized"
        assert adapter.__class__.__name__ == "SQLASTAdapter", "__name__ is not valid"

    def test_unsupported_language(self):
        """Test error on unsupported language."""
        with pytest.raises(ValueError, match="Unsupported language"):
            get_adapter("unsupported")


class TestParseCommand:
    """Tests for the parse command."""

    def test_parse_python_file(self, tmp_path, capsys):
        """Test parsing a Python file."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Run parse command
        exit_code = main(["parse", str(test_file), "-l", "python"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # Python adapter creates "module" node type
        assert result["node_type"] == "module", "Result must not be empty"

    def test_parse_yaml_file(self, tmp_path, capsys):
        """Test parsing a YAML file."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("key: value\nnested:\n  inner: data\n")

        exit_code = main(["parse", str(test_file), "-l", "yaml"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # YAML adapter creates "document" node type
        assert result["node_type"] == "document", "Result must not be empty"

    def test_parse_json_file(self, tmp_path, capsys):
        """Test parsing a JSON file."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value", "number": 42}')

        exit_code = main(["parse", str(test_file), "-l", "json"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # JSON adapter creates "document" node type
        assert result["node_type"] == "document", "Result must not be empty"

    def test_parse_sql_file(self, tmp_path, capsys):
        """Test parsing a SQL file."""
        test_file = tmp_path / "test.sql"
        test_file.write_text("SELECT * FROM users WHERE active = 1;")

        exit_code = main(["parse", str(test_file), "-l", "sql"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # SQL adapter creates "sql_document" node type
        assert result["node_type"] == "sql_document", "Result must not be empty"

    def test_parse_nonexistent_file(self, capsys):
        """Test error when file doesn't exist."""
        exit_code = main(["parse", "/nonexistent/file.py", "-l", "python"])

        assert exit_code == 1, "exit_code is not valid"
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err, "Error should be raised or set"


class TestStatsCommand:
    """Tests for the stats command."""

    def test_stats_python_file(self, tmp_path, capsys):
        """Test getting statistics for a Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            "def hello():\n    pass\n\n" "class MyClass:\n    def method(self):\n        pass\n"
        )

        exit_code = main(["stats", str(test_file), "-l", "python"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # Check for expected node types from Python adapter
        assert "module" in result, "Result must not be empty"
        assert "function" in result, "Result must not be empty"
        assert "class" in result, "Result must not be empty"

    def test_stats_yaml_file(self, tmp_path, capsys):
        """Test getting statistics for a YAML file."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("key1: value1\nkey2: value2\nlist:\n  - item1\n  - item2\n")

        exit_code = main(["stats", str(test_file), "-l", "yaml"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # Check for expected node types from YAML adapter
        assert "document" in result, "Result must not be empty"

    def test_stats_json_file(self, tmp_path, capsys):
        """Test getting statistics for a JSON file."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"users": [{"name": "Alice"}, {"name": "Bob"}]}')

        exit_code = main(["stats", str(test_file), "-l", "json"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # Check for expected node types from JSON adapter
        assert "document" in result, "Result must not be empty"

    def test_stats_sql_file(self, tmp_path, capsys):
        """Test getting statistics for a SQL file."""
        test_file = tmp_path / "test.sql"
        test_file.write_text(
            "CREATE TABLE users (id INT, name VARCHAR(100));\n" "SELECT * FROM users;\n"
        )

        exit_code = main(["stats", str(test_file), "-l", "sql"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "sql_document" in result, "Result must not be empty"


class TestQueryCommand:
    """Tests for the query command."""

    def test_query_python_functions(self, tmp_path, capsys):
        """Test querying for Python functions."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n\n" "def world():\n    pass\n")

        exit_code = main(["query", str(test_file), "-l", "python", "-t", "function"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result) == 2, "Result must not be empty"
        assert result[0]["type"] == "function", "Result must not be empty"
        assert result[0]["name"] == "hello", "Result must not be empty"
        assert result[1]["name"] == "world", "Result must not be empty"

    def test_query_with_metadata(self, tmp_path, capsys):
        """Test querying with metadata included."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    '''A greeting function.'''\n    pass\n")

        exit_code = main(["query", str(test_file), "-l", "python", "-t", "function", "-m"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result) == 1, "Result must not be empty"
        assert "metadata" in result[0], "Result must not be empty"

    def test_query_yaml_mappings(self, tmp_path, capsys):
        """Test querying for YAML mappings."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("config:\n  database:\n    host: localhost\n")

        exit_code = main(["query", str(test_file), "-l", "yaml", "-t", "mapping"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result) >= 1, "Result must not be empty"

    def test_query_json_objects(self, tmp_path, capsys):
        """Test querying for JSON objects."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"user": {"name": "Alice", "age": 30}}')

        exit_code = main(["query", str(test_file), "-l", "json", "-t", "object"])

        assert exit_code == 0, "exit_code is not valid"
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert len(result) >= 1, "Result must not be empty"


class TestMainFunction:
    """Tests for the main function."""

    def test_no_command(self, capsys):
        """Test running with no command shows help."""
        exit_code = main([])

        assert exit_code == 1, "exit_code is not valid"
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "usage:" in captured.err.lower(), "Condition must be true"

    def test_help_flag(self, capsys):
        """Test --help flag."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        assert exc_info.value.code == 0, "Value must be initialized"
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower(), "Condition must be true"
        assert "parse" in captured.out.lower(), "Condition must be true"
        assert "stats" in captured.out.lower(), "Condition must be true"
        assert "query" in captured.out.lower(), "Condition must be true"

    def test_parse_help(self, capsys):
        """Test parse --help."""
        with pytest.raises(SystemExit) as exc_info:
            main(["parse", "--help"])

        assert exc_info.value.code == 0, "Value must be initialized"
        captured = capsys.readouterr()
        assert "parse" in captured.out.lower(), "Condition must be true"
        assert "language" in captured.out.lower(), "Condition must be true"

    def test_stats_help(self, capsys):
        """Test stats --help."""
        with pytest.raises(SystemExit) as exc_info:
            main(["stats", "--help"])

        assert exc_info.value.code == 0, "Value must be initialized"
        captured = capsys.readouterr()
        assert "stats" in captured.out.lower(), "Condition must be true"

    def test_query_help(self, capsys):
        """Test query --help."""
        with pytest.raises(SystemExit) as exc_info:
            main(["query", "--help"])

        assert exc_info.value.code == 0, "Value must be initialized"
        captured = capsys.readouterr()
        assert "query" in captured.out.lower(), "Condition must be true"
        assert "type" in captured.out.lower(), "Condition must be true"
