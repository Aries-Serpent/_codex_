from __future__ import annotations

import json
from pathlib import Path

from codex_ml.analysis.providers import ExternalWebSearch


def _write_offline_index(path: Path, query: str = "codex") -> None:
    payload = {
        query: [
            {
                "Text": "Codex reference",
                "FirstURL": "https://example.com/codex",
                "snippet": "Details about Codex",
            }
        ]
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_external_web_search_loads_offline_index(tmp_path: Path) -> None:
    offline_index = tmp_path / "index.json"
    _write_offline_index(offline_index)

    search = ExternalWebSearch(endpoint=offline_index.as_uri(), enabled=True)
    result = search.search("codex")

    assert result["status"] == "ok"
    assert result["results"], "offline payload should populate results"
    entry = result["results"][0]
    assert entry["title"] == "Codex reference"
    assert entry["url"].endswith("/codex")


def test_external_web_search_supports_tilde_endpoint(monkeypatch, tmp_path: Path) -> None:
    offline_index = tmp_path / "index.json"
    _write_offline_index(offline_index)

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    search = ExternalWebSearch(endpoint="file://~/index.json", enabled=True)
    result = search.search("codex")

    assert result["status"] == "ok"
    assert any(entry["url"].endswith("/codex") for entry in result["results"])
