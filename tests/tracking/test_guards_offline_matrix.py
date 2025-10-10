from __future__ import annotations

import os

from codex_ml.tracking.guards import enforce_offline_posture


def test_enforce_offline_sets_file_uri(tmp_path):
    d = enforce_offline_posture(str(tmp_path / "mlruns_local"))
    assert d["mlflow"]["uri"].startswith("file://")
    assert "offline" in d["mlflow"]["reason"]
    assert d["wandb"]["mode"] in {"offline", "disabled"}
    # ensure envs set
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file://")
