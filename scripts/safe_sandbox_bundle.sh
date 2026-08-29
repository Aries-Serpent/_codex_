#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: safe_sandbox_bundle.sh [repo_root] [bundle_root] [bundle_name]

Create a repo-owned patch bundle without piping raw git diff output into a
consumer. The payload is written to a file, compressed, checksum-protected,
and bundled for a safe sandbox-to-primary handoff.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
bundle_root="${2:-$repo_root/.codex/sandbox-bundles}"
bundle_name="${3:-sandbox-git-transfer}"

if [[ ! -d "$repo_root/.git" ]]; then
  echo "error: $repo_root is not a git repository" >&2
  exit 1
fi

python3 "$script_dir/archive/git_patch_bundle.py" \
  bundle \
  --repo-root "$repo_root" \
  --output-dir "$bundle_root" \
  --bundle-name "$bundle_name"
