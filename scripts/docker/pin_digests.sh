#!/usr/bin/env bash
# ============================================================================
# scripts/docker/pin_digests.sh
# ============================================================================
# Re-pin all Docker base images in this repository to their current SHA256
# digests.  Run this script whenever you want to update the pinned digests
# (e.g. after a security patch to python:3.12-slim or a CUDA image update).
#
# Requirements:
#   - skopeo  (https://github.com/containers/skopeo)
#   - sed / GNU tools (standard on Linux; macOS needs GNU sed via brew)
#
# Usage:
#   bash scripts/docker/pin_digests.sh [--dry-run]
#
# With --dry-run the script prints the new FROM lines without modifying files.
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DRY_RUN=false

for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

log() { echo "[pin_digests] $*"; }
die() { echo "[pin_digests] ERROR: $*" >&2; exit 1; }

command -v skopeo >/dev/null 2>&1 || die "skopeo is required but not installed."

# ---------------------------------------------------------------------------
# resolve_digest IMAGE:TAG
# Returns the manifest-list digest (sha256:...) for the given image reference.
# ---------------------------------------------------------------------------
resolve_digest() {
  local image="$1"
  skopeo inspect "docker://${image}" 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('Digest',''))"
}

# ---------------------------------------------------------------------------
# pin_in_file FILE OLD_REF NEW_DIGEST
# Replaces FROM <OLD_REF> with FROM <OLD_REF>@<NEW_DIGEST> in FILE.
# The original tag line is kept as a comment above for human readability.
# ---------------------------------------------------------------------------
pin_in_file() {
  local file="$1"
  local old_ref="$2"    # e.g. python:3.12-slim
  local digest="$3"     # e.g. sha256:abc123...
  local new_ref="${old_ref}@${digest}"

  if ! grep -qF "FROM ${old_ref}" "${file}"; then
    return 0  # nothing to pin in this file
  fi

  log "  ${file}: ${old_ref} → ${new_ref}"
  if [[ "$DRY_RUN" == "false" ]]; then
    # Use Python for reliable in-place sed (avoids macOS/GNU sed differences)
    python3 - "${file}" "${old_ref}" "${new_ref}" <<'PYEOF'
import sys, re

filepath, old_ref, new_ref = sys.argv[1], sys.argv[2], sys.argv[3]
with open(filepath, 'r') as fh:
    content = fh.read()

# Replace pinned digest form (already has @sha256:) with new digest
pinned_pattern = re.compile(
    r'^(FROM\s+)' + re.escape(old_ref) + r'@sha256:[a-f0-9]+',
    re.MULTILINE
)
# Replace tag-only form (no @sha256 yet)
tag_only_pattern = re.compile(
    r'^(FROM\s+)' + re.escape(old_ref) + r'(?!@)',
    re.MULTILINE
)

new_content = pinned_pattern.sub(r'\g<1>' + new_ref, content)
new_content = tag_only_pattern.sub(r'\g<1>' + new_ref, new_content)

with open(filepath, 'w') as fh:
    fh.write(new_content)
PYEOF
  fi
}

# ---------------------------------------------------------------------------
# Image table: IMAGE_TAG -> list of files that use it
# Update this table whenever pyproject.toml package-dir changes require new
# Dockerfiles, or when new base images are added.
# ---------------------------------------------------------------------------

declare -A IMAGE_FILES
IMAGE_FILES["python:3.12-slim"]="Dockerfile Dockerfile.preview Dockerfile.restore .github/agents/security-scan-agent/Dockerfile docker/Dockerfile.local docker/Dockerfile.optimized"
IMAGE_FILES["python:3.12.3-slim"]=".github/agents/ci-testing-agent/Dockerfile"
IMAGE_FILES["python:3.10-slim"]="docker/Dockerfile.cpu"
IMAGE_FILES["python:3.14-slim"]="docker/Dockerfile.ci docker/Dockerfile.embedding docker/Dockerfile.gpu docker/Dockerfile.local-codex-env"
IMAGE_FILES["nvidia/cuda:13.3.0-runtime-ubuntu22.04"]="Dockerfile"
IMAGE_FILES["nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04"]="docker/Dockerfile.gpu"

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
log "Resolving digests and pinning base images..."
log "Repository root: ${REPO_ROOT}"
[[ "$DRY_RUN" == "true" ]] && log "(DRY RUN — no files will be modified)"

for image_tag in "${!IMAGE_FILES[@]}"; do
  log "Resolving ${image_tag} ..."
  digest="$(resolve_digest "${image_tag}")"
  if [[ -z "$digest" ]]; then
    echo "[pin_digests] WARN: could not resolve digest for ${image_tag} — skipping" >&2
    continue
  fi
  log "  digest: ${digest}"
  for rel_file in ${IMAGE_FILES[$image_tag]}; do
    abs_file="${REPO_ROOT}/${rel_file}"
    if [[ -f "$abs_file" ]]; then
      pin_in_file "${abs_file}" "${image_tag}" "${digest}"
    else
      log "  (skipped — file not found: ${rel_file})"
    fi
  done
done

log ""
log "Done. Commit the updated Dockerfiles:"
log "  git add Dockerfile Dockerfile.preview Dockerfile.restore docker/ .github/agents/"
log "  git commit -m 'build: re-pin Docker base images to current SHA256 digests'"
