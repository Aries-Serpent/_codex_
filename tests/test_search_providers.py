import shutil
from pathlib import Path

import pytest

from codex.search import SearchRegistry
from codex.search.providers import ExternalWebSearch


def test_internal_search_finds_known_string():
    """Internal ripgrep search should locate a known phrase.

    Skip if the ``rg`` executable is not available in the environment to avoid
    spurious failures on minimal installations.
    """

    if shutil.which("rg") is None:
        pytest.skip("ripgrep not installed")

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
