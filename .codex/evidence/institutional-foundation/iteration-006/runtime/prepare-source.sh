#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/runner/work/_codex_/_codex_
OUT="$ROOT/.codex/evidence/institutional-foundation/iteration-006/runtime"
SOURCE=fa2e6e406f5767fd8ab5a15ffc99b49f9123f71c
exec > >(tee -a "$OUT/source-preparation.log") 2>&1
set -x
test "$(git -C "$ROOT" rev-parse --verify "$SOURCE")" = "$SOURCE"
mkdir -p "$OUT/immutable-source/src/codex/institutional"
for name in assurance.py contracts.json core.py storage.py; do
  git -C "$ROOT" show "$SOURCE:src/codex/institutional/$name" \
    > "$OUT/immutable-source/src/codex/institutional/$name"
done
env -u PYTHONPATH "$OUT/cache/venv/bin/python" -I -B - <<'PY'
import hashlib
import json
from pathlib import Path

out = Path("/home/runner/work/_codex_/_codex_/.codex/evidence/institutional-foundation/iteration-006/runtime")
files = [
    {"path": str(p.relative_to(out / "immutable-source")),
     "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
     "bytes": p.stat().st_size, "mode": 0o644}
    for p in sorted((out / "immutable-source").rglob("*")) if p.is_file()
]
value = {
    "source_commit": "fa2e6e406f5767fd8ab5a15ffc99b49f9123f71c",
    "files": files,
    "preparation": "git show exact immutable commit before entering guarded SDK runtime",
    "repository_review": "PENDING_ACTUAL_ANALYTICAL_OUTPUTS",
    "G5": "NOT_RUN", "authority": "none",
}
(out / "immutable-source.json").write_text(json.dumps(value, indent=2) + "\n")
print(json.dumps(value))
PY
