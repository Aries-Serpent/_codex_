import yaml
from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


def test_train_cli_invokes_training(monkeypatch, tmp_path):
    captured = {}

    def fake_run_functional_training(*, config, resume):
        captured["resume"] = resume
        captured["seed"] = getattr(config.training, "seed", None)

    monkeypatch.setattr("codex_ml.training.run_functional_training", fake_run_functional_training)

    config_path = tmp_path / "config.yaml"
    data = {
        "seed": 5,
        "training": {
            "seed": 5,
            "texts": ["hello"],
        },
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
    assert captured["seed"] == 123
