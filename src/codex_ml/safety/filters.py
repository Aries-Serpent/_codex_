from __future__ import annotations

import ast
import hashlib
import importlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore[assignment]

from codex_ml.utils.error_log import log_error

logger = logging.getLogger(__name__)

REDACT_TOKEN = "{REDACTED}"
POLICY_ENV_VAR = "CODEX_SAFETY_POLICY_PATH"
BYPASS_ENV_VAR = "CODEX_SAFETY_BYPASS"
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs" / "safety" / "policy.yaml"
DEFAULT_LOG_PATH = Path(".codex/safety/events.ndjson")


@dataclass(frozen=True)
class RuleMatch:
    """Represents a triggered policy rule."""

    rule_id: str
    action: str
    fragment: str
    description: Optional[str] = None
    span: Optional[Tuple[int, int]] = None
    severity: Optional[str] = None
    metadata: Tuple[Tuple[str, Any], ...] = field(default_factory=tuple)

    @property
    def is_block(self) -> bool:
        return self.action == "block"

    @property
    def is_allow(self) -> bool:
        return self.action == "allow"


def _spans_overlap(span_a: Tuple[int, int], span_b: Tuple[int, int]) -> bool:
    start = max(span_a[0], span_b[0])
    end = min(span_a[1], span_b[1])
    return start < end


def _fragments_overlap(fragment_a: str, fragment_b: str) -> bool:
    if not fragment_a or not fragment_b:
        return False
    a_norm = fragment_a.lower()
    b_norm = fragment_b.lower()
    return a_norm in b_norm or b_norm in a_norm


@dataclass
class PolicyRule:
    """Single literal or regex policy rule."""

    rule_id: str
    action: str
    pattern: str
    kind: str = "literal"
    flags: int = 0
    description: Optional[str] = None
    severity: Optional[str] = None
    applies_to: Tuple[str, ...] = ("prompt", "output")
    replacement: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    _compiled: Optional[re.Pattern[str]] = field(default=None, init=False, repr=False)
    _literal_regex: Optional[re.Pattern[str]] = field(default=None, init=False, repr=False)

    def applies_to_stage(self, stage: str) -> bool:
        return stage in self.applies_to or stage == "unspecified"

    def iter_matches(self, text: str) -> Iterator[RuleMatch]:
        regex = self._get_pattern()
        if regex is None:
            return
        metadata_tuple = tuple(sorted(self.metadata.items())) if self.metadata else tuple()
        for match in regex.finditer(text):
            fragment = match.group(0)
            yield RuleMatch(
                self.rule_id,
                self.action,
                fragment,
                self.description,
                match.span(),
                self.severity,
                metadata_tuple,
            )

    def redact(self, text: str, default_token: str) -> Tuple[str, int]:
        if self.action not in {"redact", "block"}:
            return text, 0
        regex = self._get_pattern()
        if regex is None:
            return text, 0
        replacement = self.replacement or default_token
        try:
            return regex.subn(replacement, text)
        except re.error:  # pragma: no cover - defensive
            return text, 0

    def _get_pattern(self) -> Optional[re.Pattern[str]]:
        if self.kind == "literal":
            if self._literal_regex is None:
                self._literal_regex = re.compile(re.escape(self.pattern), re.IGNORECASE)
            return self._literal_regex
        if self.kind == "regex":
            if self._compiled is None:
                self._compiled = re.compile(self.pattern, self.flags)
            return self._compiled
        return None


