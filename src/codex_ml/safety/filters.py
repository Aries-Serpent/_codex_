# WHY: Introduce policy-driven safety filters with sanitization hooks
# RISK: Moderate - replaces legacy filters implementation; relies on policy parsing
# ROLLBACK: Revert src/codex_ml/safety/filters.py, configs/safety/policy.yaml, tests/safety/test_filters.py
# HOW-TO-TEST: pytest tests/safety/test_filters.py (module skipped pending integration)
from __future__ import annotations

import importlib
import logging
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple

import yaml

from codex_ml.utils.error_log import log_error

logger = logging.getLogger(__name__)

REDACT_TOKEN = "{REDACTED}"
POLICY_ENV_VAR = "CODEX_SAFETY_POLICY_PATH"
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs" / "safety" / "policy.yaml"


@dataclass(frozen=True)
class RuleMatch:
    """Represents a triggered policy rule."""

    rule_id: str
    action: str
    fragment: str
    description: Optional[str] = None
    span: Optional[Tuple[int, int]] = None

    @property
    def is_block(self) -> bool:
        return self.action == "block"

    @property
    def is_allow(self) -> bool:
        return self.action == "allow"


@dataclass
class PolicyRule:
    """Single literal or regex policy rule."""

    rule_id: str
    action: str
    pattern: str
    kind: str = "literal"
    flags: int = 0
    description: Optional[str] = None
    _compiled: Optional[re.Pattern[str]] = field(default=None, init=False, repr=False)

    def matches(self, text: str) -> Optional[RuleMatch]:
        if self.kind == "literal":
            haystack = text.lower()
            needle = self.pattern.lower()
            idx = haystack.find(needle)
            if idx != -1:
                fragment = text[idx : idx + len(self.pattern)]
                return RuleMatch(
                    self.rule_id,
                    self.action,
                    fragment,
                    self.description,
                    span=(idx, idx + len(self.pattern)),
                )
            return None

        compiled = self._get_compiled()
        match = compiled.search(text)
        if match:
            fragment = match.group(0)
            return RuleMatch(
                self.rule_id,
                self.action,
                fragment,
                self.description,
                span=match.span(),
            )
        return None

    def redact(self, text: str, token: str) -> str:
        if self.action not in {"redact", "block"}:
            return text
        if self.kind == "literal":
            return re.sub(re.escape(self.pattern), token, text, flags=re.IGNORECASE)
        compiled = self._get_compiled()
        return compiled.sub(token, text)

    def _get_compiled(self) -> re.Pattern[str]:
        if self.kind != "regex":
            raise ValueError("Attempted to compile non-regex policy rule")
        if self._compiled is None:
            self._compiled = re.compile(self.pattern, self.flags)
        return self._compiled


@dataclass
class SafetyPolicy:
    enabled: bool = True
    bypass: bool = False
    redaction_token: str = REDACT_TOKEN
    rules: Tuple[PolicyRule, ...] = field(default_factory=tuple)

    @classmethod
    def load(cls, path: Optional[Path | str] = None) -> "SafetyPolicy":
        candidates: List[Path] = []
        if path:
            candidates.append(Path(path))
        env_path = os.getenv(POLICY_ENV_VAR)
        if env_path:
            candidates.append(Path(env_path))
        candidates.append(DEFAULT_POLICY_PATH)

        for candidate in candidates:
            if candidate.exists():
                try:
                    data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
                    return cls.from_dict(data)
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning("Failed to load safety policy from %s: %s", candidate, exc)
                    break

        return cls.from_dict(DEFAULT_POLICY_DATA)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SafetyPolicy":
        enabled = bool(data.get("enabled", True))
        bypass = bool(data.get("bypass", False))
        redaction_token = str(data.get("redaction_token", REDACT_TOKEN))
        rules_data = data.get("rules", [])
        rules: List[PolicyRule] = []
        if isinstance(rules_data, Iterable):
            for idx, item in enumerate(rules_data):
                if not isinstance(item, dict):
                    continue
                action = str(item.get("action", "block")).lower().strip()
                if action not in {"block", "allow", "redact"}:
                    continue
                match_spec = item.get("match") or {}
                kind, pattern = _parse_match(match_spec)
                if kind is None or pattern is None:
                    continue
                rule_id = str(item.get("id") or f"rule_{idx}")
                flags = _parse_flags(item.get("flags"))
                description = item.get("description")
                rules.append(
                    PolicyRule(
                        rule_id=rule_id,
                        action=action,
                        pattern=pattern,
                        kind=kind,
                        flags=flags,
                        description=description,
                    )
                )
        return cls(
            enabled=enabled, bypass=bypass, redaction_token=redaction_token, rules=tuple(rules)
        )


