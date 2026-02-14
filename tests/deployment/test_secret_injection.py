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
    
    # Pattern: API_KEY followed by colon and a non-placeholder value
    # We allow ${...} placeholders
    import re
    
    # Find all lines with API_KEY that are not environment variable references
    for line in compose.split('\n'):
        if 'API_KEY' in line:
            # Skip comments
            if line.strip().startswith('#'):
                continue
            # Check if it's a placeholder pattern
            if re.search(r'\$\{[^}]+\}', line) or re.search(r'\$[A-Z_]+', line):
                continue  # It's a placeholder, OK
            # If we get here, it's a hardcoded value (not OK)
            # But we need to check if it's actually a key: value pair
            if ':' in line and not line.strip().endswith(':'):
                # This is a potential hardcoded secret
                pytest.fail(f"Found potentially hardcoded API_KEY in line: {line.strip()}")
