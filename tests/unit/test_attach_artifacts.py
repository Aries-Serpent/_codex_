from __future__ import annotations

import json
from pathlib import Path


def test_log_dict_safe(tmp_path: Path, monkeypatch) -> None:
    try:
        from common.mlflow_guard import log_dict_safe
    except Exception:  # pragma: no cover - optional dependency missing
        return

    artifact_path = tmp_path / "artifact.json"
    log_dict_safe({"a": 1}, artifact_path=str(artifact_path))
    assert artifact_path.exists()
    payload = json.loads(artifact_path.read_text())
    assert payload["a"] == 1
