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

if [[ -f "$WHEELHOUSE/CHECKSUMS.txt" ]]; then
  echo "Verifying wheelhouse checksum manifest..."
  (cd "$WHEELHOUSE" && sha256sum -c CHECKSUMS.txt >/dev/null)
else
  echo "wheelhouse checksum manifest missing: $WHEELHOUSE/CHECKSUMS.txt" >&2
  exit 2
fi

ARTIFACT_NAME="$(basename "$ARTIFACT")"
ARTIFACT_HASH="$(sha256sum "$ARTIFACT" | awk '{print $1}')"
EXPECTED_HASH="$(awk -v artifact="$ARTIFACT_NAME" '$2 == artifact {print $1; exit}' "$WHEELHOUSE/CHECKSUMS.txt")"
if [[ -z "$EXPECTED_HASH" ]]; then
  echo "Artifact $ARTIFACT_NAME is not listed in $WHEELHOUSE/CHECKSUMS.txt; refusing installation." >&2
  exit 2
fi
if [[ "$ARTIFACT_HASH" != "$EXPECTED_HASH" ]]; then
  echo "Artifact hash mismatch for $ARTIFACT_NAME; refusing installation." >&2
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
