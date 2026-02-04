"""Hardened subprocess helpers with strict validation."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Sequence

logger = logging.getLogger(__name__)

_ALLOWED_EXTENSIONS = {".py", ".sh"}
_MODULE_PATH = Path(__file__).resolve()
_PACKAGE_ROOT = _MODULE_PATH.parent.parent


def _discover_repo_root(module_path: Path) -> Path | None:
    """Return the repository root when running from a source checkout."""

    for ancestor in module_path.parents:
        tools_dir = ancestor / "tools"
        src_dir = ancestor / "src"
        if tools_dir.exists() and src_dir.exists():
            return ancestor
    return None


def _gather_allowed_roots(module_path: Path) -> tuple[Path, ...]:
    """Compute the set of directories that contain approved scripts."""

    roots: list[Path] = []
    repo_root = _discover_repo_root(module_path)
    if repo_root is not None:
        roots.extend([repo_root / "tools", repo_root / "src"])

    roots.extend([_PACKAGE_ROOT, _PACKAGE_ROOT / "tools"])

    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved.exists() and resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return tuple(unique)


_ALLOWED_ROOTS = _gather_allowed_roots(_MODULE_PATH)


def _assert_safe_script(path: Path, allowed_roots: Iterable[Path]) -> None:
    """Ensure *path* points to a script within one of *allowed_roots*."""

    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    if resolved.suffix not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"disallowed extension: {resolved.suffix}")
    roots = [root.resolve() for root in allowed_roots]
    if not any(str(resolved).startswith(str(root) + os.sep) for root in roots):
        raise ValueError(f"script outside allowed roots: {resolved}")


def run_argv(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute a fixed argv sequence with ``shell=False`` and validation."""

    if not argv or not isinstance(argv[0], str):
        raise ValueError("argv must be a non-empty sequence of strings")

    # Validate interpreter/script combinations
    exe = shutil.which(argv[0]) or argv[0]
    exe_name = Path(exe).name.lower()
    if exe_name.startswith("python") and len(argv) >= 2:
        script_arg: Path | None = None
        args_iter = iter(argv[1:])
        for arg in args_iter:
            if not arg or arg.startswith("-"):
                # Skip flags and their immediate parameters when relevant.
                if arg in {"-m", "-c"}:
                    next(args_iter, None)
                continue

            candidate = Path(arg)
            if candidate.suffix in _ALLOWED_EXTENSIONS:
                script_arg = candidate
                break

        if script_arg is not None:
            _assert_safe_script(script_arg, _ALLOWED_ROOTS)

    try:
        result = subprocess.run(  # nosec B603
            list(argv),
            cwd=str(cwd) if cwd is not None else None,
            check=check,
            capture_output=capture_output,
            text=text,
        )
    except subprocess.CalledProcessError as exc:
        logger.debug("subprocess failed: %s", exc, exc_info=True)
        raise
    return result


__all__ = ["run_argv"]
