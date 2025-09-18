from __future__ import annotations

import json
from pathlib import Path

from analysis.tests_docs_links_audit import run_audit


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_audit_flags_missing_nav_and_links(tmp_path: Path) -> None:
    repo = tmp_path
    docs = repo / "docs"

    _write_file(
        repo / "pytest.ini",
        """[pytest]\naddopts = -q --cov=src/codex_ml\n""",
    )
    _write_file(
        repo / "mkdocs.yml",
        """
site_name: Example
nav:
  - Home: index.md
  - Guide: guide.md
""".strip(),
    )
    _write_file(
        docs / "index.md",
        """
# Home

See the [guide](guide.md) for details.

Tests reference: tests/unit/test_example.py
""".strip(),
    )
    # The guide document is intentionally missing to trigger detection.

    payload = run_audit(repo)

    assert payload["pytest_ini"] == "replace --cov=src/codex_ml with --cov=src/codex in pytest.ini"
    assert "docs/index.md" in payload["mkdocs_nav"]
    assert "docs/guide.md" in payload["mkdocs_nav"]

    broken = {(item["source"], item["target"]) for item in payload["broken_links"]}
    assert ("docs/index.md", "guide.md") in broken
    assert ("mkdocs.yml", "docs/guide.md") in broken

    assert payload["missing_tests"] == ["tests/unit/test_example.py"]


def test_audit_succeeds_when_everything_present(tmp_path: Path) -> None:
    repo = tmp_path
    docs = repo / "docs"

    _write_file(
        repo / "pytest.ini",
        """[pytest]\naddopts = -q --cov=src/codex\n""",
    )
    _write_file(
        repo / "mkdocs.yml",
        """
site_name: Example
nav:
  - Home: index.md
  - Guide: guide.md
""".strip(),
    )
    _write_file(
        docs / "index.md",
        """
# Home

See the [guide](guide.md) for details.

Tests reference: tests/unit/test_example.py
""".strip(),
    )
    _write_file(docs / "guide.md", "# Guide\n")
    _write_file(repo / "tests" / "unit" / "test_example.py", "def test_example():\n    pass\n")

    payload = run_audit(repo)

    assert payload["pytest_ini"] is None
    assert payload["broken_links"] == []
    assert payload["missing_tests"] == []

    # Ensure the output can be serialised (matches CLI behaviour).
    json.dumps(payload)
