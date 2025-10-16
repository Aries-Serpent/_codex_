import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner
from typer.testing import CliRunner as TyperCliRunner

cli_module = importlib.import_module("codex.cli")
from codex_cli.app import app as codex_cli_app


@pytest.mark.parametrize(
    ("command", "expected_subcommands"),
    [
        (cli_module.cli, {"logs", "run", "tasks"}),
        (cli_module.logs, {"init", "ingest", "query"}),
        (cli_module.tokenizer_group, {"encode", "decode", "stats"}),
        (cli_module.repro_group, {"seed", "env", "system"}),
    ],
)
def test_cli_groups_list_subcommands(command, expected_subcommands) -> None:
    runner = CliRunner()
    result = runner.invoke(command, [])
    assert result.exit_code == 0
    assert "Available subcommands:" in result.output
    assert "Use '<command> --help'" in result.output
    if command.help:
        first_line = command.help.strip().splitlines()[0]
        assert first_line in result.output
    for name in expected_subcommands:
        assert name in result.output


@pytest.mark.parametrize(
    "command",
    [
        cli_module.cli,
        cli_module.logs,
        cli_module.tokenizer_group,
        cli_module.repro_group,
    ],
)
def test_cli_groups_invalid_subcommand(command) -> None:
    runner = CliRunner()
    result = runner.invoke(command, ["__missing__"])
    assert result.exit_code != 0
    assert "No such command" in result.output


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["--help"])
    assert result.exit_code == 0
    assert "Codex CLI entry point" in result.output
    assert "Typer" in result.output


def test_cli_default_mentions_typer_bridge() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, [])
    assert result.exit_code == 0
    assert "Typer" in result.output


def test_logs_group_mentions_logging_scripts() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["logs"])
    assert result.exit_code == 0
    assert "Typer-based logging" in result.output


def test_cli_list_tasks() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["tasks"])
    assert result.exit_code == 0
    out = {line.split(":")[0].strip().lstrip("- ") for line in result.output.strip().splitlines()}
    assert "ingest" in out
    assert "pool-fix" in out


def test_cli_run_invalid() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["run", "invalid_task"])
    assert result.exit_code != 0
    assert "not allowed" in result.output


def test_cli_run_valid() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        data_dir = Path("data")
        data_dir.mkdir()
        (data_dir / "example.jsonl").write_text("{}", encoding="utf-8")
        result = runner.invoke(cli_module.cli, ["run", "ingest"])
        assert result.exit_code == 0
        assert "Ingested" in result.output


def test_cli_module_run_ingest(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "example.jsonl").write_text("{}", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent / "src")
    result = subprocess.run(
        [sys.executable, "-m", "codex.cli", "run", "ingest"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    out_file = data_dir / "ingested.jsonl"
    assert out_file.exists()
    assert "Ingested" in result.stdout


def test_fix_pool_executor_created() -> None:
    import concurrent.futures as cf

    from codex.cli import _fix_pool

    try:
        _fix_pool(max_workers=2)
        executor = getattr(cf, "_executor", None)
        assert isinstance(executor, cf.ThreadPoolExecutor)
        assert executor._max_workers == 2
        fut = executor.submit(lambda: 42)
        assert fut.result() == 42
    finally:
        executor = getattr(cf, "_executor", None)
        if executor is not None:
            executor.shutdown(wait=True)
            cf._executor = None


def test_fix_pool_missing_cf(monkeypatch) -> None:
    import builtins

    from codex.cli import _fix_pool

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[override]
        if name == "concurrent.futures":
            raise ImportError("no concurrent.futures")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    # Should not raise even if concurrent.futures is unavailable
    _fix_pool(max_workers=1)



def test_typer_cli_help() -> None:
    runner = TyperCliRunner()
    result = runner.invoke(codex_cli_app, ["--help"])
    assert result.exit_code == 0
    assert "Codex CLI" in result.stdout


def test_typer_cli_track_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("mlflow", reason="mlflow not installed")
    target = tmp_path / "mlruns"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"file:{target}")
    runner = TyperCliRunner()
    result = runner.invoke(codex_cli_app, ["track-smoke", "--dir", str(target)])
    assert result.exit_code == 0
    assert "OK: tracking to" in result.stdout


def test_typer_cli_split_and_checkpoint_smoke(tmp_path: Path) -> None:
    pytest.importorskip("torch", reason="torch not installed")
    runner = TyperCliRunner()
    split = runner.invoke(codex_cli_app, ["split-smoke", "--seed", "42"])
    assert split.exit_code == 0
    out_dir = tmp_path / ".checkpoints"
    ckpt = runner.invoke(codex_cli_app, ["checkpoint-smoke", "--out", str(out_dir)])
    assert ckpt.exit_code == 0
    assert any(out_dir.glob("epoch*-metric*.pt"))
