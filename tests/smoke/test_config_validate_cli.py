"""
Test Config Validate Cli

Test module for config validate cli.
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke


def test_validate_ok(tmp_path: Path):
    """Test config validation with valid config."""
    # Import here to handle optional dependencies
    try:
        from typer.testing import CliRunner

        from codex_ml.cli.validate import app
    except ImportError:
        pytest.skip("Typer not available")
    else:
        cfg = tmp_path / "ok.yaml"
        cfg.write_text(
            "model_name: tiny\nlearning_rate: 0.001\nepochs: 1\nmax_samples: 8\n",
            encoding="utf-8",
        )
        runner = CliRunner()
        r = runner.invoke(app, ["file", str(cfg)])
        if "Path 'file' does not exist" in r.output:
            r = runner.invoke(app, [str(cfg)])
        assert r.exit_code == 0, r.output


def test_validate_bad(tmp_path: Path):
    """Test config validation with invalid config."""
    # Import here to handle optional dependencies
    try:
        from typer.testing import CliRunner

        from codex_ml.cli.validate import app
    except ImportError:
        pytest.skip("Typer not available")
    else:
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("learning_rate: -1\nepochs: 0\n", encoding="utf-8")
        runner = CliRunner()
        r = runner.invoke(app, ["file", str(cfg)])
        if "Path 'file' does not exist" in r.output:
            r = runner.invoke(app, [str(cfg)])
        assert r.exit_code != 0, "exit_code is not valid"
        assert "Invalid configuration" in r.output, "Condition must be true"
