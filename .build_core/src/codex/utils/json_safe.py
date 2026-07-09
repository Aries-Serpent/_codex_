"""
Safe JSON parsing utilities for _codex_.

Provides ``safe_json_loads`` — a drop-in replacement for ``json.loads`` that
handles JSON blobs arriving from outside trusted code (CLI output, HTTP/webhook
payloads, downloaded blobs, dynamic devcontainer files).

Behaviour on ``JSONDecodeError``:
  1. Logs the source identifier, exact character position, and an 80-char
     context window around the error (control characters escaped).
  2. Sanitises C0 control characters (\\x00–\\x1f, excluding the legal JSON
     whitespace \\t \\n \\r) by replacing each byte with its Unicode escape
     sequence ``\\uXXXX``.
  3. Retries ``json.loads`` once on the sanitised string.
  4. Writes the sanitised copy to a debug artefact under
     ``/tmp/codex-json-debug/`` for offline triage (secrets redacted from
     the log message; the raw blob is **not** written to avoid leaking secrets
     in CI artefacts).

Usage::

    from codex.utils.json_safe import safe_json_loads

    data = safe_json_loads(raw, source="POST /webhook/github")
"""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# C0 control chars that are *not* valid JSON whitespace.
# JSON allows \\t (0x09), \\n (0x0a), \\r (0x0d) inside strings.
# We escape everything else in the 0x00-0x1f range.
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# Directory for debug artefacts (sanitised blobs only — no raw secrets).
_DEBUG_DIR = Path(
    os.environ.get("CODEX_JSON_DEBUG_DIR", os.path.join(tempfile.gettempdir(), "codex-json-debug"))
)  # nosec B108

# Simple secret-pattern heuristics used to suppress key=value pairs from
# log output (we log a redacted snippet, not the raw blob).
_SECRET_RE = re.compile(
    r"(token|key|secret|password|auth|bearer|credential)[\s\"':=]+\S+",
    re.IGNORECASE,
)


def _redact(text: str) -> str:
    """Replace likely secret values in *text* for safe log output."""
    return _SECRET_RE.sub(r"\1=[REDACTED]", text)


def _context_snippet(text: str, pos: int, width: int = 80) -> str:
    """Return an escaped *width*-char window centred on *pos*."""
    half = width // 2
    start = max(0, pos - half)
    end = min(len(text), pos + half)
    snippet = text[start:end]
    return repr(snippet)


def _sanitize_control_chars(text: str) -> str:
    """Replace C0 control chars (except \\t \\n \\r) with \\uXXXX escapes."""
    return _CONTROL_CHAR_RE.sub(lambda m: f"\\u{ord(m.group()):04x}", text)


def _write_debug_artifact(sanitized: str, source: str) -> Path | None:
    """Write *sanitized* JSON to a timestamped debug file; return the path."""
    try:
        _DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        safe_src = re.sub(r"[^\w]", "_", source)[:40]
        path = _DEBUG_DIR / f"sanitized_{safe_src}_{ts}.json"
        path.write_text(sanitized, encoding="utf-8")
        return path
    except OSError as exc:
        log.debug("Could not write JSON debug artefact: %s", exc)
        return None


def safe_json_loads(
    text: str | bytes,
    *,
    source: str = "<unknown>",
    **kwargs: Any,
) -> Any:
    """Parse *text* as JSON with automatic control-character sanitisation.

    Parameters
    ----------
    text:
        Raw JSON string or bytes from an external/untrusted source.
    source:
        Human-readable identifier for log messages, e.g. ``"POST /webhook/github"``
        or ``"gh api repos/…"``.  Must not contain actual secret values.
    **kwargs:
        Forwarded verbatim to ``json.loads``.

    Returns
    -------
    Any
        Parsed Python object.

    Raises
    ------
    json.JSONDecodeError
        Re-raised after sanitisation also fails, with the original error
        message preserved.
    ValueError
        If *text* is neither ``str`` nor ``bytes``.
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    elif not isinstance(text, str):
        raise ValueError(f"safe_json_loads expects str or bytes, got {type(text).__name__}")

    # Fast path — optimistic parse (no overhead for valid JSON).
    try:
        return json.loads(text, **kwargs)
    except json.JSONDecodeError as first_err:
        # ── Diagnostic logging ──────────────────────────────────────────
        snippet = _context_snippet(text, first_err.pos)
        log.warning(
            "JSONDecodeError parsing JSON from %r at pos=%d (line %d col %d): %s | context: %s",
            source,
            first_err.pos,
            first_err.lineno,
            first_err.colno,
            first_err.msg,
            _redact(snippet),
        )

        # ── Sanitise and retry ──────────────────────────────────────────
        sanitized = _sanitize_control_chars(text)
        artifact_path = _write_debug_artifact(sanitized, source)
        if artifact_path:
            log.info("Sanitised JSON blob written to %s for triage", artifact_path)

        try:
            result = json.loads(sanitized, **kwargs)
            log.info(
                "JSONDecodeError from %r resolved after sanitising control characters",
                source,
            )
            return result
        except json.JSONDecodeError as second_err:
            log.error(
                "JSONDecodeError from %r persists after sanitisation (pos=%d): %s | "
                "Sanitised blob saved to %s",
                source,
                second_err.pos,
                second_err.msg,
                artifact_path,
            )
            raise second_err from first_err
