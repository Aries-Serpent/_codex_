#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: apply_sandbox_bundle.sh [bundle_path] [repo_root]

Verify a repo-owned sandbox bundle, then apply the patch to the given repo root.
This is the primary-side receiving path for the file-backed handoff workflow.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bundle_path="${1:-}"
repo_root="${2:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

if [[ -z "$bundle_path" ]]; then
  usage >&2
  exit 1
fi

if [[ ! -d "$repo_root/.git" ]]; then
  echo "error: $repo_root is not a git repository" >&2
  exit 1
fi

python3 "$script_dir/archive/git_patch_bundle.py" verify --bundle "$bundle_path"
python3 "$script_dir/archive/git_patch_bundle.py" apply --bundle "$bundle_path" --repo-root "$repo_root"
