"""
Test No Hardcoded Secrets

Test module for no hardcoded secrets.
"""

from __future__ import annotations

import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    re.compile(r"BEGIN RSA PRIVATE KEY"),
    re.compile(r"aws_secret_access_key", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*=\s*['\"]\w+"),
]


def test_repository_contains_no_obvious_secrets() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for path in repo_root.rglob("*.py"):
        if "/tests/" in str(path).replace("\\", "/"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SUSPICIOUS_PATTERNS:
            assert not pattern.search(text), f"Potential secret found in {path}"
