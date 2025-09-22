"""Typer-based tests for the codex_ml.plugins CLI commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pytest

pytest.importorskip("typer")
from typer.testing import CliRunner

from codex_ml.cli import plugins_cli

pytestmark = pytest.mark.not_slow


@dataclass
class _RegistryItem:
    """Simple container mimicking registry metadata entries."""

    obj: Callable[..., object]
    description: str = "Demo plugin"


class _DummyRegistry:
    """Minimal stand-in for the registry interface consumed by the CLI."""

    def __init__(self, item: _RegistryItem) -> None:
        self._item = item

    def names(self) -> tuple[str, ...]:
        return ("demo_plugin",)

    def get(self, name: str) -> _RegistryItem | None:
        if name == "demo_plugin":
            return self._item
        return None

    def load_from_entry_points(
        self, group: str, require_api: str | None = None
    ) -> tuple[dict[str, _RegistryItem], dict[str, str]]:
        return {"demo_plugin": self._item}, {}


def demo_plugin(multiplier: int = 2) -> int:
    """Return a predictable value so CLI output stays deterministic."""

    return multiplier * 2


@pytest.fixture()
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def stubbed_registry(monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    registry = _DummyRegistry(_RegistryItem(obj=demo_plugin))
    monkeypatch.setattr(plugins_cli, "_GROUPS", {"demo": registry})
    return "demo", "demo_plugin"


def test_list_displays_stubbed_plugin(
    cli_runner: CliRunner, stubbed_registry: tuple[str, str]
) -> None:
    group, plugin = stubbed_registry

    result = cli_runner.invoke(plugins_cli.app, ["list", group])

    assert result.exit_code == 0
    assert plugin in result.stdout


def test_diagnose_reports_registered_count(
    cli_runner: CliRunner, stubbed_registry: tuple[str, str]
) -> None:
    group, _ = stubbed_registry

    result = cli_runner.invoke(plugins_cli.app, ["diagnose", group])

    assert result.exit_code == 0
    assert "registered=1" in result.stdout


def test_explain_outputs_module_and_docstring(
    cli_runner: CliRunner, stubbed_registry: tuple[str, str]
) -> None:
    group, plugin = stubbed_registry

    result = cli_runner.invoke(plugins_cli.app, ["explain", group, plugin])

    assert result.exit_code == 0
    assert "module: tests.test_plugins_cli" in result.stdout
    assert "Return a predictable value" in result.stdout
    assert "(multiplier: int = 2) -> int" in result.stdout


def test_diagnose_entry_point_mode(
    cli_runner: CliRunner, stubbed_registry: tuple[str, str]
) -> None:
    group, _ = stubbed_registry

    result = cli_runner.invoke(plugins_cli.app, ["diagnose", group, "--use-entry-points"])

    assert result.exit_code == 0
    assert "registered=1" in result.stdout


@pytest.mark.usefixtures("stubbed_registry")
def test_unknown_group_exits_with_error(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(plugins_cli.app, ["list", "unknown"])

    assert result.exit_code != 0
    assert "unknown group" in result.stderr or "unknown group" in result.stdout
