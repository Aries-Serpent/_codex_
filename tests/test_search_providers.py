from pathlib import Path

from codex.search import SearchRegistry
from codex.search.providers import ExternalWebSearch


def test_internal_search_finds_known_string():
    registry = SearchRegistry(root=Path("src"))
    results = registry.search("Utility helpers for codex")
    assert any("src/codex/utils/__init__.py" in r["path"] for r in results)


def test_external_provider_disabled_by_default():
    registry = SearchRegistry()
    assert all(not isinstance(p, ExternalWebSearch) for p in registry.providers)


def test_external_search_handles_network_error(monkeypatch):
    import urllib.request

    def fail(*args, **kwargs):
        raise urllib.error.URLError("boom")

    monkeypatch.setattr(urllib.request, "urlopen", fail)
    provider = ExternalWebSearch()
    assert provider.search("python") == []
