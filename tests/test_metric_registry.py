import json

import pytest

try:
    from typer.testing import CliRunner
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    CliRunner = None  # type: ignore[assignment]

try:
    from codex_ml.cli.plugins_cli import app as plugins_app
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    plugins_app = None  # type: ignore[assignment]

from codex_ml.plugins import registries


@pytest.fixture(autouse=True)
def _clear_metric_env(monkeypatch):
    for key in ("CODEX_ML_WEIGHTED_ACCURACY_PATH", "CODEX_ML_OFFLINE_METRICS_DIR"):
        monkeypatch.delenv(key, raising=False)


def test_offline_metric_reads_weights(monkeypatch, tmp_path):
    weights_file = tmp_path / "weighted_accuracy.json"
    weights_file.write_text(json.dumps({"0": 0.2, "1": 1.8}), encoding="utf-8")
    monkeypatch.setenv("CODEX_ML_WEIGHTED_ACCURACY_PATH", str(weights_file))

    metric = registries.metrics.resolve_and_instantiate("offline:weighted-accuracy")
    score = metric(["1", "1"], ["1", "0"])

    assert score == pytest.approx(1.8 / (1.8 + 0.2))


def test_offline_metric_missing_file(tmp_path):
    bogus = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError) as excinfo:
        registries.metrics.resolve_and_instantiate(
            "offline:weighted-accuracy", weights_path=str(bogus)
        )

    assert "offline:weighted-accuracy" in str(excinfo.value)


@pytest.mark.skipif(
    CliRunner is None or plugins_app is None,
    reason="plugin CLI unavailable",
)
def test_plugin_cli_lists_metrics():
    runner = CliRunner()
    result = runner.invoke(plugins_app, ["list", "metrics"])
    assert result.exit_code == 0
    entries = result.stdout.strip().splitlines()
    assert "offline:weighted-accuracy" in entries
