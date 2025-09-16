# BEGIN: CODEX_SAFETY_FILTERS
from __future__ import annotations

import importlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Pattern, Sequence, Tuple

try:  # pragma: no cover - PyYAML optional in some environments
    import yaml
except Exception:  # pragma: no cover - safety fallback
    yaml = None  # type: ignore

from codex_ml.utils.error_log import log_error

REDACT_TOKEN = "{REDACTED}"
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs" / "safety" / "policy.yaml"


def _to_list(value: object) -> List[object]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _resolve_flags(flags: Sequence[str] | None) -> int:
    resolved = 0
    if not flags:
        return resolved
    for name in flags:
        try:
            resolved |= getattr(re, name.upper())
        except AttributeError:
            continue
    return resolved


def _normalise_stage(values: Sequence[str] | None) -> Tuple[str, ...]:
    if not values:
        return ("prompt", "output")
    stages = set()
    for raw in values:
        value = str(raw).lower()
        if value in {"*", "all", "any"}:
            return ("prompt", "output")
        if value in {"prompt", "input"}:
            stages.add("prompt")
        elif value in {"output", "response"}:
            stages.add("output")
    return tuple(sorted(stages or {"prompt", "output"}))


@dataclass
class PolicyRule:
    rule_id: str
    pattern: Pattern[str]
    action: str = "block"
    severity: str = "medium"
    applies_to: Tuple[str, ...] = ("prompt", "output")
    reason: str = ""
    replacement: str | None = None
    literal: str | None = None


@dataclass
class SafetyDecision:
    allowed: bool
    blocked: bool
    bypassed: bool
    redacted_text: str
    matches: List[dict]
    allow_hits: List[str]


class SafetyViolation(RuntimeError):
    """Raised when content is rejected by a safety rule."""

    def __init__(self, decision: SafetyDecision) -> None:
        self.decision = decision
        rule_ids = ", ".join(m.get("rule_id", "unknown") for m in decision.matches) or "unknown"
        message = f"Safety policy blocked content (rules: {rule_ids})"
        super().__init__(message)


