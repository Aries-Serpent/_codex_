#!/usr/bin/env python3
import json
from pathlib import Path
try:
    from importlib.metadata import distributions
except Exception:
    from importlib_metadata import distributions  # type: ignore

def main():
    rows = []
    for d in distributions():
        md = d.metadata
        rows.append({"name": md.get("Name",""), "version": md.get("Version",""), "license": md.get("License","")})
    out = Path("audit_artifacts"); out.mkdir(parents=True, exist_ok=True)
    (out/"license_audit.json").write_text(json.dumps(rows, indent=2))
    print("audit_artifacts/license_audit.json")

if __name__ == "__main__":
    raise SystemExit(main())
