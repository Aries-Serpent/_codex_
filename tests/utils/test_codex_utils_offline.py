import json
import os
import types
from pathlib import Path
from urllib.parse import urlparse

import pytest

from codex_utils import (
    NDJSONLogger,
    OfflineTB,
    bootstrap_mlflow_env,
    mlflow_offline_session,
    sample_system_metrics,
)
from codex_utils import repro as repro_mod


class _FakeRun:
    def __init__(self):
        self.entered = False

    def __enter__(self):
        self.entered = True
        return "active-run"

    def __exit__(self, exc_type, exc, tb):
        self.entered = False


def test_mlflow_offline_session_without_mlflow(monkeypatch, tmp_path):
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file://pre-existing")
    monkeypatch.setattr("codex_utils.mlflow_offline._safe_import_mlflow", lambda: None)

    artifacts_dir = tmp_path / "mlruns"
    with mlflow_offline_session(str(artifacts_dir)) as run:
        assert run is None
        parsed = urlparse(os.environ["MLFLOW_TRACKING_URI"])
        assert parsed.scheme == "file"
        assert Path(parsed.path) == artifacts_dir
        assert os.environ["CODEX_MLFLOW_LOCAL_DIR"] == str(artifacts_dir)
        assert artifacts_dir.exists()

    assert os.environ["MLFLOW_TRACKING_URI"] == "file://pre-existing"


def test_mlflow_offline_session_with_mlflow(monkeypatch, tmp_path):
    fake = types.SimpleNamespace()
    fake.captured: dict[str, object] = {}

    def set_tracking_uri(uri: str) -> None:
        fake.captured["uri"] = uri

    def set_experiment(exp: str) -> None:
        fake.captured["experiment"] = exp

    fake_run = _FakeRun()

    def start_run(run_name: str | None = None, tags: dict[str, str] | None = None):
        fake.captured["run_name"] = run_name
        fake.captured["tags"] = tags
        return fake_run

    fake.set_tracking_uri = set_tracking_uri
    fake.set_experiment = set_experiment
    fake.start_run = start_run

    monkeypatch.setattr("codex_utils.mlflow_offline._safe_import_mlflow", lambda: fake)

    with mlflow_offline_session(
        str(tmp_path / "mlruns"),
        experiment="exp",
        run_name="run",
        run_tags={"a": "b"},
    ) as active:
        assert active == "active-run"
        assert fake_run.entered is True

    assert fake_run.entered is False
    assert fake.captured["experiment"] == "exp"
    assert fake.captured["run_name"] == "run"
    assert fake.captured["tags"] == {"a": "b"}
    assert fake.captured["uri"].startswith("file://")


def test_bootstrap_mlflow_env_sets_local_dir(tmp_path):
    prev_tracking = os.environ.get("MLFLOW_TRACKING_URI")
    prev_codex_uri = os.environ.get("CODEX_MLFLOW_URI")
    prev_local_dir = os.environ.get("CODEX_MLFLOW_LOCAL_DIR")

    os.environ.pop("MLFLOW_TRACKING_URI", None)
    os.environ.pop("CODEX_MLFLOW_URI", None)
    os.environ.pop("CODEX_MLFLOW_LOCAL_DIR", None)

    try:
        target = tmp_path / "mlruns"
        uri = bootstrap_mlflow_env(str(target), force=True)
        parsed = urlparse(uri)
        assert parsed.scheme == "file"
        assert Path(parsed.path) == target
        assert os.environ["CODEX_MLFLOW_LOCAL_DIR"] == str(target)
        assert os.environ.get("MLFLOW_TRACKING_URI", "").startswith("file:")
    finally:
        if prev_tracking is None:
            os.environ.pop("MLFLOW_TRACKING_URI", None)
        else:
            os.environ["MLFLOW_TRACKING_URI"] = prev_tracking
        if prev_codex_uri is None:
            os.environ.pop("CODEX_MLFLOW_URI", None)
        else:
            os.environ["CODEX_MLFLOW_URI"] = prev_codex_uri
        if prev_local_dir is None:
            os.environ.pop("CODEX_MLFLOW_LOCAL_DIR", None)
        else:
            os.environ["CODEX_MLFLOW_LOCAL_DIR"] = prev_local_dir


