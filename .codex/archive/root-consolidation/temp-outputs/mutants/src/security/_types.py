"""Shared security primitives.

Extracted from core.py / content_filters.py to break the cyclic import between
those two modules.  Both modules import from here; neither imports from the other.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_PROFANITY: frozenset[str] = frozenset({"foo", "barf", "bazinga", "dang"})


# ---------------------------------------------------------------------------
# Shared exception
# ---------------------------------------------------------------------------


class SecurityError(ValueError):
    """Raised when security validation fails."""


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def sanitize_text(text: str) -> str:
    """Replace known profanity tokens with ``[REDACTED]``."""
    sanitized = text
    for word in _PROFANITY:
        sanitized = re.sub(re.escape(word), "[REDACTED]", sanitized, flags=re.I)
    return sanitized
