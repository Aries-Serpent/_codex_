"""
Test Actions Server Smoke

Test module for actions server smoke.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import pytest


def _get(url: str, timeout: int = 5, max_retries: int = 5):
    """
    GET request with retry logic for resilience.
    
    Args:
        url: URL to GET
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        
    Returns:
        Parsed JSON response
        
    Raises:
        urllib.error.URLError: If all retries are exhausted
    """
    parts = urlsplit(url)
    if parts.scheme != "http" or parts.hostname != "localhost" or parts.port != 8010:
        raise ValueError(f"unexpected smoke-test URL: {url!r}")

    last_error = None
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(  # nosec B310 -- test-only controlled URL; scheme/host/port constrained to http://localhost:8010 above  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is constrained to localhost:8010 above
                url, timeout=timeout
            ) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(0.5 * (2 ** attempt))  # Exponential backoff
            continue

    raise last_error or TimeoutError(f"Failed to connect after {max_retries} retries")


@pytest.mark.timeout(30)
def test_server_health_and_branches_smoke(tmp_path):
    """Test server health and branches endpoints with timeout protection."""
    env = os.environ.copy()
    env.setdefault("CODEX_GH_OWNER", "Aries-Serpent")
    env.setdefault("CODEX_GH_REPO", "_codex_")
    server_script = (Path.cwd() / "tools" / "actions_server.py").resolve()
    p = subprocess.Popen(  # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args -- executable and script path are explicit and shell=False is used
        [sys.executable, str(server_script)], env=env, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    try:
        # Wait for server startup with exponential backoff retry logic
        max_startup_time = 10
        start_time = time.time()
        server_ready = False

        while time.time() - start_time < max_startup_time:
            try:
                # Test with retry logic built in
                health_response = _get("http://localhost:8010/healthz", timeout=2, max_retries=3)
                if health_response.get("ok") is True:
                    server_ready = True
                    break
            except Exception as _err:
                time.sleep(0.5)

        assert server_ready, f"Server failed to start within {max_startup_time}s"

        # Now test branches endpoint
        branches = _get("http://localhost:8010/repo/branches", timeout=5, max_retries=3)
        assert isinstance(branches, list), "branches must be a list"
    finally:
        # Ensure process cleanup with proper timeout
        try:
            p.terminate()
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()


def test_assert_safe_github_url_requires_string():
    from tools import actions_server

    with pytest.raises(ValueError, match="must be a string"):
        actions_server._assert_safe_github_url(None)  # type: ignore[arg-type]


def test_gh_post_rejects_spoofed_github_url():
    from tools import actions_server

    with pytest.raises(ValueError, match="must target api.github.com"):
        actions_server.gh_post("https://api.github.com@evil.com/repos/owner/repo", {})
