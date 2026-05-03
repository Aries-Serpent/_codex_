"""Tests for the codex_ml.plugins CLI module."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

pytest.importorskip("typer")
from typer.testing import CliRunner

from codex_ml.cli import plugins_cli
from codex_ml.plugins.registry import Registry


class DummyRegistry(Registry):
    """Registry subclass that captures entry-point loading calls."""

    def __init__(self, kind: str, load_result: tuple[int, dict[str, str]] = (0, {})) -> None:
        super().__init__(kind)
        self._load_result = load_result
        self.load_calls: list[tuple[str, str]] = []

    def load_from_entry_points(self, group: str, require_api: str = "v1"):
        self.load_calls.append((group, require_api))
        return self._load_result


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def plugin_environment(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    tokenizers = DummyRegistry("tokenizers", load_result=(0, {"broken": "boom"}))

    @tokenizers.register("alpha")
    def alpha_plugin():
        """Alpha test plugin."""
        return "alpha"

    @tokenizers.register("beta")
    class BetaPlugin:
        """Beta class plugin."""

    models = DummyRegistry("models")

    @models.register("fancy")
    def fancy_model(value: int, factor: float = 1.0) -> float:
        """Fancy model plugin for explain coverage."""
        return value * factor

    monkeypatch.setattr(
        plugins_cli,
        "_GROUPS",
        {"tokenizers": tokenizers, "models": models},
    )
    return SimpleNamespace(tokenizers=tokenizers, models=models, fancy_model=fancy_model)


def test_list_command_prints_registered_names(
    runner: CliRunner, plugin_environment: SimpleNamespace
) -> None:
    result = runner.invoke(plugins_cli.app, ["list", "tokenizers"])

    assert result.exit_code == 0
    assert "alpha" in result.stdout
    assert "beta" in result.stdout


def test_diagnose_command_reports_entry_point_errors(
    runner: CliRunner, plugin_environment: SimpleNamespace
) -> None:
    result = runner.invoke(
        plugins_cli.app,
        ["diagnose", "tokenizers", "--use-entry-points"],
    )

    assert result.exit_code == 0
    assert "registered=2" in result.stdout
    assert "broken: boom" in result.stdout
    assert plugin_environment.tokenizers.load_calls == [("codex_ml.tokenizers", "v1")]


def test_explain_command_prints_plugin_metadata(
    runner: CliRunner, plugin_environment: SimpleNamespace
) -> None:
    result = runner.invoke(plugins_cli.app, ["explain", "models", "fancy"])

    assert result.exit_code == 0
    assert f"module: {plugin_environment.fancy_model.__module__}" in result.stdout
    assert "Fancy model plugin for explain coverage." in result.stdout
    assert "(value: int, factor: float = 1.0) -> float" in result.stdout


def test_explain_command_exits_non_zero_for_missing_plugin(
    runner: CliRunner, plugin_environment: SimpleNamespace
) -> None:
    result = runner.invoke(plugins_cli.app, ["explain", "models", "missing"])

    assert result.exit_code == 1
