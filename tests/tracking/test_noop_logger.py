from src.codex_ml.utils import experiment_tracking_mlflow as etm


def test_noop_logger_exposes_tracking_uri_env_default(monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    with etm.maybe_mlflow(enable=False) as m:
        assert m.get_tracking_uri().startswith("file:")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "file:/tmp/mlruns")
    with etm.maybe_mlflow(enable=False) as m:
        assert m.get_tracking_uri().startswith("file:")
