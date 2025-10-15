from __future__ import annotations

import json
from pathlib import Path

import tools.github.gh_api as gh


def test_pagination_aggregates_arrays(monkeypatch, capsys):
    calls = {"count": 0}

    def _stub_request(method, url, token, scheme, body):
        calls["count"] += 1
        if calls["count"] == 1:
            headers = {"Link": '<https://api.example/next>; rel="next"'}
            return 200, json.dumps([{"name": "a"}, {"name": "b"}]), headers
        headers = {}
        return 200, json.dumps([{"name": "c"}]), headers

    monkeypatch.setenv("GH_TOKEN", "dummy")
    monkeypatch.setattr(gh, "_request", _stub_request)

    argv = [
        "prog",
        "--method",
        "GET",
        "--path",
        "/repos/o/r/branches",
        "--paginate",
        "--max-pages",
        "10",
    ]
    monkeypatch.setattr(gh.sys, "argv", argv)

    rc = gh.main()
    assert rc == 0
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)
    assert isinstance(payload, list)
    assert [item["name"] for item in payload] == ["a", "b", "c"]


def test_cache_write_and_read(monkeypatch, tmp_path: Path, capsys):
    def _stub_request(method, url, token, scheme, body):
        return 200, json.dumps({"ok": True}), {}

    monkeypatch.setenv("GH_TOKEN", "dummy")
    monkeypatch.setattr(gh, "_request", _stub_request)
    cache_dir = tmp_path / "cache"

    argv_first = [
        "prog",
        "--method",
        "GET",
        "--path",
        "/repos/o/r/branches",
        "--cache-dir",
        str(cache_dir),
    ]
    monkeypatch.setattr(gh.sys, "argv", argv_first)
    rc_first = gh.main()
    assert rc_first == 0
    capsys.readouterr()  # drain
    cached_files = list(cache_dir.glob("*.json"))
    assert cached_files, "expected cached payload"

    def _boom(*_args, **_kwargs):  # pragma: no cover - ensures we stay offline
        raise AssertionError("network should not be called in cache-only mode")

    monkeypatch.setattr(gh, "_request", _boom)
    argv_second = [
        "prog",
        "--method",
        "GET",
        "--path",
        "/repos/o/r/branches",
        "--cache-dir",
        str(cache_dir),
        "--use-cache-only",
    ]
    monkeypatch.setattr(gh.sys, "argv", argv_second)
    rc_second = gh.main()
    assert rc_second == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["ok"] is True
