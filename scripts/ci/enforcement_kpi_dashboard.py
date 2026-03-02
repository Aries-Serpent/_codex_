"""
scripts/ci/enforcement_kpi_dashboard.py
Phase 5 — Enforcement gap scan + KPI dashboard for ci-health-monitor.yml.

Reads AGENT_REGISTRY.yaml, computes tier distribution, and writes an
enforcement KPI table to GITHUB_STEP_SUMMARY.

Usage:
  python scripts/ci/enforcement_kpi_dashboard.py
"""

from __future__ import annotations

import os
import pathlib
import sys
from collections import Counter

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".github" / "agents" / "AGENT_REGISTRY.yaml"


def main() -> None:
    try:
        import yaml
    except ImportError:
        print("::warning::pyyaml not installed — enforcement KPI scan skipped")
        sys.exit(0)

    if not REGISTRY_PATH.exists():
        print(f"::warning::Enforcement gap scan: AGENT_REGISTRY.yaml not found at {REGISTRY_PATH}")
        sys.exit(0)

    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    agents = data.get("agents", [])
    tc = Counter(a.get("enforcement_tier", "UNKNOWN") for a in agents)

    grounded = tc.get("GROUNDED", 0)
    partial = tc.get("PARTIAL", 0)
    soft = tc.get("SOFT", 0)
    total = len(agents)
    grounded_pct = round(grounded / total * 100, 1) if total else 0
    soft_pct = round(soft / total * 100, 1) if total else 0

    c3_pass = soft <= 2
    c5_pass = grounded >= 8

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null")
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n## 🛡️ Enforcement KPI Dashboard\n\n")
        f.write("| KPI | Value | Target | Status |\n")
        f.write("|-----|-------|--------|--------|\n")
        f.write(f"| Total agents | {total} | — | — |\n")
        f.write(
            f"| GROUNDED (Tier-1) | {grounded} ({grounded_pct}%) | ≥8 | {'✅' if c5_pass else '❌'} |\n"
        )
        f.write(f"| PARTIAL (Tier-2) | {partial} | — | — |\n")
        f.write(f"| SOFT (Tier-3) | {soft} ({soft_pct}%) | ≤2 | {'✅' if c3_pass else '❌'} |\n")
        f.write(f"| E→D C3 (SOFT≤2) | {soft} | ≤2 | {'✅ PASS' if c3_pass else '❌ FAIL'} |\n")
        f.write(
            f"| E→D C5 (GROUNDED≥8) | {grounded} | ≥8 | {'✅ PASS' if c5_pass else '❌ FAIL'} |\n"
        )

    print(f"✅ Enforcement KPI: GROUNDED={grounded}, PARTIAL={partial}, SOFT={soft}")
    print(f"   E→D gate: C3={c3_pass} C5={c5_pass}")


if __name__ == "__main__":
    main()
