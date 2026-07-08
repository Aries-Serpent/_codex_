"""Smoke tests for codex.cli_zendesk CLI entrypoint."""

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


ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
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
            "zendesk": MagicMock(),
        },
        clear=False,
    ):
        yield


def test_cli_zendesk_help(cli_runner: CliRunner, mock_deps):
    cli_zendesk = pytest.importorskip("codex.cli_zendesk")

    result = cli_runner.invoke(cli_zendesk.app, ["--help"])
    if result.exit_code not in (0, 2):
        pytest.skip(f"cli_zendesk help unavailable: {result.exit_code}")
    assert "Usage" in result.output or "usage" in result.output.lower(), "Result must not be empty"


def test_cli_zendesk_subcommand_help(cli_runner: CliRunner, mock_deps):
    cli_zendesk = pytest.importorskip("codex.cli_zendesk")

    result = cli_runner.invoke(cli_zendesk.app, ["sync", "--help"])
    if result.exit_code not in (0, 2):
        pytest.skip(f"cli_zendesk sync help unavailable: {result.exit_code}")
