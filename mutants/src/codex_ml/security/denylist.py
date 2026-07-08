"""
Denylist Module

This module provides functionality for denylist.

Usage:
    from security.denylist import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class DenylistViolation(RuntimeError):
    """Raised when a prompt violates denylist policy."""


@dataclass
class DenylistRules:
    sensitive_terms: list[str]
    redaction_patterns: list[tuple[re.Pattern[str], str]]
    blocked_actions: list[str]
    blocked_prompt_patterns: list[str]


def load_denylist(path: str | Path) -> DenylistRules:
    """Load denylist rules from a YAML file."""

    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Denylist configuration missing: {candidate}")

    payload: Mapping[str, Any] = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}

    sensitive_terms_raw = payload.get("sensitive_terms", [])
    sensitive_terms = [
        str(term).lower()
        for term in (sensitive_terms_raw if isinstance(sensitive_terms_raw, list) else [])
    ]

    blocked_actions_raw = payload.get("blocked_actions", [])
    blocked_actions = [
        str(action)
        for action in (blocked_actions_raw if isinstance(blocked_actions_raw, list) else [])
    ]

    blocked_patterns_raw = payload.get("blocked_prompt_patterns", [])
    blocked_prompt_patterns = [
        str(pattern).lower()
        for pattern in (blocked_patterns_raw if isinstance(blocked_patterns_raw, list) else [])
    ]

    compiled_patterns: list[tuple[re.Pattern[str], str]] = []
    redaction_raw = payload.get("redaction_patterns", [])
    if isinstance(redaction_raw, list):
        for item in redaction_raw:
            if isinstance(item, dict):
                pattern_text = str(item.get("pattern", ""))
                replacement = str(item.get("replacement", "[REDACTED]"))
                compiled_patterns.append(
                    (re.compile(pattern_text, flags=re.IGNORECASE), replacement)
                )

    return DenylistRules(
        sensitive_terms=sensitive_terms,
        redaction_patterns=compiled_patterns,
        blocked_actions=blocked_actions,
        blocked_prompt_patterns=blocked_prompt_patterns,
    )


class DenylistEnforcer:
    """Evaluate prompts against a loaded denylist."""

    def __init__(self, rules: DenylistRules) -> None:
        self.rules = rules

    @classmethod
    def from_yaml(cls, path: str | Path) -> DenylistEnforcer:
        return cls(load_denylist(path))

    def is_prompt_allowed(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        if any(term in prompt_lower for term in self.rules.sensitive_terms):
            return False
        if any(pattern in prompt_lower for pattern in self.rules.blocked_prompt_patterns):
            return False
        return all(not compiled.search(prompt) for compiled, _ in self.rules.redaction_patterns)

    def ensure_allowed(self, prompt: str) -> None:
        if not self.is_prompt_allowed(prompt):
            raise DenylistViolation("Prompt violates denylist rules")

    def redact(self, prompt: str) -> str:
        """Apply redaction patterns to a prompt."""

        redacted = prompt
        for compiled, replacement in self.rules.redaction_patterns:
            redacted = compiled.sub(replacement, redacted)
        return redacted

    def blocked_actions(self) -> Iterable[str]:
        return self.rules.blocked_actions


__all__ = ["DenylistEnforcer", "DenylistRules", "DenylistViolation", "load_denylist"]
