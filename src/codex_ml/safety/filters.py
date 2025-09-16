"""Safety policy enforcement utilities with logging support."""

from __future__ import annotations

import importlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

try:  # pragma: no cover - optional dependency
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore[assignment]

from codex_ml.utils.error_log import log_error

logger = logging.getLogger(__name__)

REDACT_TOKEN = "{REDACTED}"
POLICY_ENV_VAR = "CODEX_SAFETY_POLICY_PATH"
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs" / "safety" / "policy.yaml"


def _ensure_sequence(value: Any) -> Sequence[Any]:
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    if isinstance(value, Sequence):
        return value
    return [value]


_FLAG_LOOKUP = {
    "I": re.IGNORECASE,
    "IGNORECASE": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "M": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "S": re.DOTALL,
}


def _parse_flags(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    flags = 0
    if isinstance(value, str):
        parts = value.split("|")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        parts = value
    else:
        return 0
    for item in parts:
        if isinstance(item, str):
            flags |= _FLAG_LOOKUP.get(item.strip().upper(), 0)
    return flags


def _load_policy_file(path: Path) -> Optional[Mapping[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            if isinstance(data, Mapping):
                return data
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to parse YAML policy %s: %s", path, exc)
    try:
        data = json.loads(text)
        if isinstance(data, Mapping):
            return data
    except json.JSONDecodeError:
        pass
    logger.warning("Policy file %s is not valid JSON or YAML", path)
    return None


@dataclass(frozen=True)
class RuleMatch:
    """Represents a triggered policy rule."""

    rule_id: str
    action: str
    fragment: str
    description: Optional[str] = None
    span: Optional[Tuple[int, int]] = None
    severity: Optional[str] = None

    def overlaps(self, other: "RuleMatch") -> bool:
        if self.span and other.span:
            s1, e1 = self.span
            s2, e2 = other.span
            return s1 < e2 and s2 < e1
        if self.fragment and other.fragment:
            a = self.fragment.lower()
            b = other.fragment.lower()
            return a in b or b in a
        return False


def _match_to_dict(match: RuleMatch) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "rule_id": match.rule_id,
        "action": match.action,
        "fragment": match.fragment,
    }
    if match.description is not None:
        payload["description"] = match.description
    if match.span is not None:
        payload["span"] = list(match.span)
    if match.severity is not None:
        payload["severity"] = match.severity
    return payload


@dataclass
class PolicyRule:
    """Single policy rule compiled for fast matching."""

    rule_id: str
    action: str
    description: Optional[str] = None
    severity: Optional[str] = None
    replacement: Optional[str] = None
    patterns: Tuple[re.Pattern[str], ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Optional["PolicyRule"]:
        rule_id = str(data.get("id") or data.get("rule_id") or "")
        action = str(data.get("action", "block")).lower().strip()
        if not rule_id or action not in {"block", "allow", "redact"}:
            return None
        match_spec = data.get("match")
        if not isinstance(match_spec, Mapping):
            return None
        literals = []
        for key in ("literal", "literals"):
            if key in match_spec:
                literals.extend(_ensure_sequence(match_spec[key]))
        regexes = []
        for key in ("regex", "patterns"):
            if key in match_spec:
                regexes.extend(_ensure_sequence(match_spec[key]))
        compiled: list[re.Pattern[str]] = []
        lit_flags = _parse_flags(match_spec.get("literal_flags")) or re.IGNORECASE
        for literal in literals:
            if literal is None:
                continue
            compiled.append(re.compile(re.escape(str(literal)), lit_flags))
        regex_flags = _parse_flags(match_spec.get("flags"))
        for pattern in regexes:
            if pattern is None:
                continue
            compiled.append(re.compile(str(pattern), regex_flags))
        if not compiled:
            return None
        return cls(
            rule_id=rule_id,
            action=action,
            description=data.get("description"),
            severity=data.get("severity"),
            replacement=str(data.get("replacement")) if data.get("replacement") else None,
            patterns=tuple(compiled),
        )

    def matches(self, text: str) -> list[RuleMatch]:
        hits: list[RuleMatch] = []
        for regex in self.patterns:
            for match in regex.finditer(text):
                hits.append(
                    RuleMatch(
                        rule_id=self.rule_id,
                        action=self.action,
                        fragment=match.group(0),
                        description=self.description,
                        span=match.span(),
                        severity=self.severity,
                    )
                )
        return hits

    def substitute(self, text: str, token: str) -> str:
        replacement = self.replacement or token
        for regex in self.patterns:
            text = regex.sub(replacement, text)
        return text


@dataclass
class SafetyPolicy:
    enabled: bool = True
    bypass: bool = False
    redaction_token: str = REDACT_TOKEN
    log_path: Optional[str] = None
    rules: Tuple[PolicyRule, ...] = field(default_factory=tuple)
    log_path: Optional[Path] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SafetyPolicy":
        enabled = bool(data.get("enabled", True))
        bypass = bool(data.get("bypass", False))
        token = str(data.get("redaction_token", REDACT_TOKEN))
        log_path = data.get("log_path")
        rules_data = data.get("rules", [])
        rules: list[PolicyRule] = []
        if isinstance(rules_data, Iterable):
            for item in rules_data:
                if isinstance(item, Mapping):
                    rule = PolicyRule.from_dict(item)
                    if rule is not None:
                        rules.append(rule)
        return cls(
            enabled=enabled,
            bypass=bypass,
            redaction_token=token,
            log_path=str(log_path) if log_path else None,
            rules=tuple(rules),
        )

    @classmethod
    def load(cls, path: Optional[Path | str] = None) -> "SafetyPolicy":
        candidates: list[Path] = []
        if path:
            candidates.append(Path(path))
        env_path = os.getenv(POLICY_ENV_VAR)
        if env_path:
            candidates.append(Path(env_path))
        candidates.append(DEFAULT_POLICY_PATH)
        for candidate in candidates:
            try:
                if candidate.exists():
                    data = _load_policy_file(candidate)
                    if data:
                        policy = cls.from_dict(data)
                        return policy
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to load safety policy from %s: %s", candidate, exc)
        return cls.from_dict(DEFAULT_POLICY_DATA)


@dataclass(frozen=True)
class SafetyResult:
    stage: str
    allowed: bool
    sanitized_text: str
    matches: Tuple[dict[str, Any], ...] = field(default_factory=tuple)
    blocking_matches: Tuple[dict[str, Any], ...] = field(default_factory=tuple)
    bypassed: bool = False

    @property
    def blocked_rules(self) -> Tuple[str, ...]:
        return tuple(
            match.get("rule_id", "") for match in self.blocking_matches if match.get("rule_id")
        )


class SafetyViolation(RuntimeError):
    """Raised when safety policy enforcement blocks text."""

    def __init__(self, decision: SafetyResult) -> None:
        self.decision = decision
        self.stage = decision.stage
        blocked = ", ".join(decision.blocked_rules) or "policy"
        super().__init__(f"Safety violation during {self.stage}: blocked by {blocked}")


class SafetyFilters:
    """Evaluate text against a safety policy."""

    def __init__(self, policy: SafetyPolicy, *, policy_path: Optional[Path | str] = None) -> None:
        self.policy = policy
        self.policy_path = Path(policy_path) if policy_path else None
        self._log_path = Path(policy.log_path) if policy.log_path else None

    @classmethod
    def from_defaults(cls) -> "SafetyFilters":
        policy = SafetyPolicy.from_dict(DEFAULT_POLICY_DATA)
        return cls(policy, policy_path=DEFAULT_POLICY_PATH)

    @classmethod
    def from_policy_file(cls, path: Optional[Path | str]) -> "SafetyFilters":
        policy = SafetyPolicy.load(path)
        return cls(policy, policy_path=path)

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

    def _log_match(
        self,
        *,
        stage: str,
        match: RuleMatch,
        action: str,
        result: SafetyResult,
    ) -> None:
        if not self._log_path:
            return
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stage": stage,
                "action": action,
                "rule_id": match.rule_id,
                "fragment": match.fragment,
                "allowed": result.allowed,
                "bypassed": result.bypassed,
                "policy_path": str(self.policy_path) if self.policy_path else None,
            }
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Failed to log safety event: %s", exc)

    def evaluate(
        self,
        text: str,
        *,
        stage: str = "unspecified",
        bypass: bool = False,
    ) -> SafetyResult:
        stage = stage or "unspecified"
        if not self.policy.enabled:
            return SafetyResult(stage, True, text)
        raw_matches: list[RuleMatch] = []
        block_matches: list[RuleMatch] = []
        allow_matches: list[RuleMatch] = []
        sanitized = text
        for rule in self.policy.rules:
            rule_matches = rule.matches(text)
            if not rule_matches:
                continue
            raw_matches.extend(rule_matches)
            if rule.action == "block":
                block_matches.extend(rule_matches)
            elif rule.action == "allow":
                allow_matches.extend(rule_matches)
            if rule.action in {"block", "redact"}:
                sanitized = rule.substitute(sanitized, self.policy.redaction_token)
        if not self._external_allows(text):
            external_match = RuleMatch(
                rule_id="external",
                action="block",
                fragment="",
                description="External classifier veto",
            )
            raw_matches.append(external_match)
            block_matches.append(external_match)
        active_blocks: list[RuleMatch] = []
        if block_matches:
            for match in block_matches:
                overridden = any(match.overlaps(allow_match) for allow_match in allow_matches)
                if not overridden:
                    active_blocks.append(match)
        effective_bypass = bypass or self.policy.bypass
        allowed = not active_blocks
        bypassed = effective_bypass and bool(active_blocks)
        serialised_matches = tuple(_match_to_dict(m) for m in raw_matches)
        serialised_blocks = tuple(_match_to_dict(m) for m in active_blocks)
        result = SafetyResult(
            stage=stage,
            allowed=allowed or effective_bypass,
            sanitized_text=sanitized,
            matches=serialised_matches,
            blocking_matches=serialised_blocks,
            bypassed=bypassed,
        )
        for match in raw_matches:
            log_action = match.action
            if match.action == "block":
                if match in active_blocks:
                    log_action = "bypass" if bypassed else "block"
                else:
                    log_action = "allow"
            self._log_match(stage=stage, match=match, action=log_action, result=result)
        return result

    def enforce(
        self,
        text: str,
        *,
        stage: str = "unspecified",
        bypass: bool = False,
    ) -> str:
        result = self.evaluate(text, stage=stage, bypass=bypass)
        if result.allowed:
            return result.sanitized_text
        raise SafetyViolation(result)

    def sanitize(self, text: str, *, stage: str) -> SafetyResult:
        return self.evaluate(text, stage=stage)

    def apply(self, text: str, *, stage: str) -> str:
        return self.evaluate(text, stage=stage).sanitized_text

    def is_allowed(self, text: str) -> Tuple[bool, list[str]]:
        result = self.evaluate(text)
        return result.allowed, list(result.blocked_rules)

    def mask_logits(self, logits: Any, banned_token_ids: set[int]):
        neg_inf = float("-inf")
        try:
            import numpy as np  # pragma: no cover - optional dependency

            if isinstance(logits, np.ndarray):
                if banned_token_ids:
                    logits[(..., tuple(banned_token_ids))] = neg_inf
                return logits
        except Exception:  # pragma: no cover - optional dependency
            pass
        if isinstance(logits, list):
            for tid in banned_token_ids:
                if 0 <= tid < len(logits):
                    logits[tid] = neg_inf
            return logits
        for tid in banned_token_ids:
            try:
                logits[tid] = neg_inf
            except Exception:  # pragma: no cover - best effort
                continue
        return logits


def sanitize_prompt(prompt: str, *, filters: Optional[SafetyFilters] = None) -> SafetyResult:
    active_filters = filters or SafetyFilters.from_defaults()
    return active_filters.sanitize(prompt, stage="prompt")


def sanitize_output(output: str, *, filters: Optional[SafetyFilters] = None) -> SafetyResult:
    active_filters = filters or SafetyFilters.from_defaults()
    return active_filters.sanitize(output, stage="output")


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
            "match": {"regex": r"(?i)password\s*[:=]\s*[^\s]+"},
        },
        {
            "id": "deny.secret.api_key",
            "action": "redact",
            "match": {"regex": r"(?i)api[_-]?key\s*[:=]\s*[^\s]+"},
        },
    ],
}


__all__ = [
    "SafetyFilters",
    "SafetyPolicy",
    "PolicyRule",
    "SafetyResult",
    "SafetyViolation",
    "sanitize_prompt",
    "sanitize_output",
    "RuleMatch",
    "SafetyViolation",
]
