from pathlib import Path

from codex_ml.analysis.providers import ExternalWebSearch, InternalRepoSearch


def test_internal_repo_search(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("import os\n")
    search = InternalRepoSearch(tmp_path)
    outcome = search.search("import os")
    assert outcome["status"] == "ok"
    assert outcome["query"] == "import os"
    assert any("sample.py" in r["where"] for r in outcome["results"])


def test_external_web_search_disabled(monkeypatch):
    monkeypatch.delenv("CODEX_ANALYSIS_SEARCH_ENABLED", raising=False)
    provider = ExternalWebSearch()
    outcome = provider.search("anything")
    assert outcome["status"] == "disabled"
    assert outcome["results"] == []
