"""Prompt sanitization for injection prevention.

This module provides sanitization utilities to protect against prompt injection
attacks, code execution attempts, and other malicious patterns in user-provided prompts.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

__all__ = ["PromptSanitizer"]


class PromptSanitizer:
    """Sanitizer for detecting and preventing prompt injection attacks.

    Attributes:
        INJECTION_PATTERNS: list of regex patterns for common injection attempts.
        strict: Whether to raise errors (True) or redact patterns (False).
    """

    # Common injection patterns - based on OWASP Top 10
    INJECTION_PATTERNS = [
        r"<script\b[^>]*>.*?</script>",
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onclick=",
        r"onload=",
        r"eval\(",
        r"exec\(",
        r"__import__",
        r"subprocess",
        r"os\.system",
        r"rm\s+-rf",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"INSERT\s+INTO",
        r"UPDATE\s+.*\s+SET",
    ]

    def __init__(self, strict: bool = True):
        """Initialize the sanitizer.

        Args:
            strict: If True, raise ValueError on unsafe prompts.
                    If False, redact unsafe patterns with [REDACTED].
        """
        self.strict = strict
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]

    def sanitize(self, prompt: str) -> str:
        """Sanitize prompt by removing/escaping dangerous patterns.

        Args:
            prompt: The user-provided prompt to sanitize.

        Returns:
            The sanitized prompt (unchanged if safe, redacted if non-strict).

        Raises:
            ValueError: If prompt contains unsafe patterns and strict=True.
        """
        if not prompt:
            return prompt

        original = prompt
        found_patterns: list[str] = []

        for pattern in self.patterns:
            if pattern.search(prompt):
                found_patterns.append(pattern.pattern)
                if self.strict:
                    # Raise error in strict mode
                    logger.warning(
                        "Unsafe prompt detected (pattern: %s). Prompt rejected.",
                        pattern.pattern,
                    )
                    raise ValueError(
                        f"Unsafe prompt detected (pattern: {pattern.pattern}). "
                        f"Prompt rejected for security."
                    )
                # Remove pattern in non-strict mode
                prompt = pattern.sub("[REDACTED]", prompt)

        if prompt != original:
            logger.info(
                "Prompt sanitized: %d chars changed, patterns: %s",
                len(original) - len(prompt),
                ", ".join(found_patterns),
            )

        return prompt

    def is_safe(self, prompt: str) -> bool:
        """Check if prompt is safe without modifying.

        Args:
            prompt: The prompt to check.

        Returns:
            True if prompt is safe, False if it contains unsafe patterns.
        """
        if not prompt:
            return True

        try:
            # Use strict mode for checking
            temp_sanitizer = PromptSanitizer(strict=True)
            temp_sanitizer.sanitize(prompt)
            return True
        except ValueError as e:
            type(e).__name__
            logger.debug("ValueError: <ERROR_TYPE>")
            logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
            return False

    def get_violations(self, prompt: str) -> list[str]:
        """Get list of violated patterns in the prompt.

        Args:
            prompt: The prompt to check.

        Returns:
            list of pattern strings that matched the prompt.
        """
        if not prompt:
            return []

        violations = []
        for pattern in self.patterns:
            if pattern.search(prompt):
                violations.append(pattern.pattern)

        return violations
