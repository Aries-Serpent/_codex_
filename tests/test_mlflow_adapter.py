from __future__ import annotations


def test_maybe_mlflow_noop_when_disabled():
    from codex_ml.utils.experiment_tracking_mlflow import maybe_mlflow

    with maybe_mlflow(enable=False) as mlf:
        mlf.log_params({"a": 1})
        mlf.log_metrics({"m": 0.1}, step=1)
        mlf.log_artifact("does_not_exist.txt")


def test_maybe_mlflow_import_guard(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "mlflow":
            raise ImportError("mlflow not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    from codex_ml.utils.experiment_tracking_mlflow import maybe_mlflow

    with maybe_mlflow(enable=True) as mlf:
        mlf.log_params({"x": "y"})
