"""
Test Link Audit

Test module for link audit.
"""

from __future__ import annotations

import json

from tools.docs import link_audit


def test_link_audit_reports_missing(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("[missing](missing.md)", encoding="utf-8")
    monkeypatch.setattr(link_audit, "DOCS_ROOT", docs)
    monkeypatch.setattr(link_audit, "OUTPUT_PATH", tmp_path / "report.json")
    link_audit.main()
    data = json.loads((tmp_path / "report.json").read_text())
    assert str(docs / "index.md") in data, "Data must not be empty"
    assert data[str(docs / "index.md")] == ["missing.md"], "Data must not be empty"
