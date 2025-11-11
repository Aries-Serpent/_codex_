#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def main():
    outdir = Path("audit_artifacts")
    outdir.mkdir(parents=True, exist_ok=True)
    try:
        txt = subprocess.check_output(["pipdeptree","-j"], text=True)
        (outdir/"dep_graph.json").write_text(txt)
    except Exception:
        # fallback to freeze
        try:
            import pkg_resources
            rows = [{"name": d.project_name, "version": d.version} for d in pkg_resources.working_set]
        except Exception:
            # even simpler fallback
            rows = [{"note": "pkg_resources unavailable"}]
        (outdir/"dep_graph.json").write_text(json.dumps(rows, indent=2))
    print("audit_artifacts/dep_graph.json")

if __name__ == "__main__":
    main()
