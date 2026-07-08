"""
Test Registry Degradation

Test module for registry degradation.
"""

from __future__ import annotations

import importlib
import json
import sys
import types

import codex_ml.cli.list_plugins as list_plugins


def test_programmatic_registry_failure_degrades_to_legacy(monkeypatch, capsys):
    def _boom():
        raise RuntimeError("registry unavailable")

    fake_module = types.SimpleNamespace(registry=_boom)
    monkeypatch.setitem(sys.modules, "codex_ml.plugins.programmatic", fake_module)
    plugins_spec = importlib.util.find_spec("codex_ml.plugins")
    if plugins_spec is not None:
        plugins_pkg = importlib.import_module("codex_ml.plugins")
        monkeypatch.setattr(plugins_pkg, "programmatic", fake_module, raising=False)

    rc = list_plugins.main(["--format", "json"])
    assert rc == 0, "rc is not valid"
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert "legacy" in payload, "Condition must be true"
    assert isinstance(payload["legacy"], dict)
    assert payload["programmatic"]["names"] == [], "Condition must be true"
