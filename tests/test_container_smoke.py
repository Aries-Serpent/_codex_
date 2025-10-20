import os
import shutil
import subprocess
import time

import pytest
import requests

RUN_SMOKE = os.getenv("RUN_CONTAINER_SMOKE", "0") == "1"
DOCKER = shutil.which("docker") is not None


@pytest.mark.skipif(not RUN_SMOKE, reason="Set RUN_CONTAINER_SMOKE=1 to run container smoke tests")
@pytest.mark.skipif(not DOCKER, reason="Docker is required for this smoke test")
def test_container_health_smoke():
    image = os.getenv("SMOKE_IMAGE", "codex:local")
    host_port = int(os.getenv("SMOKE_HOST_PORT", "18001"))
    container_port = int(os.getenv("SMOKE_CONTAINER_PORT", "8000"))
    name = f"codex_smoke_test_{int(time.time())}"

    try:
        subprocess.check_call(
            ["docker", "run", "-d", "--name", name, "-p", f"{host_port}:{container_port}", image],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        urls = [f"http://127.0.0.1:{host_port}/health", f"http://127.0.0.1:{host_port}/"]
        ok = False
        for _ in range(30):
            for url in urls:
                try:
                    r = requests.get(url, timeout=1.5)
                    if r.status_code == 200:
                        ok = True
                        break
                except Exception:
                    pass
            if ok:
                break
            time.sleep(1.5)

        assert ok, "Container did not respond with 200 on /health or / within timeout"
    finally:
        subprocess.call(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
