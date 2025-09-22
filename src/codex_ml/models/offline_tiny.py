"""Minimal offline-friendly model used for registry smoke tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


@dataclass
class ResponseRule:
    prefix: str
    completion: str


class TinySequenceModel:
    """Return scripted completions using prefix matching."""

    def __init__(self, rules: Sequence[ResponseRule], *, default_completion: str) -> None:
        self.rules = list(rules)
        self.default_completion = default_completion

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "TinySequenceModel":
        responses = [
            ResponseRule(prefix=str(entry["prefix"]), completion=str(entry["completion"]))
            for entry in payload.get("responses", [])
        ]
        default = str(payload.get("default_completion", ""))
        return cls(responses, default_completion=default)

    @classmethod
    def from_file(cls, path: str | Path) -> "TinySequenceModel":
        candidate = Path(path)
        if candidate.is_dir():
            candidate = candidate / "model.json"
        if not candidate.exists():
            raise FileNotFoundError(f"Model fixture not found at {candidate}")
        payload: Dict[str, Any] = json.loads(candidate.read_text(encoding="utf-8"))
        return cls.from_payload(payload)

    def generate(self, prompt: str) -> str:
        for rule in self.rules:
            if prompt.startswith(rule.prefix):
                return rule.completion
        return self.default_completion

    def __call__(self, prompts: Iterable[str], **_: Any) -> list[str]:
        return [self.generate(prompt) for prompt in prompts]


__all__ = ["TinySequenceModel", "ResponseRule"]
