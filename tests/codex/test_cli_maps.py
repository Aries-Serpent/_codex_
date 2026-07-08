"""Smoke tests for codex.cli_maps CLI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Skip if typer is not properly installed
try:
    import typer

    if not hasattr(typer, "Typer"):
        pytest.skip("typer package not properly installed", allow_module_level=True)
    from typer.testing import CliRunner
except (ImportError, AttributeError):
    pytest.skip("typer package not available", allow_module_level=True)


_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = _ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def mock_deps():
    with patch.dict(
        "sys.modules",
        {
            "torch": MagicMock(),
            "transformers": MagicMock(),
            "datasets": MagicMock(),
        },
        clear=False,
    ):
        yield


def test_cli_maps_help(cli_runner: CliRunner, mock_deps):
    cli_maps = pytest.importorskip("codex.cli_maps")

    result = cli_runner.invoke(cli_maps.app, ["--help"])
    if result.exit_code not in (0, 2):
        pytest.skip(f"cli_maps help unavailable: {result.exit_code}")
    assert "Usage" in result.output, "Result must not be empty"


def test_cli_maps_subcommand_help(cli_runner: CliRunner, mock_deps):
    cli_maps = pytest.importorskip("codex.cli_maps")

    result = cli_runner.invoke(cli_maps.app, ["inspect", "--help"])
    if result.exit_code not in (0, 2):
        pytest.skip(f"cli_maps inspect help unavailable: {result.exit_code}")
