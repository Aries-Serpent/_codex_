"""
Test Template Lint

Test module for template lint.
"""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE_LINT = _REPO_ROOT / "tools" / "template_lint.py"


def test_template_lint_detects_missing(tmp_path):
    bad = tmp_path / "bad.html"
    bad.write_text("<html><head></head><body>no links</body></html>", encoding="utf-8")
    code = subprocess.call([sys.executable, str(_TEMPLATE_LINT), "--dir", str(tmp_path)])
    assert code == 1, "code is not valid"


def test_template_lint_passes_with_links(tmp_path):
    good = tmp_path / "good.html"
    good.write_text(
        '<html><head><link href="theme.css"><link href="print.css"></head></html>',
        encoding="utf-8",
    )
    code = subprocess.call([sys.executable, str(_TEMPLATE_LINT), "--dir", str(tmp_path)])
    assert code == 0, "code is not valid"
