#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: safe_sandbox_bundle.sh [repo_root] [bundle_root]

Creates a repo-owned sandbox bundle that stores git diff output in files,
creates a tar.gz archive, and verifies the archive with SHA-256.

The bundle is written under the repository tree so important transfer artefacts
are not lost in /tmp or other transient shell scratch locations.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

repo_root="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
bundle_root="${2:-$repo_root/.codex/sandbox-bundles}"

if [[ ! -d "$repo_root/.git" ]]; then
  echo "error: $repo_root is not a git repository" >&2
  exit 1
fi

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
bundle_dir="$bundle_root/$stamp"
mkdir -p "$bundle_dir"

# Store diffs as files instead of piping them into consumers, which avoids SIGPIPE
# when a downstream command exits early.
git -C "$repo_root" status --short > "$bundle_dir/status.txt"
git -C "$repo_root" --no-pager diff --binary --staged -- . > "$bundle_dir/staged.patch" || true
git -C "$repo_root" --no-pager diff --binary -- . > "$bundle_dir/worktree.patch" || true
git -C "$repo_root" --no-pager diff --name-only --cached > "$bundle_dir/changed_cached.txt" || true
git -C "$repo_root" --no-pager diff --name-only > "$bundle_dir/changed_worktree.txt" || true

echo "$repo_root" > "$bundle_dir/repo_root.txt"
echo "$stamp" > "$bundle_dir/stamp.txt"

archive_path="$bundle_dir/sandbox_bundle_${stamp}.tar.gz"

tar -C "$bundle_dir" -czf "$archive_path" \
  status.txt staged.patch worktree.patch changed_cached.txt changed_worktree.txt \
  repo_root.txt stamp.txt

sha256sum "$archive_path" > "$archive_path.sha256"
sha256sum -c "$archive_path.sha256" > "$bundle_dir/checksum_verification.txt" 2>&1

tar -tzf "$archive_path" > "$bundle_dir/archive_manifest.txt"

printf 'Sandbox bundle created at: %s\n' "$archive_path"
printf 'SHA256 verification: %s\n' "$bundle_dir/checksum_verification.txt"
printf 'Diff payloads stored in: %s\n' "$bundle_dir"
