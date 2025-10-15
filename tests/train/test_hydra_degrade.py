from __future__ import annotations

import codex_ml.cli.hydra_main as hydra_main


def test_hydra_missing_module_degrades(monkeypatch, capsys):
    monkeypatch.setattr(hydra_main, "hydra", None, raising=False)
    monkeypatch.setattr(hydra_main, "_hydra_entry", None, raising=False)
    rc = hydra_main.main([])
    assert rc == 0
    captured = capsys.readouterr()
    assert "hydra-core is required" in captured.err
