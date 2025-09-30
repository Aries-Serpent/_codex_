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
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "hydra-core" in captured.err


def test_codexml_cli_requires_hydra_when_running(monkeypatch):
    module = importlib.import_module("codex_ml.cli.main")
    monkeypatch.setattr(module, "_HAS_HYDRA", False, raising=False)
    monkeypatch.setattr(module, "hydra", None, raising=False)
    with pytest.raises(ImportError) as excinfo:
        module.cli(["train"])  # arbitrary arg
    assert "hydra-core" in str(excinfo.value)



def test_hydra_main_help(monkeypatch, capsys):
    module_name = "codex_ml.cli.hydra_main"
    monkeypatch.setitem(sys.modules, "hydra", None)
    monkeypatch.setitem(sys.modules, "omegaconf", None)
    if module_name in sys.modules:
        del sys.modules[module_name]
    module = importlib.import_module(module_name)
    monkeypatch.setattr(sys, 'argv', ['codex-train', '--help'])
    with pytest.raises(SystemExit) as excinfo:
        module.main()
    assert excinfo.value.code == 0
    message = capsys.readouterr().err
    assert "hydra-core" in message
    if module_name in sys.modules:
        del sys.modules[module_name]
