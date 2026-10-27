#!/usr/bin/env python3
"""Fetch and verify explicitly requested current-HEAD LFS assets, never history.

Task CLI: python scripts/ci/fetch_lfs_assets.py --include 'data/model.bin'
Requires Git LFS and permitted origin access. Full mode additionally requires
--allow-full and still obeys the current-HEAD object/declared-byte/time budgets.
No mode fetches all historical refs or falls back to a broader selection.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


class AssetError(RuntimeError):
    """Required assets are not demonstrably available."""


@dataclass(frozen=True)
class Limits:
    objects: int = 32
    bytes: int = 256 * 1024 * 1024
    seconds: float = 180
    retries: int = 2


@dataclass(frozen=True)
class Asset:
    path: str
    oid: str
    size: int


class Fetcher:
    def __init__(self, root: Path, limits: Limits):
        self.root = root.resolve()
        self.limits = limits
        if (
            min(limits.objects, limits.bytes, limits.seconds) <= 0
            or not math.isfinite(limits.seconds)
            or limits.seconds > 600
            or not 1 <= limits.retries <= 3
        ):
            raise AssetError("budgets must be positive; timeout at most 600 seconds; attempts 1..3")
        self.deadline = time.monotonic() + limits.seconds

    def run(self, *args: str, env: dict[str, str] | None = None) -> str:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise AssetError("required LFS assets unavailable: total timeout exceeded")
        child_env = dict(os.environ if env is None else env)
        child_env.pop("LFS_AUTH_TOKEN", None)
        child_env.update(GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
        # Never print git stderr: remote/helper diagnostics can contain credentials.
        with subprocess.Popen(
            ["git", "-c", "core.quotePath=false", *args],
            cwd=self.root,
            env=child_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        ) as process:
            try:
                output, _ = process.communicate(timeout=remaining)
            except subprocess.TimeoutExpired as exc:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
                raise AssetError("required LFS assets unavailable: total timeout exceeded") from exc
            if process.returncode:
                raise AssetError(
                    "Git/LFS command failed; check installed LFS, origin access and object availability"
                )
        return output.decode("utf-8", errors="strict")

    def safe_path(self, path: str, *, pattern: bool = False) -> str:
        parts = PurePosixPath(path).parts
        if (
            not path
            or path.startswith(("/", "-"))
            or any(ord(c) < 32 or ord(c) == 127 for c in path)
            or any(c in path for c in "\\,:")
            or (not pattern and any(c in path for c in "*?[]"))
            or any(p in {".", "..", ".git"} for p in path.split("/"))
            or not parts
        ):
            raise AssetError("asset paths must be safe repository-relative paths")
        if pattern and ("/" not in path or any(c in parts[0] for c in "*?[")):
            raise AssetError(
                "targeted includes need a concrete directory prefix, not a root-wide glob"
            )
        candidate = self.root / path
        if not candidate.resolve().is_relative_to(self.root):
            raise AssetError("asset path escapes the repository")
        if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != self.root):
            raise AssetError("asset paths must not traverse symlinks")
        return path

    def select(self, includes: list[str], full: bool) -> tuple[str, list[Asset]]:
        self.run("lfs", "version")
        ref = self.run("rev-parse", "--verify", "HEAD").strip()
        patterns = [""] if full else includes
        if not full and not 1 <= len(patterns) <= 32:
            raise AssetError("targeted mode needs 1..32 explicit include patterns")
        paths: set[str] = set()
        for pattern in patterns:
            if not full:
                self.safe_path(pattern, pattern=True)
            matched = self.run(
                "lfs", "ls-files", "--name-only", f"--include={pattern}", "--exclude=", ref
            ).splitlines()
            if not matched and not full:
                raise AssetError("required include matched no current-HEAD LFS assets")
            paths.update(self.safe_path(path) for path in matched)
            if len(paths) > self.limits.objects:
                raise AssetError("required asset object/path count budget exceeded before fetch")
        assets = []
        for path in sorted(paths):
            obj = f"{ref}:{path}"
            if int(self.run("cat-file", "-s", obj)) > 1024:
                raise AssetError("invalid or oversized LFS pointer")
            pointer = self.run("cat-file", "blob", obj)
            match = re.fullmatch(
                r"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?",
                pointer,
            )
            if not match:
                raise AssetError("required asset is not a supported LFS pointer")
            assets.append(Asset(path, match[1], int(match[2])))
        sizes: dict[str, int] = {}
        for asset in assets:
            if asset.oid in sizes and sizes[asset.oid] != asset.size:
                raise AssetError("inconsistent declared sizes for the same LFS object")
            sizes[asset.oid] = asset.size
        if len(sizes) > self.limits.objects or sum(sizes.values()) > self.limits.bytes:
            raise AssetError("required asset declared-byte/object budget exceeded before fetch")
        return ref, assets

    def auth_env(self) -> dict[str, str]:
        env = dict(os.environ)
        token = env.pop("LFS_AUTH_TOKEN", "")
        if token:
            remote = urlsplit(self.run("remote", "get-url", "origin").strip())
            if (
                remote.scheme != "https"
                or remote.hostname != "github.com"
                or remote.username
                or remote.port not in {None, 443}
            ):
                raise AssetError("setup token may only authenticate an HTTPS github.com origin")
            # In-memory, URL-scoped config; never persisted to the repository.
            index = int(env.get("GIT_CONFIG_COUNT", "0"))
            env["GIT_CONFIG_COUNT"] = str(index + 1)
            env[f"GIT_CONFIG_KEY_{index}"] = "http.https://github.com/.extraheader"
            encoded = base64.b64encode(f"x-access-token:{token}".encode()).decode()
            env[f"GIT_CONFIG_VALUE_{index}"] = f"AUTHORIZATION: basic {encoded}"
        return env

    def verify(self, assets: list[Asset]) -> None:
        for asset in assets:
            path = self.root / self.safe_path(asset.path)
            if not path.is_file() or path.stat().st_size != asset.size:
                raise AssetError("required asset missing, still a pointer, modified, or wrong size")
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    if time.monotonic() >= self.deadline:
                        raise AssetError("required asset verification timeout exceeded")
                    digest.update(chunk)
            if digest.hexdigest() != asset.oid:
                raise AssetError("required asset content hash mismatch")

    def fetch(
        self, includes: list[str], *, full: bool = False, verify_only: bool = False
    ) -> list[Asset]:
        ref, assets = self.select(includes, full)
        if verify_only:
            self.verify(assets)
            return assets
        if not assets:
            return assets
        env = self.auth_env()
        for attempt in range(self.limits.retries):
            try:
                self.run(
                    "-c",
                    "lfs.fetchrecentalways=false",
                    "-c",
                    "lfs.concurrenttransfers=2",
                    "-c",
                    "lfs.transfer.maxretries=0",
                    "lfs",
                    "fetch",
                    f"--include={','.join(includes) if not full else ''}",
                    "--exclude=",
                    "origin",
                    ref,
                    env=env,
                )
                break
            except AssetError:
                if attempt + 1 == self.limits.retries or time.monotonic() >= self.deadline:
                    raise
        # Checkout accepts positional paths, not --include. Only selected paths
        # are materialized; Git LFS does not overwrite locally modified content.
        for asset in assets:
            self.run("lfs", "checkout", "--", asset.path)
        self.verify(assets)
        return assets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--include", action="append", default=[], help="Comma-separated narrow patterns; repeatable"
    )
    parser.add_argument("--mode", choices=["none", "targeted", "full"], default="targeted")
    parser.add_argument(
        "--allow-full",
        action="store_true",
        help="Explicit current-HEAD full selection (still bounded)",
    )
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--max-objects", type=int, default=32)
    parser.add_argument("--max-bytes", type=int, default=256 * 1024 * 1024)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument(
        "--status", type=Path, help="Machine-readable readiness, including failures"
    )
    args = parser.parse_args()
    result = {"status": "not-ready", "scope": "current-HEAD", "assets": []}
    code = 0
    try:
        if args.mode == "full" and not args.allow_full:
            raise AssetError("full mode requires explicit --allow-full; never a fallback")
        if args.mode == "none":
            if args.include:
                raise AssetError("none mode conflicts with required includes")
            result["status"] = "not-requested"
        else:
            includes = [p.strip() for group in args.include for p in group.split(",")]
            if args.mode == "full" and includes:
                raise AssetError("full and targeted intent must not be combined")
            fetcher = Fetcher(
                args.repo_root,
                Limits(args.max_objects, args.max_bytes, args.timeout, args.attempts),
            )
            assets = fetcher.fetch(includes, full=args.mode == "full", verify_only=args.verify_only)
            result.update(status="ready", assets=[a.path for a in assets])
    except AssetError as exc:
        result["error"] = f"Required LFS assets unavailable: {exc}. No broad fallback attempted."
        code = 1
    except (OSError, ValueError, UnicodeError):
        # No raw subprocess/exception output: URLs and diagnostics may hold secrets.
        result["error"] = (
            "Required LFS assets unavailable: invalid intent, budget, timeout, content, or origin/LFS access. Check narrow paths and permitted credentials; no broad fallback was attempted."
        )
        code = 1
    if args.status:
        args.status.parent.mkdir(parents=True, exist_ok=True)
        args.status.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
