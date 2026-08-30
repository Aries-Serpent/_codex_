"""
Test Secret Injection

Test module for secret injection.
"""

import re
from pathlib import Path

import pytest


def test_compose_does_not_embed_secrets() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    # Check that secret values are not hardcoded
    # Allow environment variable placeholders: ${VAR}, ${VAR:-default}, $VAR
    # Disallow hardcoded values like: API_KEY: "actual-secret-value"
 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    # Find all lines with API_KEY that are not environment variable references
    for line in compose.split("\n"):
        if "API_KEY" not in line:
            continue

        # Skip comments
        if line.strip().startswith("#"):
            continue

        # Check if it's a placeholder pattern - these are OK
        if re.search(r"\$\{[^}]+\}", line) or re.search(r"\$[A-Z_]+", line):
            continue

        # Check if it's a key: value pair (not just a key definition)
        if ":" not in line or line.strip().endswith(":"):
            continue

        # If we get here, it's a hardcoded secret value (not OK)
        pytest.fail(f"Found potentially hardcoded API_KEY in line: {line.strip()}")
