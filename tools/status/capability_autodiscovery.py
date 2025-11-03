#!/usr/bin/env python3
import json
from pathlib import Path

RULES = [
  ("Tokenization","Data I/O","tokenization/cli.py",["token","encode","decode"],3,4),
  ("Modeling (dtype/device)","Model","src/codex_ml/models/factory.py",["dtype","device"],3,4),
  ("Eval & Metrics","Eval","src/codex_ml/eval/runner.py",["metrics","sink"],2,4),
  ("Internal Tests","Quality","noxfile.py",["session","pytest"],2,4),
  ("Docker","Ops","Dockerfile",["FROM","RUN"],2,4),
]

def score(cap):
    # trivial severity/confidence; adjust later
    return {"severity": cap[4], "confidence": cap[5]}

def main():
    root = Path(".")
    caps = []
    for name, cat, path, _kw, sev, conf in RULES:
        p = root / path
        status = "Implemented" if p.exists() else "Missing"
        caps.append({
          "name": name, "category": cat, "status": status,
          "artifacts": path if p.exists() else "(absent)",
          "gaps": "" if p.exists() else f"{path} not found",
          "risks": "" if p.exists() else "Feature absent",
          "severity": sev, "confidence": conf,
          "patch_plan": "create minimal scaffold" if not p.exists() else "n/a",
          "rollback": "delete scaffold" if not p.exists() else "n/a"
        })
    outdir = root/"audit_artifacts"; outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"capabilities_scored.json").write_text(json.dumps(caps, indent=2))
    print("audit_artifacts/capabilities_scored.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
