"""
Test Cli Logging Integration

Test module for cli logging integration.
"""

import json
from pathlib import Path

import torch
from codex_ml.evaluation import cli as eval_cli
from typer.testing import CliRunner


class NoopLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.write_text("")  # create

    def log(self, record):
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    def close(self):
        pass


def test_cli_uses_logger(tmp_path, monkeypatch):
    runner = CliRunner()
    # minimal injected config
    model = torch.nn.Linear(4, 3)
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(4, 4)
    targets = torch.randint(0, 3, (4,))
    cfg = {
        "_model_obj": model,
        "_eval_dataloader": list(zip(inputs, targets)),
        "_criterion": criterion,
        "evaluation": {"metrics": {}},
        "logging": {"mlflow": False},
    }
    monkeypatch.setattr(eval_cli, "_load_config", lambda _: cfg)
    monkeypatch.setattr(
        "codex_ml.evaluation.cli.build_loggers", lambda opts: [NoopLogger(tmp_path / "m.ndjson")]
    )
    res = runner.invoke(eval_cli.app, ["run", "--config", str(tmp_path / "fake.json")])
    assert res.exit_code == 0
    assert (tmp_path / "m.ndjson").exists()
    lines = (tmp_path / "m.ndjson").read_text().strip().splitlines()
    assert any(json.loads(l).get("type") == "epoch" for l in lines)
