from collections.abc import Mapping

import yaml
from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_train_cli_invokes_training(monkeypatch, tmp_path):
    captured = {}

    def fake_run_functional_training(*, config, resume):
        captured["resume"] = resume
        captured["config"] = config

    monkeypatch.setattr("codex_ml.training.run_functional_training", fake_run_functional_training)

    config_path = tmp_path / "config.yaml"
    data = {
        "training": {
            "seed": 5,
            "dataset": {
                "train_texts": ["hello"],
            },
        }
    }
    with config_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh)

    runner = CliRunner()
    result = runner.invoke(
        codex,
        ["train", "--config", str(config_path), "--resume", "--seed", "123"],
    )

    assert result.exit_code == 0, result.output
    assert captured["resume"] is True

    cfg = captured["config"]
    if hasattr(cfg, "get"):
        seed = cfg.get("seed")
        dataset = cfg.get("dataset")
    else:  # pragma: no cover - defensive fallback for alternate config types
        seed = getattr(cfg, "seed", None)
        dataset = getattr(cfg, "dataset", None)

    assert seed == 123
    if isinstance(dataset, Mapping):
        assert list(dataset.get("train_texts", [])) == ["hello"]
