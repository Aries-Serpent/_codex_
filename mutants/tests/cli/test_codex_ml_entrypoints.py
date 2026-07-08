"""Smoke tests for additional codex_ml CLI entrypoints."""

from __future__ import annotations

import importlib
import importlib.util
import sys
import types
from collections.abc import Callable
from types import SimpleNamespace

import pytest

CLI_MODULES = [
    "codex_ml.cli.tracking_decide",
    "codex_ml.cli.generate",
    "codex_ml.cli.minimal_train",
    "codex_ml.cli.train_minimal",
    "codex_ml.cli.simple_cli",
    "codex_ml.cli.eval_minimal",
    "codex_ml.cli.hydra_entry",
    "codex_ml.cli.codex_env",
    "codex_ml.cli.infer",
    "codex_ml.cli.list_plugins",
    "codex_ml.cli.entrypoints",
    "codex_ml.cli.deploy",
    "codex_ml.cli.migrate_data",
    "codex_ml.cli.checkpoint_validate",
    "codex_ml.cli.detectors",
]


@pytest.fixture(autouse=True)
def stub_optional_deps(monkeypatch):
    """Stub heavy optional dependencies for lightweight CLI imports."""

    class DummyDataset:  # pragma: no cover - compatibility shim
        pass

    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(Dataset=DummyDataset))

    torch_module = types.ModuleType("torch")
    torch_module.__spec__ = importlib.util.spec_from_loader("torch", loader=None)
    monkeypatch.setitem(sys.modules, "torch", torch_module)
    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(
            AutoModelForCausalLM=type("AutoModelForCausalLM", (), {}),
            AutoTokenizer=type("AutoTokenizer", (), {}),
            PreTrainedTokenizerBase=type("PreTrainedTokenizerBase", (), {}),
        ),
    )


@pytest.mark.parametrize("module_name", CLI_MODULES)
def test_cli_modules_importable(module_name):
    """Modules should import without raising to satisfy readiness checks."""

    module = importlib.import_module(module_name)
    assert module is not None, "module must be initialized"


def _maybe_invoke(app_factory: Callable[[], object]) -> None:
    """Invoke Typer app help output if click runner is available."""

    try:
        from typer.testing import CliRunner
    except ImportError:
        pytest.skip("typer not available")

    runner = CliRunner()
    result = runner.invoke(app_factory(), ["--help"])
    assert result.exit_code == 0, "Result must not be empty"
    assert "--help" in result.output, "Result must not be empty"


def test_tracking_decide_cli_help():
    """tracking_decide exposes Typer app when typer is installed."""

    module = importlib.import_module("codex_ml.cli.tracking_decide")
    app = getattr(module, "app", None)
    if app is None:
        pytest.skip("Typer not installed")
    assert hasattr(app, "info")
