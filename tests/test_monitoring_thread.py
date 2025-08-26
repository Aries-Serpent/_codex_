import argparse
import importlib


def test_offline_bootstrap(tmp_path, monkeypatch):
    m = importlib.import_module("codex_ml.monitoring.codex_logging")
    parser = argparse.ArgumentParser()
    m._codex_patch_argparse(parser)
    args = parser.parse_args(
        [
            "--enable-wandb",
            "--mlflow-enable",
            "--mlflow-tracking-uri",
            str(tmp_path / "mlruns"),
            "--mlflow-experiment",
            "codex-test",
            "--tb-logdir",
            str(tmp_path / "tb"),
        ]
    )
    monkeypatch.setenv("WANDB_MODE", "offline")
    loggers = m._codex_logging_bootstrap(args)
    m._codex_log_all(0, {"loss": 0.0}, loggers)
    sysd = m._codex_sample_system()
    assert isinstance(sysd, dict)
    if loggers.tb is not None:
        assert (tmp_path / "tb").exists()
