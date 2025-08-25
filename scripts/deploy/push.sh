# BEGIN: CODEX_DEPLOY_SCRIPT
#!/usr/bin/env bash
set -euo pipefail
umask 077
if [[ -z "${REGISTRY:-}" ]]; then
  echo "Set REGISTRY (e.g., ghcr.io/owner/repo:tag) to push"; exit 1
fi
: "${IMAGE:=codex-api:local}"
docker tag "$IMAGE" "$REGISTRY"
docker push "$REGISTRY"
echo "Pushed $REGISTRY"