@dataclass
class SafetyPolicy:
    enabled: bool = True
    bypass: bool = False
    redaction_token: str = REDACT_TOKEN
    rules: Tuple[PolicyRule, ...] = field(default_factory=tuple)
    log_path: Optional[Path] = None
    version: Optional[int] = None
    source_path: Optional[Path] = field(default=None, repr=False, compare=False)

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
                data = _load_policy_file(candidate)
                if data is None:
                    continue
                if not isinstance(data, dict):
                    logger.warning(
                        "Ignoring safety policy at %s: expected mapping but got %s",
                        candidate,
                        type(data).__name__,
                    )
                    continue
                try:
                    policy = cls.from_dict(data)
                    policy.source_path = candidate
                    return policy
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning("Failed to parse safety policy from %s: %s", candidate, exc)

        fallback = cls.from_dict(DEFAULT_POLICY_DATA)
        fallback.source_path = None
        return fallback

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SafetyPolicy":
        enabled = bool(data.get("enabled", True))
        bypass = bool(data.get("bypass", False))
        redaction_token = str(data.get("redaction_token", REDACT_TOKEN))
        log_path_val = data.get("log_path")
        log_path = Path(log_path_val) if isinstance(log_path_val, str) and log_path_val else None
        version = data.get("version")

        rules: List[PolicyRule] = []
        rules.extend(_build_allow_rules(data.get("allow")))

        rules_data = data.get("rules", [])
        if isinstance(rules_data, Iterable):
            for idx, item in enumerate(rules_data):
                if not isinstance(item, dict):
                    continue
                action = str(item.get("action", "block")).lower().strip()
                if action not in {"block", "allow", "redact", "flag"}:
                    continue
                match_spec = item.get("match") or {}
                metadata = {}
                if "reason" in item:
                    metadata["reason"] = item["reason"]
                applies_to = _parse_applies_to(item.get("applies_to"))
                replacement = item.get("replacement")
                description = item.get("description")
                severity = item.get("severity")
                rule_id = str(item.get("id") or f"rule_{idx}")
                for kind, pattern, flags in _iter_match_specs(match_spec):
                    rules.append(
                        PolicyRule(
                            rule_id=rule_id,
                            action=action,
                            pattern=pattern,
                            kind=kind,
                            flags=flags,
                            description=description,
                            severity=str(severity) if severity is not None else None,
                            applies_to=applies_to,
                            replacement=str(replacement) if replacement not in (None, "") else None,
                            metadata=metadata,
                        )
                    )

        return cls(
            enabled=enabled,
            bypass=bypass,
            redaction_token=redaction_token,
            rules=tuple(rules),
            log_path=log_path,
            version=int(version) if isinstance(version, int) else None,
        )


@dataclass(frozen=True)
class SafetyResult:
    stage: str
    allowed: bool
    sanitized_text: str
    matches: Tuple[RuleMatch, ...] = tuple()
    bypassed: bool = False

    @property
    def blocked_rules(self) -> Tuple[str, ...]:
        return tuple(match.rule_id for match in self.matches if match.is_block)


class SafetyViolation(RuntimeError):
    """Raised when a safety policy blocks content without bypass."""

    def __init__(
        self, stage: str, decision: SafetyResult, policy_path: Optional[Path] = None
    ) -> None:
        self.stage = stage
        self.decision = decision
        self.policy_path = policy_path
        blocked = ", ".join(decision.blocked_rules) or "policy"
        location = f" ({policy_path})" if policy_path else ""
        super().__init__(f"{stage} blocked by safety policy{location}: {blocked}")


