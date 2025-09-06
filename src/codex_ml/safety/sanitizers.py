from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern

DEFAULT_SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]

DEFAULT_PII_PATTERNS = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"),
    re.compile(r"\+?\d[\d .-]{8,}\d"),
]

DEFAULT_JAILBREAK_PATTERNS = [
    re.compile(r"(?i)ignore all (previous|prior) instructions"),
    re.compile(r"(?i)jailbreak|do anything now"),
]


@dataclass
class SafetyConfig:
    """Configuration for prompt and output sanitisation."""

    strict: bool = False
    max_output_chars: int = 8000
    secret_patterns: List[Pattern[str]] = field(default_factory=lambda: DEFAULT_SECRET_PATTERNS)
    pii_patterns: List[Pattern[str]] = field(default_factory=lambda: DEFAULT_PII_PATTERNS)
    jailbreak_patterns: List[Pattern[str]] = field(
        default_factory=lambda: DEFAULT_JAILBREAK_PATTERNS
    )


def _flag(text: str, patterns: List[Pattern[str]]) -> bool:
    return any(p.search(text) for p in patterns)


def _redact(text: str, patterns: List[Pattern[str]], label: str) -> tuple[str, int]:
    count = 0
    for p in patterns:
        text, n = p.subn(f"«REDACTED:{label}»", text)
        count += n
    return text, count


def sanitize_prompt(text: str, cfg: SafetyConfig | None = None) -> Dict:
    """Sanitise ``text`` before it is used as a prompt."""

    cfg = cfg or SafetyConfig()
    flags = {
        "secrets": _flag(text, cfg.secret_patterns),
        "pii": _flag(text, cfg.pii_patterns),
        "jailbreak": _flag(text, cfg.jailbreak_patterns),
    }
    tx, r1 = _redact(text, cfg.secret_patterns, "SECRET")
    tx, r2 = _redact(tx, cfg.pii_patterns, "PII")
    return {"text": tx, "flags": flags, "redactions": {"secrets": r1, "pii": r2}}


def sanitize_output(text: str, cfg: SafetyConfig | None = None) -> Dict:
    """Redact secrets/PII and optionally truncate model output."""

    cfg = cfg or SafetyConfig()
    tx, r1 = _redact(text, cfg.secret_patterns, "SECRET")
    tx, r2 = _redact(tx, cfg.pii_patterns, "PII")
    truncated = False
    if len(tx) > cfg.max_output_chars:
        tx = tx[: cfg.max_output_chars] + "…"
        truncated = True
    flags = {"truncated": truncated}
    return {"text": tx, "flags": flags, "redactions": {"secrets": r1, "pii": r2}}
