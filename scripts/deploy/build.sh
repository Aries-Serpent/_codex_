# BEGIN: CODEX_DEPLOY_SCRIPT
#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${IMAGE:=codex-api:local}"
docker build -t "$IMAGE" -f Dockerfile .
echo "Built $IMAGE"
