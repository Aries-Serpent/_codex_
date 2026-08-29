import pytest

pytest.importorskip("parso")
"""
Test Providers

Test module for providers.
"""

from pathlib import Path

from codex_ml.analysis.providers import ExternalWebSearch, InternalRepoSearch


def test_internal_repo_search(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("import os\n")
    search = InternalRepoSearch(tmp_path)
    outcome = search.search("import os")
    assert outcome["status"] == "ok", "Condition must be true"
    assert outcome["query"] == "import os", "Condition must be true"
    assert any("sample.py" in r["where"] for r in outcome["results"]), "Result must not be empty"


def test_external_web_search_disabled(monkeypatch):
    monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENABLED", raising=False)

    called = False

    def fail_if_called(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("HTTP layer should not be invoked when disabled")

    provider = ExternalWebSearch(http_get=fail_if_called)
    outcome = provider.search("anything")
    assert outcome["status"] == "disabled", "Condition must be true"
    assert outcome["results"] == [], "Result must not be empty"
    assert not called, "Condition must be true"
