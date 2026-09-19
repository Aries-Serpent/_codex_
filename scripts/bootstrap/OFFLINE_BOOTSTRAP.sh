#!/usr/bin/env bash
set -euo pipefail

# Offline installation bootstrap for packaged external deployments.
# Usage:
#   OFFLINE_BOOTSTRAP.sh --wheelhouse ./wheelhouse --artifact ./dist/codex_ml-0.1.0-py3-none-any.whl

WHEELHOUSE=""
ARTIFACT=""
VENV_DIR=".venv-offline"
PYTHON_BIN="python3"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wheelhouse)
      WHEELHOUSE="$2"
      shift 2
      ;;
    --artifact)
      ARTIFACT="$2"
      shift 2
      ;;
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$WHEELHOUSE" || -z "$ARTIFACT" ]]; then
  echo "Usage: $0 --wheelhouse <path> --artifact <wheel> [--venv <path>] [--python <bin>]" >&2
  exit 2
fi

if [[ ! -d "$WHEELHOUSE" ]]; then
  echo "wheelhouse not found: $WHEELHOUSE" >&2
  exit 2
fi

if [[ ! -f "$ARTIFACT" ]]; then
  echo "artifact not found: $ARTIFACT" >&2
  exit 2
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

MANIFEST_PATH="$WHEELHOUSE/manifest.json"
LEGACY_CHECKSUM_PATH="$WHEELHOUSE/CHECKSUMS.txt"
LEGACY_MANIFEST_PATH="$WHEELHOUSE/OFFLINE_MANIFEST.txt"

if [[ -f "$MANIFEST_PATH" ]]; then
  echo "Verifying signed wheelhouse manifest and artifact hash..."
  MASTER_KEY="${CODEX_MASTER_KEY:-${OFFLINE_MASTER_KEY:-}}"
  if [[ -z "$MASTER_KEY" ]]; then
    echo "CODEX_MASTER_KEY or OFFLINE_MASTER_KEY must be set to verify the signed wheelhouse manifest." >&2
    exit 2
  fi
  CODEX_MASTER_KEY="$MASTER_KEY" "$PYTHON_BIN" - "$WHEELHOUSE" "$ARTIFACT" <<'PY'
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path

wheelhouse = Path(sys.argv[1])
artifact = Path(sys.argv[2])
master_key = (os.environ.get("CODEX_MASTER_KEY") or os.environ.get("OFFLINE_MASTER_KEY") or "").strip()
if not master_key:
    raise SystemExit("CODEX_MASTER_KEY must be set to verify the signed wheelhouse manifest")
manifest_path = wheelhouse / "manifest.json"
if not manifest_path.exists():
    raise SystemExit(f"wheelhouse manifest missing: {manifest_path}")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
expected_sig = (manifest.get("signature") or "").strip()
if not expected_sig:
    raise SystemExit(f"signed wheelhouse manifest is missing a signature: {manifest_path}")
unsigned = {key: value for key, value in manifest.items() if key != "signature"}
canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
actual_sig = hmac.new(master_key.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
if not hmac.compare_digest(expected_sig, actual_sig):
    raise SystemExit("wheelhouse manifest signature mismatch; refusing installation")
artifact_name = artifact.name
wheel_data = manifest.get("wheels", {})
if artifact_name not in wheel_data:
    raise SystemExit(f"Artifact {artifact_name} is not listed in {manifest_path}; refusing installation")
actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
expected_hash = wheel_data[artifact_name].get("sha256")
if not expected_hash:
    raise SystemExit(f"Artifact {artifact_name} is missing a manifest hash; refusing installation")
if actual_hash != expected_hash:
    raise SystemExit(f"Artifact hash mismatch for {artifact_name}; refusing installation")
PY
elif [[ -f "$LEGACY_CHECKSUM_PATH" ]]; then
  echo "Verifying legacy wheelhouse checksum manifest..."
  if ! sha256sum -c "$LEGACY_CHECKSUM_PATH" --status --ignore-missing >/dev/null 2>&1; then
    echo "Legacy wheelhouse checksum verification failed for $LEGACY_CHECKSUM_PATH" >&2
    exit 2
  fi
  if [[ -f "$LEGACY_MANIFEST_PATH" ]]; then
    echo "Using legacy offline manifest: $LEGACY_MANIFEST_PATH"
  fi
  "$PYTHON_BIN" - "$WHEELHOUSE" "$ARTIFACT" <<'PY'
import hashlib
import os
import sys
from pathlib import Path

wheelhouse = Path(sys.argv[1])
artifact = Path(sys.argv[2])
checksum_path = wheelhouse / "CHECKSUMS.txt"
if not checksum_path.exists():
    raise SystemExit(f"legacy checksum manifest missing: {checksum_path}")
artifact_name = artifact.name
checksum_matches = False
for raw_line in checksum_path.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#"):
        continue
    if "  " not in line:
        continue
    digest, name = [part.strip() for part in line.rsplit("  ", 1)]
    if name == artifact_name:
        actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if digest == actual_hash:
            checksum_matches = True
            break
if not checksum_matches:
    raise SystemExit(f"Artifact {artifact_name} is not present in or does not match {checksum_path}; refusing installation")
PY
else
  echo "wheelhouse manifest missing: $MANIFEST_PATH" >&2
  exit 2
fi

python -m pip install --upgrade pip
python -m pip install --no-index --find-links "$WHEELHOUSE" "$ARTIFACT"

cat <<'EOF'
Offline bootstrap complete.

Next steps:
1. source <venv>/bin/activate
2. codex --help
3. python -m codex_ml.cli.offline_bootstrap bootstrap --root ./.codex/offline
EOF
