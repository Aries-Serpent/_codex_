"""Utilities for redacting secrets and PII from structured data."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


class SecretRedactor:
    """Redact common secret patterns (API keys, tokens, and PII)."""

    DEFAULT_PATTERNS: Mapping[str, str] = {
        "api_key": r"api[_-]?key[\"'\s:=]+([a-zA-Z0-9\-_]+)",
        "bearer_token": r"bearer[\"'\s:=]+([a-zA-Z0-9\-_.]+)",  # nosec B105
        "aws_secret": r"aws[_-]?secret[_-]?access[_-]?key[\"'\s:=]+([a-zA-Z0-9/+=]+)",  # nosec B105
        "password": r"password[\"'\s:=]+([^\s\"']+)",  # nosec B105
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    }

    KEY_HINT_LABELS: Mapping[str, str] = {
        "apikey": "API_KEY",  # pragma: allowlist secret
        "token": "TOKEN",  # pragma: allowlist secret  # nosec B105
        "secret": "SECRET",  # pragma: allowlist secret  # nosec B105
        "password": "PASSWORD",  # pragma: allowlist secret  # nosec B105
        "passphrase": "PASSWORD",  # pragma: allowlist secret  # nosec B105
        "email": "EMAIL",  # pragma: allowlist secret
        "bearer": "BEARER_TOKEN",  # pragma: allowlist secret
    }

    def __init__(self, patterns: Mapping[str, str] | None = None) -> None:
        compiled: dict[str, re.Pattern[str]] = {}
        for name, pattern in (patterns or self.DEFAULT_PATTERNS).items():
            compiled[name] = re.compile(pattern, flags=re.IGNORECASE)
        self._patterns = compiled

    def redact(self, text: str) -> str:
        """Return ``text`` with all known secret patterns replaced."""

        result = text
        for name, pattern in self._patterns.items():
            replacement = f"[REDACTED_{name.upper()}]"
            result = pattern.sub(replacement, result)
        return result

    def redact_dict(self, data: Mapping[str, Any]) -> dict[str, Any]:
        """Recursively redact secrets within nested mappings."""

        redacted: dict[str, Any] = {}
        for key, value in data.items():
            redacted[key] = self._redact_value(value, key_hint=str(key))
        return redacted

    def _redact_value(self, value: Any, *, key_hint: str | None = None) -> Any:
        if isinstance(value, str):
            sanitized = self.redact(value)
            if sanitized == value and key_hint:
                label = self._label_for_key(key_hint)
                if label:
                    return f"[REDACTED_{label}]"
            return sanitized
        if isinstance(value, Mapping):
            return self.redact_dict(value)
        if isinstance(value, list):
            return [self._redact_value(item, key_hint=key_hint) for item in value]
        if isinstance(value, tuple):  # pragma: no cover - defensive
            return tuple(self._redact_value(item, key_hint=key_hint) for item in value)
        return value

    def _label_for_key(self, key: str) -> str | None:
        normalized = "".join(ch for ch in key.lower() if ch.isalnum())
        for hint, label in self.KEY_HINT_LABELS.items():
            if hint in normalized:
                return label
        return None


__all__ = ["SecretRedactor"]
