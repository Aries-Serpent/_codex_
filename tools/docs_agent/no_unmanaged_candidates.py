from __future__ import annotations

import argparse
import json
from pathlib import Path

from .coverage import run_coverage
from .utils import parse_common_args, write_json


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Fail if unmanaged candidate files exist")
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root)
    result = run_coverage(repo_root, strict=False)
    
    # Load policy to check fail_on_unmanaged_candidates setting
    from .utils import load_policy
    policy = load_policy(repo_root)
    should_fail_on_unmanaged = policy.get("enforcement", {}).get("fail_on_unmanaged_candidates", True)
    
    report = {
        "ok": (len(result["report"]["unmanaged_files"]) == 0 or not should_fail_on_unmanaged),
        "unmanaged_count": len(result["report"]["unmanaged_files"]),
        "unmanaged_files": result["report"]["unmanaged_files"],
        "message": (
            "No unmanaged candidate files"
            if len(result["report"]["unmanaged_files"]) == 0
            else (
                "Unmanaged candidate files detected (but policy allows them)"
                if not should_fail_on_unmanaged
                else "Unmanaged candidate files detected"
            )
        ),
        "policy_enforcement": {
            "fail_on_unmanaged_candidates": should_fail_on_unmanaged,
        },
    }
    out = repo_root / "docs-data" / "generated" / "unmanaged-candidates-report.json"
    write_json(out, report)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
