"""
Test No Hardcoded Secrets

Test module for no hardcoded secrets.
"""

from __future__ import annotations

import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    # Actual PEM private-key material (header followed by a base64 body), any key
    # type. A bare header string (e.g. a detector rule list in a secrets scanner)
    # is not key material and is intentionally not flagged.
    re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"  # pragma: allowlist secret
        r"\s*(?:\\n|\n)\s*[A-Za-z0-9+/=]{40,}"
    ),
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


def test_private_key_pattern_detects_pem_material() -> None:
    """The PEM pattern must still flag real key blocks of every common type."""
    body = "MIIEowIBAAKCAQEA" + "A" * 48
    pem_pattern = SUSPICIOUS_PATTERNS[0]
    for kind in ("RSA ", "EC ", "DSA ", "OPENSSH ", "ENCRYPTED ", ""):
        block = f"-----BEGIN {kind}PRIVATE KEY-----\n{body}\n"  # pragma: allowlist secret
        assert pem_pattern.search(block), kind
        escaped = f'KEY = "-----BEGIN {kind}PRIVATE KEY-----\\n{body}"'  # pragma: allowlist secret
        assert pem_pattern.search(escaped), kind
    assert not pem_pattern.search('"patterns": ["BEGIN RSA PRIVATE KEY"]')
