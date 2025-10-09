"""Shared regular expressions for environment and credential validation."""

from __future__ import annotations

import re

__all__ = ["ENV_ASSIGNMENT", "PEM_BLOCK"]

# Environment assignments follow KEY=VALUE with uppercase letters and underscores.
ENV_ASSIGNMENT = re.compile(r"^(?:[A-Z_][A-Z0-9_]*)(?:=[^\n\r]*)?$")

# PEM blocks guard against pathological payloads (e.g., single-char floods) while
# remaining permissive for valid Base64 body content.
PEM_BLOCK = re.compile(
    r"(?ms)^-----BEGIN (?P<label>[A-Z ]+)-----\n"
    r"(?![Zz]+(?:\n[Zz]+)*\n?$)(?P<body>[A-Za-z0-9+/=\n]{1,8192})\n"
    r"-----END (?P=label)-----\s*$"
)
