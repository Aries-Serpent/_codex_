"""
Sandbox Module

This module provides functionality for sandbox.

Usage:
    from safety.sandbox import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# BEGIN: CODEX_SANDBOX
from __future__ import annotations

import contextlib
import logging
import os
import shutil

try:
    import resource

    _HAS_RESOURCE = True
except ImportError:  # Windows — resource is POSIX-only
    resource = None  # type: ignore[assignment]
    _HAS_RESOURCE = False
import subprocess  # nosec B404 - subprocess is required for sandboxing; see docs/security/Bandit_Fixes.md
import tempfile
from pathlib import Path
from typing import Any, Optional


def _scrub_env() -> dict[str, Any]:
    return {
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }


def _restrict_fs(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    os.umask(0o077)


def run_in_sandbox(
    argv: list[str],
    stdin: Optional[bytes] = None,
    cwd: Optional[Path] = None,
    timeout: int = 10,
    mem_mb: int = 256,
    _no_network: bool = True,
    enforce_limits: bool = False,
) -> subprocess.CompletedProcess:
    """Run *argv* in a restricted subprocess.

    On POSIX (Linux / macOS) the child process is constrained by
    ``resource`` limits (address space, CPU time, file descriptors).

    On Windows, ``resource`` is unavailable.  If *enforce_limits* is ``True``
    a ``RuntimeError`` is raised immediately so callers know limits cannot be
    enforced — preventing silent sandbox escapes.  If *enforce_limits* is
    ``False`` (the default) the sandbox still runs but **without** OS-level
    resource limits; a warning is logged.
    """
    work = Path(cwd) if cwd else Path(tempfile.mkdtemp(prefix="codex_sbx_"))
    _restrict_fs(work)
    env = _scrub_env()
    for key in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "no_proxy",
    ]:
        env.pop(key, None)

    if not _HAS_RESOURCE:
        if enforce_limits:
            raise RuntimeError(
                "run_in_sandbox: resource limits cannot be enforced on this platform "
                "(Windows / no `resource` module). "
                "Pass enforce_limits=False to run without OS-level constraints, "
                "or deploy on Linux/macOS for full sandboxing."
            )
        logging.getLogger(__name__).warning(
            "run_in_sandbox: resource module unavailable — "
            "running WITHOUT memory/CPU limits (Windows). "
            "Use enforce_limits=True to prevent execution on unsupported platforms."
        )

    def _limits() -> None:
        if not _HAS_RESOURCE:
            return  # Already warned above; no-op here
        as_bytes = mem_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (as_bytes, as_bytes))
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))

    preexec = _limits if _HAS_RESOURCE else None
    if not argv:
        raise ValueError("sandbox.run: argv must be non-empty")
    exe = shutil.which(str(argv[0]))
    if exe is None:
        raise FileNotFoundError(f"sandbox.run: executable not found: {argv[0]!r}")
    argv = [exe, *[str(arg) for arg in argv[1:]]]

    try:
        # Use explicit proc management (not `with Popen`) to avoid the
        # __exit__ calling proc.wait() on a potentially live process when
        # TimeoutExpired is raised before we have a chance to kill it.
        proc = subprocess.Popen(  # nosec B603 - inputs validated; shell=False; absolute executable enforced
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(work),
            env=env,
            preexec_fn=preexec,
            text=False,
        )
        try:
            stdout, stderr = proc.communicate(input=stdin, timeout=timeout + 1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()  # drain pipes; output discarded (process killed on timeout)
            raise
        cp = subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)

        def _sanitize(data: bytes) -> bytes:
            s = data.decode("utf-8", errors="ignore")
            for tag in ["password", "api_key", "secret", "AKIA"]:
                s = s.replace(tag, "***")
            return s.encode("utf-8")

        cp.stdout = _sanitize(cp.stdout or b"")
        cp.stderr = _sanitize(cp.stderr or b"")
        return cp
    finally:
        if not cwd:
            with contextlib.suppress(Exception):
                shutil.rmtree(work)


def docker_available() -> bool:
    return shutil.which("docker") is not None


def firejail_available() -> bool:
    return shutil.which("firejail") is not None
