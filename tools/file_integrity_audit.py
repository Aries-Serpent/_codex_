#!/usr/bin/env python3
"""Utility to snapshot and compare repository file hashes."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def git_file_list() -> list[str]:
    """Return a list of tracked files using git."""
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(output: Path) -> None:
    manifest = {}
    for name in git_file_list():
        p = Path(name)
        if p.is_file():
            manifest[name] = file_hash(p)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def compare(manifest_path: Path, allowlist_path: Path | None) -> int:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    current = {name: file_hash(Path(name)) for name in manifest}
    changed = {
        name: {"expected": manifest[name], "actual": current.get(name)}
        for name in manifest
        if manifest[name] != current.get(name)
    }
    if allowlist_path and allowlist_path.exists():
        with allowlist_path.open("r", encoding="utf-8") as f:
            allowed = {line.strip() for line in f if line.strip()}
        changed = {k: v for k, v in changed.items() if k not in allowed}
    if changed:
        json.dump(changed, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    snap = sub.add_parser("snapshot", help="Write a manifest of file hashes")
    snap.add_argument("path", type=Path)

    comp = sub.add_parser("compare", help="Compare current state with a manifest")
    comp.add_argument("manifest", type=Path)
    comp.add_argument("--allow", type=Path, default=None, help="Allow-list file")

    args = parser.parse_args()
    if args.cmd == "snapshot":
        snapshot(args.path)
        return 0
    if args.cmd == "compare":
        return compare(args.manifest, args.allow)
    return 1


if __name__ == "__main__":
    sys.exit(main())
