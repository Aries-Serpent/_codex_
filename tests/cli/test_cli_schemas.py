from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import jsonschema  # type: ignore
except Exception:  # pragma: no cover - optional dependency not installed
    jsonschema = None  # type: ignore[assignment]
    pytestmark = pytest.mark.skip(reason="jsonschema not installed")

SCHEMAS = Path("schemas/cli")


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def test_list_plugins_matches_schema():
    schema = _load_schema("list_plugins.schema.json")
    proc = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli.list_plugins", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout or "{}")
    jsonschema.validate(instance=payload, schema=schema)


def test_gh_api_envelope_schema(monkeypatch, capsys):
    schema = _load_schema("gh_api_envelope.schema.json")
    import tools.github.gh_api as gh

    monkeypatch.setenv("GH_TOKEN", "dummy-token")

    def _stub_request(method, url, token, scheme, body):
        return 200, json.dumps([{"name": "branch"}]), {}

    monkeypatch.setattr(gh, "_request", _stub_request)
    rc = gh.main(
        [
            "--method",
            "GET",
            "--path",
            "/repos/owner/repo/branches",
            "--json-envelope",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    jsonschema.validate(instance=payload, schema=schema)
    assert payload["ok"] is True
