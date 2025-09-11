#!/usr/bin/env python3
"""Snapshot and compare file manifests with optional allow-lists."""

import argparse
import fnmatch
import hashlib
import json
import pathlib
from typing import Dict, List

DEFAULT_EXCLUDES = [
    "*__pycache__/*",
    ".pytest_cache/*",
    "site/*",
    ".ruff_cache/*",
    ".codex/warehouse/*",
    ".codex/bundles/*",
]


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_manifest(
    root: pathlib.Path, excludes: List[str] | None = None
) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    excludes = excludes or []
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            rel = str(p.relative_to(root))
            if match_any(rel, DEFAULT_EXCLUDES + excludes):
                continue
            out[rel] = {"sha256": sha256(p), "size": p.stat().st_size}
    return out


def save(path: str, obj: Dict[str, Dict[str, int]]) -> None:
    pathlib.Path(path).write_text(json.dumps(obj, indent=2), encoding="utf-8")


def load(path: str) -> Dict[str, Dict[str, int]]:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def match_any(path: str, patterns: List[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)


def compare(
    pre: str, post: str, allow_removed: List[str], allow_added: List[str], allow_changed: List[str]
) -> bool:
    pre_map = load(pre)
    post_map = load(post)
    pre_hash_to_paths: Dict[str, set] = {}
    post_hash_to_paths: Dict[str, set] = {}
    for p, meta in pre_map.items():
        pre_hash_to_paths.setdefault(meta["sha256"], set()).add(p)
    for p, meta in post_map.items():
        post_hash_to_paths.setdefault(meta["sha256"], set()).add(p)
    removed = [p for p in pre_map if p not in post_map]
    added = [p for p in post_map if p not in pre_map]
    changed = [
        p for p in pre_map if p in post_map and pre_map[p]["sha256"] != post_map[p]["sha256"]
    ]
    moves: List[Dict[str, str]] = []
    rem_left = []
    for p in removed:
        targets = sorted(post_hash_to_paths.get(pre_map[p]["sha256"], set()))
        if targets:
            moves.append({"from": p, "to": targets[0]})
        else:
            rem_left.append(p)
    add_left = set(added)
    for m in moves:
        if m["to"] in add_left:
            add_left.remove(m["to"])
    unexpected_removed = [p for p in rem_left if not match_any(p, allow_removed)]
    unexpected_added = [p for p in add_left if not match_any(p, allow_added)]
    unexpected_changed = [p for p in changed if not match_any(p, allow_changed)]
    result = {
        "summary": {
            "removed": len(removed),
            "added": len(added),
            "changed": len(changed),
            "moves": len(moves),
            "unexpected_removed": len(unexpected_removed),
            "unexpected_added": len(unexpected_added),
            "unexpected_changed": len(unexpected_changed),
        },
        "details": {
            "removed": removed,
            "added": added,
            "changed": changed,
            "moves": moves,
            "unexpected_removed": unexpected_removed,
            "unexpected_added": list(unexpected_added),
            "unexpected_changed": unexpected_changed,
        },
    }
    print(json.dumps(result, indent=2))
    return not (unexpected_removed or unexpected_added or unexpected_changed)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("snapshot")
    s1.add_argument("out")
    s2 = sub.add_parser("compare")
    s2.add_argument("pre")
    s2.add_argument("post")
    s2.add_argument("--allow-removed", action="append", default=[])
    s2.add_argument("--allow-added", action="append", default=[])
    s2.add_argument("--allow-changed", action="append", default=[])
    args = ap.parse_args()
    root = pathlib.Path(".").resolve()
    if args.cmd == "snapshot":
        save(args.out, walk_manifest(root))
        print(f"[integrity] snapshot -> {args.out}")
        return 0
    ok = compare(args.pre, args.post, args.allow_removed, args.allow_added, args.allow_changed)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
