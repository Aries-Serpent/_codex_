"""
Prompting Module

This module provides functionality for prompting.

Usage:
    from codex_audit.prompting import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from .policy import build_policy_mapping
from .scorecard import render_scorecard


def _load_gate_results(path: Path) -> Sequence[Mapping[str, object]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _load_policy_map(path: Path) -> Mapping[str, object]:
    if not path.exists():
        return build_policy_mapping()
    return json.loads(path.read_text(encoding="utf-8"))


def _render_gate_bullets(results: Sequence[Mapping[str, object]]) -> str:
    lines = []
    for gate in results:
        icon = (
            "✅" if gate.get("status") == "pass" else "⚠️" if gate.get("status") == "warn" else "❌"
        )
        ra = gate.get("ra_rule", "RA-1")
        lines.append(
            f"- {icon} {gate.get('gate_id')} ({gate.get('category')}): {gate.get('detail')} [RA: {ra}]"  # noqa: E501
        )
    return "\n".join(lines) if lines else "- No gates recorded"


def prepare_repo_status_prompt(
    template_path: Path | None = None,
    gate_results_path: Path | None = None,
    policy_map_path: Path | None = None,
    scorecard_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    template = template_path or Path("prompts/repo_status_update_for_codex.md")
    gates_path = gate_results_path or Path("artifacts/gate_results.json")
    policy_path = policy_map_path or Path("artifacts/ra_policy_map.json")
    scorecard_target = scorecard_path or Path("artifacts/repo_audit_scorecard.md")
    output = output_path or Path("artifacts/repo_status_update_prompt.txt")

    gates = _load_gate_results(gates_path)
    policy_map = _load_policy_map(policy_path)
    render_scorecard(
        gate_results_path=gates_path,
        policy_map=policy_map,
        output_path=scorecard_target,
    )

    ra_rules: dict[str, Any] = policy_map.get("ra_rules", {})  # type: ignore[assignment]
    ra_lines = [f"- {k}: {v}" for k, v in sorted(ra_rules.items())]
    gate_bullets = _render_gate_bullets(gates)

    today = date.today().isoformat()
    prompt_template = template.read_text(encoding="utf-8")
    populated = prompt_template.format(
        date=today,
        gate_results=gate_bullets,
        scorecard_path=scorecard_target,
        ra_policy="\n".join(ra_lines),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(populated, encoding="utf-8")
    return output
