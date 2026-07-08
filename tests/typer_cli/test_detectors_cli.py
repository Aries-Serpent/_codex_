"""
Test Detectors Cli

Test module for detectors cli.
"""

from __future__ import annotations

import importlib
import json


def test_cli_detectors_run_integration(capsys):
    mod = importlib.import_module("codex_ml.cli.detectors")
    # call main() directly to avoid external deps
    exit_code = mod.main(["run"])
    assert exit_code == 0, "exit_code is not valid"
    out = capsys.readouterr().out
    data = json.loads(out)
    assert 0.0 <= data["total_score"] <= 1.0, "Data must not be empty"
    assert "by_detector" in data and "details" in data, "Data must not be empty"
