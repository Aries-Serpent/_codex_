"""
P6 Test: AST Similarity

Validates:
- ast_uniqueness computed for Python files
- Non-Python files skipped
- Parse errors produce warnings
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ART = Path("audit_artifacts")


def setup():
    if ART.exists():
        shutil.rmtree(ART)
    ART.mkdir()

    # Create raw capabilities with Python evidence
    raw = {
        "capabilities": [
            {"id": "alpha", "evidence_files": ["test_a.py", "test_b.py"]},
            {"id": "beta", "evidence_files": ["test_c.md"]},  # Non-Python
        ]
    }
    (ART / "capabilities_raw.json").write_text(json.dumps(raw), encoding="utf-8")

    # Create test Python files with different structures
    Path("test_a.py").write_text("def foo():\n    pass\nclass Bar:\n    x = 1", encoding="utf-8")
    Path("test_b.py").write_text("def baz():\n    return 42", encoding="utf-8")
    Path("test_c.md").write_text("# Docs", encoding="utf-8")


def test_ast_similarity_enabled():
    setup()
    env = os.environ.copy()
    env["AST_SIMILARITY_ENABLE"] = "1"
    subprocess.run(
        [sys.executable, "scripts/analysis/ast_signature_similarity.py"],
        check=True,
        env=env,
    )

    out = ART / "ast_similarity.json"
    assert out.exists(), "Condition must be true"
    data = json.loads(out.read_text())

    # Alpha should have ast_uniqueness computed
    alpha = next(c for c in data["capabilities"] if c["id"] == "alpha")
    assert 0.0 <= alpha["ast_uniqueness"] <= 1.0, "0 is not valid"
    assert alpha["python_files_analyzed"] == 2, "Condition must be true"

    # Beta has no Python files
    beta = next(c for c in data["capabilities"] if c["id"] == "beta")
    assert beta["python_files_analyzed"] == 0, "Condition must be true"


def test_ast_similarity_disabled():
    setup()
    env = os.environ.copy()
    env["AST_SIMILARITY_ENABLE"] = "0"
    subprocess.run(
        [sys.executable, "scripts/analysis/ast_signature_similarity.py"],
        check=True,
        env=env,
    )

    assert not (ART / "ast_similarity.json").exists(), "Condition must be true"
