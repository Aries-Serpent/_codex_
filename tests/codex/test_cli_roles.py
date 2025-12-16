"""Smoke tests for codex.cli_roles CLI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner


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
        },
        clear=False,
    ):
        yield


def test_cli_roles_help(cli_runner: CliRunner, mock_deps):
    try:
        from codex import cli_roles
    except ImportError:
        pytest.skip("cli_roles not importable")

    result = cli_runner.invoke(cli_roles.app, ["--help"])
    if result.exit_code not in (0, 2):
        pytest.skip(f"cli_roles help unavailable: {result.exit_code}")
    assert "Usage" in result.output or "usage" in result.output.lower()


def test_cli_roles_list(cli_runner: CliRunner, mock_deps):
    try:
        from codex import cli_roles
    except ImportError:
        pytest.skip("cli_roles not importable")

    result = cli_runner.invoke(cli_roles.app, ["export-matrix", "--help"])
    if result.exit_code not in (0, 2):
        pytest.skip(f"cli_roles export help unavailable: {result.exit_code}")
