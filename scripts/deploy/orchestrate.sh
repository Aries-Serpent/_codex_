#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage: $0 <build|push|run> [--gpu] [--dry-run] [args...]

Commands:
  build     Build the Docker image (multi-stage targets available)
  push      Push the built image to the configured registry
  run       Execute docker-compose with optional overrides

Options:
  --gpu     Target the GPU runtime stage
  --dry-run Print the command without executing it
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

command=$1
shift

gpu_target=false
dry_run=false
extra_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gpu)
      gpu_target=true
      ;;
    --dry-run)
      dry_run=true
      ;;
    *)
      extra_args+=("$1")
      ;;
  esac
  shift || true
done

image_tag=${CODEX_IMAGE:-codex:local}
run_cmd() {
  if [[ "${dry_run}" == true ]]; then
    echo "[dry-run] $*"
  else
    echo "+ $*"
    eval "$@"
  fi
}

case "${command}" in
  build)
    target="cpu-runtime"
    [[ "${gpu_target}" == true ]] && target="gpu-runtime"
    run_cmd "docker build --target ${target} -t ${image_tag} ${extra_args[*]:-} ."
    ;;
  push)
    run_cmd "docker push ${image_tag}"
    ;;
  run)
    compose_cmd="docker compose up ${extra_args[*]:-}"
    run_cmd "${compose_cmd}"
    ;;
  *)
    usage
    exit 1
    ;;
 esac
