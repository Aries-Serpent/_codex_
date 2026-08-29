"""
Workflow Owner Audit — D6 exit criteria #4 helper.

Checks that every .github/workflows/*.yml has an owner entry in
.codex/DOMAIN_OWNERSHIP.md or a .meta file in .github/workflow-archive/.

Usage:
    python scripts/ci/workflow_owner_audit.py [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_owned_workflows() -> set[str]:
    """Collect workflow names that have owner records."""
    owned: set[str] = set()

    # 1. Scan DOMAIN_OWNERSHIP.md for workflow references
    dom_path = Path(".codex/DOMAIN_OWNERSHIP.md")
    if dom_path.exists():
        text = dom_path.read_text()
        for match in re.findall(r"`([a-z0-9_\-]+\.yml)`", text):
            owned.add(match)

    # 2. Scan .meta files in workflow-archive
    for meta in Path(".github/workflow-archive").rglob("*.meta"):
        owned.add(meta.stem.replace(".yml", "") + ".yml")

    # 3. Scan CONSOLIDATION_PLAN.md
    plan = Path("docs/workflows/CONSOLIDATION_PLAN.md")
    if plan.exists():
        for match in re.findall(r"`([a-z0-9_\-]+\.yml)`", plan.read_text()):
            owned.add(match)

    return owned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=".codex/reports/ci/workflow_owner_audit.json")
    parser.add_argument("--threshold", type=float, default=90.0,
                        help="Minimum %% of workflows that must have owners")
    args = parser.parse_args()

    workflow_dir = Path(".github/workflows")
    all_workflows = sorted(p.name for p in workflow_dir.glob("*.yml") if p.is_file())
    owned = load_owned_workflows()

    missing_owner = [w for w in all_workflows if w not in owned]
    owned_count = len(all_workflows) - len(missing_owner)
    coverage_pct = round(owned_count / len(all_workflows) * 100, 1) if all_workflows else 0.0

    report = {
        "generated_at": _ts(),
        "total_workflows": len(all_workflows),
        "owned_workflows": owned_count,
        "missing_owner": missing_owner,
        "coverage_pct": coverage_pct,
        "threshold_pct": args.threshold,
        "passed": coverage_pct >= args.threshold,
    }

    print(json.dumps(report, indent=2))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2))

    if report["passed"]:
        print(f"::notice::✅ D6 exit criteria #4: {coverage_pct}% workflows have owners")
    else:
        print(f"::warning::D6 workflow owner coverage {coverage_pct}% below {args.threshold}%")
        if missing_owner:
            print("Workflows missing owners:")
            for w in missing_owner[:20]:
                print(f"  - {w}")

    if not report["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
