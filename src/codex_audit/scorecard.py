from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping
import json

from .gates import GateResult


def _load_gate_results(path: Path) -> Iterable[GateResult]:
    data = json.loads(path.read_text(encoding="utf-8"))
    for entry in data:
        yield GateResult(
            gate_id=entry["gate_id"],
            category=entry["category"],
            status=entry["status"],
            description=entry.get("description", ""),
            detail=entry.get("detail", ""),
            ra_rule=entry.get("ra_rule", "RA-1"),
            rollback=entry.get("rollback", ""),
        )


def _format_gate_result(result: GateResult) -> str:
    icon = "✅" if result.status == "pass" else "⚠️" if result.status == "warn" else "❌"
    return f"- {icon} **{result.gate_id}** ({result.category}) — {result.description} [{result.status}] | RA: {result.ra_rule}. {result.detail}"


def render_scorecard(
    gate_results_path: Path | None = None,
    policy_map: Mapping[str, object] | None = None,
    output_path: Path | None = None,
) -> Path:
    gate_path = gate_results_path or Path("artifacts/gate_results.json")
    if not gate_path.exists():
        raise FileNotFoundError(f"Gate results not found: {gate_path}")

    output = output_path or Path("artifacts/repo_audit_scorecard.md")
    output.parent.mkdir(parents=True, exist_ok=True)

    policy_section = ""
    if policy_map:
        ra_rules = policy_map.get("ra_rules", {})
        policy_lines = ["## RA Policy Reference"]
        for ra_id, desc in sorted(ra_rules.items()):
            policy_lines.append(f"- **{ra_id}**: {desc}")
        policy_section = "\n".join(policy_lines) + "\n\n"

    lines = [
        "# Repo Audit Scorecard",
        "",
        "## Gate Results",
    ]

    gate_results = list(_load_gate_results(gate_path))
    for result in gate_results:
        lines.append(_format_gate_result(result))

    if policy_section:
        lines.append("")
        lines.append(policy_section.rstrip())

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
