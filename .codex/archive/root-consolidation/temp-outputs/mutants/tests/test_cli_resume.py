"""
Test Cli Resume

Test module for cli resume.
"""

import json
from pathlib import Path

from click.testing import CliRunner

from codex_ml.cli.codex_cli import resume as resume_cmd


def test_resume_cli_requires_checkpoint(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"config_path": str(tmp_path / "cfg.yaml")}), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(resume_cmd, [str(manifest)])
    assert result.exit_code != 0, "Result must not be empty"
    assert "checkpoint" in result.output.lower(), "Result must not be empty"


def test_resume_cli_calls_training(monkeypatch, tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text("seed: 1", encoding="utf-8")
    ckpt = tmp_path / "ckpt.pt"
    manifest.write_text(
        json.dumps(
            {
                "config_path": str(cfg_path),
                "best_checkpoint": str(ckpt),
            }
        ),
        encoding="utf-8",
    )

    class DummyTraining:
        output_dir = str(tmp_path)
        resume_from = None

    dummy_cfg = type("Cfg", (), {"training": DummyTraining()})()
    dummy_raw = type("Raw", (), {"training": DummyTraining()})()

    monkeypatch.setattr(
        "codex_ml.cli.codex_cli.load_app_config", lambda path, overrides: (dummy_cfg, dummy_raw)
    )
    called = {}

    def fake_run(config, resume=False):
        called["resume"] = resume
        called["resume_from"] = getattr(config, "resume_from", None)

    monkeypatch.setattr("codex_ml.training.run_functional_training", fake_run)

    runner = CliRunner()
    result = runner.invoke(resume_cmd, [str(manifest)])
    assert result.exit_code == 0, "Result must not be empty"
    assert called["resume"] is True, "Condition must be true"
    assert called["resume_from"] == str(ckpt), "Condition must be true"
