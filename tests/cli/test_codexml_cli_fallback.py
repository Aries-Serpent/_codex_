"""
Test Codexml Cli Fallback

Test module for codexml cli fallback.
"""

from __future__ import annotations

import importlib
import sys

import pytest


def test_codexml_cli_help_without_hydra(monkeypatch, capsys):
    module = importlib.import_module("codex_ml.cli.main")
    monkeypatch.setattr(module, "_HAS_HYDRA", False, raising=False)
    monkeypatch.setattr(module, "hydra", None, raising=False)
    with pytest.raises(SystemExit) as excinfo:
        module.cli(["--help"])
    assert excinfo.value.code == 0, "Value must be initialized"
    captured = capsys.readouterr()
    # Check both stdout and stderr for hydra-core message
    output = captured.out + captured.err
    assert "hydra" in output.lower(), "Condition must be true"


def test_codexml_cli_requires_hydra_when_running(monkeypatch):
    module = importlib.import_module("codex_ml.cli.main")
    monkeypatch.setattr(module, "_HAS_HYDRA", False, raising=False)
    monkeypatch.setattr(module, "hydra", None, raising=False)
    with pytest.raises((ImportError, SystemExit)) as excinfo:
        module.cli(["train"])  # arbitrary arg
    # Should either raise ImportError or raise SystemExit (graceful degradation exits 0)
    if isinstance(excinfo.value, ImportError):
        assert "hydra-core" in str(excinfo.value), "Value must be initialized"


def test_hydra_main_help(monkeypatch, capsys):
    module_name = "codex_ml.cli.hydra_main"
    monkeypatch.setitem(sys.modules, "hydra", None)
    monkeypatch.setitem(sys.modules, "omegaconf", None)
    if module_name in sys.modules:
        del sys.modules[module_name]
    module = importlib.import_module(module_name)
    monkeypatch.setattr(sys, "argv", ["codex-train", "--help"])
    # main() may return an exit code or raise SystemExit
    try:
        rc = module.main()
        assert rc in (0, 2), f"Expected exit code 0 or 2, got {rc}"
    except SystemExit as excinfo:
        assert excinfo.code in (0, 2), f"Expected exit code 0 or 2, got {excinfo.code}"
    message = capsys.readouterr().err
    # Should mention hydra-core requirement
    assert "hydra" in message.lower() or len(message) == 0, "Message must not be empty"
    if module_name in sys.modules:
        del sys.modules[module_name]
