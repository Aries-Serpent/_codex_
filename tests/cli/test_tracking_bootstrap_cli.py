import json
import subprocess
import sys
from pathlib import Path


def _run(*argv: str) -> tuple[int, dict]:
    process = subprocess.run(
        [sys.executable, "-m", "codex_ml.cli", *argv],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(process.stdout or "{}")
    return process.returncode, payload


def test_tracking_bootstrap_offline_defaults(tmp_path: Path) -> None:
    code, payload = _run("tracking", "bootstrap", "--mlflow", "--wandb")
    assert code == 0
    assert payload.get("ok") is True
    assert "mlflow" in payload or "wandb" in payload


def test_tracking_bootstrap_file_uri(tmp_path: Path) -> None:
    uri = f"file:{(tmp_path / 'mlruns').as_posix()}"
    code, payload = _run("tracking", "bootstrap", "--mlflow", "--mlflow-uri", uri)
    assert code == 0
    mlflow_payload = payload.get("mlflow", {})
    assert mlflow_payload.get("enabled") in {True, False}
    assert mlflow_payload.get("tracking_uri") is not None
