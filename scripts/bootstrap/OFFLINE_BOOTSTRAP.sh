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

python -m pip install --upgrade pip
python -m pip install --no-index --find-links "$WHEELHOUSE" "$ARTIFACT"

cat <<'EOF'
Offline bootstrap complete.

Next steps:
1. source <venv>/bin/activate
2. codex --help
3. python -m codex_ml.cli.offline_bootstrap bootstrap --root ./.codex/offline
EOF
