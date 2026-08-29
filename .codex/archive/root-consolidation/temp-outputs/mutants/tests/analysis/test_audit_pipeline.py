import pytest

pytest.importorskip("parso")
"""
Test Audit Pipeline

Test module for audit pipeline.
"""

from pathlib import Path

from codex_ml.analysis.parsers import parse_tiered
from codex_ml.cli.audit_pipeline import audit_file


def test_parse_tiered_ast_mode():
    code = """\nimport os\n\nclass A:\n    def f(self):\n        return os.getcwd()\n"""
    result = parse_tiered(code)
    assert result.mode == "ast", "Result must not be empty"
    assert result.ast_tree is not None, "ast_tree must be initialized"


def test_audit_file_roundtrip(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo(x):\n    return x * 2\n")
    report = audit_file(sample)
    assert report["mode"] == "ast", "rep is not valid"
    assert report["metrics"]["mccabe_minimal"] == 1, "rep is not valid"
    assert report["extraction"]["functions"][0]["name"] == "foo", "rep is not valid"
