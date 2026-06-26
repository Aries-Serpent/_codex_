"""
Test System Metrics Flag

Test module for system metrics flag.
"""

from pathlib import Path

from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_train_starts_system_metrics(monkeypatch, tmp_path: Path):
    output_dir = tmp_path / "run"
    cfg_obj = type(
        "Cfg", (), {"training": type("T", (), {"output_dir": str(output_dir), "seed": 0})()}
    )()
    raw_cfg = type("RCfg", (), {"training": type("T", (), {"output_dir": str(output_dir)})()})()

    calls = {}

    def fake_load_app_config(path, overrides):
        return cfg_obj, raw_cfg

    class DummyLogger:
        def __init__(self, path):
            calls["logger_path"] = path

        def __enter__(self):
            calls["logger_started"] = True
            return self

        def __exit__(self, exc_type, exc, tb):
            calls["logger_stopped"] = True
            return False

    def fake_run_functional_training(config=None, resume=False):
        calls["ran"] = True

    monkeypatch.setattr("codex_ml.cli.codex_cli.load_app_config", fake_load_app_config)
    monkeypatch.setattr("codex_ml.training.run_functional_training", fake_run_functional_training)
    monkeypatch.setattr("codex_ml.cli.codex_cli.SystemMetricsLogger", DummyLogger)

    config_path = tmp_path / "config.yaml"
    config_path.write_text("training: {}\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        codex,
        [
            "train",
            "--config",
            str(config_path),
            "--system-metrics",
        ],
    )

    assert result.exit_code == 0, "Result must not be empty"
    assert calls.get("ran"), "Condition must be true"
    assert calls.get("logger_started"), "Condition must be true"
    assert calls.get("logger_stopped"), "Condition must be true"
