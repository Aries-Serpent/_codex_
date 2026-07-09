"""Skill manifest and execution envelope models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _normalize_tags(tags: list[str] | tuple[str, ...] | None) -> list[str]:
    """Normalize capability tags to a stable, deduplicated list."""
    if not tags:
        return []
    normalized = {tag.strip().lower() for tag in tags if tag and tag.strip()}
    return sorted(normalized)


@dataclass(slots=True)
class SkillExecutionEnvelope:
    """Execution envelope describing how a skill should be invoked."""

    skill_name: str
    capability_tags: list[str]
    enforcement_tier: str = "UNSPECIFIED"
    budget_tokens: int | None = None
    timeout_ms: int | None = None
    doc_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def attributes(self) -> dict[str, Any]:
        """Return a flat mapping useful for telemetry attributes."""
        return {
            "skill.name": self.skill_name,
            "skill.capability_tags": ",".join(_normalize_tags(self.capability_tags)),
            "skill.enforcement_tier": self.enforcement_tier,
            "skill.budget_tokens": self.budget_tokens,
            "skill.timeout_ms": self.timeout_ms,
            "skill.doc_path": self.doc_path,
            "skill.metadata": self.metadata,
        }


@dataclass(slots=True)
class SkillManifest:
    """Declarative manifest describing a skill and its routing attributes."""

    name: str
    description: str = ""
    capability_tags: list[str] = field(default_factory=list)
    integration_points: list[str] = field(default_factory=list)
    enforcement_tier: str = "UNSPECIFIED"
    budget_tokens: int | None = None
    timeout_ms: int | None = None
    doc_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.capability_tags = _normalize_tags(self.capability_tags)
        self.integration_points = [ip for ip in self.integration_points if ip]

    def to_envelope(self) -> SkillExecutionEnvelope:
        """Convert this manifest into an execution envelope."""
        return SkillExecutionEnvelope(
            skill_name=self.name,
            capability_tags=self.capability_tags,
            enforcement_tier=self.enforcement_tier,
            budget_tokens=self.budget_tokens,
            timeout_ms=self.timeout_ms,
            doc_path=self.doc_path,
            metadata=self.metadata,
        )

    def merge_metadata(self, extra: dict[str, Any] | None = None) -> None:
        """Merge additional metadata into the manifest."""
        if not extra:
            return
        self.metadata = {**self.metadata, **extra}
