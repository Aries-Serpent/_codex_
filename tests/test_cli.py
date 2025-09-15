import importlib
import os
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

cli_module = importlib.import_module("codex.cli")


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["--help"])
    assert result.exit_code == 0
    assert "Codex CLI entry point" in result.output


def test_cli_list_tasks() -> None:
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["tasks"])
    assert result.exit_code == 0
    out = {line.split(":")[0] for line in result.output.strip().splitlines()}
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
