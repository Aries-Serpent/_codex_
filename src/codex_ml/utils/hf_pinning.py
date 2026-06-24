"""Utilities enforcing pinned Hugging Face downloads."""

from __future__ import annotations

import logging
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class HFModelUnavailableError(RuntimeError):
    """Raised when a HuggingFace model cannot be loaded from cache or network.

    Tests that require a specific model should catch this and call
    ``pytest.skip()`` so CI runs gracefully in offline/cold-cache environments:

        try:
            tok = load_from_pretrained(AutoTokenizer, "sshleifer/tiny-gpt2")
        except HFModelUnavailableError as exc:
            pytest.skip(str(exc))
    """


# Hexadecimal commit hashes with at least 7 characters are considered immutable.
_COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{7,}$")
_ENV_VARS = ("CODEX_HF_REVISION", "HF_REVISION", "HF_MODEL_REVISION")
_LOCAL_PREFIXES = ("./", "../", "/")

# Stable revisions for built-in examples and smoke tests. These values were
# retrieved from Hugging Face's model metadata on 2025-09-25.
KNOWN_MODEL_REVISIONS: dict[str, str] = {  # pragma: allowlist secret
    "openai-community/gpt2": "607a30d783dfa663caf39e06633721c8d4cfcd7e",  # pragma: allowlist secret
    "gpt2": "607a30d783dfa663caf39e06633721c8d4cfcd7e",  # pragma: allowlist secret
    "sshleifer/tiny-gpt2": "5f91d94bd9cd7190a9f3216ff93cd1dd95f2c7be",  # pragma: allowlist secret
    "hf-internal-testing/llama-tokenizer": "99b822d16c88d1d1130b3806c97ee9d89a9c9999",  # pragma: allowlist secret  # noqa: E501
    "sentence-transformers/all-MiniLM-L6-v2": "8b3219a92973c328a8e22fadcfa821b5dc75636a",  # pragma: allowlist secret  # noqa: E501
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
) -> tuple[str | None, dict[str, Any]]:
    """Return ``(revision, other_kwargs)`` ensuring immutable revisions.

    Priority order:
    1. Explicit ``revision`` / ``commit_id`` in kwargs (caller-supplied)
    2. ``KNOWN_MODEL_REVISIONS`` — curated production pins always win over
       environment variables so test stubs like ``HF_REVISION=abcdef0``
       cannot shadow a carefully-pinned revision.
    3. Environment variables (``CODEX_HF_REVISION``, ``HF_REVISION``, …)
    4. Error — remote identifiers require an explicit hash.
    """

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
    # Check curated known revisions BEFORE env vars so that test stubs
    # (e.g. HF_REVISION=abcdef0 set by tests/models/conftest.py) cannot
    # accidentally override a legitimate pinned hash.
    if norm_id and norm_id in KNOWN_MODEL_REVISIONS:
        return KNOWN_MODEL_REVISIONS[norm_id], other
    for env_var in _ENV_VARS:
        env_revision = os.getenv(env_var)
        if env_revision:
            return _validate_revision(env_revision), other
    raise ValueError(
        "Remote Hugging Face identifiers require an explicit commit hash. "
        "Set one of {vars} or pass revision=... at the call site.".format(vars=", ".join(_ENV_VARS))
    )


def load_from_pretrained(factory: Any, identifier: Any, **kwargs: Any) -> Any:
    """Invoke ``factory.from_pretrained`` with a verified revision.

    Degradation strategy (Try best option → fallback → skip-friendly error):

    1. Try ``local_files_only=True`` — use the local HuggingFace cache.
       Fast and works fully offline when the model is pre-cached.
    2. Fall back to a full network download if the cache misses.
    3. If both fail, raise :class:`HFModelUnavailableError` — a named
       exception that tests can catch to call ``pytest.skip()`` instead of
       hard-failing in offline / cold-cache CI environments.

    Example test usage::

        try:
            tok = load_from_pretrained(AutoTokenizer, "sshleifer/tiny-gpt2")
        except HFModelUnavailableError as exc:
            pytest.skip(str(exc))
    """

    revision, extra = ensure_pinned_kwargs(identifier, kwargs)
    method = factory.from_pretrained

    call_kwargs: dict[str, Any] = dict(extra)
    if revision is not None:
        call_kwargs["revision"] = revision

    cache_exc: Exception | None = None

    # Attempt 1: local cache only (fast, works offline)
    if not call_kwargs.get("local_files_only"):
        try:
            return method(identifier, local_files_only=True, **call_kwargs)
        except (IOError, OSError) as exc:  # OSError / EnvironmentError for cache miss
            cache_exc = exc
            logger.debug(
                "HF cache miss for %s (rev=%s): %s — falling back to network",
                identifier,
                revision,
                exc,
            )

    # Attempt 2: full network download
    try:
        return method(identifier, **call_kwargs)
    except (ValueError, TypeError) as network_exc:
        # Both attempts failed — raise a named error so callers can skip gracefully
        errors = []
        if cache_exc is not None:
            errors.append(f"cache: {cache_exc}")
        errors.append(f"network: {network_exc}")
        raise HFModelUnavailableError(
            f"Model '{identifier}' (rev={revision}) is unavailable. "
            f"Errors: {'; '.join(errors)}. "
            "Pre-populate the HuggingFace cache or ensure network access."
        ) from network_exc


__all__ = [
    "KNOWN_MODEL_REVISIONS",
    "HFModelUnavailableError",
    "ensure_pinned_kwargs",
    "load_from_pretrained",
]
