import os
import copy

import pytest

from codex_ml.tracking.guards import decide_mlflow_tracking_uri


def env_with(**kvs):
    e = copy.deepcopy(os.environ)
    # Avoid leakage from prior modules that may set offline flags globally.
    e.pop("MLFLOW_OFFLINE", None)
    for k, v in kvs.items():
        if v is None and k in e:
            e.pop(k)
        elif v is not None:
            e[k] = v
    return e


@pytest.mark.parametrize(
    "mlflow_uri",
    [
        None,
        "./mlruns",
        "file:///tmp/mlruns",
        "http://127.0.0.1:5000",
    ],
)
@pytest.mark.parametrize("mlflow_offline", [None, "0", "1", "true"])
@pytest.mark.parametrize("wandb_mode", [None, "online", "offline", "disabled"])
@pytest.mark.parametrize("allow_remote", [None, "0", "1", "true"])
def test_mlflow_guard_matrix(mlflow_uri, mlflow_offline, wandb_mode, allow_remote):
    """
    Matrix of (offline flags) x (URIs) x (allow overrides).
    Acceptance:
      - Remote URIs are rewritten to file:// when offline and not explicitly allowed.
      - Local/file URIs are preserved/normalized.
      - When offline and URI unset -> default file://<abs>/mlruns is injected.
    """
    e = env_with(
        MLFLOW_TRACKING_URI=(mlflow_uri if mlflow_uri is not None else None),
        MLFLOW_OFFLINE=mlflow_offline,
        WANDB_MODE=wandb_mode,
        CODEX_ALLOW_REMOTE_TRACKING=allow_remote,
    )
    decision = decide_mlflow_tracking_uri(e)
    offline = (mlflow_offline and mlflow_offline.strip() not in {"0", ""}) or (
        wandb_mode in {"offline", "disabled"}
    )

    if allow_remote and allow_remote.strip().lower() in {"1", "true"}:
        # Explicitly allowed: never rewrite
        assert decision.reason == "explicit_allow"
        return

    if offline:
        if mlflow_uri is None:
            assert decision.uri and decision.uri.startswith("file:///")
            assert decision.uri.endswith("/mlruns")
            assert decision.reason == "offline_default_local_uri"
        elif isinstance(mlflow_uri, str) and mlflow_uri.startswith("http"):
            assert decision.uri and decision.uri.startswith("file:///")
            assert decision.uri.endswith("/mlruns")
            assert decision.blocked and "rewrite" in decision.reason
        else:
            assert decision.uri and decision.uri.startswith("file:///")
            assert decision.reason in {
                "offline_local_ok",
                "offline_enforced_rewrite_remote_to_local",
            }
    else:
        # No enforcement; normalization may occur
        if mlflow_uri is None:
            assert decision.uri is None
        elif mlflow_uri.startswith("http"):
            assert decision.uri == mlflow_uri
        else:
            assert decision.uri.startswith("file:///")


@pytest.mark.parametrize("enable", [None, "offline", "disabled"])
def test_wandb_offline_enforces_local(enable):
    """
    WANDB gating: offline or disabled implies ML tracking must stay local.
    """
    e = env_with(WANDB_MODE=enable, MLFLOW_TRACKING_URI="http://mlflow.example:5000")
    d = decide_mlflow_tracking_uri(e)
    if enable in {"offline", "disabled"}:
        assert d.uri and d.uri.startswith("file://")
        assert d.blocked
    else:
        assert d.uri == "http://mlflow.example:5000"
        assert not d.blocked
