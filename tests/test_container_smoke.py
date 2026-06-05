"""
Test Container Smoke

Test module for container smoke.
"""

import os
import re
import shutil
import subprocess
import sys

import pytest


def docker_available() -> bool:
    return shutil.which("docker") is not None


def script(path: str) -> str:
    return os.path.join("scripts", "ci", path)


_IMAGE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*(?::[A-Za-z0-9._-]+)?$")


def _validated_smoke_image(raw: str) -> str:
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
        "bash",
        script("container_smoke.sh"),
        image,
        "8000",
        str(host_port),
    ]
    print(f"[test] Running: {' '.join(cmd)}", file=sys.stderr)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    assert proc.returncode == 0
