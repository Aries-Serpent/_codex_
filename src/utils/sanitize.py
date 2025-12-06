#!/usr/bin/env python3
"""
Minimal, safe sanitization helpers for user-provided prompts.

This module provides an explicit html-escaping function to be used for any
context that may render prompts to HTML or untrusted viewers.

If later you need richer sanitization (strip tags, allowlist), replace these
helpers with a vetted library such as 'bleach' and add focused tests.
"""
import html
from typing import Optional


def sanitize_prompt(prompt: Optional[str]) -> str:
    """
    Escape a prompt string for safe HTML embedding / display.
    - None -> empty string
    - returns a string where <, >, &, ", ' are escaped

    NOTE: This *does not* perform semantic validation (e.g., remove SQL),
    it only escapes HTML-sensitive characters to prevent XSS when prompts
    are displayed on web pages / logs that permit HTML.
    """
    if prompt is None:
        return ""
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(str(prompt), quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    escaped = escaped.replace("'", "&#x27;")
    return escaped
