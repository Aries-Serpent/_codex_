"""Utilities enforcing pinned Hugging Face downloads."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple
from urllib.parse import urlparse

# Hexadecimal commit hashes with at least 7 characters are considered immutable.
_COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{7,}$")
_ENV_VAR = "CODEX_HF_REVISION"
_LOCAL_PREFIXES = ("./", "../", "/")

# Stable revisions for built-in examples and smoke tests. These values were
# retrieved from Hugging Face's model metadata on 2025-09-25.
KNOWN_MODEL_REVISIONS: Dict[str, str] = {
    "openai-community/gpt2": "607a30d783dfa663caf39e06633721c8d4cfcd7e",
    "gpt2": "607a30d783dfa663caf39e06633721c8d4cfcd7e",
    "sshleifer/tiny-gpt2": "5f91d94bd9cd7190a9f3216ff93cd1dd95f2c7be",
    "hf-internal-testing/llama-tokenizer": "d02ad6cb9dd2c2296a6332199fa2fdca5938fef0",
}


def _normalize_identifier(identifier: Any) -> str | None:
    if identifier is None:
        return None
    if isinstance(identifier, os.PathLike):
        return os.fspath(identifier)
    return str(identifier)


def _looks_like_local(identifier: str | None) -> bool:
    """Heuristically determine whether an identifier points to local files."""

    if identifier is None:
        return True
    if identifier.startswith(_LOCAL_PREFIXES):
        return True
    parsed = urlparse(identifier)
    if parsed.scheme and parsed.scheme != "file":
        return False
    path = Path(identifier).expanduser()
    return path.exists()


def _validate_revision(revision: str) -> str:
    value = revision.strip()
    if not _COMMIT_PATTERN.match(value):
        raise ValueError(
            "Expected a commit hash (>=7 hex chars) for Hugging Face revision; "
            f"received '{revision}'"
        )
    return value


def ensure_pinned_kwargs(
    identifier: Any,
    kwargs: Mapping[str, Any] | None = None,
) -> Tuple[str | None, Dict[str, Any]]:
    """Return ``(revision, other_kwargs)`` ensuring immutable revisions."""

    norm_id = _normalize_identifier(identifier)
    other = dict(kwargs or {})
    if "commit_id" in other:
        other["commit_id"] = _validate_revision(str(other["commit_id"]))
        return other["commit_id"], other
    revision = other.pop("revision", None)
    if revision is not None:
        return _validate_revision(str(revision)), other
    if _looks_like_local(norm_id):
        return None, other
    env_revision = os.getenv(_ENV_VAR)
    if env_revision:
        return _validate_revision(env_revision), other
    if norm_id and norm_id in KNOWN_MODEL_REVISIONS:
        return KNOWN_MODEL_REVISIONS[norm_id], other
    raise ValueError(
        "Remote Hugging Face identifiers require an explicit commit hash. "
        "Set CODEX_HF_REVISION or pass revision=... at the call site."
    )


def load_from_pretrained(factory: Any, identifier: Any, **kwargs: Any) -> Any:
    """Invoke ``factory.from_pretrained`` with a verified revision."""

    revision, extra = ensure_pinned_kwargs(identifier, kwargs)
    method = getattr(factory, "from_pretrained")
    if revision is None:
        return method(identifier, **extra)
    return method(identifier, revision=revision, **extra)


__all__ = ["ensure_pinned_kwargs", "load_from_pretrained", "KNOWN_MODEL_REVISIONS"]
