"""Shared schema and integrity helpers for content-addressable SQLite archives."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterator

SCHEMA_VERSION = 1
DEFAULT_MAX_BLOB_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_TEXT_BYTES = 64 * 1024 * 1024
DEFAULT_DENIED_COMPONENTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".worktrees",
    "__pycache__",
    "node_modules",
    "venv",
}
DEFAULT_DENIED_GLOBS = {"*.db", "*.pyc", "*.pyo", "*.sqlite", "*.sqlite3"}

SCHEMA_SQL = """
CREATE TABLE archive_manifest (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    schema_version INTEGER NOT NULL,
    source_root TEXT NOT NULL,
    source_of_truth TEXT NOT NULL,
    merkle_root_sha256 TEXT NOT NULL,
    entry_count INTEGER NOT NULL,
    blob_count INTEGER NOT NULL
);
CREATE TABLE content_blobs (
    blob_sha256 TEXT PRIMARY KEY,
    codec TEXT NOT NULL CHECK (codec IN ('zlib', 'none')),
    raw_size INTEGER NOT NULL CHECK (raw_size >= 0),
    raw_payload BLOB NOT NULL
);
CREATE TABLE tree_entries (
    entry_id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    entry_type TEXT NOT NULL CHECK (entry_type IN ('file', 'dir', 'symlink')),
    mode INTEGER NOT NULL,
    mtime_ns INTEGER NOT NULL,
    size INTEGER NOT NULL CHECK (size >= 0),
    blob_sha256 TEXT REFERENCES content_blobs(blob_sha256),
    git_blob_oid TEXT,
    symlink_target TEXT,
    text_encoding TEXT,
    line_endings TEXT,
    text_sha256 TEXT
);
CREATE INDEX tree_entries_path_idx ON tree_entries(path);
CREATE INDEX tree_entries_type_idx ON tree_entries(entry_type);
CREATE TABLE text_documents (
    entry_id INTEGER PRIMARY KEY REFERENCES tree_entries(entry_id),
    utf8_text TEXT NOT NULL
);
CREATE TABLE ast_symbols (
    symbol_id INTEGER PRIMARY KEY,
    entry_id INTEGER NOT NULL REFERENCES tree_entries(entry_id),
    parent_symbol_id INTEGER REFERENCES ast_symbols(symbol_id),
    symbol_kind TEXT NOT NULL,
    symbol_name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    signature TEXT,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    decorators_json TEXT NOT NULL,
    bases_json TEXT NOT NULL,
    call_targets_json TEXT NOT NULL
);
CREATE INDEX ast_symbols_name_idx ON ast_symbols(symbol_name);
CREATE INDEX ast_symbols_qualified_idx ON ast_symbols(qualified_name);
CREATE INDEX ast_symbols_kind_idx ON ast_symbols(symbol_kind);
CREATE TABLE fts_documents (
    id INTEGER PRIMARY KEY,
    entry_id INTEGER NOT NULL REFERENCES tree_entries(entry_id),
    document_type TEXT NOT NULL,
    symbol_name TEXT NOT NULL,
    path TEXT NOT NULL,
    content TEXT NOT NULL
);
CREATE VIRTUAL TABLE fts_code_index USING fts5(
    document_type UNINDEXED,
    symbol_name UNINDEXED,
    path UNINDEXED,
    content,
    content='fts_documents',
    content_rowid='id'
);
CREATE TRIGGER fts_documents_insert AFTER INSERT ON fts_documents BEGIN
    INSERT INTO fts_code_index(rowid, document_type, symbol_name, path, content)
    VALUES (new.id, new.document_type, new.symbol_name, new.path, new.content);
END;
CREATE TRIGGER fts_documents_delete AFTER DELETE ON fts_documents BEGIN
    INSERT INTO fts_code_index(fts_code_index, rowid, document_type, symbol_name, path, content)
    VALUES ('delete', old.id, old.document_type, old.symbol_name, old.path, old.content);
