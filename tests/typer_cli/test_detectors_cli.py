from __future__ import annotations
import json
import importlib


def test_cli_detectors_run_integration(capsys):
    mod = importlib.import_module("codex_ml.cli.detectors")
    # call main() directly to avoid external deps
    exit_code = mod.main(["run"])
    assert exit_code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert 0.0 <= data["total_score"] <= 1.0
    assert "by_detector" in data and "details" in data
