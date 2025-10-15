from __future__ import annotations

import json
import types
from pathlib import Path

import tools.github.gh_api as gh


def test_pagination_aggregates_arrays(monkeypatch, capsys):
    calls = {"n": 0}

    def _stub_request(method, url, token, scheme, body):
        calls["n"] += 1
        if calls["n"] == 1:
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
    monkeypatch.setattr(
        gh,
        "sys",
        types.SimpleNamespace(argv=argv, stdout=gh.sys.stdout, stderr=gh.sys.stderr),
    )

    rc = gh.main()
    assert rc == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert isinstance(payload, list)
    assert [item["name"] for item in payload] == ["a", "b", "c"]


def test_cache_write_and_read(monkeypatch, tmp_path: Path, capsys):
    def _stub_request(method, url, token, scheme, body):
        return 200, json.dumps({"ok": True}), {}

    monkeypatch.setenv("GH_TOKEN", "dummy")
    monkeypatch.setattr(gh, "_request", _stub_request)
    cache_dir = tmp_path / "cache"

    argv1 = [
        "prog",
        "--method",
        "GET",
        "--path",
        "/repos/o/r/branches",
        "--cache-dir",
        str(cache_dir),
    ]
    monkeypatch.setattr(
        gh,
        "sys",
        types.SimpleNamespace(argv=argv1, stdout=gh.sys.stdout, stderr=gh.sys.stderr),
    )
    rc1 = gh.main()
    assert rc1 == 0
    capsys.readouterr()
    cached_files = list(cache_dir.glob("*.json"))
    assert cached_files, "expected a cached JSON file"

    def _boom(*_args, **_kwargs):
        raise AssertionError("network should not be called in cache-only mode")

    monkeypatch.setattr(gh, "_request", _boom)
    argv2 = [
        "prog",
        "--method",
        "GET",
        "--path",
        "/repos/o/r/branches",
        "--cache-dir",
        str(cache_dir),
        "--use-cache-only",
    ]
    monkeypatch.setattr(
        gh,
        "sys",
        types.SimpleNamespace(argv=argv2, stdout=gh.sys.stdout, stderr=gh.sys.stderr),
    )
    rc2 = gh.main()
    assert rc2 == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload.get("ok") is True
