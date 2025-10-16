from __future__ import annotations

from pathlib import Path

from src import logging_utils


def test_setup_logging_tensorboard(monkeypatch, tmp_path):
    events: list[tuple[str, float, int]] = []

    class StubWriter:
        def __init__(self, log_dir: str) -> None:
            self.log_dir = Path(log_dir)

        def add_scalar(self, name: str, value: float, step: int) -> None:
            events.append((name, value, step))

        def flush(self) -> None:
            events.append(("flush", 0.0, 0))

        def close(self) -> None:
            events.append(("close", 0.0, 0))

    monkeypatch.setattr(logging_utils, "SummaryWriter", StubWriter)

    session = logging_utils.setup_logging(
        logging_utils.LoggingConfig(enable_tensorboard=True, tensorboard_log_dir=str(tmp_path))
    )
    logging_utils.log_metrics(session, {"loss": 1.0}, step=1)
    logging_utils.shutdown_logging(session)

    assert ("loss", 1.0, 1) in events
    assert ("close", 0.0, 0) in events


def test_setup_logging_mlflow(monkeypatch):
    class StubMlflow:
        def __init__(self) -> None:
            self.started: list[str] = []
            self.logged: list[tuple[dict[str, float], int]] = []
            self.ended = 0

        def set_tracking_uri(self, uri: str) -> None:
            self.uri = uri

        def start_run(self, run_name: str) -> None:
            self.started.append(run_name)

        def log_metrics(self, metrics: dict[str, float], step: int) -> None:
            self.logged.append((metrics, step))

        def end_run(self) -> None:
            self.ended += 1

    stub = StubMlflow()
    monkeypatch.setattr(logging_utils, "mlflow", stub)

    session = logging_utils.setup_logging(
        logging_utils.LoggingConfig(enable_mlflow=True, mlflow_offline=True, mlflow_run_name="demo")
    )
    logging_utils.log_metrics(session, {"accuracy": 0.9}, step=2)
    logging_utils.shutdown_logging(session)

    assert stub.started == ["demo"]
    assert stub.logged == [({"accuracy": 0.9}, 2)]
    assert stub.ended == 1
