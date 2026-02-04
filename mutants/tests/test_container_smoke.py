"""
Test Container Smoke

Test module for container smoke.
"""

import os
import shutil
import subprocess
import sys

import pytest


def docker_available() -> bool:
    return shutil.which("docker") is not None


def script(path: str) -> str:
    return os.path.join("scripts", "ci", path)


@pytest.mark.skipif(
    os.environ.get("RUN_CONTAINER_SMOKE", "0") != "1",
    reason="Set RUN_CONTAINER_SMOKE=1 to enable container smoke test",
)
@pytest.mark.skipif(not docker_available(), reason="Docker not available in environment")
def test_container_smoke_basic(tmp_path):
    image = os.environ.get("SMOKE_IMAGE", "codex:local")
    # Use an ephemeral host port in the high range to avoid conflicts
    host_port = int(os.environ.get("SMOKE_HOST_PORT", "18000"))
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
