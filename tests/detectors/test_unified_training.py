from __future__ import annotations

import sys
import types

from codex_ml.detectors.unified_training import detect


def test_unified_training_detector_missing_module(monkeypatch):
    monkeypatch.setitem(sys.modules, "codex_ml.training.unified_training", None)

    def fake_import(name):
        raise ModuleNotFoundError(name)

    monkeypatch.setattr("codex_ml.detectors.unified_training.import_module", fake_import)
    res = detect(None)
    assert res.detector == "unified_training" and res.score in (0.0, 0.5)
    assert any(f.name == "module.import" and not f.passed for f in res.findings)


def test_unified_training_detector_symbols_present(monkeypatch):
    m = types.SimpleNamespace(train=lambda *a, **k: None, resume=lambda *a, **k: None)
    # ensure parent package path exists in sys.modules
    pkg = types.ModuleType("codex_ml")
    sys.modules.setdefault("codex_ml", pkg)
    subpkg = types.ModuleType("codex_ml.training")
    sys.modules.setdefault("codex_ml.training", subpkg)
    sys.modules["codex_ml.training.unified_training"] = m
    res = detect(None)
    assert res.score == 1.0
    assert any(f.name == "symbol.train" and f.passed for f in res.findings)
    assert any(f.name == "symbol.resume" and f.passed for f in res.findings)
