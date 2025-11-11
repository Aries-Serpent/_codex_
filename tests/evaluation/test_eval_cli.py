import json
from pathlib import Path
from typer.testing import CliRunner
import torch
import typer
import types

from codex_ml.evaluation import cli as eval_cli


class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = torch.nn.Linear(4, 3)

    def forward(self, x):
        return self.lin(x)


class DummyLogger:
    def __init__(self, path: Path):
        self.path = path
        self.fh = open(self.path, "a", encoding="utf-8")

    def log(self, record):
        self.fh.write(json.dumps(record) + "\n")
        self.fh.flush()

    def close(self):
        try:
            self.fh.close()
        except Exception:
            pass


def test_run_command_json_output(tmp_path: Path, monkeypatch):
    runner = CliRunner()

    # Prepare dummy config injected via _load_config
    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(6, 4)
    targets = torch.randint(0, 3, (6,))

    cfg = {
        "_model_obj": model,
        "_eval_dataloader": list(zip(inputs, targets)),
        "_criterion": criterion,
        "evaluation": {"metrics": {}},
        "logging": {"mlflow": False},
        "seed": 42,
    }

    def fake_load_config(path: Path):
        return cfg

    # Patch logger builder to write under tmp_path
    def fake_build_loggers(opts):
        return [DummyLogger(tmp_path / "metrics.ndjson")]

    monkeypatch.setattr(eval_cli, "_load_config", fake_load_config)
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    # Lazy import location for build_loggers in the function body, patch target module
    import codex_ml.evaluation.loop as loop_mod
    import codex_ml.logging.registry as reg_mod  # for type lint
    monkeypatch.setattr("codex_ml.evaluation.cli.build_loggers", fake_build_loggers, raising=True)

    result = runner.invoke(
        eval_cli.app,
        ["run", "--config", str(tmp_path / "fake.json"), "--json", "--device", "cpu"],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert "loss" in data and "count" in data and "metrics" in data

    # Ensure NDJSON log file was written
    ndjson_file = tmp_path / "metrics.ndjson"
    assert ndjson_file.exists()
    lines = [json.loads(l) for l in ndjson_file.read_text().splitlines() if l.strip()]
    assert any(rec.get("type") == "epoch" for rec in lines)


def test_report_command_and_compare(tmp_path: Path):
    runner = CliRunner()
    nd1 = tmp_path / "m1.ndjson"
    nd2 = tmp_path / "m2.ndjson"

    epoch1 = {
        "type": "epoch",
        "loss": 1.0,
        "count": 6,
        "metrics": {"acc": 0.5},
        "batches": 2,
        "duration_sec": 0.01,
    }
    epoch2 = dict(epoch1)

    nd1.write_text(json.dumps(epoch1) + "\n")
    nd2.write_text(json.dumps(epoch2) + "\n")

    # Report without compare
    r1 = runner.invoke(eval_cli.app, ["report", "--input", str(nd1), "--json"])
    assert r1.exit_code == 0, r1.stdout
    out = json.loads(r1.stdout)
    assert out["loss"] == 1.0 and out["count"] == 6

    # Report with compare that matches
    r2 = runner.invoke(
        eval_cli.app, ["report", "--input", str(nd1), "--compare", str(nd2), "--json"]
    )
    assert r2.exit_code == 0, r2.stdout
    out2 = json.loads(r2.stdout)
    assert out2.get("determinism_match") is True

    # Now change m2 to force mismatch
    epoch2["loss"] = 0.9
    nd2.write_text(json.dumps(epoch2) + "\n")
    r3 = runner.invoke(
        eval_cli.app, ["report", "--input", str(nd1), "--compare", str(nd2)]
    )
    assert r3.exit_code == 4
    assert "Determinism mismatch" in r3.stderr or "Determinism mismatch" in r3.stdout


def test_run_command_invalid_config(tmp_path: Path, monkeypatch):
    runner = CliRunner()
    def fake_load_config(path: Path):
        return {}  # Missing required injected objects
    monkeypatch.setattr(eval_cli, "_load_config", fake_load_config)
    res = runner.invoke(eval_cli.app, ["run", "--config", str(tmp_path / "fake.json")])
    assert res.exit_code == 2
    assert "Config must inject" in res.stdout


def test_load_config_toml(tmp_path: Path):
    """Test that _load_config handles TOML files with proper tomllib/tomli fallback (P1 fix)"""
    toml_config = tmp_path / "test.toml"
    toml_config.write_text("""
[model]
name = "test_model"

[data]
dataset = "test_data"
""")
    
    # Should not raise ModuleNotFoundError on Python <3.11
    cfg = eval_cli._load_config(toml_config)
    assert cfg["model"]["name"] == "test_model"
    assert cfg["data"]["dataset"] == "test_data"


def test_load_config_json(tmp_path: Path):
    """Test that _load_config handles JSON files correctly"""
    json_config = tmp_path / "test.json"
    json_config.write_text('{"model": {"name": "test"}, "data": {"dataset": "test"}}')
    
    cfg = eval_cli._load_config(json_config)
    assert cfg["model"]["name"] == "test"
    assert cfg["data"]["dataset"] == "test"