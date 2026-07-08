"""Unit tests for codex_ml.utils.subproc."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from codex_ml.utils.subproc import (
    _assert_safe_script,
    _discover_repo_root,
    _gather_allowed_roots,
    run_argv,
)

_MODULE_PATH = Path(__file__).resolve()


# ---------------------------------------------------------------------------
# _discover_repo_root
# ---------------------------------------------------------------------------


def test_discover_repo_root_finds_repo_from_module():
    result = _discover_repo_root(_MODULE_PATH)
    # Running inside a source checkout; should find a root with tools/ and src/
    assert result is not None, "result must be initialized"
    assert (result / "src").exists(), "Result must not be empty"
    assert (result / "tools").exists(), "Result must not be empty"


def test_discover_repo_root_returns_none_for_isolated_path(tmp_path: Path):
    isolated = tmp_path / "some" / "module.py"
    result = _discover_repo_root(isolated)
    assert result is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# _gather_allowed_roots
# ---------------------------------------------------------------------------


def test_gather_allowed_roots_returns_tuple():
    roots = _gather_allowed_roots(_MODULE_PATH)
    assert isinstance(roots, tuple)


def test_gather_allowed_roots_non_empty_in_repo():
    roots = _gather_allowed_roots(_MODULE_PATH)
    assert len(roots) > 0, "Roots must not be empty"


def test_gather_allowed_roots_unique():
    roots = _gather_allowed_roots(_MODULE_PATH)
    seen = set()
    for r in roots:
        assert r not in seen, f"Duplicate root: {r}"
        seen.add(r)


def test_gather_allowed_roots_all_exist():
    roots = _gather_allowed_roots(_MODULE_PATH)
    for r in roots:
        assert r.exists(), f"Root does not exist: {r}"


# ---------------------------------------------------------------------------
# _assert_safe_script
# ---------------------------------------------------------------------------


def test_assert_safe_script_raises_for_nonexistent_file(tmp_path: Path):
    non_existent = tmp_path / "ghost.py"
    with pytest.raises(FileNotFoundError):
        _assert_safe_script(non_existent, [tmp_path])


def test_assert_safe_script_raises_for_disallowed_extension(tmp_path: Path):
    bad_ext = tmp_path / "script.exe"
    bad_ext.write_text("#!/bin/sh")
    with pytest.raises(ValueError, match="disallowed extension"):
        _assert_safe_script(bad_ext, [tmp_path])


def test_assert_safe_script_raises_for_script_outside_allowed_roots(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    script = outside / "evil.py"
    script.write_text("print('evil')")
    with pytest.raises(ValueError, match="outside allowed roots"):
        _assert_safe_script(script, [allowed])


def test_assert_safe_script_passes_for_valid_py_inside_allowed(tmp_path: Path):
    allowed = tmp_path / "scripts"
    allowed.mkdir()
    script = allowed / "run.py"
    script.write_text("print('ok')")
    _assert_safe_script(script, [allowed])  # should not raise


def test_assert_safe_script_passes_for_sh_inside_allowed(tmp_path: Path):
    allowed = tmp_path / "scripts"
    allowed.mkdir()
    script = allowed / "run.sh"
    script.write_text("#!/bin/sh\necho ok")
    _assert_safe_script(script, [allowed])  # should not raise


# ---------------------------------------------------------------------------
# run_argv
# ---------------------------------------------------------------------------


def test_run_argv_basic_python_version():
    result = run_argv([sys.executable, "--version"])
    assert result.returncode == 0, "Result must not be empty"


def test_run_argv_echo_like_command():
    result = run_argv([sys.executable, "-c", "import sys; sys.exit(0)"])
    assert result.returncode == 0, "Result must not be empty"


def test_run_argv_raises_for_empty_argv():
    with pytest.raises(ValueError):
        run_argv([])


def test_run_argv_raises_for_non_string_argv():
    with pytest.raises((ValueError, TypeError)):
        run_argv([123])  # type: ignore[list-item]


def test_run_argv_captures_stdout():
    result = run_argv([sys.executable, "-c", "print('hello')"])
    assert "hello" in result.stdout, "Result must not be empty"


def test_run_argv_check_false_allows_nonzero_exit():
    result = run_argv([sys.executable, "-c", "import sys; sys.exit(1)"], check=False)
    assert result.returncode == 1, "Result must not be empty"


def test_run_argv_check_true_raises_on_failure():
    with pytest.raises(subprocess.CalledProcessError):
        run_argv([sys.executable, "-c", "import sys; sys.exit(2)"], check=True)


def test_run_argv_with_cwd(tmp_path: Path):
    result = run_argv([sys.executable, "-c", "import os; print(os.getcwd())"], cwd=tmp_path)
    assert str(tmp_path) in result.stdout.strip(), "Result must not be empty"


def test_run_argv_non_python_command():
    # Run a simple non-python command (python with -c works as non-script)
    result = run_argv([sys.executable, "-c", "pass"])
    assert result.returncode == 0, "Result must not be empty"
