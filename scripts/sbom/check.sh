#!/usr/bin/env bash
set -euo pipefail

# SBOM reverse-dependency check (Python + Node aware)
# Non-blocking by default; set STRICT_SBOM=1 to fail on issues.

# Enable ** globbing for recursive file matches and treat missing globs as empty
shopt -s globstar nullglob || true

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")"
OUT_DIR="$ROOT/.codex/sbom"
mkdir -p "$OUT_DIR"

STRICT="${STRICT_SBOM:-0}"
fail=0

log() { echo "[sbom] $*"; }
warn() { echo "::warning ::$*"; }
err()  { echo "::error ::$*"; }

has_py=0
has_node=0
if compgen -G "$ROOT/**/pyproject.toml" >/dev/null || compgen -G "$ROOT/**/requirements.txt" >/dev/null; then
  has_py=1
fi
if compgen -G "$ROOT/**/package.json" >/dev/null; then
  has_node=1
fi

log "detect: python=$has_py, node=$has_node"

# Prefer cdxgen if available (multi-ecosystem SBOM)
if command -v cdxgen >/dev/null 2>&1; then
  log "cdxgen found; generating CycloneDX SBOM"
  cdxgen -r -o "$OUT_DIR/sbom.cdx.json" || { warn "cdxgen failed"; [ "$STRICT" = "1" ] && fail=1; }
else
  log "cdxgen not found; using lightweight fallbacks"
fi

if [ "$has_py" = "1" ]; then
  if command -v pip-audit >/dev/null 2>&1; then
    log "running pip-audit"
    pip-audit -r requirements.txt -f json -o "$OUT_DIR/pip-audit.json" || {
      warn "pip-audit found issues or failed"
      [ "$STRICT" = "1" ] && fail=1
    }
  else
    log "pip-audit not found; capturing pip list"
    python3 -m pip list --format=json > "$OUT_DIR/pip-list.json" || true
  fi
fi

if [ "$has_node" = "1" ]; then
  if command -v npm >/dev/null 2>&1; then
    log "capturing npm ls --json"
    npm ls --json --all > "$OUT_DIR/npm-ls.json" || warn "npm ls returned non-zero (possible unmet peer deps)"
  fi
fi

if [ "$fail" -ne 0 ]; then
  err "SBOM checks flagged issues (STRICT_SBOM=1)."
  exit 1
fi
log "SBOM checks complete (non-blocking). Outputs in $OUT_DIR"
