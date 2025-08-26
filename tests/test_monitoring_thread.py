from pathlib import Path

from tools.monitoring_integrate import MonitoringSession


def test_codex_logging_bootstrap(tmp_path, monkeypatch):
    import argparse
    import importlib

    mod = importlib.import_module("codex_ml.monitoring.codex_logging")
    parser = argparse.ArgumentParser()
    mod._codex_patch_argparse(parser)
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
    for mode in ("offline", "disabled"):
        monkeypatch.setenv("WANDB_MODE", mode)
        loggers = mod._codex_logging_bootstrap(args)
        mod._codex_log_all(0, {"loss": 0.0, **mod._codex_sample_system()}, loggers)


def test_system_metrics_thread_shutdown(tmp_path: Path) -> None:
    """SystemMetrics thread should terminate cleanly when session exits."""

    with MonitoringSession(
        tmp_path,
        "test",
        enable_tb=False,
        enable_wandb=False,
        enable_mlflow=False,
        metrics_interval=0.1,
    ) as mon:
        thread = mon.metrics_thread
        assert thread and thread.is_alive()

    assert thread is not None
    thread.join(timeout=1)
    assert not thread.is_alive()
