import yaml
from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_cli_train_creates_checkpoint(tmp_path):
    dataset_path = tmp_path / "train.jsonl"
    dataset_path.write_text(
        '{"text": "hello world"}\n{"text": "another sample"}\n', encoding="utf-8"
    )
    output_dir = tmp_path / "run"
    cfg_path = tmp_path / "config.yaml"
    cfg = {
        "seed": 7,
        "output_dir": str(output_dir),
        "max_epochs": 2,
        "dataset": {
            "train_path": str(dataset_path),
            "format": "jsonl",
        },
    }
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(codex, ["train", "--config", str(cfg_path)])

    assert result.exit_code == 0, result.output
    assert "Training complete" in result.output

    checkpoint_root = output_dir / "checkpoints"
    assert checkpoint_root.exists()
    epochs = sorted(checkpoint_root.glob("epoch-*"))
    assert epochs, "No checkpoints were generated"
