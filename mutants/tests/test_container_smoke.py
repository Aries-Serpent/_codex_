"""
Test Container Smoke

Test module for container smoke.

SECURITY NOTICE:
This test module runs Docker commands via subprocess for integration testing.
All subprocess operations use shlex.quote() to safely quote arguments, preventing
command injection. The subprocess.run() calls use shell=False for additional safety.
These operations are test-only and not used in production.

Code coverage: CWE-78 (Improper Neutralization of Special Elements in subprocess)
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from codex.logging.structured_logger import logger


def docker_available() -> bool:
    return shutil.which("docker") is not None


def script(path: str) -> str:
    return os.path.join("scripts", "ci", path)


_IMAGE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*(?::[A-Za-z0-9._-]+)?$")


def _validated_smoke_image(raw: str) -> str:
    """Validate Docker image name to prevent command injection.

    Security measures:
    - Validates against Docker image name format regex
    - Prevents shell metacharacters and escape sequences

    Args:
        raw: Docker image name to validate

    Returns:
        Validated image name

    Raises:
        ValueError: If image name is invalid
    """
    if not _IMAGE_NAME_RE.fullmatch(raw):
        msg = "Invalid SMOKE_IMAGE value; expected docker image reference format"
        raise ValueError(msg)
    return raw


def _validated_host_port(raw: str) -> int:
    port = int(raw)
    if port < 1024 or port > 65535:
        msg = "Invalid SMOKE_HOST_PORT value; expected integer in range 1024-65535"
        raise ValueError(msg)
    return port


def _validated_script_path(name: str) -> str:
    """Validate script path to prevent path traversal and symlink attacks.

    Security measures:
    - Only allows files under scripts/ci directory
    - Rejects path traversal attempts (..)
    - Rejects symbolic links (prevents symlink following attacks)

    Args:
        name: Script filename to validate

    Returns:
        Absolute path to validated script

    Raises:
        ValueError: If path is invalid or outside allowed root
    """
    script_path = Path(script(name)).resolve()
    allowed_root = (Path.cwd() / "scripts" / "ci").resolve()
    script_path.relative_to(allowed_root)
    if not script_path.is_file() or script_path.is_symlink():
        msg = "Invalid smoke script path; expected a real file under scripts/ci"
        raise ValueError(msg)
    return str(script_path)


def _bash_executable() -> str:
    bash_path = shutil.which("bash")
    if not bash_path:
        raise RuntimeError("bash executable not found")
    return bash_path


@pytest.mark.skipif(
    os.environ.get("RUN_CONTAINER_SMOKE", "0") != "1",
    reason="Set RUN_CONTAINER_SMOKE=1 to enable container smoke test",
)
@pytest.mark.skipif(not docker_available(), reason="Docker not available in environment")
def test_container_smoke_basic(tmp_path):
    image = _validated_smoke_image(os.environ.get("SMOKE_IMAGE", "codex:local"))
    # Use an ephemeral host port in the high range to avoid conflicts
    host_port = _validated_host_port(os.environ.get("SMOKE_HOST_PORT", "18000"))
    cmd = [
        _bash_executable(),
        _validated_script_path("container_smoke.sh"),
        shlex.quote(image),
        shlex.quote("8000"),
        shlex.quote(str(host_port)),
    ]
    logger.error(f"[test] Running: {shlex.join(cmd)}")
    # Allow enough time for slower CI/container startup while still failing reasonably fast.
    # lgtm[py/subprocess-tainted-env-args] - Safe: Validated via _validated_smoke_image() and _validated_host_port()
    # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args
    proc = subprocess.run(
        cmd, capture_output=True, text=True, timeout=300, check=False, shell=False
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    assert proc.returncode == 0, "returncode is not valid"
