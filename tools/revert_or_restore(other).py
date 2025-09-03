#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offline revert/restore helper.

Scenarios:
1) Restore from guarded backups:
   python tools/revert_or_restore.py --from-backup 20250901T154500Z
   (copies from .codex/patch_backups/<ts>/... back to working tree)

2) Undo uncommitted changes safely (working tree + index):
   python tools/revert_or_restore.py --git-restore
   (uses `git restore -SW .`, available since Git 2.23+)  [git-restore docs]

3) Revert a committed patch by SHA (creates a new "revert" commit):
   python tools/revert_or_restore.py --git-revert <COMMIT_SHA>  [git-revert docs]

The script also surfaces any *.rej files produced by `git apply --reject`.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUPS = ROOT / ".codex" / "patch_backups"


def _run(cmd):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def list_rejects():
    rej = list(ROOT.rglob("*.rej"))
    if rej:
        print("\n[info] Found .rej files from a patch apply (manual merge likely required):")
        for p in rej:
            print(" -", p.relative_to(ROOT))
    else:
        print("\n[info] No .rej files detected.")


def restore_from_backup(ts: str):
    src = BACKUPS / ts
    if not src.exists():
        raise SystemExit(f"[error] backup timestamp not found: {src}")
    restored = 0
    for p in src.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src)
            dst = ROOT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            restored += 1
    print(f"[ok] restored {restored} files from {src}")


def git_restore_all():
    # Restore both index and worktree (-SW)
    # Equivalent to pre-2.23 `git checkout .`, but modern and explicit.
    r = _run(["git", "restore", "-SW", "."])
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("[error] git restore -SW . failed. Ensure you are in a Git repo.")
    print("[ok] git restore -SW . completed")


def git_revert_commit(sha: str):
    # Creates a new revert commit of the given SHA; requires clean tree.
    r = _run(["git", "revert", "--no-edit", sha])
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("[error] git revert failed. Ensure tree is clean and SHA is correct.")
    print(f"[ok] reverted commit {sha}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--from-backup",
        help="Timestamp dir under .codex/patch_backups to restore (e.g., 20250901T154500Z)",
    )
    ap.add_argument(
        "--git-restore",
        action="store_true",
        help="Undo uncommitted changes with `git restore -SW .`",
    )
    ap.add_argument("--git-revert", metavar="SHA", help="Revert a committed patch by commit SHA")
    args = ap.parse_args()

    list_rejects()

    if args.from_backup:
        restore_from_backup(args.from_backup)

    if args.git_restore:
        git_restore_all()

    if args.git_revert:
        git_revert_commit(args.git_revert)

    if not any([args.from_backup, args.git_restore, args.git_revert]):
        print("\n[usage]")
        print("  python tools/revert_or_restore.py --from-backup <TIMESTAMP>")
        print("  python tools/revert_or_restore.py --git-restore")
        print("  python tools/revert_or_restore.py --git-revert <COMMIT_SHA>")


if __name__ == "__main__":
    main()
