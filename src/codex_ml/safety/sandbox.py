# BEGIN: CODEX_SANDBOX
from __future__ import annotations

import contextlib
import os
import resource
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def _scrub_env() -> dict:
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
    no_network: bool = True,
) -> subprocess.CompletedProcess:
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

    def _limits() -> None:
        as_bytes = mem_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (as_bytes, as_bytes))
        resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))

    preexec = _limits if hasattr(resource, "setrlimit") else None
    try:
        cp = subprocess.run(
            argv,
            input=stdin,
            cwd=str(work),
            env=env,
            preexec_fn=preexec,
            timeout=timeout + 1,
            text=False,
            capture_output=True,
        )

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
