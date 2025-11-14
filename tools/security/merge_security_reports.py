"""
Merge security artifacts into an aggregated quick summary.

Inputs (if present):
  - artifacts/security_report.json
  - artifacts/bandit_report.txt
  - artifacts/gitleaks_report.json
Output:
  - artifacts/security_summary.json
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ART = Path("artifacts")


def count_gitleaks(raw: str) -> int:
    try:
        data = json.loads(raw or "[]")
        if isinstance(data, dict) and "findings" in data:
            return len(data.get("findings") or [])
        if isinstance(data, list):
            return len(data)
    except Exception:
        return 0
    return 0


def main() -> None:
    pip_path = ART / "security_report.json"
    bandit_path = ART / "bandit_report.txt"
    gitleaks_path = ART / "gitleaks_report.json"

    summary: Dict[str, Any] = {}
    if pip_path.exists():
        try:
            raw = json.loads(pip_path.read_text(encoding="utf-8"))
            deps = raw if isinstance(raw, list) else raw.get("dependencies", [])
            hc = 0
            items = []
            for dep in deps:
                name = dep.get("name") or dep.get("package", {}).get("name")
                for v in dep.get("vulns") or dep.get("vulnerabilities") or []:
                    sev = (v.get("severity") or "").upper()
                    vid = v.get("id") or v.get("vuln_id")
                    if sev in {"HIGH", "CRITICAL"}:
                        hc += 1
                        items.append({"pkg": name, "id": vid, "severity": sev})
            summary["pip_audit"] = {"high_critical": hc, "high_critical_list": items}
        except Exception:
            summary["pip_audit"] = {"error": "parse_failed"}

    if bandit_path.exists():
        summary["bandit"] = {"present": True}
    if gitleaks_path.exists():
        summary["gitleaks"] = {"findings_count": count_gitleaks(gitleaks_path.read_text(encoding="utf-8"))}

    (ART / "security_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Wrote artifacts/security_summary.json")


if __name__ == "__main__":
    main()
