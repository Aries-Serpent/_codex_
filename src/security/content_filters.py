"""Content filtering helpers consolidating previously scattered logic."""

from __future__ import annotations

import re

from ._types import _PROFANITY, SecurityError, sanitize_text  # noqa: F401

# Re-export for backward compatibility – callers may do:
#   from src.security.content_filters import SecurityError
#   from src.security.content_filters import sanitize_text
__all__ = [
    "SecurityError",
    "_PROFANITY",
    "sanitize_text",
    "detect_profanity",
    "detect_personal_data",
    "detect_malware_patterns",
    "enforce_content_policies",
]

_PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b\d{4} \d{4} \d{4} \d{4}\b"),  # Credit card (simplified)
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
]
_MALWARE_PATTERNS = [
    re.compile(r"(?:powershell.exe\s+-enc)", re.I),
    re.compile(r"curl\s+http[s]?://[\w./-]+\s*-o\s+/tmp/\w+", re.I),
    re.compile(r"rm\s+-rf\s+/", re.I),
]


def detect_profanity(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in _PROFANITY)


def detect_personal_data(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {"pii": []}
    for pattern in _PII_PATTERNS:
        matches_found = pattern.findall(text)
        if matches_found:
            matches["pii"].extend(matches_found)
    return matches


def detect_malware_patterns(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in _MALWARE_PATTERNS:
        if pattern.search(text):
            hits.append(pattern.pattern)
    return hits


def enforce_content_policies(text: str) -> None:
    if detect_profanity(text):
        raise SecurityError("Profanity detected")
    if detect_personal_data(text)["pii"]:
        raise SecurityError("PII detected")
    if detect_malware_patterns(text):
        raise SecurityError("Malware pattern detected")
