#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    scored = Path("audit_artifacts/capabilities_scored.json")
    gaps = Path("audit_artifacts/gaps.json")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(f"reports/capability_matrix_{ts}.md")
    out.parent.mkdir(parents=True, exist_ok=True)

    caps = []
    if scored.exists():
        data = json.loads(scored.read_text(encoding="utf-8"))
        caps = data.get("capabilities", [])

    gap_flags = set()
    if gaps.exists():
        g = json.loads(gaps.read_text(encoding="utf-8"))
        for item in g.get("items", []):
            gap_flags.add(item.get("name"))

    lines = []
    lines.append(f"# Capability Matrix — {ts}")
    lines.append("")
    lines.append("| Name | Category | Status | Severity | Confidence | Weight | Gap | Evidence |")
    lines.append("|---|---|---|---:|---:|---:|---|---|")
    for c in caps:
        lines.append(
            f"| {c.get('name','')} | {c.get('category','')} | {c.get('status','')} | "
            f"{c.get('severity',0)} | {c.get('confidence',0)} | {c.get('weight',0):.3f} | "
            f"{'YES' if c.get('name') in gap_flags else ''} | {c.get('artifacts','')} |"
        )

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
