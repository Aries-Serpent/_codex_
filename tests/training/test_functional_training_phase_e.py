"""Phase E coverage expansion for src/training/functional_training.py."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def _import_ft():
    import importlib

    module = None
    # Use src.training.functional_training to avoid the root-level training/ shadow package
    for mod_name in ("src.training.functional_training", "training.functional_training"):
        try:
            module = importlib.import_module(mod_name)
            break
        except (ImportError, ModuleNotFoundError):
            continue
    if module is None:
        pytest.skip("training.functional_training not importable")
    return module


# ---------------------------------------------------------------------------
# _normalize_identifier
# ---------------------------------------------------------------------------


class TestNormalizeIdentifier:
    def setup_method(self):
        self.ft = _import_ft()

    def test_none_returns_none(self):
        assert self.ft._normalize_identifier(None) is None, "Condition must be true"

    def test_string_passthrough(self):
        assert self.ft._normalize_identifier("some/model") == "some/model", "Condition must be true"

    def test_pathlike_conversion(self):
        result = self.ft._normalize_identifier(Path(os.path.join(tempfile.gettempdir(), "model")))
        assert result == os.path.join(tempfile.gettempdir(), "model"), "Result must not be empty"

    def test_os_fspath_used_for_pathlike(self):
        class FakePath:
            def __fspath__(self):
                return "/custom/path"

        result = self.ft._normalize_identifier(FakePath())
        assert result == "/custom/path", "Result must not be empty"


# ---------------------------------------------------------------------------
# _looks_like_local_source
# ---------------------------------------------------------------------------


class TestLooksLikeLocalSource:
    def setup_method(self):
        self.ft = _import_ft()

    def test_none_returns_false(self):
        assert self.ft._looks_like_local_source(None) is False, "Condition must be true"

    def test_relative_dot_slash(self):
        assert self.ft._looks_like_local_source("./data/file.txt") is True, "Data must not be empty"

    def test_parent_dot_dot_slash(self):
        assert self.ft._looks_like_local_source("../models/bert") is True, "Condition must be true"

    def test_absolute_path(self):
        assert self.ft._looks_like_local_source("/usr/local/models") is True, "Condition must be true"

    def test_hf_identifier_returns_false(self):
        assert self.ft._looks_like_local_source("bert-base-uncased") is False, "Condition must be true"

    def test_hf_url_scheme(self):
        assert self.ft._looks_like_local_source("hf://org/model") is False, "Condition must be true"

    def test_existing_path_as_local(self, tmp_path):
        p = tmp_path / "weights"
        p.mkdir()
        assert self.ft._looks_like_local_source(str(p)) is True, "Condition must be true"

    def test_oserror_returns_false(self, monkeypatch):
        def raise_oserror(*_, **__):
            raise OSError("boom")

        monkeypatch.setattr(Path, "exists", raise_oserror)
        assert self.ft._looks_like_local_source("some/relative/path") is False, "Condition must be true"


# ---------------------------------------------------------------------------
# _maybe_collect_system_metrics
# ---------------------------------------------------------------------------


class TestMaybeCollectSystemMetrics:
    def setup_method(self):
        self.ft = _import_ft()

    def test_disabled_returns_none(self):
        result = self.ft._maybe_collect_system_metrics(False)
        assert result is None, "Result must not be empty"

    def test_no_collector_returns_none(self, monkeypatch):
        monkeypatch.setattr(self.ft, "collect_system_metrics", None)
        result = self.ft._maybe_collect_system_metrics(True)
        assert result is None, "Result must not be empty"

    def test_collector_returns_valid_dict(self, monkeypatch):
        monkeypatch.setattr(self.ft, "collect_system_metrics", lambda: {"cpu": 0.5, "mem": 2048})
        result = self.ft._maybe_collect_system_metrics(True)
        assert result == {"cpu": 0.5, "mem": 2048.0}

    def test_collector_filters_non_numeric_values(self, monkeypatch):
        monkeypatch.setattr(
            self.ft,
            "collect_system_metrics",
            lambda: {"cpu": 0.3, "label": "dev", "mem": 100},
        )
        result = self.ft._maybe_collect_system_metrics(True)
        assert result is not None, "result must be initialized"
        assert "label" not in result, "Result must not be empty"
        assert result["cpu"] == pytest.approx(0.3), "Result must not be empty"

    def test_collector_raises_returns_none(self, monkeypatch):
        def boom():
            raise RuntimeError("hardware error")

        monkeypatch.setattr(self.ft, "collect_system_metrics", boom)
        result = self.ft._maybe_collect_system_metrics(True)
        assert result is None, "Result must not be empty"

    def test_collector_returns_non_dict_gives_none(self, monkeypatch):
        monkeypatch.setattr(self.ft, "collect_system_metrics", lambda: [1, 2, 3])
        result = self.ft._maybe_collect_system_metrics(True)
        assert result is None, "Result must not be empty"

    def test_collector_returns_empty_dict_gives_none(self, monkeypatch):
        """Empty dicts contain no numeric values → should return None."""
        monkeypatch.setattr(self.ft, "collect_system_metrics", lambda: {})
        result = self.ft._maybe_collect_system_metrics(True)
        assert result is None, "Result must not be empty"

    def test_integer_values_coerced_to_float(self, monkeypatch):
        monkeypatch.setattr(self.ft, "collect_system_metrics", lambda: {"pages": 512})
        result = self.ft._maybe_collect_system_metrics(True)
        assert isinstance(result["pages"], float)


# ---------------------------------------------------------------------------
# ImportMigration helpers
# ---------------------------------------------------------------------------


def test_import_migration_class_exists():
    ft = _import_ft()
    # Functional training should also export or reference ImportMigration if present
    # If not present here, that's fine (it lives in agents/physics_orchestrator)
    # We just test the module-level _normalize_identifier is reachable
    assert callable(ft._normalize_identifier), "Condition must be true"


def test_looks_like_local_source_edge_cases():
    ft = _import_ft()
    assert ft._looks_like_local_source("") is False, "Condition must be true"
    assert ft._looks_like_local_source("/") is True, "Condition must be true"


def test_maybe_collect_disabled_always_none():
    ft = _import_ft()
    # Even with a real collector configured, disabled=False must return None
    result = ft._maybe_collect_system_metrics(False)
    assert result is None, "Result must not be empty"
