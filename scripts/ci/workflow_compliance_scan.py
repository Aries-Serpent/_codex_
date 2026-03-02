"""
scripts/ci/workflow_compliance_scan.py
Phase 0 (WU-0.1): Scan all .github/workflows/*.yml for compliance.
Checks: concurrency, timeout, cascade risk, base-ref fetch, enforcement tier.
Output: docs/audits/WORKFLOW_COMPLIANCE_MATRIX.md
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WF_DIR    = REPO_ROOT / ".github" / "workflows"
OUT_FILE  = REPO_ROOT / "docs" / "audits" / "WORKFLOW_COMPLIANCE_MATRIX.md"


@dataclass
class WorkflowAudit:
    name: str
    path: str
    has_concurrency: bool = False
    has_timeout: bool = False
    has_cascade_risk: bool = False    # workflow_run: ["*"] without self-exclusion
    has_base_ref_fetch: bool = False  # cross-branch diff with explicit fetch
    enforcement_tier: str = "SOFT"    # GROUNDED | PARTIAL | SOFT
    notes: list[str] = field(default_factory=list)


def audit_workflow(path: pathlib.Path) -> WorkflowAudit:
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        wf = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return WorkflowAudit(
            path.stem, str(path), notes=[f"YAML parse error: {exc}"]
        )

    audit = WorkflowAudit(name=path.stem, path=str(path.relative_to(REPO_ROOT)))

    # Check concurrency
    if "concurrency" in (wf or {}):
        audit.has_concurrency = True

    # Check timeout on all jobs
    jobs = (wf or {}).get("jobs", {}) or {}
    if jobs and all("timeout-minutes" in j for j in jobs.values()):
        audit.has_timeout = True

    # Check cascade risk: workflow_run wildcard without self-exclusion
    on_triggers = (wf or {}).get("on", {})
    if isinstance(on_triggers, dict):
        wf_run = on_triggers.get("workflow_run", {})
        if isinstance(wf_run, dict):
            workflows = wf_run.get("workflows", [])
            if "*" in workflows:
                has_exclusion = any(
                    "github.event.workflow_run.name !=" in str(j.get("if", ""))
                    for j in jobs.values()
                )
                audit.has_cascade_risk = not has_exclusion

    # Check base-ref fetch for cross-branch diffs
    if "base_ref" in text or "github.base_ref" in text:
        if "git fetch origin" in text:
            audit.has_base_ref_fetch = True
        else:
            audit.notes.append("⚠️ Cross-branch diff without explicit base-ref fetch")

    # Classify enforcement tier
    if "cognitive-preflight" in text or "exit 1" in text:
        audit.enforcement_tier = "GROUNDED"
    elif "::warning::" in text or "createComment" in text:
        audit.enforcement_tier = "PARTIAL"

    return audit


def generate_matrix() -> None:
    audits = [audit_workflow(p) for p in sorted(WF_DIR.glob("*.yml"))]

    lines = [
        "# Workflow Compliance Matrix",
        f"> Generated: Phase 0 audit (WU-0.1) | {len(audits)} workflows scanned\n",
        "| Workflow | Concurrency | Timeout | Cascade Risk | Base-Ref Fetch | Enforcement Tier | Notes |",
        "|----------|:-----------:|:-------:|:------------:|:--------------:|:----------------:|-------|",
    ]
    for a in audits:
        lines.append(
            f"| `{a.name}` "
            f"| {'✅' if a.has_concurrency else '❌'} "
            f"| {'✅' if a.has_timeout else '❌'} "
            f"| {'⚠️' if a.has_cascade_risk else '✅'} "
            f"| {'✅' if a.has_base_ref_fetch else 'N/A'} "
            f"| {a.enforcement_tier} "
            f"| {'; '.join(a.notes) or '—'} |"
        )

    # KPI summary
    grounded = sum(1 for a in audits if a.enforcement_tier == "GROUNDED")
    partial  = sum(1 for a in audits if a.enforcement_tier == "PARTIAL")
    soft     = sum(1 for a in audits if a.enforcement_tier == "SOFT")
    cascade  = sum(1 for a in audits if a.has_cascade_risk)
    missing_concurrency = sum(1 for a in audits if not a.has_concurrency)
    missing_timeout     = sum(1 for a in audits if not a.has_timeout)

    lines += [
        "\n## KPI Summary",
        "| KPI | Count |",
        "|-----|-------|",
        f"| GROUNDED workflows     | {grounded} |",
        f"| PARTIAL workflows      | {partial} |",
        f"| SOFT workflows         | {soft} |",
        f"| Cascade risk           | {cascade} |",
        f"| Missing concurrency    | {missing_concurrency} |",
        f"| Missing timeout        | {missing_timeout} |",
    ]

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("\n".join(lines) + "\n")
    print(f"Matrix written: {OUT_FILE} ({len(audits)} workflows)")
    print(f"  GROUNDED={grounded}  PARTIAL={partial}  SOFT={soft}")
    print(f"  Cascade risk={cascade}  Missing concurrency={missing_concurrency}  Missing timeout={missing_timeout}")


if __name__ == "__main__":
    generate_matrix()
