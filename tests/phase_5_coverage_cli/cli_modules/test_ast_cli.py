"""Tests for the ``codex.cli.ast_cli`` module.

``codex.cli.ast_cli`` is a compatibility re-export of
``aries_serpent_core.cli.ast_cli``: ``get_adapter`` plus the ``parse`` /
``stats`` / ``query`` sub-command handlers, which log JSON via ``logger.info``
and return an exit code (0 success, 1 failure, never raising for missing files).
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pytest

from codex.cli import ast_cli

_LOGGER = "aries_serpent_core.cli.ast_cli"


def _logged_json(caplog: pytest.LogCaptureFixture) -> object:
    records = [r for r in caplog.records if r.name == _LOGGER and r.levelno == logging.INFO]
    assert records, "command must log its JSON result"
    return json.loads(records[-1].getMessage())


def _query_args(path: Path, node_type: str, *, metadata: bool = False) -> argparse.Namespace:
    return argparse.Namespace(file=str(path), language="python", type=node_type, metadata=metadata)


class TestGetAdapter:
    """Test get_adapter function."""

    def test_get_adapter_python(self) -> None:
        adapter = ast_cli.get_adapter("python")
        assert type(adapter).__name__ == "PythonASTAdapter"

    def test_get_adapter_yaml(self) -> None:
        adapter = ast_cli.get_adapter("yaml")
        assert type(adapter).__name__ == "YAMLASTAdapter"

    def test_get_adapter_json(self) -> None:
        adapter = ast_cli.get_adapter("json")
        assert type(adapter).__name__ == "JSONASTAdapter"

    def test_get_adapter_sql(self) -> None:
        pytest.importorskip("sqlparse")  # optional extra ("core"); adapter guards it
        adapter = ast_cli.get_adapter("sql")
        assert type(adapter).__name__ == "SQLASTAdapter"

    def test_get_adapter_invalid_language(self) -> None:
        with pytest.raises(ValueError):
            ast_cli.get_adapter("invalid_language")

    def test_get_adapter_case_sensitive(self) -> None:
        with pytest.raises(ValueError):
            ast_cli.get_adapter("Python")

    def test_get_adapter_returns_instance(self) -> None:
        adapter = ast_cli.get_adapter("python")
        assert callable(adapter.parse)
        assert callable(adapter.parse_file)
        assert ast_cli.get_adapter("python") is not adapter, "a fresh adapter per call"


class TestParseCommand:
    """Test parse_command function."""

    def test_parse_command_exists(self) -> None:
        assert hasattr(ast_cli, "parse_command")

    def test_parse_command_is_callable(self) -> None:
        assert callable(ast_cli.parse_command)

    def test_parse_command_python_file(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello():\n    return 'world'\n")
        caplog.set_level(logging.INFO, logger=_LOGGER)

        assert ast_cli.parse_command(argparse.Namespace(file=str(py_file), language="python")) == 0
        tree = _logged_json(caplog)
        assert tree["node_type"] == "module"
        assert tree["file_path"] == str(py_file)
        assert tree["children_count"] == 1

    def test_parse_command_with_query(self, tmp_path: Path) -> None:
        """Extra namespace attributes are ignored by the parse handler."""
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")
        args = argparse.Namespace(file=str(py_file), language="python", query="FunctionDef")
        assert ast_cli.parse_command(args) == 0

    def test_parse_command_invalid_file(self, caplog: pytest.LogCaptureFixture) -> None:
        args = argparse.Namespace(file="/nonexistent/file.py", language="python")
        assert ast_cli.parse_command(args) == 1
        assert "File not found" in caplog.text

    def test_parse_command_empty_file(self, tmp_path: Path) -> None:
        py_file = tmp_path / "empty.py"
        py_file.write_text("")
        assert ast_cli.parse_command(argparse.Namespace(file=str(py_file), language="python")) == 0


class TestQueryCommand:
    """Test query_command function (``-t/--type`` and ``-m/--metadata``)."""

    def test_query_command_exists(self) -> None:
        assert hasattr(ast_cli, "query_command")

    def test_query_command_is_callable(self) -> None:
        assert callable(ast_cli.query_command)

    def test_query_command_function_defs(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("def func1():\n    pass\ndef func2():\n    pass\n")
        caplog.set_level(logging.INFO, logger=_LOGGER)

        assert ast_cli.query_command(_query_args(py_file, "function")) == 0
        result = _logged_json(caplog)
        assert [n["name"] for n in result] == ["func1", "func2"]
        assert all(n["type"] == "function" and "metadata" not in n for n in result)

    def test_query_command_class_defs(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("class MyClass:\n    pass\n")
        caplog.set_level(logging.INFO, logger=_LOGGER)

        assert ast_cli.query_command(_query_args(py_file, "class", metadata=True)) == 0
        result = _logged_json(caplog)
        assert [n["name"] for n in result] == ["MyClass"]
        assert {"line_start", "line_end", "column_start", "column_end"} <= result[0].keys()
        assert isinstance(result[0]["metadata"], dict)

    def test_query_command_invalid_node_type(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")
        caplog.set_level(logging.INFO, logger=_LOGGER)

        assert ast_cli.query_command(_query_args(py_file, "InvalidNodeType")) == 0
        assert _logged_json(caplog) == []


class TestStatisticsCommand:
    """Test statistics command."""

    def test_stats_command_exists(self) -> None:
        assert callable(ast_cli.stats_command)

    def test_stats_python_file(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text(
            "def func1():\n    pass\n" "def func2():\n    pass\n" "class MyClass:\n    pass\n"
        )
        caplog.set_level(logging.INFO, logger=_LOGGER)

        assert ast_cli.stats_command(argparse.Namespace(file=str(py_file), language="python")) == 0
        stats = _logged_json(caplog)
        assert stats["function"] == 2
        assert stats["class"] == 1


class TestLanguageSupport:
    """Test language support."""

    def test_supported_languages(self) -> None:
        langs = ["python", "yaml", "json"]
        try:
            import sqlparse  # noqa: F401
        except ImportError:  # optional extra; covered by test_get_adapter_sql
            pass
        else:
            langs.append("sql")
        for lang in langs:
            assert ast_cli.get_adapter(lang) is not None, lang

    def test_language_detection(self) -> None:
        with pytest.raises(ValueError, match="python, yaml, json, sql"):
            ast_cli.get_adapter("cobol")

    def test_python_parsing(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1\ny = 2\n")
        adapter = ast_cli.get_adapter("python")

        root = adapter.parse_file(str(py_file))
        assert root.node_type == "module"
        assert adapter.get_stats().get("assignment") == 2
        assert adapter.parse(py_file.read_text()).node_type == "module"


class TestArgumentParsing:
    """Test argument parsing via ``main``."""

    def test_main_has_argparse(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert ast_cli.main([]) == 1  # no sub-command -> help + failure
        assert "parse" in capsys.readouterr().out

    def test_parse_args_basic(self, tmp_path: Path) -> None:
        py_file = tmp_path / "test.py"
        py_file.write_text("def f():\n    pass\n")
        assert ast_cli.main(["parse", str(py_file), "-l", "python"]) == 0
        assert ast_cli.main(["query", str(py_file), "-l", "python", "-t", "function", "-m"]) == 0
        with pytest.raises(SystemExit):
            ast_cli.main(["query", str(py_file), "-l", "python"])  # --type is required


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_python_file(self, tmp_path: Path) -> None:
        py_file = tmp_path / "empty.py"
        py_file.write_text("")
        adapter = ast_cli.get_adapter("python")
        root = adapter.parse_file(str(py_file))
        assert root.node_type == "module"
        assert root.children == []

    def test_unicode_content(self, tmp_path: Path) -> None:
        py_file = tmp_path / "unicode.py"
        py_file.write_text(
            "# -*- coding: utf-8 -*-\n# 你好世界\ndef grüß():\n    return '你好'\n",
            encoding="utf-8",
        )
        adapter = ast_cli.get_adapter("python")
        adapter.parse_file(str(py_file))
        assert [n.name for n in adapter.find_nodes_by_type("function")] == ["grüß"]

    def test_large_file(self, tmp_path: Path) -> None:
        py_file = tmp_path / "large.py"
        py_file.write_text("\n".join(f"def func{i}():\n    pass" for i in range(100)))
        adapter = ast_cli.get_adapter("python")
        adapter.parse_file(str(py_file))
        assert len(adapter.find_nodes_by_type("function")) == 100

    def test_complex_syntax(self, tmp_path: Path) -> None:
        py_file = tmp_path / "complex.py"
        py_file.write_text(
            "def func(a, b=1, *args, **kwargs):\n"
            "    @decorator\n"
            "    def inner():\n"
            "        return [x for x in range(10) if x % 2]\n"
            "    return inner()\n"
        )
        adapter = ast_cli.get_adapter("python")
        adapter.parse_file(str(py_file))
        assert sorted(n.name for n in adapter.find_nodes_by_type("function")) == ["func", "inner"]


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_language_error_message(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            ast_cli.get_adapter("invalid")
        assert "Unsupported language: invalid" in str(exc_info.value)

    def test_file_not_found_handling(self, caplog: pytest.LogCaptureFixture) -> None:
        """Handlers report a missing file via exit code 1 rather than raising."""
        for handler in (ast_cli.parse_command, ast_cli.stats_command):
            caplog.clear()
            args = argparse.Namespace(file="/does/not/exist.py", language="python")
            assert handler(args) == 1
            assert "File not found" in caplog.text
        assert ast_cli.query_command(_query_args(Path("/does/not/exist.py"), "function")) == 1

    def test_malformed_python_syntax(self, tmp_path: Path) -> None:
        py_file = tmp_path / "malformed.py"
        py_file.write_text("def func(\n  invalid syntax")
        adapter = ast_cli.get_adapter("python")
        with pytest.raises(SyntaxError):
            adapter.parse_file(str(py_file))


class TestModuleStructure:
    """Test module structure."""

    def test_has_get_adapter(self) -> None:
        assert hasattr(ast_cli, "get_adapter")

    def test_has_parse_command(self) -> None:
        assert hasattr(ast_cli, "parse_command")

    def test_functions_callable(self) -> None:
        assert callable(ast_cli.get_adapter)
        assert callable(ast_cli.parse_command)

    def test_adapter_imports(self) -> None:
        from aries_serpent_core.ast_adapters import PythonASTAdapter

        assert isinstance(ast_cli.get_adapter("python"), PythonASTAdapter)