def test_mlflow_offline_session_start_run_false(monkeypatch, tmp_path):
    fake = types.SimpleNamespace()
    fake.set_tracking_uri = lambda uri: None
    fake.set_experiment = lambda exp: None
    fake.start_run = lambda **_: pytest.fail("start_run should not be called")

    monkeypatch.setattr("codex_utils.mlflow_offline._safe_import_mlflow", lambda: fake)

    with mlflow_offline_session(
        str(tmp_path / "mlruns"),
        start_run=False,
    ) as module:
        assert module is fake


def test_rng_roundtrip(tmp_path):
    state = repro_mod.set_seed(1337)
    baseline = [__import__("random").random() for _ in range(3)]
    save_path = tmp_path / "rng.json"
    repro_mod.save_rng(str(save_path), state)

    restored = repro_mod.load_rng(str(save_path))
    repro_mod.set_seed(123)
    repro_mod.restore_rng(restored)
    assert [__import__("random").random() for _ in range(3)] == baseline

    if repro_mod.np is not None:
        repro_mod.restore_rng(restored)
        np_vals = repro_mod.np.random.rand(2)
        repro_mod.restore_rng(restored)
        np_vals_again = repro_mod.np.random.rand(2)
        assert repro_mod.np.allclose(np_vals, np_vals_again)

    if repro_mod.torch is not None and hasattr(repro_mod.torch, "rand"):
        repro_mod.restore_rng(restored)
        t_vals = repro_mod.torch.rand(2)
        repro_mod.restore_rng(restored)
        t_vals_again = repro_mod.torch.rand(2)
        assert repro_mod.torch.allclose(t_vals, t_vals_again)


def test_ndjson_logger(tmp_path):
    target = tmp_path / "metrics.ndjson"
    with NDJSONLogger(str(target)) as logger:
        logger.write({"step": 1})
        logger.write_many([{"step": 2}])
    lines = target.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["step"] for line in lines] == [1, 2]

    with pytest.raises(RuntimeError):
        logger.write({"step": 3})


def test_ndjson_logger_path_property(tmp_path):
    target = tmp_path / "out.ndjson"
    with NDJSONLogger(str(target)) as logger:
        assert Path(logger.path) == target


class _DummyWriter:
    def __init__(self, logdir: str):
        self.logdir = logdir
        self.records: list[tuple[str, float, int]] = []
        self.closed = False

    def add_scalar(self, tag: str, value: float, step: int) -> None:
        self.records.append((tag, value, step))

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True


@pytest.fixture()
def dummy_writer(monkeypatch, tmp_path):
    writer = _DummyWriter(str(tmp_path))
    monkeypatch.setattr("codex_utils.logging_setup.SummaryWriter", lambda logdir: writer)
    return writer


def test_offline_tb_logs_scalars(dummy_writer):
    with OfflineTB(dummy_writer.logdir) as tb:
        assert tb.enabled
        tb.log_scalar("loss", 1.0, 1)
        tb.log_scalars({"acc": 0.5}, step=2)
    assert dummy_writer.closed is True
    assert ("loss", 1.0, 1) in dummy_writer.records
    assert ("acc", 0.5, 2) in dummy_writer.records


def test_offline_tb_disabled(monkeypatch, tmp_path):
    monkeypatch.setattr("codex_utils.logging_setup.SummaryWriter", None, raising=False)
    with OfflineTB(str(tmp_path)) as tb:
        assert not tb.enabled
        tb.log_scalar("loss", 1.0, 1)
        tb.log_scalars({"acc": 0.5}, step=2)


def test_sample_system_metrics_with_psutil(monkeypatch):
    process = types.SimpleNamespace(
        cpu_percent=lambda interval=None: 7.0,
        memory_info=lambda: types.SimpleNamespace(rss=512 * 1024**2),
    )
    fake_psutil = types.SimpleNamespace(
        cpu_percent=lambda interval=None: 42.0,
        virtual_memory=lambda: types.SimpleNamespace(percent=33.0, used=2 * 1024**3),
        Process=lambda: process,
    )
    monkeypatch.setattr("codex_utils.logging_setup.psutil", fake_psutil)

    payload = sample_system_metrics()
    assert payload["cpu_percent"] == pytest.approx(42.0)
    assert payload["mem_percent"] == pytest.approx(33.0)
    assert payload["process"]["rss_gb"] == pytest.approx(0.5, rel=1e-6)


def test_sample_system_metrics_without_psutil(monkeypatch):
    monkeypatch.setattr("codex_utils.logging_setup.psutil", None, raising=False)
    payload = sample_system_metrics()
    assert "cpu_percent" in payload
    assert payload["mem_percent"] is None
    assert "time_unix" in payload
