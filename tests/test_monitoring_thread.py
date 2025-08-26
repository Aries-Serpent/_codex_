from pathlib import Path

from tools.monitoring_integrate import MonitoringSession


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

