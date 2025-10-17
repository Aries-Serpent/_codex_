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
from collections.abc import Iterable, Iterator, Sequence
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


def _scan_lines(lines: Iterable[str]) -> list[tuple[str, int, str]]:
    """Return matches for each pattern found in *lines*.

    This helper is shared by the plain-text and archive scanners so that new
    signatures only need to be added in one place.
    """

    hits: list[tuple[str, int, str]] = []
    for idx, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip("\r\n")
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                hits.append((name, idx, line))
    return hits


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
    try:
        kind = _archive_kind(path)
        if kind == "zip":
            return _scan_zip(path)
        if kind == "tar":
            return _scan_tar(path)
        if path.suffix.lstrip(".") in SKIP_EXT:
            return []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return _scan_lines(handle)
    except Exception:
        return []


def _iter_zip_members(path: Path) -> Iterator[tuple[str, Sequence[str]]]:
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue
            suffix = Path(name).suffix.lstrip(".")
            if suffix in SKIP_EXT:
                continue
            try:
                raw = archive.read(name)
            except Exception as exc:
                LOGGER.debug("Unable to read %s from %s: %s", name, path, exc)
                continue
            text = raw.decode("utf-8", errors="ignore").splitlines()
            yield name, text


def _iter_tar_members(path: Path) -> Iterator[tuple[str, Sequence[str]]]:
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            suffix = Path(member.name).suffix.lstrip(".")
            if suffix in SKIP_EXT:
                continue
            try:
                extracted = archive.extractfile(member)
            except Exception as exc:
                LOGGER.debug("Unable to extract %s from %s: %s", member.name, path, exc)
                extracted = None
            if extracted is None:
                continue
            try:
                text = extracted.read().decode("utf-8", errors="ignore").splitlines()
            except Exception as exc:
                LOGGER.debug("Unable to decode %s from %s: %s", member.name, path, exc)
                continue
            yield member.name, text


def scan_archive(path: Path) -> list[tuple[str, int, str, str]]:
    hits: list[tuple[str, int, str, str]] = []
    try:
        if zipfile.is_zipfile(path):
            for name, lines in _iter_zip_members(path):
                for pattern, line_no, text in _scan_lines(lines):
                    hits.append((pattern, line_no, text, name))
        elif tarfile.is_tarfile(path):
            for name, lines in _iter_tar_members(path):
                for pattern, line_no, text in _scan_lines(lines):
                    hits.append((pattern, line_no, text, name))
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
                for name, idx, line in _scan_lines(data.splitlines()):
                    hits.append((name, f"{member}:{idx}", line))
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
                for name, idx, line in _scan_lines(data.splitlines()):
                    hits.append((name, f"{member.name}:{idx}", line))
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
        archive_hits = scan_archive(target) if target.is_file() else []
        for name, line_no, text, member in archive_hits:
            print(f"[SECRET?] {target}!{member}:{line_no} {name}: {text}")
            found += 1
        for name, line_no, text in scan_file(target):
            print(f"[SECRET?] {target}:{line_no} {name}: {text}")
            found += 1
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
