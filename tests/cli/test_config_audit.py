import json
import subprocess
import sys
from pathlib import Path


def _run_config(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "codex_ml.cli", "config", *args],
        text=True,
        capture_output=True,
        cwd=cwd,
    )


def test_config_audit_first_ok(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("defaults:\n  - _self_\n  - dataset: base\n", encoding="utf-8")
    proc = _run_config("--audit", "first", "--path", str(cfg))
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["position"] == 0
    assert payload["_self_"] is True


def test_config_audit_missing_self(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("defaults:\n  - dataset: base\n", encoding="utf-8")
    proc = _run_config("--audit", "first", "--path", str(cfg))
    assert proc.returncode == 3
    payload = json.loads(proc.stdout)
    assert payload["_self_"] is False
    assert payload["ok"] is False


def test_config_audit_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "nope.yaml"
    proc = _run_config("--path", str(missing))
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["_self_"] is False
    assert payload["position"] is None
