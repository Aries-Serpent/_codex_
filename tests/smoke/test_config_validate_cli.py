from pathlib import Path

import pytest
from typer.testing import CliRunner

from codex_ml.cli.validate import app

pytestmark = pytest.mark.smoke


def test_validate_ok(tmp_path: Path):
    cfg = tmp_path / "ok.yaml"
    cfg.write_text(
        "model_name: tiny\nlearning_rate: 0.001\nepochs: 1\nmax_samples: 8\n",
        encoding="utf-8",
    )
    r = CliRunner().invoke(app, ["file", str(cfg)])
    assert r.exit_code == 0, r.output


def test_validate_bad(tmp_path: Path):
    cfg = tmp_path / "bad.yaml"
    cfg.write_text("learning_rate: -1\nepochs: 0\n", encoding="utf-8")
    r = CliRunner().invoke(app, ["file", str(cfg)])
    assert r.exit_code != 0
    assert "Invalid configuration" in r.output
