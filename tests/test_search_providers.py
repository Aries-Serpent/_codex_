import shutil
from pathlib import Path

import pytest

from codex.search import SearchRegistry
from codex.search.providers import ExternalWebSearch


def test_internal_search_finds_known_string():
    if shutil.which("rg") is None:
        pytest.skip("ripgrep not installed")
    registry = SearchRegistry(root=Path(__file__).resolve().parents[1] / "src")
    results = registry.search("Utility helpers for codex")
    assert any("src/codex/utils/__init__.py" in r["path"] for r in results)


def test_external_provider_disabled_by_default():
    registry = SearchRegistry()
    assert all(not isinstance(p, ExternalWebSearch) for p in registry.providers)


def test_external_search_handles_network_error(monkeypatch):
    from tools.security import net

    def fail(*_args, **_kwargs):
        raise OSError("boom")

    monkeypatch.setattr(net, "safe_fetch", fail)
    provider = ExternalWebSearch()
    assert provider.search("python") == []