class SafetyFilters:
    def __init__(self, policy: Optional[SafetyPolicy] = None):
        self.policy = policy or SafetyPolicy.load()
        self.policy_path = getattr(self.policy, "source_path", None)
        log_target = self.policy.log_path or DEFAULT_LOG_PATH
        try:
            self.log_path = Path(log_target)
        except TypeError:  # pragma: no cover - defensive
            self.log_path = DEFAULT_LOG_PATH

    @classmethod
    def from_defaults(cls) -> "SafetyFilters":
        return cls(_cached_default_policy())

    @classmethod
    def from_policy_file(cls, path: Optional[Path | str]) -> "SafetyFilters":
        return cls(SafetyPolicy.load(path))

    def evaluate(
        self,
        text: str,
        *,
        stage: str = "unspecified",
        bypass: bool = False,
        log: bool = True,
    ) -> SafetyResult:
        if not self.policy.enabled:
            return SafetyResult(stage=stage, allowed=True, sanitized_text=text)

        matches, sanitized_block, sanitized_allow = self._scan(text, stage)
        allow_matches = [match for match in matches if match.is_allow]
        block_matches = [match for match in matches if match.is_block]

        overridden_blocks: set[RuleMatch] = set()
        if block_matches:
            for block_match in block_matches:
                if self._allow_overrides_block(block_match, allow_matches):
                    overridden_blocks.add(block_match)

        blocked = bool(block_matches) and len(overridden_blocks) != len(block_matches)
        visible_matches = tuple(match for match in matches if match not in overridden_blocks)
        sanitized_text = sanitized_allow if overridden_blocks else sanitized_block

        if not self._external_allows(text):
            external = RuleMatch("external", "block", "", "External classifier veto")
            visible_matches = visible_matches + (external,)
            blocked = True

        effective_bypass = bypass or self.policy.bypass
        allowed = not blocked or effective_bypass
        bypassed = blocked and allowed

        decision = SafetyResult(
            stage=stage,
            allowed=allowed,
            sanitized_text=sanitized_text,
            matches=visible_matches,
            bypassed=bypassed,
        )

        if log and visible_matches:
            self._log_decision(stage, text, decision, bypass=bypassed)

        return decision

    def sanitize(self, text: str, *, stage: str) -> SafetyResult:
        return self.evaluate(text, stage=stage)

    def is_allowed(self, text: str, *, stage: str = "unspecified") -> Tuple[bool, List[str]]:
        result = self.evaluate(text, stage=stage)
        return result.allowed, sorted(result.blocked_rules)

    def apply(self, text: str, *, stage: str = "unspecified") -> str:
        result = self.evaluate(text, stage=stage)
        return result.sanitized_text

    def enforce(self, text: str, *, stage: str, bypass: bool = False) -> str:
        if not self.policy.enabled:
            return text
        effective_bypass = self._effective_bypass(bypass)
        decision = self.evaluate(text, stage=stage, bypass=effective_bypass, log=False)
        if decision.matches:
            self._log_decision(stage, text, decision, bypass=decision.bypassed)
        if decision.allowed:
            return decision.sanitized_text
        raise SafetyViolation(stage, decision, self.policy_path)

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

    def _scan(self, text: str, stage: str) -> Tuple[List[RuleMatch], str, str]:
        matches: List[RuleMatch] = []
        sanitized_block = text
        sanitized_allow = text
        for rule in self.policy.rules:
            if not rule.applies_to_stage(stage):
                continue
            rule_matches = list(rule.iter_matches(text))
            if not rule_matches:
                continue
            matches.extend(rule_matches)
            if rule.action in {"block", "redact"}:
                sanitized_block, _ = rule.redact(sanitized_block, self.policy.redaction_token)
            if rule.action == "redact":
                sanitized_allow, _ = rule.redact(sanitized_allow, self.policy.redaction_token)
        return matches, sanitized_block, sanitized_allow

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

    def _effective_bypass(self, bypass_flag: bool) -> bool:
        if bypass_flag:
            return True
        env = os.getenv(BYPASS_ENV_VAR, "").strip().lower()
        if env in {"1", "true", "yes", "on"}:
            return True
        return self.policy.bypass

    def _log_decision(
        self, stage: str, original_text: str, decision: SafetyResult, *, bypass: bool
    ) -> None:
        if not decision.matches:
            return
        path = self.log_path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:  # pragma: no cover - defensive
            pass

        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            digest = hashlib.sha256(original_text.encode("utf-8", errors="ignore")).hexdigest()
        except Exception:  # pragma: no cover - defensive
            digest = ""

        try:
            with path.open("a", encoding="utf-8") as fh:
                for match in decision.matches:
                    action = "bypass" if bypass and match.is_block else match.action
                    entry: Dict[str, Any] = {
                        "event": "safety.decision",
                        "timestamp": timestamp,
                        "stage": stage,
                        "rule_id": match.rule_id,
                        "action": action,
                        "allowed": decision.allowed,
                        "bypass": bypass,
                        "severity": match.severity,
                        "description": match.description,
                        "policy": str(self.policy_path) if self.policy_path else None,
                        "sanitized_text": decision.sanitized_text,
                        "fragment": match.fragment,
                        "text_digest": digest,
                    }
                    if match.metadata:
                        entry["metadata"] = dict(match.metadata)
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:  # pragma: no cover - best effort logging
            logger.debug("Failed to log safety event: %s", exc)