@dataclass
class SafetyFilters:
    rules: List[PolicyRule] = field(default_factory=list)
    allow_literals: List[str] = field(default_factory=list)
    allow_patterns: List[Pattern[str]] = field(default_factory=list)
    bypass_default: bool = False
    log_path: Path = Path(".codex/safety/events.ndjson")
    policy_path: Path | None = None

    @classmethod
    def from_defaults(cls) -> "SafetyFilters":
        """Load filters from the repository policy or fall back to hard-coded rules."""

        filt = cls.from_policy_file(DEFAULT_POLICY_PATH)
        if filt.rules:
            return filt
        return cls._fallback()

    @classmethod
    def from_policy_file(cls, policy_path: os.PathLike[str] | str | None) -> "SafetyFilters":
        path = Path(policy_path) if policy_path else DEFAULT_POLICY_PATH
        if yaml is None or not path.exists():
            return cls._fallback(policy_path=path if path.exists() else None)

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:  # pragma: no cover - YAML parse errors
            log_error("safety.policy", f"{exc.__class__.__name__}: {exc}", str(path))
            return cls._fallback(policy_path=path)

        allow_cfg = data.get("allow", {}) or {}
        allow_literals = [str(v) for v in _to_list(allow_cfg.get("literals"))]
        allow_patterns: List[Pattern[str]] = []
        for entry in _to_list(allow_cfg.get("patterns")):
            if isinstance(entry, dict):
                pattern = entry.get("pattern")
                if not pattern:
                    continue
                flags = _resolve_flags(_to_list(entry.get("flags")))
            else:
                pattern = entry
                flags = 0
            try:
                allow_patterns.append(re.compile(str(pattern), flags))
            except re.error as exc:  # pragma: no cover - invalid regex
                log_error("safety.policy", f"regex error: {exc}", str(pattern))

        rules: List[PolicyRule] = []
        for idx, item in enumerate(_to_list(data.get("rules"))):
            if not isinstance(item, dict):
                continue
            rule_id = str(item.get("id") or f"rule_{idx}")
            action = str(item.get("action", "block")).lower()
            severity = str(item.get("severity", "medium"))
            applies_to = _normalise_stage(_to_list(item.get("applies_to")))
            reason = str(item.get("reason", ""))
            replacement = item.get("replacement")
            match_cfg = item.get("match", {}) or {}
            base_flags = _resolve_flags(_to_list(match_cfg.get("flags")))

            for literal in _to_list(match_cfg.get("literals")):
                text = str(literal)
                try:
                    pattern = re.compile(re.escape(text), re.IGNORECASE | base_flags)
                except re.error:
                    continue
                rules.append(
                    PolicyRule(
                        rule_id=rule_id,
                        pattern=pattern,
                        action=action,
                        severity=severity,
                        applies_to=applies_to,
                        reason=reason,
                        replacement=str(replacement) if replacement else None,
                        literal=text,
                    )
                )

            for pat_entry in _to_list(match_cfg.get("patterns")):
                if isinstance(pat_entry, dict):
                    pat_text = pat_entry.get("pattern")
                    if not pat_text:
                        continue
                    flags = base_flags | _resolve_flags(_to_list(pat_entry.get("flags")))
                else:
                    pat_text = pat_entry
                    flags = base_flags
                try:
                    pattern = re.compile(str(pat_text), flags)
                except re.error as exc:
                    log_error("safety.policy", f"regex error: {exc}", str(pat_text))
                    continue
                rules.append(
                    PolicyRule(
                        rule_id=rule_id,
                        pattern=pattern,
                        action=action,
                        severity=severity,
                        applies_to=applies_to,
                        reason=reason,
                        replacement=str(replacement) if replacement else None,
                    )
                )

        log_path = Path(data.get("log_path") or ".codex/safety/events.ndjson")
        bypass = bool(data.get("bypass", False))
        return cls(
            rules=rules,
            allow_literals=allow_literals,
            allow_patterns=allow_patterns,
            bypass_default=bypass,
            log_path=log_path,
            policy_path=path,
        )

    @classmethod
    def _fallback(cls, policy_path: Path | None = None) -> "SafetyFilters":
        block_literals = [
            "rm -rf /",
            "format c:",
            "mkfs",
            "shutdown -h now",
            "kill yourself",
            "weapon schematic",
            "drop database",
        ]
        allow_literals = ["rm -rf build", "drop database schema_example"]
        regex_redact = [
            PolicyRule(
                rule_id="default.secrets",
                pattern=re.compile(r"(?i)password\s*[:=]\s*\S+"),
                action="redact",
                severity="high",
            ),
            PolicyRule(
                rule_id="default.secrets",
                pattern=re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"),
                action="redact",
                severity="high",
            ),
            PolicyRule(
                rule_id="default.secrets",
                pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
                action="redact",
                severity="high",
            ),
            PolicyRule(
                rule_id="default.pii",
                pattern=re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
                action="redact",
                severity="medium",
            ),
        ]
        block_rules = [
            PolicyRule(
                rule_id="default.block",
                pattern=re.compile(re.escape(lit), re.IGNORECASE),
                action="block",
                severity="high",
                literal=lit,
            )
            for lit in block_literals
        ]
        allow_patterns = [re.compile(r"(?i)test(_|-)?password")]
        return cls(
            rules=block_rules + regex_redact,
            allow_literals=allow_literals,
            allow_patterns=allow_patterns,
            policy_path=policy_path,
        )

    def _allow_hits(self, text: str) -> List[str]:
        lowered = text.lower()
        hits = [lit for lit in self.allow_literals if lit.lower() in lowered]
        for pattern in self.allow_patterns:
            if pattern.search(text):
                hits.append(pattern.pattern)
        return hits

    def _env_bypass(self) -> bool:
        value = os.getenv("CODEX_SAFETY_BYPASS")
        if value is None:
            return False
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def _run_external_classifier(self, text: str) -> bool | None:
        hook = os.getenv("CODEX_SAFETY_CLASSIFIER")
        if not hook:
            return None
        try:
            mod_name, fn_name = hook.split(":", 1)
            fn = getattr(importlib.import_module(mod_name), fn_name)
            return bool(fn(text))
        except Exception as exc:  # pragma: no cover - optional hook failures
            log_error("safety_classifier", str(exc), hook)
            return True

    def _log_events(
        self,
        *,
        stage: str,
        original: str,
        redacted: str,
        triggered: List[PolicyRule],
        decision: SafetyDecision,
    ) -> None:
        if not triggered and not decision.allow_hits:
            return
        try:
            from codex_ml.safety.sanitizers import SafetyConfig, sanitize_output

            cfg = SafetyConfig()
            safe_original = sanitize_output(original, cfg)["text"]
            safe_redacted = sanitize_output(redacted, cfg)["text"]
        except Exception:  # pragma: no cover - sanitiser optional
            safe_original = original
            safe_redacted = redacted

        base = {
            "event": "safety.filter",
            "stage": stage,
            "allow_hits": decision.allow_hits,
            "bypassed": decision.bypassed,
        }
        for rule in triggered:
            action = rule.action
            if decision.allow_hits and rule.action == "block":
                action = "allow"
            elif decision.bypassed and rule.action == "block":
                action = "bypass"
            entry = {
                **base,
                "rule_id": rule.rule_id,
                "action": action,
                "severity": rule.severity,
                "reason": rule.reason,
                "pattern": rule.literal or rule.pattern.pattern,
                "text": safe_original,
                "redacted": safe_redacted,
            }
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:  # pragma: no cover - best-effort logging
                pass

    def evaluate(
        self,
        text: str,
        *,
        stage: str = "prompt",
        bypass: bool | None = None,
    ) -> SafetyDecision:
        stage_norm = stage.lower()
        allow_hits = self._allow_hits(text)
        triggered: List[PolicyRule] = []
        redacted = text
        blocked = False
        for rule in self.rules:
            if stage_norm not in rule.applies_to:
                continue
            if not rule.pattern.search(text):
                continue
            triggered.append(rule)
            if rule.action == "redact":
                repl = rule.replacement or REDACT_TOKEN
                redacted = rule.pattern.sub(repl, redacted)
            elif rule.action == "block":
                blocked = True
        external_decision = self._run_external_classifier(text)
        external_veto = external_decision is False
        if external_veto:
            triggered.append(
                PolicyRule(
                    rule_id="external",
                    pattern=re.compile(r"(?s).*"),
                    action="block",
                    severity="critical",
                    applies_to=("prompt", "output"),
                    reason="external classifier veto",
                    literal="external",
                )
            )
            blocked = True
            allow_hits = []
        effective_bypass = (
            bypass if bypass is not None else (self._env_bypass() or self.bypass_default)
        )
        allowed = not blocked or bool(allow_hits) or effective_bypass
        decision = SafetyDecision(
            allowed=allowed,
            blocked=blocked,
            bypassed=bool(blocked and effective_bypass and not allow_hits),
            redacted_text=redacted,
            matches=[
                {
                    "rule_id": rule.rule_id,
                    "action": rule.action,
                    "severity": rule.severity,
                    "pattern": rule.literal or rule.pattern.pattern,
                }
                for rule in triggered
            ],
            allow_hits=allow_hits,
        )
        self._log_events(
            stage=stage_norm,
            original=text,
            redacted=redacted,
            triggered=triggered,
            decision=decision,
        )
        return decision

    def is_allowed(self, text: str, stage: str = "prompt") -> Tuple[bool, List[str]]:
        decision = self.evaluate(text, stage=stage)
        return decision.allowed, [m.get("rule_id", "") for m in decision.matches]

    def enforce(self, text: str, *, stage: str = "prompt", bypass: bool | None = None) -> str:
        decision = self.evaluate(text, stage=stage, bypass=bypass)
        if decision.blocked and not decision.allowed:
            raise SafetyViolation(decision)
        return decision.redacted_text

    def apply(self, text: str, *, stage: str = "output") -> str:
        return self.evaluate(text, stage=stage).redacted_text

    def mask_logits(self, logits, banned_token_ids: set[int]):
        neg_inf = float("-inf")
        try:
            if hasattr(logits, "shape"):
                last = logits.shape[-1]
                for tid in banned_token_ids:
                    if 0 <= tid < last:
                        logits[..., tid] = neg_inf
                return logits
        except Exception:  # pragma: no cover - tolerant path
            pass
        if isinstance(logits, list):
            for tid in banned_token_ids:
                if 0 <= tid < len(logits):
                    logits[tid] = neg_inf
            return logits
        return logits
