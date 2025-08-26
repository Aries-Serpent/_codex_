from pathlib import Path

from codex_ml.analysis.providers import InternalRepoSearch, ExternalWebSearch


def test_internal_repo_search(tmp_path: Path):
    sample = tmp_path / "sample.py"
    sample.write_text("import os\n")
    search = InternalRepoSearch(tmp_path)
    results = search.search("import os")
    assert any("sample.py" in r["where"] for r in results)


def test_external_web_search_disabled():
    provider = ExternalWebSearch()
    assert provider.search("anything") == [{"disabled": True, "query": "anything"}]
