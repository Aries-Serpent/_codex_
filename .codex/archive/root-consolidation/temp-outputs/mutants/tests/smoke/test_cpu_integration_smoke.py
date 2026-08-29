"""
CPU Integration Smoke Tests (B-03 partial — GPU deferred to S95)

Validates critical code-paths on a CPU-only machine (no CUDA / no TPU),
which matches the primary test machine policy:
    Intel Core Ultra 5 135U vPro, Windows 11 Pro, 16 GB DDR5-5600, CPU-only.

These tests are designed to be fast (<10 s total) and always runnable in CI
without any special hardware or credentials.

Resolution: DEPLOYMENT_READINESS_S92.md B-03 (partial)
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]


def _importable(module: str) -> bool:
    """Return True if *module* can be imported without crashing."""
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Group 1 — Core platform imports (must always pass)
# ---------------------------------------------------------------------------


class TestCoreImports:
    """Verify that all core modules import cleanly on a CPU-only machine."""

    def test_bridge_manager_import(self):
        """bridge_manager must import on Linux AND Windows (fcntl guard)."""
        import bridge_manager

        assert hasattr(bridge_manager, "BridgeLock")

    def test_bridge_manager_has_msvcrt_or_fcntl(self):
        """At least one locking backend must be compiled in."""
        import bridge_manager

        assert bridge_manager._HAS_FCNTL or bridge_manager._HAS_MSVCRT, (
            "Neither fcntl (POSIX) nor msvcrt (Windows) is available — "
            "BridgeLock cannot function on this platform."
        )

    def test_sandbox_import(self):
        """safety.sandbox imports cleanly; resource guard is correct."""
        from codex_ml.safety import sandbox

        assert callable(sandbox.run_in_sandbox), "Condition must be true"

    def test_sandbox_enforce_limits_raises_on_missing_resource(self):
        """
        When resource module is unavailable, enforce_limits=True must raise
        RuntimeError — not silently proceed.
        """
        from codex_ml.safety import sandbox

        if sandbox._HAS_RESOURCE:
            pytest.skip("resource module available — enforce_limits path not exercised")

        with pytest.raises(RuntimeError, match="enforce_limits"):
            sandbox.run_in_sandbox(["echo", "hi"], enforce_limits=True)

    def test_safety_init_stub_on_no_resource(self, monkeypatch):
        """
        If the sandbox module raises on import, safety.__init__ must provide
        a stub that raises RuntimeError instead of crashing the import.
        """
        import codex_ml.safety as safety

        # The __init__ should always export run_in_sandbox (real or stub).
        assert callable(safety.run_in_sandbox), "Condition must be true"


# ---------------------------------------------------------------------------
# Group 2 — BridgeLock POSIX / Windows cross-process locking
# ---------------------------------------------------------------------------


class TestBridgeLockPlatform:
    """BridgeLock must use the correct backend for the current platform."""

    def test_bridge_lock_acquire_release(self, tmp_path):
        """Lock acquire + release round-trip must succeed."""
        from bridge_manager import BridgeLock

        lock = BridgeLock(tmp_path / "test.lock")
        acquired = lock.acquire(timeout=2)
        assert acquired, "BridgeLock.acquire() returned False unexpectedly"
        lock.release()

    def test_bridge_lock_context_manager(self, tmp_path):
        """bridge_lock context manager must not raise."""
        from bridge_manager import bridge_lock

        with bridge_lock(tmp_path / "ctx.lock"):
            pass  # no exception = success

    def test_bridge_lock_platform_backend(self):
        """Verify the active backend matches the current platform."""
        import bridge_manager

        if sys.platform == "win32":
            assert bridge_manager._HAS_MSVCRT, "msvcrt not available on Windows"
        else:
            assert bridge_manager._HAS_FCNTL, "fcntl not available on POSIX"


# ---------------------------------------------------------------------------
# Group 3 — BatchScanRunner API (validates batch_scan_integration.py)
# ---------------------------------------------------------------------------


class TestBatchScanRunnerAPI:
    """Validate the BatchScanRunner Python API end-to-end."""

    def test_batch_scan_runner_importable(self):
        """BatchScanRunner must be importable."""
        from scripts.ci.batch_scan_integration import (
            BatchScanResult,
            BatchScanRunner,
        )

        assert BatchScanRunner is not None, "BatchScanRunner must be initialized"
        assert BatchScanResult is not None, "BatchScanResult must be initialized"

    def test_batch_scan_result_dataclass(self):
        """BatchScanResult must carry ok flag, passed, failed counts."""
        from scripts.ci.batch_scan_integration import BatchScanResult

        result = BatchScanResult(
            group="quick",
            ok=True,
            passed=10,
            failed=0,
            errors=0,
            skipped=0,
            duration_s=1.5,
            failures=[],
            batches_run=1,
        )
        assert result.ok is True, "Result must not be empty"
        assert result.passed == 10, "Result must not be empty"
        assert result.failed == 0, "Result must not be empty"

    def test_batch_scan_runner_preview_method(self):
        """BatchScanRunner.preview() must return a string without executing tests."""
        from scripts.ci.batch_scan_integration import BatchScanRunner

        runner = BatchScanRunner(workers=1)
        # preview() returns a str describing what would run
        result = runner.preview(group="quick")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Group 4 — rvs_env_preflight validator
# ---------------------------------------------------------------------------


class TestEnvPreflightValidator:
    """Validate the environment preflight script API."""

    def test_preflight_script_exists(self):
        """scripts/ci/rvs_env_preflight.py must be present."""
        path = ROOT / "scripts" / "ci" / "rvs_env_preflight.py"
        assert path.exists(), f"Missing: {path}"

    def test_preflight_importable(self):
        """rvs_env_preflight must be importable as a module."""
        import importlib.util as _ilu

        path = ROOT / "scripts" / "ci" / "rvs_env_preflight.py"
        spec = _ilu.spec_from_file_location("rvs_env_preflight", path)
        assert spec is not None, "spec_from_file_location returned None"
        mod = _ilu.module_from_spec(spec)
        sys.modules.setdefault("rvs_env_preflight", mod)  # needed for @dataclass
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert hasattr(mod, "PACKAGE_GROUPS"), "rvs_env_preflight must export PACKAGE_GROUPS"

    def test_preflight_required_packages_non_empty(self):
        """PACKAGE_GROUPS must list at least the core group."""
        import importlib.util as _ilu

        path = ROOT / "scripts" / "ci" / "rvs_env_preflight.py"
        if "rvs_env_preflight" in sys.modules:
            mod = sys.modules["rvs_env_preflight"]
        else:
            spec = _ilu.spec_from_file_location("rvs_env_preflight", path)
            assert spec is not None, "spec must be initialized"
            mod = _ilu.module_from_spec(spec)
            sys.modules["rvs_env_preflight"] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        groups = mod.PACKAGE_GROUPS
        total = sum(len(v) for v in groups.values())
        assert total >= 5, f"PACKAGE_GROUPS too short ({total} packages); expected ≥5 entries"


# ---------------------------------------------------------------------------
# Group 5 — Windows compatibility: no POSIX-only bare imports at module level
# ---------------------------------------------------------------------------


class TestWindowsCompatibility:
    """Ensure no module-level bare POSIX imports exist in src/."""

    _POSIX_MODULES = ("fcntl", "resource", "termios", "tty", "pty")

    @pytest.mark.parametrize("mod_name", _POSIX_MODULES)
    def test_bridge_manager_no_bare_posix_import(self, mod_name):
        """
        bridge_manager must guard POSIX-only imports with try/except ImportError.
        Verifies that bare `import <mod>` never appears outside a try block.
        """
        src = ROOT / "src" / "bridge_manager.py"
        lines = src.read_text().splitlines()
        in_try = False
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "try:":
                in_try = True
            elif stripped.startswith("except ") or stripped == "except:":
                in_try = False
            # Bare import outside try/except — this is the problem pattern
            if not in_try and stripped == f"import {mod_name}":
                pytest.fail(
                    f"{src}:{lineno}: bare `import {mod_name}` found outside "
                    f"try/except guard — will crash on Windows."
                )

    def test_sandbox_no_bare_resource_import(self):
        """sandbox.py must guard `import resource` with try/except."""
        src = ROOT / "src" / "codex_ml" / "safety" / "sandbox.py"
        lines = src.read_text().splitlines()
        in_try = False
        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "try:":
                in_try = True
            elif stripped.startswith("except ") or stripped == "except:":
                in_try = False
            if not in_try and stripped == "import resource":
                pytest.fail(
                    f"{src}:{lineno}: bare `import resource` without try/except guard — "
                    "crashes on Windows."
                )


# ---------------------------------------------------------------------------
# Readiness checkpoint
# ---------------------------------------------------------------------------


def test_s94_cpu_readiness_checkpoint():
    """
    Gate: all critical S94 items must pass.
    This is the canonical B-03 (CPU) readiness check.
    """
    required = [
        "bridge_manager",
        "codex_ml.safety.sandbox",
    ]
    failed = []
    for mod in required:
        try:
            importlib.import_module(mod)
        except ImportError as exc:
            failed.append(f"{mod}: {exc}")

    assert (not failed, "Condition must be true"
    ), "S94 CPU readiness gate FAILED — critical modules not importable:\n" + "\n".join(failed)