@dataclass(frozen=True)
class SafetyResult:
    stage: str
    allowed: bool
    sanitized_text: str
    matches: Tuple[RuleMatch, ...] = tuple()

    @property
    def blocked_rules(self) -> Tuple[str, ...]:
        return tuple(match.rule_id for match in self.matches if match.is_block)


class SafetyFilters:
    def __init__(self, policy: Optional[SafetyPolicy] = None):
        self.policy = policy or SafetyPolicy.load()

    @classmethod
    def from_defaults(cls) -> "SafetyFilters":
        return cls(_cached_default_policy())

    def evaluate(self, text: str) -> SafetyResult:
        if not self.policy.enabled or self.policy.bypass:
            return SafetyResult(
                stage="unspecified", allowed=True, sanitized_text=text, matches=tuple()
            )

        matches, sanitized_allowed, sanitized_blocked = self._scan(text)
        allow_matches = [match for match in matches if match.is_allow]
        overridden_blocks = {
            match
            for match in matches
            if match.is_block and self._allow_overrides_block(match, allow_matches)
        }
        unresolved_blocks = [
            match for match in matches if match.is_block and match not in overridden_blocks
        ]

        if unresolved_blocks:
            return SafetyResult(
                stage="unspecified",
                allowed=False,
                sanitized_text=sanitized_blocked,
                matches=tuple(matches),
            )

        if not self._external_allows(text):
            extended_matches = tuple(
                list(matches) + [RuleMatch("external", "block", "", "External classifier veto")]
            )
            return SafetyResult(
                stage="unspecified",
                allowed=False,
                sanitized_text=sanitized_blocked,
                matches=extended_matches,
            )

        return SafetyResult(
            stage="unspecified",
            allowed=True,
            sanitized_text=sanitized_allowed,
            matches=tuple(match for match in matches if match not in overridden_blocks),
        )

    def sanitize(self, text: str, *, stage: str) -> SafetyResult:
        result = self.evaluate(text)
        return SafetyResult(
            stage=stage,
            allowed=result.allowed,
            sanitized_text=result.sanitized_text,
            matches=result.matches,
        )

    def is_allowed(self, text: str) -> Tuple[bool, List[str]]:
        result = self.evaluate(text)
        block_ids = sorted(result.blocked_rules)
        return result.allowed, block_ids

    def apply(self, text: str) -> str:
        result = self.evaluate(text)
        return result.sanitized_text

    def mask_logits(self, logits, banned_token_ids: set[int]):
        neg_inf = float("-inf")
        try:
            if hasattr(logits, "shape"):
                last = logits.shape[-1]
                for tid in banned_token_ids:
                    if 0 <= tid < last:
                        logits[..., tid] = neg_inf
                return logits
        except Exception:  # pragma: no cover - defensive
            pass
        if isinstance(logits, list):
            for tid in banned_token_ids:
                if 0 <= tid < len(logits):
                    logits[tid] = neg_inf
            return logits
        return logits

    def _scan(self, text: str) -> Tuple[List[RuleMatch], str, str]:
        matches: List[RuleMatch] = []
        sanitized_allowed = text
        sanitized_blocked = text
        for rule in self.policy.rules:
            match = rule.matches(text)
            if match:
                matches.append(match)
                action = match.action
                if action == "redact":
                    sanitized_allowed = rule.redact(sanitized_allowed, self.policy.redaction_token)
                    sanitized_blocked = rule.redact(sanitized_blocked, self.policy.redaction_token)
                elif action == "block":
                    sanitized_blocked = rule.redact(sanitized_blocked, self.policy.redaction_token)
        return matches, sanitized_allowed, sanitized_blocked

    @staticmethod
    def _allow_overrides_block(block_match: RuleMatch, allow_matches: List[RuleMatch]) -> bool:
        if not allow_matches:
            return False
        block_span = block_match.span
        for allow_match in allow_matches:
            allow_span = allow_match.span
            if block_span and allow_span:
                if _spans_overlap(block_span, allow_span):
                    return True
            else:
                if _fragments_overlap(block_match.fragment, allow_match.fragment):
                    return True
        return False

    def _external_allows(self, text: str) -> bool:
        hook = os.getenv("CODEX_SAFETY_CLASSIFIER")
        if not hook:
            return True
        try:
            mod_name, fn_name = hook.split(":", 1)
            fn = getattr(importlib.import_module(mod_name), fn_name)
        except Exception as exc:  # pragma: no cover - optional feature
            log_error("safety_classifier", str(exc), hook)
            return True
        try:
            return bool(fn(text))
        except Exception as exc:  # pragma: no cover - optional feature
            log_error("safety_classifier", str(exc), hook)
            return True


