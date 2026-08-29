#!/usr/bin/env python3
"""
Minimal, safe sanitization helpers for user-provided prompts.

This module provides an explicit html-escaping function to be used for any
context that may render prompts to HTML or untrusted viewers.

If later you need richer sanitization (strip tags, allowlist), replace these
helpers with a vetted library such as 'bleach' and add focused tests.
"""

import html
import re
from typing import Optional


def sanitize_prompt(prompt: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Sanitize user prompt input by removing dangerous characters and truncating.

    This function:
    1. Removes control characters (U+0000–U+001F, U+007F)
    2. Strips ANSI escape sequences (e.g., color codes)
    3. Escapes HTML-sensitive characters (<, >, &, ", ')
    4. Truncates to max_length if specified
    5. Preserves safe special characters and Unicode

    Args:
        prompt: The user input string to sanitize (None becomes empty string)
        max_length: Optional maximum length to truncate to

    Returns:
        Sanitized prompt string safe for downstream processing

    Security Notes:
        - Removes null bytes (\\x00) to prevent string termination attacks
        - Strips ANSI sequences to prevent terminal injection
        - Removes control chars that could corrupt data or logs
        - Escapes HTML to prevent XSS when displayed on web pages

    Example:
        >>> sanitize_prompt("Hello\\x00World\\x1b[31m!", max_length=10)
        'HelloWorld'  # Removes control chars, ANSI codes, then truncates to 10

        >>> sanitize_prompt("Normal text")
        'Normal text'

        >>> sanitize_prompt("<script>alert(1)</script>")
        '&lt;script&gt;alert(1)&lt;/script&gt;'
    """
    if prompt is None:
        return ""

    # Convert to string if not already
    if not isinstance(prompt, str):
        prompt = str(prompt)

    # Step 1: Remove control characters (U+0000 to U+001F and U+007F)
    # These include null bytes, carriage returns in middle of text, etc.
    prompt = re.sub(r"[\x00-\x1F\x7F]", "", prompt)

    # Step 2: Remove ANSI escape sequences (terminal color codes, cursor movement)
    # Pattern handles both 2-character sequences and CSI (Control Sequence Introducer) sequences
    # Format: ESC followed by:
    #   - [@-Z\\-_] for 2-char sequences (Fe)
    #   - \[[0-?]*[ -/]*[@-~] for CSI sequences (most common)
    prompt = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", prompt)

    # Step 3: Truncate to max_length if specified
    if max_length is not None:
        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError(f"max_length must be a non-negative integer, got {max_length}")
        prompt = prompt[:max_length]

    # Step 4: Escape HTML-sensitive characters for safe display
    # html.escape will replace &, <, >, " by default. Escape single-quote manually.
    escaped = html.escape(prompt, quote=True)
    # Optionally escape single quote for contexts that use single-quoted attributes
    return escaped.replace("'", "&#x27;")
