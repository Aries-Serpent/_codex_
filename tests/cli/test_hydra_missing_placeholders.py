from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("hydra")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_audit_config_reports_missing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    configs = tmp_path / "configs"
    _write(
        configs / "config.yaml",
        "defaults:\n  - _self_\nlearning_rate: ???\n",
    )

    from codex_ml.cli import hydra_audit

    rc = hydra_audit.audit_config(["--config-root", str(configs), "--config-name", "config"])
    if rc == 4:
        pytest.skip("hydra-core unavailable")
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)
    assert rc == 3
    assert payload["missing"] == ["learning_rate"]


def test_audit_config_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    configs = tmp_path / "configs"
    _write(
        configs / "config.yaml",
        "defaults:\n  - _self_\nlearning_rate: 3e-4\n",
    )

    from codex_ml.cli import hydra_audit

    rc = hydra_audit.audit_config(["--config-root", str(configs), "--config-name", "config"])
    if rc == 4:
        pytest.skip("hydra-core unavailable")
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)
    assert rc == 0
    assert payload["missing"] == []
