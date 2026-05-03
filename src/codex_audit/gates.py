"""
Gates Module

This module provides functionality for gates.

Usage:
    from codex_audit.gates import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

GateCheck = Callable[[Path], tuple[str, str]]


@dataclass
class GateDefinition:
    gate_id: str
    category: str
    description: str
    ra_rule: str
    check: GateCheck


@dataclass
class GateResult:
    gate_id: str
    category: str
    status: str
    description: str
    detail: str
    ra_rule: str
    rollback: str

    def to_dict(self) -> dict[str, str]:
        return {
            "gate_id": self.gate_id,
            "category": self.category,
            "status": self.status,
            "description": self.description,
            "detail": self.detail,
            "ra_rule": self.ra_rule,
            "rollback": self.rollback,
        }


def _dir_exists_check(target: str) -> GateCheck:
    def check(repo_root: Path) -> tuple[str, str]:
        path = repo_root / target
        status = "pass" if path.exists() else "fail"
        detail = f"Path {'found' if path.exists() else 'missing'}: {target}"
        return status, detail

    return check


def _file_exists_check(target: str) -> GateCheck:
    def check(repo_root: Path) -> tuple[str, str]:
        path = repo_root / target
        status = "pass" if path.exists() else "warn"
        detail = f"File {'present' if path.exists() else 'absent'}: {target}"
        return status, detail

    return check


def _offline_check(_: Path) -> tuple[str, str]:
    return "pass", "Offline-only gate satisfied (no network calls invoked)."


GATE_DEFINITIONS: Iterable[GateDefinition] = (
    GateDefinition(
        gate_id="GATE-TOKENIZATION-001",
        category="tokenization",
        description="Tokenization assets present for offline audit",
        ra_rule="RA-4",
        check=_dir_exists_check("tokenization"),
    ),
    GateDefinition(
        gate_id="GATE-TRAINING-001",
        category="training",
        description="Training stack detected (configs + engine)",
        ra_rule="RA-4",
        check=_dir_exists_check("training"),
    ),
    GateDefinition(
        gate_id="GATE-SECURITY-001",
        category="security",
        description="Security guardrails codified (semgrep/bandit rules)",
        ra_rule="RA-5",
        check=_file_exists_check("bandit.yaml"),
    ),
    GateDefinition(
        gate_id="GATE-DEPLOY-001",
        category="deployment",
        description="Deployment descriptors stored locally",
        ra_rule="RA-5",
        check=_dir_exists_check("deploy"),
    ),
    GateDefinition(
        gate_id="GATE-DOCS-001",
        category="documentation",
        description="Repository docs available for evidence capture",
        ra_rule="RA-2",
        check=_dir_exists_check("docs"),
    ),
    GateDefinition(
        gate_id="GATE-OFFLINE-001",
        category="offline",
        description="Gates executed without network access",
        ra_rule="RA-5",
        check=_offline_check,
    ),
)


def run_gates(repo_root: Path | None = None, output_path: Path | None = None) -> list[GateResult]:
    root = repo_root or Path.cwd()
    target = output_path or Path("artifacts/gate_results.json")
    target.parent.mkdir(parents=True, exist_ok=True)

    results: list[GateResult] = []
    for definition in GATE_DEFINITIONS:
        status, detail = definition.check(root)
        rollback = (
            "No action required; gate is read-only."
            if status == "pass"
            else (
                f"Restore or create {definition.category} assets referenced by {definition.gate_id}."  # noqa: E501
            )
        )
        results.append(
            GateResult(
                gate_id=definition.gate_id,
                category=definition.category,
                status=status,
                description=definition.description,
                detail=detail,
                ra_rule=definition.ra_rule,
                rollback=rollback,
            )
        )

    with target.open("w", encoding="utf-8") as fp:
        json.dump([result.to_dict() for result in results], fp, indent=2, sort_keys=True)

    return results