END;
"""


def iter_deterministic_tree(
    root: Path,
    denied_components: set[str] | None = None,
    denied_globs: set[str] | None = None,
) -> Iterator[tuple[Path, str, os.stat_result]]:
    """Yield paths in sorted depth-first order without following symlinks."""
    denied = DEFAULT_DENIED_COMPONENTS if denied_components is None else denied_components
    globs = DEFAULT_DENIED_GLOBS if denied_globs is None else denied_globs
    stack = [root]
    while stack:
        path = stack.pop()
        rel_path = path.relative_to(root).as_posix()
        info = path.lstat()
        is_root = rel_path == "."
        parts = Path(rel_path).parts if not is_root else ()
        prefixes = [Path(*parts[: index + 1]) for index in range(len(parts))]
        excluded = any(part in denied for part in parts) or any(
            prefix.match(pattern) for prefix in prefixes for pattern in globs
        )
        if excluded:
            continue
        if not is_root:
            yield path, rel_path, info
        if stat.S_ISDIR(info.st_mode):
            with os.scandir(path) as entries:
                children = sorted((Path(entry.path) for entry in entries), key=lambda p: p.name)
            stack.extend(reversed(children))


def inspect_text(raw: bytes) -> tuple[str | None, str | None, str | None]:
    """Return UTF-8 text, detected source encoding, and line-ending class."""
    candidates: list[tuple[str, str]] = []
    if raw.startswith((b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")):
        candidates.append(("utf-32", "utf-32"))
    elif raw.startswith((b"\xfe\xff", b"\xff\xfe")):
        candidates.append(("utf-16", "utf-16"))
    elif raw.startswith(b"\xef\xbb\xbf"):
        candidates.append(("utf-8-bom", "utf-8-sig"))
    else:
        if b"\x00" in raw:
            return None, None, None
        candidates.extend((("utf-8", "utf-8"), ("cp1252", "cp1252"), ("latin-1", "latin-1")))
    for label, codec in candidates:
        try:
            text = raw.decode(codec)
        except UnicodeDecodeError:
            continue
        if label == "latin-1":
            controls = sum(ord(char) < 32 and char not in "\t\n\r\f" for char in text)
            if text and controls / len(text) > 0.01:
                return None, None, None
        endings = set()
        if "\r\n" in text:
            endings.add("CRLF")
        remainder = text.replace("\r\n", "")
        if "\n" in remainder:
            endings.add("LF")
        if "\r" in remainder:
            endings.add("CR")
        line_endings = "MIXED" if len(endings) > 1 else next(iter(endings), "NONE")
        return text, label, line_endings
    return None, None, None


def git_blob_oids(root: Path) -> dict[str, str]:
    """Read committed Git blob IDs for files below root, if root is in a worktree."""
    try:
        top_level = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        relative_root = root.resolve().relative_to(Path(top_level).resolve()).as_posix()
        command = ["git", "-C", top_level, "ls-tree", "-r", "-z", "HEAD"]
        if relative_root != ".":
            command.extend(["--", relative_root])
        output = subprocess.run(command, check=True, capture_output=True).stdout
    except (OSError, ValueError, subprocess.CalledProcessError):
        return {}
    result: dict[str, str] = {}
    for record in output.split(b"\0"):
        if not record:
            continue
        header, path_bytes = record.split(b"\t", 1)
        fields = header.split()
        if len(fields) == 3 and fields[1] == b"blob":
            path = os.fsdecode(path_bytes)
            if relative_root != ".":
                prefix = relative_root + "/"
                if path.startswith(prefix):
                    path = path[len(prefix) :]
            result[path] = fields[2].decode("ascii")
    return result


def compute_merkle_root(connection: Any) -> str:
    columns = (
        "path",
        "entry_type",
        "mode",
        "mtime_ns",
        "size",
        "blob_sha256",
        "git_blob_oid",
        "symlink_target",
        "text_sha256",
    )
    rows = connection.execute(
        "SELECT " + ", ".join(columns) + " FROM tree_entries ORDER BY path COLLATE BINARY"
    )
    digest = hashlib.sha256()
    for row in rows:
        payload = json.dumps(
            dict(zip(columns, row)),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        digest.update(payload)
        digest.update(b"\n")
    return digest.hexdigest()


def run_secret_scanners(root: Path, allowed_paths: set[str] | None = None) -> None:
    """Fail closed unless both secret scanners run clean or report allowlisted paths."""
    gitleaks = shutil.which("gitleaks")
    detect_secrets = shutil.which("detect-secrets")
    if not gitleaks or not detect_secrets:
        raise RuntimeError("gitleaks and detect-secrets are required before packing")
    allowed = allowed_paths or set()
    with tempfile.TemporaryDirectory(prefix="cdx-scan-") as temp_dir:
        report = Path(temp_dir) / "gitleaks.json"
        try:
            gitleaks_result = subprocess.run(
                [
                    gitleaks,
                    "dir",
                    "--report-format",
                    "json",
                    "--report-path",
                    str(report),
                    str(root),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if gitleaks_result.returncode not in (0, 1) or not report.exists():
                raise RuntimeError("gitleaks scan failed")
            gitleaks_findings = json.loads(report.read_text(encoding="utf-8"))
            detect_result = subprocess.run(
                [detect_secrets, "scan", "--all-files", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            if detect_result.returncode != 0:
                raise RuntimeError("detect-secrets scan failed")
            detect_findings = json.loads(detect_result.stdout)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError("secret scan could not be completed") from exc
    flagged: set[str] = set()
    for finding in gitleaks_findings:
        file_path = finding.get("File")
        if file_path:
            flagged.add(_scanner_relative_path(root, file_path))
    for file_path, findings in detect_findings.get("results", {}).items():
        if findings:
            flagged.add(_scanner_relative_path(root, file_path))
    if flagged - allowed:
        raise RuntimeError("secret scan flagged files; archive creation blocked")


def _scanner_relative_path(root: Path, reported_path: str) -> str:
    path = Path(reported_path)
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        normalized = reported_path.replace("\\", "/").removeprefix("./")
        if normalized.startswith("/") or ".." in Path(normalized).parts:
            raise RuntimeError("secret scanner returned an out-of-root path")
        return normalized
