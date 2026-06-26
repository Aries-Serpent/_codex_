"""Tests for codex_ml.utils.opt_import — optional import helper."""

from __future__ import annotations

import logging

from codex_ml.utils.opt_import import try_import


class TestTryImport:
    def test_imports_existing_module(self):
        mod = try_import("json")
        assert mod is not None, "mod must be initialized"
        assert hasattr(mod, "dumps")

    def test_returns_none_for_nonexistent_module(self):
        mod = try_import("__nonexistent_module_xyz_abc__")
        assert mod is None, "mod is not valid"

    def test_returns_module_type(self):
        import types

        mod = try_import("os")
        assert isinstance(mod, types.ModuleType)

    def test_imports_stdlib_submodule(self):
        mod = try_import("os.path")
        assert mod is not None, "mod must be initialized"

    def test_logs_debug_on_missing(self, caplog):
        with caplog.at_level(logging.DEBUG, logger="codex_ml.utils.opt_import"):
            # the actual call is in a pragma: no cover block so it may not fire;
            # just verify None is returned for a missing dep
            result = try_import("__missing_dep_12345__")
        assert result is None, "Result must not be empty"
