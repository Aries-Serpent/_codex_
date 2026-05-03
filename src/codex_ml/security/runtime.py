"""Runtime security helpers for prompt scanning and secret loading."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path


class PromptSecurityError(ValueError):
    """Raised when unsafe content is detected in a prompt."""


class SecretNotFoundError(KeyError):
    """Raised when a secret cannot be located in the secure store."""


_DEFAULT_PATTERNS: Sequence[str] = (
    r"drop\s+table",
    r"rm\s+-rf",
    r"select\s+\*\s+from",
    r"\bssh-key\b",
)


def scan_prompt_for_unsafe_content(prompt: str, patterns: Sequence[str] | None = None) -> None:
    """Raise if the prompt contains unsafe patterns.

    The check is intentionally lightweight to avoid false positives while still
    catching common destructive intents during offline evaluation and packaging.
    """

    if not isinstance(prompt, str):
        raise PromptSecurityError("prompt must be a string")

    candidates = patterns or _DEFAULT_PATTERNS
    for pattern in candidates:
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            raise PromptSecurityError(f"Prompt rejected due to unsafe content: '{pattern}'")


def load_secret(
    name: str,
    *,
    store_path: str | Path = ".codex/secrets.json",
    env_prefix: str = "CODEX_SECRET_",
) -> str:
    """Retrieve a secret value from environment or local secure store.

    No network operations are performed; the store is a simple JSON mapping.
    """

    from os import environ

    env_key = f"{env_prefix}{name.upper()}"
    if env_key in environ:
        return environ[env_key]

    path = Path(store_path)
    if not path.exists():
        raise SecretNotFoundError(f"Secret '{name}' not found; store {store_path} missing")

    data: Mapping[str, str] = json.loads(path.read_text(encoding="utf-8") or "{}")
    if name not in data:
        raise SecretNotFoundError(f"Secret '{name}' not present in store {store_path}")
    return data[name]


__all__ = [
    "PromptSecurityError",
    "SecretNotFoundError",
    "load_secret",
    "scan_prompt_for_unsafe_content",
]
