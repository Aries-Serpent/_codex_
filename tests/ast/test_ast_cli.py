"""
Test Ast Cli

Test module for ast cli.
"""

import pytest

pytest.importorskip("typer")


from pathlib import Path

from typer.testing import CliRunner

from codex.ast.cli import app


def test_ast_cli_help():
    runner = CliRunner()
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0, "exit_code is not valid"
    assert "AST tools" in res.stdout, "Condition must be true"


def test_analyze_json(tmp_path: Path):
    f = tmp_path / "x.py"
    f.write_text("logger.info('hi')\n")
    runner = CliRunner()
    res = runner.invoke(app, ["analyze", str(tmp_path), "--json"])
    assert res.exit_code == 0, "exit_code is not valid"
    assert '"files"' in res.stdout, "Condition must be true"


def test_diff_invalid_arg(tmp_path: Path):
    a = tmp_path / "a.py"
    a.write_text("a=1\n")
    # b missing
    runner = CliRunner()
    res = runner.invoke(app, ["diff", str(a), str(tmp_path / "missing.py")])
    assert res.exit_code != 0, "exit_code is not valid"
