#!/usr/bin/env python3
"""
Self-hosted runner doctor: list, find offline, cleanup repo registrations & local dirs.
All operations default to --dry-run. Requires GH_PAT with repo Actions permissions.
from __future__ import annotations
import argparse, json, os, sys, shutil, time, urllib.request

API = "https://api.github.com"
OWNER = os.environ.get("OWNER", "Aries-Serpent")
REPO = os.environ.get("REPO", "_codex_")


def _req(path: str, token: str, method: str = "GET"):
    url = f"{API}{path}"
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "codex-runner-doctor",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
        return json.loads(resp.read().decode("utf-8"))


def list_runners(token: str):
    return _req(f"/repos/{OWNER}/{REPO}/actions/runners", token).get("runners", [])


def delete_runner(token: str, runner_id: int):
    path = f"/repos/{OWNER}/{REPO}/actions/runners/{runner_id}"
    req = urllib.request.Request(
        f"{API}{path}",
        method="DELETE",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
        return resp.status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gh-pat", default=os.environ.get("GH_PAT"))
    ap.add_argument("--cleanup-offline", action="store_true")
    ap.add_argument("--cleanup-dirs", action="store_true")
    ap.add_argument("--dirs-glob", default="actions-runner")
    ap.add_argument("--min-age-mins", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true", default=True)
    args = ap.parse_args()
    if not args.gh_pat:
        print("GH_PAT required", file=sys.stderr)
        return 2

    runners = list_runners(args.gh_pat)
    now = time.time()
    print(json.dumps({"count": len(runners), "sample": runners[:3]}, indent=2))

    if args.cleanup_offline:
        for r in runners:
            if r.get("status") == "offline":
                rid = r["id"]
                name = r.get("name")
                print(f"[doctor] offline: id={rid} name={name}")
                if not args.dry_run:
                    delete_runner(args.gh_pat, rid)
                    print(f"[doctor] deleted: id={rid}")

    if args.cleanup_dirs:
        base = args.dirs_glob
        if os.path.isdir(base):
            for entry in os.scandir(base):
                if entry.is_dir():
                    age_min = int((now - entry.stat().st_mtime) / 60)
                    if age_min >= args.min_age_mins:
                        print(f"[doctor] stale dir: {entry.path} age_min={age_min}")
                        if not args.dry_run:
                            shutil.rmtree(entry.path, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
