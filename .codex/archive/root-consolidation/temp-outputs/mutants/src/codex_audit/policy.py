"""
Policy Module

This module provides functionality for policy.

Usage:
    from codex_audit.policy import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from pathlib import Path

RA_RULES: Mapping[str, str] = {
    "RA-1": "No fabrication: every assertion must be grounded in repository evidence.",
    "RA-2": "Label clarity: responses must mark content as verified, inferred, or planned.",
    "RA-3": "Tool traceability: preserve the command or tool that produced each artifact.",
    "RA-4": "Scope-constrained mutation: only touch in-scope files with reversible steps.",
    "RA-5": "YAML/CI safety: keep CI, YAML, and infra edits deterministic and offline.",
}


def _default_capabilities() -> list[str]:
    return [
        "Tokenization",
        "ChatGPT Codex Modeling",
        "Training Engine",
        "Configuration Management",
        "Security & Safety",
        "Deployment",
        "Documentation & Examples",
    ]


def _default_tracks() -> Mapping[str, str]:
    return {
        "A": "Diff drafting / atomic fixes",
        "B": "Refinement with evidence linking",
        "C": "Capability inventory and status",
        "D": "Audit policy integration",
        "E": "Offline gating and reproducibility",
        "F": "Prompt/plan synthesis",
    }


@dataclass
class CapabilityPolicy:
    name: str
    ra_rules: Sequence[str]
    rationale: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ra_rules": list(self.ra_rules),
            "rationale": self.rationale,
        }


@dataclass
class TrackPolicy:
    track: str
    focus: str
    ra_rules: Sequence[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "track": self.track,
            "focus": self.focus,
            "ra_rules": list(self.ra_rules),
        }


def build_policy_mapping(
    capabilities: Sequence[str] | None = None, tracks: Mapping[str, str] | None = None
) -> dict[str, object]:
    caps = capabilities or _default_capabilities()
    track_map = tracks or _default_tracks()

    cap_policies: list[CapabilityPolicy] = []
    for cap in caps:
        ra_links = ["RA-1", "RA-2", "RA-3"]
        if "token" in cap.lower():
            ra_links.append("RA-4")
        if "deploy" in cap.lower() or "infra" in cap.lower():
            ra_links.append("RA-5")
        cap_policies.append(
            CapabilityPolicy(
                name=cap,
                ra_rules=sorted(set(ra_links)),
                rationale="Policy anchors for capability-specific audit checks.",
            )
        )

    track_policies: list[TrackPolicy] = []
    for track, focus in track_map.items():
        ra_links: list[str] = ["RA-1", "RA-3"]  # type: ignore[no-redef]
        if track in {"A", "B"}:
            ra_links.append("RA-2")
        if track in {"D", "E"}:
            ra_links.append("RA-5")
        if track in {"B", "C", "F"}:
            ra_links.append("RA-4")
        track_policies.append(
            TrackPolicy(
                track=track,
                focus=focus,
                ra_rules=sorted(set(ra_links)),
            )
        )

    return {
        "ra_rules": dict(RA_RULES),
        "capabilities": [cap.to_dict() for cap in cap_policies],
        "tracks": [track.to_dict() for track in track_policies],
    }


def write_policy_mapping(
    path: Path, mapping: MutableMapping[str, object] | None = None
) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    mapping_to_write = mapping or build_policy_mapping()
    with path.open("w", encoding="utf-8") as fp:
        json.dump(mapping_to_write, fp, indent=2, sort_keys=True)
    return mapping_to_write  # type: ignore[return-value]
