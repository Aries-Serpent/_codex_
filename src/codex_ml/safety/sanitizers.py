from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Pattern

try:  # pragma: no cover - optional dependency
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore[assignment]

DEFAULT_SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"-----BEGIN (?:RSA|EC|DSA) PRIVATE KEY-----"),
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"),
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


def _safe_load_yaml(policy_yaml: str) -> Dict:
    if not policy_yaml or yaml is None:
        return {}
    try:
        data = yaml.safe_load(policy_yaml)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _extend_patterns(base: List[Pattern[str]], patterns: Iterable[str] | None) -> None:
    if not patterns:
        return
    for pattern in patterns:
        try:
            compiled = re.compile(pattern)
        except Exception:
            continue
        base.append(compiled)


def sanitize_prompt(
    text: str, cfg: SafetyConfig | None = None, *, policy_yaml: str | None = None
) -> Dict:
    """Sanitise ``text`` before it is used as a prompt."""

    cfg = cfg or SafetyConfig()
    secret_patterns = list(cfg.secret_patterns)
    pii_patterns = list(cfg.pii_patterns)
    jailbreak_patterns = list(cfg.jailbreak_patterns)

    if policy_yaml:
        overrides = _safe_load_yaml(policy_yaml)
        if overrides:
            _extend_patterns(secret_patterns, overrides.get("secrets") or overrides.get("regex"))
            _extend_patterns(pii_patterns, overrides.get("pii"))
            _extend_patterns(jailbreak_patterns, overrides.get("jailbreak"))

    flags = {
        "secrets": _flag(text, secret_patterns),
        "pii": _flag(text, pii_patterns),
        "jailbreak": _flag(text, jailbreak_patterns),
    }
    tx, r1 = _redact(text, secret_patterns, "SECRET")
    tx, r2 = _redact(tx, pii_patterns, "PII")
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
