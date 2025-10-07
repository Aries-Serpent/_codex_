import os
import importlib
import pytest


def _reload():
    if "codex_ml.monitoring.codex_logging" in list(globals()):
        import sys

        sys.modules.pop("codex_ml.monitoring.codex_logging", None)
    return importlib.import_module("codex_ml.monitoring.codex_logging")


@pytest.mark.parametrize(
    "offline,uri,expect_block",
    [
        ("1", "http://remote.example/mlflow", True),
        ("1", "file:./local_runs", False),
        ("0", "http://remote.example/mlflow", False),  # guard disabled
    ],
)
def test_mlflow_guard_variants(monkeypatch, offline, uri, expect_block):
    monkeypatch.setenv("MLFLOW_OFFLINE", offline)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)
    mod = _reload()
    if offline == "1" and uri.startswith("http"):
        with pytest.raises(ValueError):
            mod._resolve_mlflow_tracking_uri(uri)  # type: ignore
    else:
        # Should not raise
        try:
            mod._resolve_mlflow_tracking_uri(uri)  # type: ignore
        except ValueError:
            assert expect_block, "Unexpected block scenario"


def test_wandb_offline_default(monkeypatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    os.environ.pop("WANDB_ENABLE", None)
    # We only verify no crash on import; wandb optional
    import codex_ml.monitoring.tracking as tracking  # noqa: F401


def test_literal_uri_preserved(monkeypatch):
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "")
    monkeypatch.setenv("CODEX_MLFLOW_URI", "")
    from codex_ml.tracking.mlflow_guard import ensure_file_backend_decision

    decision = ensure_file_backend_decision(requested_uri="uri", allow_remote=False, force=True)
    assert decision.effective_uri == "uri"
    assert decision.fallback_reason is None
