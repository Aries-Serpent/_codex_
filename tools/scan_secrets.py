#!/usr/bin/env python3
"""Lightweight local secrets scanner for diffs and paths.

Usage:
  python tools/scan_secrets.py --diff HEAD            # scan staged vs HEAD
  python tools/scan_secrets.py path/to/file_or_dir    # scan files

Exit non-zero if suspicious patterns are found. Designed for local use and
invoked via `make` targets; no external services required.
"""

from __future__ import annotations

import argparse
import logging
import re
import subprocess
import sys
import tarfile
import zipfile
from collections.abc import Iterable
from pathlib import Path

PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "slack_token": re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA|EC|DSA) PRIVATE KEY-----"),
    "password_kv": re.compile(r"(?i)password\s*[:=]\s*\S+"),
    "api_key_kv": re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"),
}

SKIP_EXT = {"png", "jpg", "jpeg", "gif", "pdf", "mp4"}


LOGGER = logging.getLogger(__name__)


def _archive_kind(path: Path) -> str | None:
    name = path.name.lower()
    if name.endswith(".zip"):
        return "zip"
    if name.endswith(".tar"):
        return "tar"
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        return "tar"
    if name.endswith(".tar.bz2") or name.endswith(".tbz2"):
        return "tar"
    if name.endswith(".tar.xz") or name.endswith(".txz"):
        return "tar"
    return None


def iter_changed_paths(diff_ref: str) -> list[Path]:
    out = subprocess.check_output(["git", "diff", "--name-only", diff_ref], text=True)
    return [Path(p) for p in out.splitlines() if p.strip()]


def scan_file(path: Path) -> list[tuple[str, int | str, str]]:
    hits = []
    try:
        kind = _archive_kind(path)
        if kind == "zip":
            return _scan_zip(path)
        if kind == "tar":
            return _scan_tar(path)
        if path.suffix.lstrip(".") in SKIP_EXT:
            return hits
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for idx, line in enumerate(handle, 1):
                for name, pattern in PATTERNS.items():
                    if pattern.search(line):
                        hits.append((name, idx, line.rstrip()))
    except Exception:
        return hits
    return hits


def _scan_zip(path: Path) -> list[tuple[str, str, str]]:
    hits: list[tuple[str, str, str]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                if member.endswith("/"):
                    continue
                try:
                    data = archive.read(member).decode("utf-8", errors="ignore")
                except Exception as exc:
                    LOGGER.debug("Skipping ZIP member %s in %s: %s", member, path, exc)
                    continue
                for idx, line in enumerate(data.splitlines(), 1):
                    for name, pattern in PATTERNS.items():
                        if pattern.search(line):
                            hits.append((name, f"{member}:{idx}", line.rstrip()))
    except Exception as exc:
        LOGGER.debug("Failed to scan ZIP archive %s: %s", path, exc)
        return hits
    return hits


def _scan_tar(path: Path) -> list[tuple[str, str, str]]:
    hits: list[tuple[str, str, str]] = []
    try:
        with tarfile.open(path) as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                try:
                    extracted = archive.extractfile(member)
                except Exception as exc:
                    LOGGER.debug("Skipping TAR member %s in %s: %s", member.name, path, exc)
                    continue
                if extracted is None:
                    continue
                try:
                    data = extracted.read().decode("utf-8", errors="ignore")
                except Exception as exc:
                    LOGGER.debug("Failed to read TAR member %s in %s: %s", member.name, path, exc)
                    continue
                finally:
                    extracted.close()
                for idx, line in enumerate(data.splitlines(), 1):
                    for name, pattern in PATTERNS.items():
                        if pattern.search(line):
                            hits.append((name, f"{member.name}:{idx}", line.rstrip()))
    except Exception as exc:
        LOGGER.debug("Failed to scan TAR archive %s: %s", path, exc)
        return hits
    return hits


def _iter_targets(paths: Iterable[str]) -> list[Path]:
    targets: list[Path] = []
    for entry in paths:
        candidate = Path(entry)
        if candidate.is_dir():
            targets.extend(q for q in candidate.rglob("*") if q.is_file())
        elif candidate.is_file():
            targets.append(candidate)
    return targets


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--diff", default=None)
    args = parser.parse_args(argv)

    if args.diff:
        targets = [p for p in iter_changed_paths(args.diff) if Path(p).exists()]
    else:
        targets = _iter_targets(args.paths)

    found = 0
    for target in targets:
        for name, line_no, text in scan_file(target):
            print(f"[SECRET?] {target}:{line_no} {name}: {text}")
            found += 1
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
