from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("jsonschema")
pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/validate_configs.py"


def test_group_validation_report(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--group",
            "logging",
            "--group",
            "tracking",
            "--quiet",
            "--report",
            str(report),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    content = json.loads(report.read_text(encoding="utf-8"))
    assert content["total"] >= 2
    assert content["counts"].get("fail", 0) == 0


def test_strict_rejects_partial_overlays(tmp_path: Path) -> None:
    config_root = tmp_path / "configs"
    config_root.mkdir(parents=True, exist_ok=True)
    partial_cfg = config_root / "logging.yaml"
    partial_cfg.write_text(
        """
telemetry:
  exporter: prometheus
  metrics: []
""",
        encoding="utf-8",
    )
    schema = ROOT / "configs/schemas/logging.schema.yaml"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--root",
            str(config_root),
            "--schema",
            str(schema),
            "--strict",
            "--quiet",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "required property" in result.stdout or "required property" in result.stderr


def test_malformed_config_is_rejected() -> None:
    bad_config = ROOT / "tests/fixtures/malformed_config.yaml"
    schema = ROOT / "configs/schemas/training.schema.yaml"
    result = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--config",
            str(bad_config),
            "--schema",
            str(schema),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (
        "failed to load config" in result.stdout
        or "required property" in result.stdout
        or "failed to load config" in result.stderr
        or "required property" in result.stderr
    )
