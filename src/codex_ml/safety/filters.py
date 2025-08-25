# BEGIN: CODEX_SAFETY_FILTERS
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Iterable, List, Pattern, Tuple

REDACT_TOKEN = "{REDACTED}"

@dataclass
class SafetyFilters:
    blocklist: List[str] = field(default_factory=list)
    allowlist: List[str] = field(default_factory=list)
    regex_block: List[Pattern[str]] = field(default_factory=list)
    regex_allow: List[Pattern[str]] = field(default_factory=list)

    @classmethod
    def from_defaults(cls) -> "SafetyFilters":
        block = [
            "rm -rf /",
            "format c:",
            "mkfs",
            "shutdown -h now",
            "credit card",
            "ssn",
            "social security number",
            "drop database",
            "weapon schematic",
            "kill yourself",
        ]
        allow = [
            "rm -rf build",
            "drop database schema_example",
        ]
        rblock = [
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"(?i)password\s*[:=]"),
            re.compile(r"(?i)api[_-]?key\s*[:=]"),
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            re.compile(r"\b(rm\s+-rf\s+/(?!\w))"),
        ]
        rallow = [
            re.compile(r"(?i)test(_|-)?password"),
        ]
        return cls(block, allow, rblock, rallow)

    def _listed(self, text: str, items: Iterable[str]) -> List[str]:
        t = text.lower()
        return [w for w in items if w.lower() in t]

    def _regex_hits(self, text: str, pats: Iterable[Pattern[str]]) -> List[str]:
        hits: List[str] = []
        for p in pats:
            if p.search(text):
                hits.append(p.pattern)
        return hits

    def is_allowed(self, text: str) -> Tuple[bool, List[str]]:
        allow_hits = set(self._listed(text, self.allowlist) + self._regex_hits(text, self.regex_allow))
        block_hits = set(self._listed(text, self.blocklist) + self._regex_hits(text, self.regex_block))
        if block_hits and not allow_hits:
            return False, sorted(block_hits)
        return True, sorted(block_hits)

    def apply(self, text: str) -> str:
        ok, _ = self.is_allowed(text)
        if ok:
            return text
        red = text
        for lit in self._listed(text, self.blocklist):
            red = re.sub(re.escape(lit), REDACT_TOKEN, red, flags=re.IGNORECASE)
        for pat in self.regex_block:
            red = pat.sub(REDACT_TOKEN, red)
        return red

    def mask_logits(self, logits, banned_token_ids: set[int]):
        neg_inf = float("-inf")
        try:
            import numpy as np  # type: ignore
            if hasattr(logits, "shape"):
                last = logits.shape[-1]
                for tid in banned_token_ids:
                    if 0 <= tid < last:
                        logits[..., tid] = neg_inf
                return logits
        except Exception:
            pass
        if isinstance(logits, list):
            for tid in banned_token_ids:
                if 0 <= tid < len(logits):
                    logits[tid] = neg_inf
            return logits
        return logits
