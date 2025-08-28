from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
from collections import Counter
import re


@dataclass
class Intent:
    name: str
    confidence: float
    slots: Dict[str, str]


@dataclass
class ParseResult:
    intents: List[Intent]
    key_entities: List[str]
    meta: Dict[str, str]


class SemParser:
    """Lightweight rule-and-score parser."""

    RULES = [
        ("AUDIT_REPO", [re.compile(r"\baudit\b"), re.compile(r"\brepo|repository\b")], {}),
        ("FIX_PRECOMMIT", [re.compile(r"\bpre-?commit\b"), re.compile(r"\bhung|stall|timeout\b")], {}),
        ("TEST_COVERAGE", [re.compile(r"\bpytest\b"), re.compile(r"\bcoverage|--cov\b")], {}),
        ("PLAN_TASKS", [re.compile(r"\bplan|tasks|prioriti[sz]e\b")], {}),
        ("BUILD_PIPELINE", [re.compile(r"\bpipeline|orchestrat|workflow\b")], {}),
    ]

    def parse(self, text: str) -> ParseResult:
        signals = Counter()
        intents: List[Intent] = []
        entities: List[str] = []

        for name, pats, slots in self.RULES:
            score = 0
            for p in pats:
                matches = p.findall(text.lower())
                score += len(matches)
            if score:
                intents.append(Intent(name=name, confidence=min(1.0, 0.35 + 0.2 * score), slots=slots))

        entities += re.findall(r"`([^`]+)`", text)
        entities += re.findall(r"\bSTEP\s*\d+\b", text, flags=re.I)
        entities = list(dict.fromkeys(entities))
        intents.sort(key=lambda i: i.confidence, reverse=True)
        return ParseResult(intents=intents, key_entities=entities, meta={"source": "semparser:v1"})
