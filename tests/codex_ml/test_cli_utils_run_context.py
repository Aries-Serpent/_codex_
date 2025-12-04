from pathlib import Path
import yaml

from codex_ml.cli import utils as cli_utils


def test_create_run_dir_and_manifest(tmp_path: Path):
    base_dir = tmp_path / "runs"
    ctx = cli_utils.create_run_dir(base_dir, mode="train", seed=42)
    assert "seed42" in ctx.run_id
    assert Path(ctx.run_dir).exists()

    cfg = {"model": {"hidden_size": 16}}
    ctx.config_path = "dummy_config.yaml"
    cli_utils.write_run_manifest(ctx, cfg)

    manifest_path = Path(ctx.run_dir) / "run_manifest.yaml"
    assert manifest_path.exists()
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["context"]["seed"] == 42
    assert data["config"]["model"]["hidden_size"] == 16

    index_path = Path(ctx.run_dir).parent.parent / "runs_index.txt"
    assert index_path.exists()
    idx_line = index_path.read_text(encoding="utf-8").strip()
    assert "train" in idx_line
    assert "seed42" in idx_line
