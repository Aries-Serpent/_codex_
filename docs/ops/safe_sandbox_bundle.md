# Safe sandbox bundle flow

This is the approved sandbox-to-primary transfer path: write the patch bundle to a repo-owned file, checksum and verify it, then ship the archive instead of streaming raw `git diff` output through a pipe.

## Audit summary: transfer artefact and root-archive conventions in this repo

The repository already encodes a clear hierarchy for transfer and archival safety:

- Canonical repository metadata stays at the repo root. The cleanup standards call out `README.md`, `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, `pyproject.toml`, `requirements*.txt`, and similar files as root-owned and non-negotiable in `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md`.
- Generated or historical work products are deliberately moved out of the root into structured archive locations such as `.codex/archive/root-consolidation/` and `misc/repo-owner-review/`.
- Operational policy is explicit: `.github/TEMPORARY_FILES_POLICY.md` forbids storing important output under `/tmp`, `/var/tmp`, or any non-repository scratch path, and directs work products to repo-owned directories instead.
- The archival workflow in `.github/workflows/scheduled-archival.yml` targets stale content and expects archive outputs under `misc/repo-owner-review/archived/` or similar review-managed paths.
- The root-consolidation index in `.codex/archive/root-consolidation/INDEX.md` treats temporary outputs, phase history, and deprecated reports as archive-managed assets, not root-owned files.

The safe operational rule is simple: keep transfer payloads in repo-owned staging and archive directories; never persist meaningful state in a transient shell temp directory. The canonical helper for this pattern is `scripts/archive/git_patch_bundle.py`, which writes the patch to disk, verifies the archive checksum, and then applies it on the receiving side.

## Why the flow must avoid SIGPIPE

A common failure mode is piping diff output directly into a consumer that exits early, for example:

```bash
git diff --binary HEAD | head
```

When `head` exits after the first screen, the upstream `git diff` process can receive a SIGPIPE and terminate unexpectedly. That causes partial or lost transfer artefacts at exactly the time the bundle is being prepared.

The repo safety pattern is to treat the diff as a file first and only then read or inspect that file later. The bundle itself should be produced from the staged file set, and the archive should be validated with a checksum before it is treated as trustworthy.

## Safe flow

Use a repo-owned bundle directory under `.codex/sandbox-bundles/<timestamp>/` (or an approved repo review path such as `misc/repo-owner-review/`). The flow is:

1. Create a bundle directory inside the repository.
2. Write the work-tree and staged diffs to files in that directory.
3. Write a manifest and any summary metadata to the same directory.
4. Create the archive from the bundle directory (not from a pipe).
5. Produce a checksum for the archive and verify it.
6. Store the manifest and validation output next to the archive so the transfer is auditable.

Example sequence:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(git rev-parse --show-toplevel)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
bundle_dir="$repo_root/.codex/sandbox-bundles/$stamp"
mkdir -p "$bundle_dir"

# Store the raw diffs in files; do not pipe them directly into a consumer.
git -C "$repo_root" status --short > "$bundle_dir/status.txt"
git -C "$repo_root" --no-pager diff --binary --staged -- . > "$bundle_dir/staged.patch"
git -C "$repo_root" --no-pager diff --binary -- . > "$bundle_dir/worktree.patch"

git -C "$repo_root" --no-pager diff --name-only --cached > "$bundle_dir/changed_cached.txt"
git -C "$repo_root" --no-pager diff --name-only > "$bundle_dir/changed_worktree.txt"

# Build the archive from the repository-managed bundle directory.
tar -C "$bundle_dir" -czf "$bundle_dir/sandbox_bundle_${stamp}.tar.gz" \
  status.txt staged.patch worktree.patch changed_cached.txt changed_worktree.txt

sha256sum "$bundle_dir/sandbox_bundle_${stamp}.tar.gz" \
  > "$bundle_dir/sandbox_bundle_${stamp}.tar.gz.sha256"
sha256sum -c "$bundle_dir/sandbox_bundle_${stamp}.tar.gz.sha256" \
  > "$bundle_dir/checksum_verification.txt"

tar -tzf "$bundle_dir/sandbox_bundle_${stamp}.tar.gz" \
  > "$bundle_dir/archive_manifest.txt"
```

This pattern preserves the source diff, prevents SIGPIPE, and produces a verified bundle with an audit trail.

## Recommended repo hygiene rules

- Never write important transfer artefacts to `/tmp` or a shell scratch directory.
- Always place bundle payloads under repo-owned paths such as `.codex/`, `misc/repo-owner-review/`, or the project’s archive roots.
- Treat generated diffs, manifests, and checksum files as durable transfer artefacts, not ephemeral logs.
- Verify the archive before transferring it elsewhere.
- Keep archive names timestamped and human-readable, and keep the checksum beside the archive.

## Reference conventions already in this repo

- `.codex/archive/root-consolidation/INDEX.md`
- `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md`
- `.github/TEMPORARY_FILES_POLICY.md`
- `.github/workflows/scheduled-archival.yml`

The bundle flow above respects those conventions and keeps the repo hygiene rules intact while avoiding SIGPIPE-related data loss.
