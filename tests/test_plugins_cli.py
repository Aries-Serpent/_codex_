"""Smoke tests for the codex_ml.plugins CLI commands."""

from __future__ import annotations

import contextlib
from collections.abc import Iterator

import pytest

pytest.importorskip("typer")

from typer.testing import CliRunner

from codex_ml.cli import plugins_cli
from codex_ml.plugins import registries


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def isolate_plugin_registries() -> Iterator[None]:
    """Reset plugin registries so tests can freely register temporary plugins."""

    groups = dict(plugins_cli._GROUPS)
    snapshots = {name: reg._items.copy() for name, reg in groups.items()}
    try:
        yield
    finally:
        for name, reg in groups.items():
            reg._items = snapshots[name]


@pytest.fixture()
def temporary_model_plugin(isolate_plugin_registries: None) -> Iterator[str]:
    """Register a simple model plugin for exercising CLI commands."""

    @registries.models.register("Example_Model", description="example")
    def _model_plugin(multiplier: int = 2) -> int:
        """Return a predictable integer so diagnostics can inspect it."""

        return multiplier * 2

    yield "example_model"

    # Ensure the registry is cleaned up even if a test fails early.
    with contextlib.suppress(KeyError):
        del registries.models._items["example_model"]


def test_list_command_shows_registered_plugin(
    cli_runner: CliRunner, temporary_model_plugin: str
) -> None:
    result = cli_runner.invoke(plugins_cli.app, ["list", "models"])

    assert result.exit_code == 0
    assert temporary_model_plugin in result.stdout


def test_diagnose_reports_registered_count(
    cli_runner: CliRunner, temporary_model_plugin: str
) -> None:
    result = cli_runner.invoke(plugins_cli.app, ["diagnose", "models"])

    assert result.exit_code == 0
    assert "registered=1" in result.stdout


def test_explain_outputs_module_and_docstring(
    cli_runner: CliRunner, temporary_model_plugin: str
) -> None:
    result = cli_runner.invoke(plugins_cli.app, ["explain", "models", temporary_model_plugin])

    assert result.exit_code == 0
    assert "module: tests.test_plugins_cli" in result.stdout
    assert "Return a predictable integer" in result.stdout
    assert "(multiplier: int = 2) -> int" in result.stdout


def test_unknown_group_exits_with_error(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(plugins_cli.app, ["list", "unknown"])

    assert result.exit_code != 0
    assert "unknown group" in result.stderr or "unknown group" in result.stdout