def sanitize_prompt(prompt: str, *, filters: Optional[SafetyFilters] = None) -> SafetyResult:
    active_filters = filters or SafetyFilters.from_defaults()
    return active_filters.sanitize(prompt, stage="prompt")


def sanitize_output(output: str, *, filters: Optional[SafetyFilters] = None) -> SafetyResult:
    active_filters = filters or SafetyFilters.from_defaults()
    return active_filters.sanitize(output, stage="output")


def _spans_overlap(first: Tuple[int, int], second: Tuple[int, int]) -> bool:
    return max(first[0], second[0]) < min(first[1], second[1])


def _fragments_overlap(first: str, second: str) -> bool:
    if not first or not second:
        return False
    left = first.lower()
    right = second.lower()
    return left in right or right in left


@lru_cache(maxsize=1)
def _cached_default_policy() -> SafetyPolicy:
    return SafetyPolicy.load()


DEFAULT_POLICY_DATA: dict[str, Any] = {
    "enabled": True,
    "bypass": False,
    "redaction_token": REDACT_TOKEN,
    "rules": [
        {"id": "deny.shell.rm_root", "action": "block", "match": {"literal": "rm -rf /"}},
        {"id": "deny.shell.format_c", "action": "block", "match": {"literal": "format c:"}},
        {"id": "deny.shell.mkfs", "action": "block", "match": {"literal": "mkfs"}},
        {"id": "deny.shell.shutdown", "action": "block", "match": {"literal": "shutdown -h now"}},
        {"id": "deny.secret.credit_card", "action": "block", "match": {"literal": "credit card"}},
        {"id": "deny.secret.ssn", "action": "block", "match": {"literal": "ssn"}},
        {
            "id": "deny.secret.ssn_phrase",
            "action": "block",
            "match": {"literal": "social security number"},
        },
        {"id": "deny.sql.drop_database", "action": "block", "match": {"literal": "drop database"}},
        {
            "id": "deny.weapon.schematic",
            "action": "block",
            "match": {"literal": "weapon schematic"},
        },
        {"id": "deny.selfharm", "action": "block", "match": {"literal": "kill yourself"}},
        {"id": "allow.shell.rm_build", "action": "allow", "match": {"literal": "rm -rf build"}},
        {
            "id": "allow.sql.drop_schema_example",
            "action": "allow",
            "match": {"literal": "drop database schema_example"},
        },
        {
            "id": "deny.secret.aws_access_key",
            "action": "block",
            "match": {"regex": r"AKIA[0-9A-Z]{16}"},
        },
        {
            "id": "deny.secret.password_key",
            "action": "redact",
            "match": {"regex": r"(?i)password\\s*[:=]\\s*[^\\s]+"},
        },
        {
            "id": "deny.secret.api_key",
            "action": "redact",
            "match": {"regex": r"(?i)api[_-]?key\\s*[:=]\\s*[^\\s]+"},
        },
        {
            "id": "deny.secret.ssn_regex",
            "action": "block",
            "match": {"regex": r"\\b\\d{3}-\\d{2}-\\d{4}\\b"},
        },
        {
            "id": "deny.shell.rm_root_regex",
            "action": "block",
            "match": {"regex": r"\\b(rm\\s+-rf\\s+/(?!\\w))"},
        },
        {
            "id": "allow.secret.test_password",
            "action": "allow",
            "match": {"regex": r"(?i)test(_|-)?password"},
        },
    ],
}


FLAG_LOOKUP = {
    "IGNORECASE": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "VERBOSE": re.VERBOSE,
}


def _parse_match(match_spec: Any) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(match_spec, dict):
        return None, None
    if "literal" in match_spec:
        pattern = match_spec["literal"]
        if pattern is None:
            return None, None
        return "literal", str(pattern)
    if "regex" in match_spec:
        pattern = match_spec["regex"]
        if pattern is None:
            return None, None
        return "regex", str(pattern)
    return None, None


def _parse_flags(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    flags = 0
    values: Iterable[Any]
    if isinstance(value, str):
        values = (part.strip() for part in value.split("|"))
    elif isinstance(value, Iterable):
        values = value
    else:
        return 0
    for item in values:
        if not isinstance(item, str):
            continue
        name = item.strip().upper()
        flags |= FLAG_LOOKUP.get(name, 0)
    return flags


__all__ = [
    "SafetyFilters",
    "SafetyPolicy",
    "PolicyRule",
    "SafetyResult",
    "sanitize_prompt",
    "sanitize_output",
    "RuleMatch",
]
