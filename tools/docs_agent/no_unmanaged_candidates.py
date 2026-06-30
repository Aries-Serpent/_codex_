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
    report = {
        "ok": len(result["report"]["unmanaged_files"]) == 0,
        "unmanaged_count": len(result["report"]["unmanaged_files"]),
        "unmanaged_files": result["report"]["unmanaged_files"],
        "message": (
            "No unmanaged candidate files"
            if len(result["report"]["unmanaged_files"]) == 0
            else "Unmanaged candidate files detected"
        ),
    }
    out = repo_root / "docs-data" / "generated" / "unmanaged-candidates-report.json"
    write_json(out, report)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
