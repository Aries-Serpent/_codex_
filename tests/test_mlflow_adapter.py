import sys

from codex_ml.utils.logging_mlflow import mlflow_run


def test_mlflow_run_missing_dependency(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "mlflow", None)
    with mlflow_run(enabled=True, params={"a": 1}):
        pass


def test_mlflow_run_disabled() -> None:
    with mlflow_run(enabled=False, params={"a": 1}):
        pass
