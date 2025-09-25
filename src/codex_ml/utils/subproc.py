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
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ALLOWED_ROOTS = (_REPO_ROOT / "tools", _REPO_ROOT / "src")


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
        _assert_safe_script(Path(argv[1]), _ALLOWED_ROOTS)

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