def _load_policy_file(path: Path) -> Optional[Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        try:
            return yaml.safe_load(text) or {}
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to load safety policy from %s: %s", path, exc)
            return None
    logger.debug("PyYAML not available; using minimal parser for %s", path)
    try:
        return _minimal_yaml_load(text)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to parse safety policy from %s without PyYAML: %s", path, exc)
        return None


def _minimal_yaml_load(text: str) -> Any:
    tokens = _tokenize_yaml(text)
    if not tokens:
        return {}
    value, _ = _parse_yaml_block(tokens, 0, tokens[0][0])
    return value


def _tokenize_yaml(text: str) -> List[Tuple[int, str]]:
    tokens: List[Tuple[int, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        tokens.append((indent, line.lstrip(" ")))
    return tokens


def _parse_yaml_block(tokens: List[Tuple[int, str]], index: int, indent: int) -> Tuple[Any, int]:
    if index < len(tokens) and tokens[index][1].startswith("- "):
        return _parse_yaml_list(tokens, index, indent)
    return _parse_yaml_dict(tokens, index, indent)


def _parse_yaml_dict(
    tokens: List[Tuple[int, str]], index: int, indent: int
) -> Tuple[Dict[str, Any], int]:
    result: Dict[str, Any] = {}
    while index < len(tokens):
        current_indent, content = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            break
        if content.startswith("- "):
            list_value, index = _parse_yaml_list(tokens, index, indent)
            return list_value, index
        key, value_str = _split_key_value(content)
        index += 1
        if value_str is not None:
            result[key] = _parse_scalar(value_str)
        else:
            if index < len(tokens) and tokens[index][0] > indent:
                nested_indent = tokens[index][0]
                nested, index = _parse_yaml_block(tokens, index, nested_indent)
            else:
                nested = {}
            result[key] = nested
    return result, index


def _parse_yaml_list(
    tokens: List[Tuple[int, str]], index: int, indent: int
) -> Tuple[List[Any], int]:
    items: List[Any] = []
    while index < len(tokens):
        current_indent, content = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            break
        if not content.startswith("- "):
            break
        item_content = content[2:]
        index += 1
        if not item_content:
            if index < len(tokens) and tokens[index][0] > indent:
                nested, index = _parse_yaml_block(tokens, index, tokens[index][0])
            else:
                nested = None
            items.append(nested)
            continue
        key, value_str = _split_key_value(item_content)
        if key is None:
            items.append(_parse_scalar(item_content))
            continue
        item_dict: Dict[str, Any] = {}
        if value_str is not None:
            item_dict[key] = _parse_scalar(value_str)
        else:
            if index < len(tokens) and tokens[index][0] > indent:
                nested, index = _parse_yaml_block(tokens, index, tokens[index][0])
            else:
                nested = {}
            item_dict[key] = nested
        while index < len(tokens) and tokens[index][0] > indent:
            sub_indent, sub_content = tokens[index]
            if sub_content.startswith("- "):
                nested_list, index = _parse_yaml_list(tokens, index, sub_indent)
                item_dict.setdefault(key, nested_list)
                break
            sub_key, sub_value = _split_key_value(sub_content)
            index += 1
            if sub_value is not None:
                item_dict[sub_key] = _parse_scalar(sub_value)
            else:
                if index < len(tokens) and tokens[index][0] > sub_indent:
                    nested, index = _parse_yaml_block(tokens, index, tokens[index][0])
                else:
                    nested = {}
                item_dict[sub_key] = nested
        items.append(item_dict)
    return items, index


def _split_key_value(content: str) -> Tuple[Optional[str], Optional[str]]:
    if ":" in content:
        key, rest = content.split(":", 1)
        key = key.strip()
        value = rest.strip()
        if value == "":
            return key, None
        return key, value
    return None, content.strip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "None"}:
        return None
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            pass
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


def _iter_match_specs(match_spec: Any) -> Iterator[Tuple[str, str, int]]:
    if isinstance(match_spec, str):
        yield "literal", match_spec, 0
        return
    if not isinstance(match_spec, dict):
        return
    if "literal" in match_spec:
        literal = match_spec.get("literal")
        if literal not in (None, ""):
            yield "literal", str(literal), 0
    if "literals" in match_spec and isinstance(match_spec["literals"], Iterable):
        for literal in match_spec["literals"]:
            if literal not in (None, ""):
                yield "literal", str(literal), 0
    if "regex" in match_spec:
        pattern = match_spec.get("regex")
        if pattern not in (None, ""):
            yield "regex", str(pattern), _parse_flags(match_spec.get("flags"))
    if "patterns" in match_spec and isinstance(match_spec["patterns"], Iterable):
        for item in match_spec["patterns"]:
            if isinstance(item, dict):
                pattern = item.get("pattern")
                if pattern not in (None, ""):
                    yield "regex", str(pattern), _parse_flags(item.get("flags"))
            elif item not in (None, ""):
                yield "regex", str(item), 0


def _build_allow_rules(spec: Any) -> List[PolicyRule]:
    rules: List[PolicyRule] = []
    if not isinstance(spec, dict):
        return rules
    for idx, (kind, pattern, flags) in enumerate(_iter_match_specs(spec)):
        rules.append(
            PolicyRule(
                rule_id=f"allow.rule_{idx}",
                action="allow",
                pattern=pattern,
                kind=kind,
                flags=flags,
            )
        )
    return rules


def _parse_applies_to(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ("prompt", "output")
    stages: List[str] = []
    items: Iterable[Any]
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, Iterable):
        items = value
    else:
        return ("prompt", "output")
    for item in items:
        if not isinstance(item, str):
            continue
        stage = item.strip().lower()
        if stage in {"prompt", "output"}:
            stages.append(stage)
        elif stage in {"all", "*"}:
            return ("prompt", "output")
    return tuple(stages) if stages else ("prompt", "output")


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
    flag_lookup = {
        "IGNORECASE": re.IGNORECASE,
        "MULTILINE": re.MULTILINE,
        "DOTALL": re.DOTALL,
        "VERBOSE": re.VERBOSE,
    }
    for item in values:
        if not isinstance(item, str):
            continue
        name = item.strip().upper()
        flags |= flag_lookup.get(name, 0)
    return flags


def sanitize_prompt(prompt: str, *, filters: Optional[SafetyFilters] = None) -> SafetyResult:
    active_filters = filters or SafetyFilters.from_defaults()
    return active_filters.sanitize(prompt, stage="prompt")


def sanitize_output(output: str, *, filters: Optional[SafetyFilters] = None) -> SafetyResult:
    active_filters = filters or SafetyFilters.from_defaults()
    return active_filters.sanitize(output, stage="output")


@lru_cache(maxsize=1)
def _cached_default_policy() -> SafetyPolicy:
    return SafetyPolicy.load()


DEFAULT_POLICY_DATA: Dict[str, Any] = {
    "version": 1,
    "enabled": True,
    "bypass": False,
    "log_path": str(DEFAULT_LOG_PATH),
    "redaction_token": REDACT_TOKEN,
    "rules": [
        {"id": "deny.shell.rm_root", "action": "block", "match": {"literals": ["rm -rf /"]}},
        {"id": "deny.shell.format_c", "action": "block", "match": {"literals": ["format c:"]}},
        {"id": "deny.shell.mkfs", "action": "block", "match": {"literals": ["mkfs"]}},
        {
            "id": "deny.shell.shutdown",
            "action": "block",
            "match": {"literals": ["shutdown -h now"]},
        },
        {
            "id": "deny.secret.credit_card",
            "action": "block",
            "match": {"literals": ["credit card"]},
        },
        {"id": "deny.secret.ssn", "action": "block", "match": {"literals": ["ssn"]}},
        {
            "id": "deny.secret.ssn_phrase",
            "action": "block",
            "match": {"literals": ["social security number"]},
        },
        {
            "id": "deny.sql.drop_database",
            "action": "block",
            "match": {"literals": ["drop database"]},
        },
        {
            "id": "deny.weapon.schematic",
            "action": "block",
            "match": {"literals": ["weapon schematic"]},
        },
        {"id": "deny.selfharm", "action": "block", "match": {"literals": ["kill yourself"]}},
        {"id": "allow.shell.rm_build", "action": "allow", "match": {"literals": ["rm -rf build"]}},
        {
            "id": "allow.sql.drop_schema_example",
            "action": "allow",
            "match": {"literals": ["drop database schema_example"]},
        },
        {
            "id": "deny.secret.aws_access_key",
            "action": "block",
            "match": {"patterns": [r"AKIA[0-9A-Z]{16}"]},
        },
        {
            "id": "deny.secret.password_key",
            "action": "redact",
            "replacement": "{REDACTED}",
            "match": {"patterns": [r"(?i)password\\s*[:=]\\s*[^\\s]+"]},
        },
        {
            "id": "deny.secret.api_key",
            "action": "redact",
            "replacement": "{REDACTED}",
            "match": {"patterns": [r"(?i)api[_-]?key\\s*[:=]\\s*[^\\s]+"]},
        },
        {
            "id": "deny.secret.ssn_regex",
            "action": "block",
            "match": {"patterns": [r"\\b\\d{3}-\\d{2}-\\d{4}\\b"]},
        },
        {
            "id": "deny.shell.rm_root_regex",
            "action": "block",
            "match": {"patterns": [r"\\b(rm\\s+-rf\\s+/(?!\\w))"]},
        },
        {
            "id": "allow.secret.test_password",
            "action": "allow",
            "match": {"patterns": [r"(?i)test(_|-)?password"]},
        },
    ],
}


__all__ = [
    "SafetyFilters",
    "SafetyPolicy",
    "PolicyRule",
    "SafetyResult",
    "sanitize_prompt",
    "sanitize_output",
    "RuleMatch",
    "SafetyViolation",
]
