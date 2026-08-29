#!/usr/bin/env python3
"""Bundle repo changes as a file-backed patch archive.

This is the safe replacement for raw `git diff | ...` forwarding across the
sandbox/primary boundary. The sandbox writes the patch and metadata to files,
compresses the patch, verifies the checksum, and ships a single tar.gz bundle.
The primary side verifies the checksum and then applies the patch using `git apply`.

Example usage:
  python scripts/archive/git_patch_bundle.py bundle --repo-root . --output-dir .codex/archive/root-consolidation/temp-outputs/sandbox-transfer
  python scripts/archive/git_patch_bundle.py apply --bundle .codex/archive/root-consolidation/temp-outputs/sandbox-transfer/example.bundle.tar.gz --repo-root .
  python scripts/archive/git_patch_bundle.py verify --bundle .codex/archive/root-consolidation/temp-outputs/sandbox-transfer/example.bundle.tar.gz
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BUNDLE_DIR = Path(".codex/archive/root-consolidation/temp-outputs/sandbox-transfer")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {repo_root}: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


def _ensure_git_repo(repo_root: Path) -> None:
    if not (repo_root / ".git").exists():
        raise ValueError(f"Not a git repository: {repo_root}")


def _status_details(repo_root: Path) -> tuple[list[str], list[str], list[str]]:
    lines = [line for line in git(repo_root, "status", "--porcelain=v1").splitlines() if line.strip()]
    added_or_new: list[str] = []
    deleted: list[str] = []

    for line in lines:
        status_code = line[:2]
        relative_path = line[3:]
        if status_code.startswith("??"):
            added_or_new.append(relative_path)
        elif status_code.startswith("A") or status_code.startswith("AM"):
            added_or_new.append(relative_path)
        elif "D" in status_code:
            deleted.append(relative_path)

    return lines, added_or_new, deleted


def _snapshot_new_files(repo_root: Path, snapshot_dir: Path, new_files: list[str]) -> list[str]:
    written: list[str] = []
    for relative_path in new_files:
        source = repo_root / relative_path
        if not source.exists():
            continue

        destination = snapshot_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        written.append(relative_path)
    return written


def bundle_changes(repo_root: str | Path, output_dir: str | Path, bundle_name: str = "sandbox-git-transfer") -> Path:
    repo_root = Path(repo_root).resolve()
    output_dir = Path(output_dir).resolve()
    _ensure_git_repo(repo_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle_name = bundle_name.strip() or "sandbox-git-transfer"
    bundle_tag = bundle_name.replace(" ", "_")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_prefix = f"{bundle_tag}-{stamp}"

    patch_path = output_dir / f"{bundle_prefix}.patch"
    gzip_path = output_dir / f"{bundle_prefix}.patch.gz"
    status_path = output_dir / f"{bundle_prefix}.git-status.txt"
    manifest_path = output_dir / f"{bundle_prefix}.manifest.json"
    snapshot_dir = output_dir / f"{bundle_prefix}.snapshot"

    status_lines, new_files, deleted_files = _status_details(repo_root)
    if not status_lines:
        raise ValueError(f"No git changes detected in {repo_root}; nothing to bundle.")

    patch_result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "diff",
            "--binary",
            "--no-ext-diff",
            "--full-index",
            "--src-prefix=a/",
            "--dst-prefix=b/",
            "HEAD",
        ],
        capture_output=True,
        check=False,
    )
    if patch_result.returncode not in (0, 1):
        raise RuntimeError(f"Failed to generate git diff: {patch_result.stderr.decode(errors='replace') or patch_result.stdout.decode(errors='replace')}")

    patch_path.write_bytes(patch_result.stdout or b"")
    with gzip.open(gzip_path, "wb") as gz, patch_path.open("rb") as src:
        shutil.copyfileobj(src, gz)

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_files = _snapshot_new_files(repo_root, snapshot_dir, new_files)
    status_path.write_text("\n".join(status_lines) + ("\n" if status_lines else ""), encoding="utf-8")

    manifest = {
        "bundle_name": bundle_name,
        "bundle_prefix": bundle_prefix,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_root": str(repo_root),
        "patch_file": patch_path.name,
        "patch_sha256": sha256_file(patch_path),
        "compressed_patch_file": gzip_path.name,
        "compressed_patch_sha256": sha256_file(gzip_path),
        "git_status_file": status_path.name,
        "snapshot_dir": snapshot_dir.name,
        "snapshot_files": snapshot_files,
        "deleted_files": deleted_files,
        "head_sha": git(repo_root, "rev-parse", "HEAD").strip(),
        "status_lines": status_lines,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    bundle_tar = output_dir / f"{bundle_prefix}.bundle.tar.gz"
    with tarfile.open(bundle_tar, "w:gz") as archive:
        for item in (patch_path, gzip_path, status_path, manifest_path):
            archive.add(item, arcname=item.name)
        if snapshot_files:
            archive.add(snapshot_dir, arcname=snapshot_dir.name)

    bundle_hash = sha256_file(bundle_tar)
    bundle_hash_path = bundle_tar.with_name(f"{bundle_tar.name}.sha256")
    bundle_hash_path.write_text(f"{bundle_hash}  {bundle_tar.name}\n", encoding="utf-8")

    print(f"[OK] Bundle created: {bundle_tar}")
    print(f"[OK] Bundle SHA256: {bundle_hash}")
    print(f"[OK] Patch SHA256: {manifest['patch_sha256']}")
    print(f"[OK] Compressed patch SHA256: {manifest['compressed_patch_sha256']}")
    return bundle_tar


def _decompress_patch(gzip_path: Path, target: Path) -> None:
    with gzip.open(gzip_path, "rb") as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst)


def verify_bundle(bundle_path: str | Path) -> dict:
    bundle_path = Path(bundle_path).resolve()
    if not bundle_path.exists():
        raise FileNotFoundError(f"Bundle not found: {bundle_path}")

    bundle_hash_path = bundle_path.with_name(f"{bundle_path.name}.sha256")
    if bundle_hash_path.exists():
        expected_bundle_hash = None
        for line in bundle_hash_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                expected_bundle_hash = line.split()[0]
                break
        if expected_bundle_hash is None:
            raise ValueError(f"Checksum file is empty: {bundle_hash_path}")

        actual_bundle_hash = sha256_file(bundle_path)
        if actual_bundle_hash != expected_bundle_hash:
            raise ValueError(
                f"Archive checksum mismatch: expected {expected_bundle_hash}, got {actual_bundle_hash}"
            )

    with tempfile.TemporaryDirectory(prefix="patch-bundle-") as td:
        extract_dir = Path(td)
        with tarfile.open(bundle_path, "r:gz") as archive:
            archive.extractall(extract_dir, filter="data")

        manifest_files = sorted(extract_dir.glob("*.manifest.json"))
        if not manifest_files:
            raise ValueError(f"Bundle does not contain a manifest: {bundle_path}")

        manifest = json.loads(manifest_files[0].read_text(encoding="utf-8"))
        gzip_name = manifest["compressed_patch_file"]
        gzip_path = extract_dir / gzip_name
        if not gzip_path.exists():
            raise ValueError(f"Compressed patch is missing from bundle: {gzip_name}")

        actual_hash = sha256_file(gzip_path)
        expected_hash = manifest["compressed_patch_sha256"]
        if actual_hash != expected_hash:
            raise ValueError(
                f"Checksum mismatch for compressed patch: expected {expected_hash}, got {actual_hash}"
            )

        patch_path = extract_dir / manifest["patch_file"]
        if not patch_path.exists():
            raise ValueError(f"Patch file is missing from bundle: {patch_path.name}")

        if sha256_file(patch_path) != manifest["patch_sha256"]:
            raise ValueError("Patch file checksum mismatch; bundle may be corrupted.")

        print(f"[OK] Bundle verified: {bundle_path}")
        return manifest


def apply_bundle(bundle_path: str | Path, repo_root: str | Path) -> Path:
    bundle_path = Path(bundle_path).resolve()
    repo_root = Path(repo_root).resolve()
    _ensure_git_repo(repo_root)

    manifest = verify_bundle(bundle_path)
    with tempfile.TemporaryDirectory(prefix="patch-apply-") as td:
        extract_dir = Path(td)
        with tarfile.open(bundle_path, "r:gz") as archive:
            archive.extractall(extract_dir, filter="data")

        patch_name = manifest["patch_file"]
        compressed_name = manifest["compressed_patch_file"]
        patch_path = extract_dir / patch_name
        if not patch_path.exists():
            gz_path = extract_dir / compressed_name
            patch_path = extract_dir / "git-transfer.patch"
            _decompress_patch(gz_path, patch_path)

        snapshot_dir = extract_dir / manifest.get("snapshot_dir", "")
        if snapshot_dir.exists():
            for relative_path in manifest.get("snapshot_files", []):
                source = snapshot_dir / relative_path
                destination = repo_root / relative_path
                if source.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)

        for relative_path in manifest.get("deleted_files", []):
            destination = repo_root / relative_path
            if destination.exists():
                destination.unlink()

        if patch_path.stat().st_size == 0:
            print(f"[WARN] Patch bundle is empty; applied snapshot payload only to {repo_root}")
            print(f"[OK] Snapshot payload applied to: {repo_root}")
            return repo_root

        check_proc = subprocess.run(
            ["git", "-C", str(repo_root), "apply", "--check", "--binary", "--whitespace=nowarn", str(patch_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if check_proc.returncode != 0:
            raise RuntimeError(f"git apply --check failed: {check_proc.stderr.strip() or check_proc.stdout.strip()}")

        apply_proc = subprocess.run(
            ["git", "-C", str(repo_root), "apply", "--index", "--binary", "--whitespace=nowarn", str(patch_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if apply_proc.returncode != 0:
            raise RuntimeError(f"git apply --index failed: {apply_proc.stderr.strip() or apply_proc.stdout.strip()}")

        print(f"[OK] Patch applied to: {repo_root}")
        return repo_root


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "File-backed git patch bundle helper for sandbox-to-primary handoff. "
            "Avoids SIGPIPE by never piping git diff directly to another process."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    bundle = subparsers.add_parser("bundle", help="Create a compressed patch bundle from the current repo state")
    bundle.add_argument("--repo-root", default=".", help="Repository root to bundle")
    bundle.add_argument("--output-dir", default=str(DEFAULT_BUNDLE_DIR), help="Directory to write the bundle archive")
    bundle.add_argument("--bundle-name", default="sandbox-git-transfer", help="Bundle file prefix")

    verify = subparsers.add_parser("verify", help="Verify a bundle’s checksum before applying it")
    verify.add_argument("--bundle", required=True, help="Path to the .tar.gz bundle")

    apply = subparsers.add_parser("apply", help="Verify and apply a bundle to a target repo")
    apply.add_argument("--bundle", required=True, help="Path to the .tar.gz bundle")
    apply.add_argument("--repo-root", default=".", help="Repository root to receive the patch")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "bundle":
            bundle_changes(args.repo_root, args.output_dir, args.bundle_name)
            return 0
        if args.command == "verify":
            verify_bundle(args.bundle)
            return 0
        if args.command == "apply":
            apply_bundle(args.bundle, args.repo_root)
            return 0
    except Exception as exc:  # pragma: no cover - CLI failure reporting
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
