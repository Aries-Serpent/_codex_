"""
Test No Hardcoded Secrets

Test module for no hardcoded secrets.
"""

from __future__ import annotations

import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    re.compile(r"BEGIN RSA PRIVATE KEY"),  # pragma: allowlist secret
    # Match aws_secret_access_key when assigned to a hardcoded value (not os.getenv)
    # This allows legitimate config key usage but catches actual secrets
    re.compile(r"aws_secret_access_key\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*=\s*['\"]\w+"),
]


def test_repository_contains_no_obvious_secrets() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for path in repo_root.rglob("*.py"):
        # Skip test files, test fixture scripts, provider example code,
        # and virtual-environment site-packages (contain library source with
        # legitimate key-format strings used in documentation/tests).
        path_str = str(path).replace("\\", "/")
        if (
            "/tests/" in path_str
            or "/.github/agents/scripts/" in path_str
            or "/providers/" in path_str
            or "/.venv" in path_str
            or "/venv/" in path_str
            or "/site-packages/" in path_str
            or "/temp/" in path_str
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SUSPICIOUS_PATTERNS:
            assert not pattern.search(text), f"Potential secret found in {path}"
