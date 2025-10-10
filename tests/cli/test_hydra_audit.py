from __future__ import annotations

import json
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_defaults_audit_flags_self(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    configs = tmp_path / "configs"
    _write(configs / "db" / "mysql.yaml", "host: localhost\n")
    _write(
        configs / "exp" / "config.yaml",
        "defaults:\n  - db: mysql\n  - _self_\n",
    )

    from codex_ml.cli import hydra_audit

    rc = hydra_audit.main(["defaults-audit", "--config-root", str(configs)])
    captured = capsys.readouterr().out.strip()
    payload = json.loads(captured)

    assert rc == 0
    assert payload["issues"] == 0
    assert payload["files"] >= 1


def test_defaults_audit_missing_self(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    configs = tmp_path / "configs"
    _write(configs / "db" / "postgresql.yaml", "host: localhost\n")
    _write(configs / "exp" / "config.yaml", "defaults:\n  - db: postgresql\n")

    from codex_ml.cli import hydra_audit

    rc = hydra_audit.main(["defaults-audit", "--config-root", str(configs)])
    captured = capsys.readouterr().out.strip()
    payload = json.loads(captured)

    assert rc == 3
    assert payload["issues"] >= 1
