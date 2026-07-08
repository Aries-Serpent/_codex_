"""
Test Cli Utils Run Context

Test module for cli utils run context.
"""

from pathlib import Path

import yaml

from codex_ml.cli import utils as cli_utils


def test_create_run_dir_and_manifest(tmp_path: Path):
    base_dir = tmp_path / "runs"
    ctx = cli_utils.create_run_dir(base_dir, mode="train", seed=42)
    assert "seed42" in ctx.run_id, "Condition must be true"
    assert Path(ctx.run_dir).exists(), "Condition must be true"

    cfg = {"model": {"hidden_size": 16}}
    ctx.config_path = "dummy_config.yaml"
    cli_utils.write_run_manifest(ctx, cfg)

    manifest_path = Path(ctx.run_dir) / "run_manifest.yaml"
    assert manifest_path.exists(), "Condition must be true"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["context"]["seed"] == 42, "Data must not be empty"
    assert data["config"]["model"]["hidden_size"] == 16, "Data must not be empty"

    index_path = Path(ctx.run_dir).parent.parent / "runs_index.txt"
    assert index_path.exists(), "Condition must be true"
    idx_line = index_path.read_text(encoding="utf-8").strip()
    assert "train" in idx_line, "Condition must be true"
    assert "seed42" in idx_line, "Condition must be true"
