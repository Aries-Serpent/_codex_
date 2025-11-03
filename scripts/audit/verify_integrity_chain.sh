#!/usr/bin/env bash
set -euo pipefail

if [ ! -f audit_run_manifest.json ]; then
  echo "[FAIL] audit_run_manifest.json missing. Run scripts/audit/run_full_audit.sh"
  exit 1
fi

echo "[INFO] Verifying audit integrity chain hashes"
python - <<'PY'
import json, hashlib, sys
from pathlib import Path
m = json.loads(Path("audit_run_manifest.json").read_text(encoding="utf-8"))
ok = True
for a in m.get("artifacts", []):
    p = Path(a["path"])
    if not p.exists():
        print(f"[MISS] {p}")
        ok = False
        continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != a["sha256"]:
        print(f"[MISMATCH] {p} expected {a['sha256']} got {h}")
        ok = False
if ok:
    print("[OK] Integrity verified")
    sys.exit(0)
else:
    print("[FAIL] Integrity verification failed")
    sys.exit(1)
PY
