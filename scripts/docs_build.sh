#!/usr/bin/env bash
set -euo pipefail

# Flags
SKIP_OPTIONAL="${SKIP_OPTIONAL:-1}"
FAIL_ON_MISSING="${FAIL_ON_MISSING:-0}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART_DIR="${ROOT}/artifacts/docs"
MANIFEST="${ROOT}/artifacts/docs_manifest.sha"

mkdir -p "${ART_DIR}"

echo "[INFO] Docs build starting (SKIP_OPTIONAL=${SKIP_OPTIONAL}, FAIL_ON_MISSING=${FAIL_ON_MISSING})"

# Discover top-level importable packages (dirs with __init__.py)
mapfile -t PKG_DIRS < <(find "${ROOT}" -maxdepth 1 -type d ! -name '.*' \
  ! -name 'scripts' ! -name 'tests' ! -name 'docs' ! -name 'reports' \
  ! -name 'audit_artifacts' ! -name 'artifacts' -print)

PACKAGES=()
for d in "${PKG_DIRS[@]}"; do
  if [ -f "${d}/__init__.py" ]; then
    base="$(basename "${d}")"
    PACKAGES+=("${base}")
  fi
done

# Preflight import check (strict mode)
if [ "${FAIL_ON_MISSING}" = "1" ]; then
  echo "[INFO] Strict import preflight..."
  python - <<'PY' "${PACKAGES[@]}"
import importlib, sys, os
pkgs = sys.argv[1:]
missing = []
for m in pkgs:
    try:
        importlib.import_module(m)
    except Exception as e:
        missing.append((m, str(e)))
if missing:
    print("[ERROR] Missing imports (strict):", missing)
    sys.exit(2)
print("[INFO] Strict preflight OK")
PY
else
  echo "[WARN] Strict mode disabled; missing imports will be tolerated."
fi

# Build using pdoc if available; otherwise generate a simple index
if python -c "import pdoc" >/dev/null 2>&1; then
  echo "[INFO] Using pdoc for API docs"
  # Environment hint for optional deps gating
  export CODEX_DOCS_SKIP_OPTIONAL="${SKIP_OPTIONAL}"
  # If no explicit packages, default to repository root module discovery
  if [ "${#PACKAGES[@]}" -gt 0 ]; then
    pdoc --force --output-dir "${ART_DIR}" "${PACKAGES[@]}" || true
  else
    pdoc --force --output-dir "${ART_DIR}" . || true
  fi
else
  echo "[WARN] pdoc not installed; generating index only."
fi

# Always create a minimal index with build info
BUILD_INFO="${ART_DIR}/INDEX.md"
{
  echo "# API Documentation Index"
  echo ""
  echo "- Generated: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  echo "- SKIP_OPTIONAL=${SKIP_OPTIONAL}"
  echo "- FAIL_ON_MISSING=${FAIL_ON_MISSING}"
  echo ""
  echo "## Discovered Packages"
  if [ "${#PACKAGES[@]}" -eq 0 ]; then
    echo "- (none)"
  else
    for p in "${PACKAGES[@]}"; do echo "- ${p}"; done
  fi
} > "${BUILD_INFO}"

# Manifest of docs files (sha256)
( cd "${ART_DIR}" && find . -type f -print0 | sort -z | xargs -0 sha256sum ) > "${MANIFEST}"

echo "[INFO] Docs build finished. Artifacts in ${ART_DIR}"

