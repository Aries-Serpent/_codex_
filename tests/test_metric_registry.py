from __future__ import annotations

import json

import pytest

from codex_ml.metrics.registry import get_metric
from codex_ml.plugins.registries import metrics as plugin_metrics


def test_weighted_accuracy_offline(tmp_path):
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(json.dumps({"0": 1.0, "1": 2.0}), encoding="utf-8")

    metric = get_metric("offline:weighted-accuracy")
    score = metric([0, 1, 1], [0, 1, 0], weights_path=str(weights_file))
    assert pytest.approx(score) == 0.75


def test_weighted_accuracy_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.json"
    monkeypatch.delenv("CODEX_ML_WEIGHTED_ACCURACY_PATH", raising=False)
    monkeypatch.setenv("CODEX_ML_OFFLINE_METRICS_DIR", str(tmp_path / "other"))

    metric = get_metric("offline:weighted-accuracy")
    with pytest.raises(FileNotFoundError):
        metric([1], [1], weights_path=str(missing))


def test_plugin_catalogue_weighted_accuracy(tmp_path):
    weights_file = tmp_path / "weights.json"
    weights_file.write_text(json.dumps({"0": 1.0, "1": 2.0}), encoding="utf-8")

    metric = plugin_metrics.resolve_and_instantiate(
        "offline:weighted-accuracy",
        weights_path=str(weights_file),
    )
    score = metric([0, 1, 1], [0, 1, 0])
    assert pytest.approx(score) == 0.75


def test_plugin_catalogue_weighted_accuracy_missing(tmp_path, monkeypatch):
    missing = tmp_path / "missing.json"
    monkeypatch.delenv("CODEX_ML_WEIGHTED_ACCURACY_PATH", raising=False)
    monkeypatch.setenv("CODEX_ML_OFFLINE_METRICS_DIR", str(tmp_path / "other"))

    with pytest.raises(FileNotFoundError):
        plugin_metrics.resolve_and_instantiate(
            "offline:weighted-accuracy",
            weights_path=str(missing),
        )


def test_plugins_cli_lists_offline_metrics():
    pytest.importorskip("typer")
    from typer.testing import CliRunner

    from codex_ml.cli import plugins_cli

    runner = CliRunner()
    result = runner.invoke(plugins_cli.app, ["list", "metrics"])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert any("offline:weighted-accuracy" in line for line in output)
