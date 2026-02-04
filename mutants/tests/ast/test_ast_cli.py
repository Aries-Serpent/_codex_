"""
Test Ast Cli

Test module for ast cli.
"""

from pathlib import Path

from codex.ast.cli import app
from typer.testing import CliRunner


def test_ast_cli_help():
    runner = CliRunner()
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "AST tools" in res.stdout


def test_analyze_json(tmp_path: Path):
    f = tmp_path / "x.py"
    f.write_text("print('hi')\n")
    runner = CliRunner()
    res = runner.invoke(app, ["analyze", str(tmp_path), "--json"])
    assert res.exit_code == 0
    assert '"files"' in res.stdout


def test_diff_invalid_arg(tmp_path: Path):
    a = tmp_path / "a.py"
    a.write_text("a=1\n")
    # b missing
    runner = CliRunner()
    res = runner.invoke(app, ["diff", str(a), str(tmp_path / "missing.py")])
    assert res.exit_code != 0
