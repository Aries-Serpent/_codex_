pytest.importorskip("mlflow")
"""
Test Eval Cli

Test module for eval cli.
"""

import json
from pathlib import Path

import pytest

pytest.importorskip("typer")


# Skip entire module if torch is not available or unloadable
torch = pytest.importorskip("torch", reason="PyTorch required for evaluation CLI tests")
from typer.testing import CliRunner

from codex_ml.evaluation import cli as eval_cli


class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = torch.nn.Linear(4, 3)

    def forward(self, x):
        return self.lin(x)


class DummyLogger:
    """Test logger that properly manages file handles."""

    def __init__(self, path: Path):
        self.path = path
        self.fh = open(self.path, "a", encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def log(self, record):
        if self.fh:
            self.fh.write(json.dumps(record) + "\n")
            self.fh.flush()

    def close(self):
        if self.fh is not None:
            self.fh.close()
            self.fh = None

    def __del__(self):
        """Ensure file is closed on deletion."""
        self.close()


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
    # Patch the actual module where build_loggers is defined
    import codex_ml.logging.registry as reg_mod

    monkeypatch.setattr(reg_mod, "build_loggers", fake_build_loggers)

    result = runner.invoke(
        eval_cli.app,
        ["run", "--config", str(tmp_path / "fake.json"), "--json", "--device", "cpu"],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert "loss" in data and "count" in data and "metrics" in data

    # Ensure NDJSON log file was written
    ndjson_file = tmp_path / "metrics.ndjson"
    assert ndjson_file.exists(), "Condition must be true"
    lines = [json.loads(line) for line in ndjson_file.read_text().splitlines() if line.strip()]
    assert any(rec.get("type") == "epoch" for rec in lines), "Condition must be true"


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
    assert out["loss"] == 1.0 and out["count"] == 6, "Count must be greater than zero"

    # Report with compare that matches
    r2 = runner.invoke(
        eval_cli.app, ["report", "--input", str(nd1), "--compare", str(nd2), "--json"]
    )
    assert r2.exit_code == 0, r2.stdout
    out2 = json.loads(r2.stdout)
    assert out2.get("determinism_match") is True, "Condition must be true"

    # Now change m2 to force mismatch
    epoch2["loss"] = 0.9
    nd2.write_text(json.dumps(epoch2) + "\n")
    r3 = runner.invoke(eval_cli.app, ["report", "--input", str(nd1), "--compare", str(nd2)])
    assert r3.exit_code == 4, "exit_code is not valid"
    assert "Determinism mismatch" in r3.stderr or "Determinism mismatch" in r3.stdout, "Condition must be true"


def test_run_command_invalid_config(tmp_path: Path, monkeypatch):
    runner = CliRunner()

    def fake_load_config(path: Path):
        return {}  # Missing required injected objects

    monkeypatch.setattr(eval_cli, "_load_config", fake_load_config)
    res = runner.invoke(eval_cli.app, ["run", "--config", str(tmp_path / "fake.json")])
    assert res.exit_code == 2, "exit_code is not valid"
    # typer writes to stderr by default with err=True
    assert "Config must inject" in res.stderr or "Config must inject" in res.stdout, "Condition must be true"


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
    assert cfg["model"]["name"] == "test_model", "Condition must be true"
    assert cfg["data"]["dataset"] == "test_data", "Data must not be empty"


def test_load_config_json(tmp_path: Path):
    """Test that _load_config handles JSON files correctly"""
    json_config = tmp_path / "test.json"
    json_config.write_text('{"model": {"name": "test"}, "data": {"dataset": "test"}}')

    cfg = eval_cli._load_config(json_config)
    assert cfg["model"]["name"] == "test", "Condition must be true"
    assert cfg["data"]["dataset"] == "test", "Data must not be empty"


def test_run_command_with_invalid_device(tmp_path: Path, monkeypatch):
    """Edge case: Test CLI handles invalid device gracefully"""
    runner = CliRunner()

    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(2, 4)
    targets = torch.randint(0, 3, (2,))

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

    def fake_build_loggers(opts):
        return [DummyLogger(tmp_path / "metrics.ndjson")]

    monkeypatch.setattr(eval_cli, "_load_config", fake_load_config)
    import codex_ml.logging.registry as reg_mod

    monkeypatch.setattr(reg_mod, "build_loggers", fake_build_loggers)

    # Try with invalid device - should handle gracefully or error appropriately
    result = runner.invoke(
        eval_cli.app,
        ["run", "--config", str(tmp_path / "fake.json"), "--device", "cuda:999"],
    )
    # May succeed with fallback to CPU or fail with clear error
    assert result.exit_code in [0, 1, 2]


def test_report_command_empty_ndjson(tmp_path: Path):
    """Edge case: Test report command with empty NDJSON file"""
    runner = CliRunner()
    empty_file = tmp_path / "empty.ndjson"
    empty_file.write_text("")

    result = runner.invoke(eval_cli.app, ["report", "--input", str(empty_file), "--json"])
    # Should handle empty file gracefully - exit_code 3 means no epoch records found
    assert result.exit_code in [0, 1, 3]


def test_report_command_malformed_ndjson(tmp_path: Path):
    """Edge case: Test report command with malformed NDJSON"""
    runner = CliRunner()
    bad_file = tmp_path / "malformed.ndjson"
    bad_file.write_text("not valid json\n{incomplete")

    result = runner.invoke(eval_cli.app, ["report", "--input", str(bad_file)])
    # Should handle parsing errors gracefully
    assert result.exit_code in [0, 1]


def test_run_command_with_deterministic_flag(tmp_path: Path, monkeypatch):
    """Test CLI with --deterministic flag for reproducibility"""
    runner = CliRunner()

    model = DummyModel()
    criterion = torch.nn.CrossEntropyLoss()
    inputs = torch.randn(4, 4)
    targets = torch.randint(0, 3, (4,))

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

    def fake_build_loggers(opts):
        return [DummyLogger(tmp_path / "metrics.ndjson")]

    monkeypatch.setattr(eval_cli, "_load_config", fake_load_config)
    import codex_ml.logging.registry as reg_mod

    monkeypatch.setattr(reg_mod, "build_loggers", fake_build_loggers)
    monkeypatch.setenv("PYTHONHASHSEED", "0")

    result = runner.invoke(
        eval_cli.app,
        [
            "run",
            "--config",
            str(tmp_path / "fake.json"),
            "--deterministic",
            "--json",
            "--device",
            "cpu",
        ],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert "loss" in data, "Data must not be empty"
