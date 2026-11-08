"""Shared schema and integrity helpers for content-addressable SQLite archives."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import hmac
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zlib
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, cast

SCHEMA_VERSION = 1
DEFAULT_MAX_BLOB_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_TEXT_BYTES = 64 * 1024 * 1024
SECRET_SCANNER_VERSIONS = {"gitleaks": "8.30.1", "detect-secrets": "1.5.0"}
SECRET_SCANNER_TIMEOUT_SECONDS = 600
TRUSTED_GITLEAKS_CONFIG = b"[extend]\nuseDefault = true\n"
FINDING_IDENTITY_VERSION = 2
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

SCHEMA_DDL = SCHEMA_SQL

__all__ = [
    "SCHEMA_VERSION",
    "SCHEMA_SQL",
    "SCHEMA_DDL",
    "DEFAULT_MAX_BLOB_BYTES",
    "DEFAULT_MAX_TEXT_BYTES",
    "DEFAULT_DENIED_COMPONENTS",
    "DEFAULT_DENIED_GLOBS",
    "SECRET_SCANNER_VERSIONS",
    "SECRET_SCANNER_TIMEOUT_SECONDS",
    "TRUSTED_GITLEAKS_CONFIG",
    "FINDING_IDENTITY_VERSION",
    "iter_deterministic_tree",
    "inspect_text",
    "inspect_and_pack_blob",
    "git_blob_oids",
    "compute_merkle_root",
    "run_secret_scanners",
    "run_secret_scanner",
    "_canonical_scanner_finding",
    "_validate_external_path",
    "validate_safe_rel_path",
    "validate_symlink_target",
    "verify_archive",
    "verify_archive_connection",
    "validate_inventory",
    "run_cdx_common_preflight",
]


@contextmanager
def _scanner_workspace(
    roots: list[Path],
    directory: Path | None,
    config: Path | None,
    ignore: Path | None,
) -> Iterator[tuple[Path, Path, Path, Path]]:
    """Never let the scanned tree supply scanner configuration or suppression."""
    for path, _relative, _info in iter_deterministic_tree(
        roots[0], denied_components=set(), denied_globs=set()
    ):
        if path.name == ".gitleaksignore":
            raise RuntimeError("source gitleaks ignore files are unsupported; no contents skipped")
    parent = (directory or roots[0].absolute().parent).resolve(strict=True)
    _validate_external_path(roots, parent / ".cdx-scanner-workspace", must_exist=False)
    with tempfile.TemporaryDirectory(prefix="cdx-scan-", dir=parent) as work:
        workspace = Path(work)
        effective = []
        for candidate, name, payload in (
            (config, "gitleaks.toml", TRUSTED_GITLEAKS_CONFIG),
            (ignore, "gitleaks.ignore", b""),
        ):
            if candidate is not None:
                candidate = _validate_external_path(roots, candidate, must_exist=True)
                fd = os.open(candidate, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(fd, "rb") as stream:
                    info = os.fstat(stream.fileno())
                    if (
                        not stat.S_ISREG(info.st_mode)
                        or info.st_size != len(payload)
                        or stream.read(len(payload) + 1) != payload
                    ):
                        raise RuntimeError("untrusted secret scanner configuration")
                if candidate.is_symlink():
                    raise RuntimeError("untrusted secret scanner configuration")
            # Pin private copies, not mutable caller-owned files.
            pinned = workspace / name
            pinned.write_bytes(TRUSTED_GITLEAKS_CONFIG if name == "gitleaks.toml" else b"")
            pinned.chmod(0o600)
            effective.append(pinned)
        yield workspace, workspace, effective[0], effective[1]


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


def inspect_and_pack_blob(
    raw: bytes, *, max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES
) -> dict[str, Any]:
    """Return the canonical stored blob and optional lossless text metadata."""
    if type(max_blob_bytes) is not int or max_blob_bytes <= 0 or len(raw) > max_blob_bytes:
        raise ValueError("content exceeds the blob byte budget")
    text, encoding, endings = inspect_text(raw)
    return {
        "blob_sha256": hashlib.sha256(raw).hexdigest(),
        "codec": "zlib",
        "raw_size": len(raw),
        "raw_payload": zlib.compress(raw, level=9),
        "text": text,
        "text_encoding": encoding,
        "line_endings": endings,
        "text_sha256": (
            hashlib.sha256(text.encode("utf-8")).hexdigest() if text is not None else None
        ),
    }


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


def _scanner_json(raw: str) -> Any:
    def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate scanner report key")
            result[key] = value
        return result

    def reject_constant(_value: str) -> Any:
        raise ValueError("invalid scanner JSON constant")

    return json.loads(raw, object_pairs_hook=unique_keys, parse_constant=reject_constant)


def run_secret_scanners(
    root: Path,
    dispositions_path: Path | None = None,
    inventory_path: Path | None = None,
    source_root: Path | None = None,
    *,
    observation_sink: Any = None,
    report_sink: Any = None,
    scanner_environment: dict[str, str] | None = None,
    scanner_directory: Path | None = None,
    gitleaks_config: Path | None = None,
    gitleaks_ignore: Path | None = None,
) -> None:
    """Fail closed unless every exact scanner finding has an active disposition."""
    root = root.resolve(strict=True)
    if dispositions_path is not None and not isinstance(dispositions_path, Path):
        raise RuntimeError("path-wide secret allowlists are not supported")
    roots = [root]
    if source_root is not None:
        roots.append(source_root)
    if dispositions_path is not None:
        dispositions_path = _validate_external_path(roots, dispositions_path, must_exist=True)
    if inventory_path is not None:
        inventory_path = _validate_external_path(roots, inventory_path, must_exist=False)
    gitleaks = shutil.which("gitleaks")
    detect_secrets = shutil.which("detect-secrets")
    if not gitleaks or not detect_secrets:
        raise RuntimeError("gitleaks and detect-secrets are required before packing")
    # Exit 1 can mean partial failure, even when a report contains findings.
    finding_exit = 2

    def retain(stage: str, result: Any, raw_report: str | None = None) -> None:
        if report_sink is not None:
            report_sink(
                stage,
                {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "report": raw_report,
                },
            )

    with _scanner_workspace(roots, scanner_directory, gitleaks_config, gitleaks_ignore) as (
        workspace,
        report_directory,
        config,
        ignore,
    ):
        report = workspace / "gitleaks.json"
        supplied = scanner_environment or {}
        execution: dict[str, Any] = {
            "cwd": report_directory,
            "env": {
                "PATH": supplied.get("PATH", os.environ.get("PATH", "")),
                "HOME": str(workspace),
                "LC_ALL": "C.UTF-8",
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        }
        configuration = [
            "--config",
            str(config),
            "--ignore-gitleaks-allow",
            "--gitleaks-ignore-path",
            str(ignore),
            "--exit-code",
            str(finding_exit),
        ]
        try:
            gitleaks_version = subprocess.run(
                [gitleaks, "version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=SECRET_SCANNER_TIMEOUT_SECONDS,
                **execution,
            )
            detect_version = subprocess.run(
                [detect_secrets, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=SECRET_SCANNER_TIMEOUT_SECONDS,
                **execution,
            )
            retain("gitleaks-version", gitleaks_version)
            retain("detect-secrets-version", detect_version)
            if gitleaks_version.returncode != 0 or detect_version.returncode != 0:
                raise RuntimeError("secret scanner version could not be determined")
            versions = {
                "gitleaks": _scanner_version(gitleaks_version.stdout),
                "detect-secrets": _scanner_version(detect_version.stdout),
            }
            if versions != SECRET_SCANNER_VERSIONS:
                raise RuntimeError("secret scanner version does not match the pinned version")
            gitleaks_result = subprocess.run(
                [
                    gitleaks,
                    "dir",
                    "--redact=100",
                    "--report-format",
                    "json",
                    "--report-path",
                    str(report),
                    *configuration,
                    str(root),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=SECRET_SCANNER_TIMEOUT_SECONDS,
                **execution,
            )
            raw_report = None
            if report.exists():
                with report.open(encoding="utf-8") as stream:
                    raw_report = stream.read(16 * 1024 * 1024 + 1)
                if len(raw_report.encode("utf-8")) > 16 * 1024 * 1024:
                    raise RuntimeError("gitleaks report exceeds the retention limit")
            retain("gitleaks", gitleaks_result, raw_report)
            if gitleaks_result.returncode not in (0, finding_exit) or not report.exists():
                raise RuntimeError("gitleaks scan failed")
            gitleaks_findings = _scanner_json(raw_report or "")
            if not isinstance(gitleaks_findings, list) or any(
                not isinstance(finding, dict) for finding in gitleaks_findings
            ):
                raise RuntimeError("gitleaks returned an invalid report")
            if (gitleaks_result.returncode == finding_exit) != bool(gitleaks_findings):
                raise RuntimeError("gitleaks status and report disagree")
            detect_result = subprocess.run(
                [detect_secrets, "scan", "--no-verify", "--all-files", str(root)],
                capture_output=True,
                text=True,
                check=False,
                timeout=SECRET_SCANNER_TIMEOUT_SECONDS,
                **execution,
            )
            retain("detect-secrets", detect_result)
            if detect_result.returncode != 0:
                raise RuntimeError("detect-secrets scan failed")
            detect_findings = _scanner_json(detect_result.stdout)
            if not isinstance(detect_findings, dict):
                raise RuntimeError("detect-secrets returned an invalid report")
        except (OSError, ValueError, RecursionError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("secret scan could not be completed") from exc

    findings: list[dict[str, Any]] = []
    for finding in gitleaks_findings:
        findings.append(
            _scanner_finding(
                root,
                "gitleaks",
                versions["gitleaks"],
                finding,
                report_directory=report_directory,
            )
        )
    detect_results = detect_findings.get("results")
    if not isinstance(detect_results, dict):
        raise RuntimeError("detect-secrets returned an invalid report")
    for file_path, records in detect_results.items():
        if not isinstance(records, list):
            raise RuntimeError("detect-secrets returned an invalid report")
        for finding in records:
            if not isinstance(finding, dict):
                raise RuntimeError("detect-secrets returned an invalid finding")
            record = dict(finding)
            record["File"] = file_path
            findings.append(
                _scanner_finding(
                    root,
                    "detect-secrets",
                    versions["detect-secrets"],
                    record,
                    report_directory=report_directory,
                )
            )

    dispositions = (
        _load_finding_dispositions(dispositions_path) if dispositions_path is not None else []
    )
    if not findings:
        if dispositions:
            raise RuntimeError("secret finding dispositions are stale")
        if inventory_path is not None:
            _write_finding_inventory(inventory_path, [], roots)
        if observation_sink is not None:
            observation_sink([], copy.deepcopy(detect_findings))
        return

    key_text = os.environ.get("CDX_FINDING_HMAC_KEY", "")
    if len(key_text.encode("utf-8")) < 32:
        raise RuntimeError(
            "secret scan found unresolved findings; a private finding HMAC key is required"
        )
    key = key_text.encode("utf-8")
    for finding in findings:
        finding["finding_id"] = _finding_id(key, finding)
    identities = [finding["finding_id"] for finding in findings]
    if len(set(identities)) != len(identities):
        raise RuntimeError("secret scanner returned ambiguous duplicate findings")

    if inventory_path is not None:
        _write_finding_inventory(inventory_path, findings, roots)
    if observation_sink is not None:
        observation_sink(copy.deepcopy(findings), copy.deepcopy(detect_findings))
    disposition_by_id: dict[str, dict[str, Any]] = {}
    for disposition in dispositions:
        finding_id = disposition["finding_id"]
        if finding_id in disposition_by_id:
            raise RuntimeError("finding disposition contains duplicate identities")
        disposition_by_id[finding_id] = disposition

    observed = {finding["finding_id"]: finding for finding in findings}
    if set(disposition_by_id) != set(observed):
        raise RuntimeError("secret scan findings are unresolved or dispositions are stale")
    for finding_id, disposition in disposition_by_id.items():
        finding = observed[finding_id]
        for field in (
            "scanner",
            "scanner_version",
            "path",
            "file_sha256",
            "rule",
            "start_line",
            "end_line",
        ):
            if disposition[field] != finding[field]:
                raise RuntimeError("secret scan disposition does not match the current finding")
        if disposition["disposition"] != "false_positive":
            raise RuntimeError("secret scan finding is not affirmatively cleared")
        if not disposition["evidence_ref"].strip() or not disposition["reviewed_by"].strip():
            raise RuntimeError("secret scan disposition lacks review evidence")
        evidence_path = _validate_external_path(
            roots, Path(disposition["evidence_ref"]), must_exist=True
        )
        try:
            evidence_digest = hashlib.sha256()
            with evidence_path.open("rb") as evidence_file:
                for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
                    evidence_digest.update(chunk)
        except OSError as exc:
            raise RuntimeError("secret scan review evidence could not be verified") from exc
        if evidence_digest.hexdigest() != disposition["evidence_sha256"]:
            raise RuntimeError("secret scan review evidence digest does not match")


run_secret_scanner = run_secret_scanners


def _scanner_relative_path(
    root: Path, reported_path: Any, *, report_directory: Path | None = None
) -> str:
    if not isinstance(reported_path, str) or not reported_path:
        raise RuntimeError("secret scanner returned an invalid file path")
    path = Path(reported_path)
    root_path = Path(os.path.abspath(root))
    if path.is_absolute():
        candidates = [path]
    elif report_directory is not None:
        candidates = [report_directory / path]
    else:
        candidates = [Path.cwd() / path, root_path / path]
    for candidate in candidates:
        try:
            relative = Path(os.path.abspath(candidate)).relative_to(root_path).as_posix()
        except (OSError, ValueError):
            continue
        if relative and relative != "." and ".." not in Path(relative).parts:
            return relative
    raise RuntimeError("secret scanner returned an out-of-root path")


def _scanner_version(output: str) -> str:
    version = output.strip()
    if not version or len(version) > 128 or "\n" in version:
        raise RuntimeError("secret scanner returned an invalid version")
    return version.removeprefix("v")


def _scanner_finding(
    root: Path,
    scanner: str,
    version: str,
    record: dict[str, Any],
    *,
    report_directory: Path | None = None,
) -> dict[str, Any]:
    path_value = record.get("File")
    path = _scanner_relative_path(root, path_value, report_directory=report_directory)
    file_path = root / path
    try:
        file_info = file_path.lstat()
        if not stat.S_ISREG(file_info.st_mode):
            raise RuntimeError("secret scanner finding is not a regular file")
        file_digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeError("secret scanner finding file could not be verified") from exc

    return _canonical_scanner_finding(scanner, version, path, file_digest, record)


def _canonical_scanner_finding(
    scanner: str, version: str, path: str, file_digest: str, record: dict[str, Any]
) -> dict[str, Any]:
    """Canonicalize metadata over bytes already acquired by the calling producer."""
    path_value = record.get("File")
    if scanner == "gitleaks":
        rule = record.get("RuleID")
        start = record.get("StartLine")
        end = record.get("EndLine", start)
    else:
        rule = record.get("type")
        start = record.get("line_number")
        end = start
    if (
        not isinstance(rule, str)
        or not rule
        or not isinstance(start, int)
        or isinstance(start, bool)
        or start < 1
        or not isinstance(end, int)
        or isinstance(end, bool)
        or end < start
    ):
        raise RuntimeError("secret scanner returned incomplete finding metadata")
    canonical_record = dict(record)
    canonical_record["File"] = path
    if scanner == "gitleaks":
        fingerprint = record.get("Fingerprint")
        if fingerprint == f"{path_value}:{rule}:{start}":
            canonical_record["Fingerprint"] = f"{path}:{rule}:{start}"
        if "Tags" in record:
            tags = record["Tags"]
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                raise RuntimeError("gitleaks returned invalid finding tags")
            canonical_record["Tags"] = sorted(tags)
    return {
        "scanner": scanner,
        "scanner_version": version,
        "path": path,
        "file_sha256": file_digest,
        "rule": rule,
        "start_line": start,
        "end_line": end,
        "_record": canonical_record,
    }


def _gitleaks_private_span(
    raw: bytes,
    record: dict[str, Any],
    *,
    version: str,
    unfragmented: bool = False,
    source_window: tuple[int, int] | None = None,
) -> tuple[bytes | None, str]:
    """Map a bounded v8.30.1 file Match privately, never recover its Secret.

    location.go uses byte offsets and the preceding LF index as the column
    origin on later lines. Large input needs caller-verified unfragmented
    provenance or the exact fragment byte window; stock reports lack that proof.
    Neither keyword is inferred from the untrusted report.
    """
    if version != "8.30.1":
        return None, "unsupported_scanner_version"
    tags = record.get("Tags")
    if tags is not None and (
        not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags)
    ):
        return None, "unsupported_tags"
    if any(re.search(r"encoded|decoded|decode-depth", tag, re.I) for tag in tags or []) or any(
        re.search(r"encoded|decoded|decode.depth", field, re.I) for field in record
    ):
        return None, "unsupported_decoding"
    if (
        record.get("Fragment") is not None
        or record.get("Commit")
        or record.get("SymlinkFile")
        or "!" in str(record.get("File", ""))
    ):
        return None, "unsupported_fragment_or_nested_source"
    if type(unfragmented) is not bool:
        return None, "unsupported_fragment_origin"
    line_offset = 0
    if source_window is not None:
        if (
            unfragmented
            or not isinstance(source_window, tuple)
            or len(source_window) != 2
            or any(type(value) is not int for value in source_window)
            or not 0 <= source_window[0] < source_window[1] <= len(raw)
            or source_window[1] - source_window[0] > DEFAULT_MAX_TEXT_BYTES
        ):
            return None, "unsupported_fragment_origin"
        origin, limit = source_window
        line_offset = raw.count(b"\n", 0, origin)
        raw = raw[origin:limit]
    elif len(raw) >= 100_000 and not unfragmented:
        return None, "unsupported_fragment_origin"
    if len(raw) > DEFAULT_MAX_TEXT_BYTES or b"\x00" in raw or b"\r" in raw.replace(b"\r\n", b""):
        return None, "unsupported_source_encoding_or_size"
    try:
        raw.decode("utf-8")
    except UnicodeError:
        return None, "unsupported_source_encoding_or_size"
    coordinates = [
        record.get(field) for field in ("StartLine", "EndLine", "StartColumn", "EndColumn")
    ]
    if any(type(value) is not int or value < 1 for value in coordinates):
        return None, "unsupported_coordinates"
    start, end, left, right = (cast(int, value) for value in coordinates)
    start -= line_offset
    end -= line_offset
    if not 1 <= start <= end or end - start > 100:
        return None, "unsupported_coordinates"
    # Find only the requested origins, rather than allocating one Python integer
    # for every newline of a large file.
    origins = {1: 0}
    previous = -1
    for line in range(2, end + 1):
        previous = raw.find(b"\n", previous + 1)
        if previous < 0:
            return None, "unsupported_coordinates"
        if line in (start, end):
            origins[line] = previous
    next_lf = raw.find(b"\n", origins[end] + (end > 1))
    # location.go does not set a usable end column for a multi-line match
    # ending beyond the final LF when its start was already found.
    if end > start and next_lf < 0:
        return None, "unsupported_unterminated_multiline"
    begin = origins[start] + left - 1
    finish = origins[end] + right

    def content_bounds(line: int) -> tuple[int, int]:
        lower = origins[line] + (line > 1)
        newline = raw.find(b"\n", lower)
        upper = newline if newline >= 0 else len(raw)
        if upper > lower and raw[upper - 1 : upper] == b"\r":
            upper -= 1
        return lower, upper

    first_lower, first_upper = content_bounds(start)
    last_lower, last_upper = content_bounds(end)
    if not (
        first_lower <= begin < first_upper
        and last_lower < finish <= last_upper
        and 0 < finish - begin <= 65536
    ):
        return None, "unsupported_coordinates"
    # Byte columns must land on complete UTF-8 code points, not character
    # indexes or the interior of a multi-byte sequence.
    try:
        raw[:begin].decode("utf-8")
        span = raw[begin:finish]
        span.decode("utf-8")
    except UnicodeError:
        return None, "unsupported_utf8_boundary"
    return span, "mapped_reported_match_not_secret"


def _finding_id(key: bytes, finding: dict[str, Any]) -> str:
    identity = {field: value for field, value in finding.items() if field != "finding_id"}
    identity["identity_version"] = FINDING_IDENTITY_VERSION
    payload = json.dumps(
        identity,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def _write_finding_inventory(
    path: Path, findings: list[dict[str, Any]], source_roots: list[Path]
) -> None:
    destination = _validate_external_path(source_roots, path, must_exist=False)
    safe_findings = [
        {field: value for field, value in finding.items() if field != "_record"}
        for finding in findings
    ]
    document = {"schema_version": 1, "findings": safe_findings}
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("redacted finding inventory could not be written") from exc


def _validate_external_path(source_roots: list[Path], path: Path, *, must_exist: bool) -> Path:
    if path.is_symlink():
        raise RuntimeError("secret finding files must not be symlinks")
    try:
        parent = path.parent.resolve(strict=True)
        destination = parent / path.name
        if must_exist:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise RuntimeError("secret finding dispositions must be a regular file")
            destination = path.resolve(strict=True)
        elif path.exists():
            raise RuntimeError("secret finding inventory must not overwrite an existing file")
        for source_root in source_roots:
            source = source_root.resolve(strict=True)
            if destination == source or source in destination.parents:
                raise RuntimeError("secret finding files must be outside the source tree")
    except OSError as exc:
        raise RuntimeError("secret finding file path could not be verified") from exc
    return destination


def _load_finding_dispositions(path: Path) -> list[dict[str, Any]]:
    fields = {
        "scanner",
        "scanner_version",
        "finding_id",
        "path",
        "file_sha256",
        "rule",
        "start_line",
        "end_line",
        "disposition",
        "evidence_ref",
        "evidence_sha256",
        "reviewed_by",
    }

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    try:
        document = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("secret finding dispositions could not be read") from exc
    if (
        not isinstance(document, dict)
        or set(document) != {"schema_version", "dispositions"}
        or not isinstance(document.get("schema_version"), int)
        or isinstance(document.get("schema_version"), bool)
        or document.get("schema_version") != 1
        or not isinstance(document.get("dispositions"), list)
    ):
        raise RuntimeError("secret finding dispositions have an unsupported schema")

    result = document["dispositions"]
    for disposition in result:
        if not isinstance(disposition, dict) or set(disposition) != fields:
            raise RuntimeError("secret finding disposition has invalid fields")
        if (
            not isinstance(disposition["scanner"], str)
            or disposition["scanner"] not in {"gitleaks", "detect-secrets"}
            or not isinstance(disposition["scanner_version"], str)
            or not isinstance(disposition["finding_id"], str)
            or len(disposition["finding_id"]) != 64
            or any(char not in "0123456789abcdef" for char in disposition["finding_id"])
            or not isinstance(disposition["path"], str)
            or not isinstance(disposition["file_sha256"], str)
            or len(disposition["file_sha256"]) != 64
            or any(char not in "0123456789abcdef" for char in disposition["file_sha256"])
            or not isinstance(disposition["rule"], str)
            or not isinstance(disposition["start_line"], int)
            or isinstance(disposition["start_line"], bool)
            or not isinstance(disposition["end_line"], int)
            or isinstance(disposition["end_line"], bool)
            or not isinstance(disposition["disposition"], str)
            or not isinstance(disposition["evidence_ref"], str)
            or not isinstance(disposition["evidence_sha256"], str)
            or len(disposition["evidence_sha256"]) != 64
            or any(char not in "0123456789abcdef" for char in disposition["evidence_sha256"])
            or not isinstance(disposition["reviewed_by"], str)
        ):
            raise RuntimeError("secret finding disposition has invalid values")
    return result


def validate_safe_rel_path(path: str) -> PurePosixPath:
    from scripts.archive.codex_rehydrate import validate_safe_rel_path as validate

    return validate(path)


def validate_symlink_target(
    link_path: str,
    target: str,
    *,
    allow_external: bool = False,
    archive_symlinks: set[str] | None = None,
) -> None:
    from scripts.archive.codex_rehydrate import validate_symlink_target as validate

    return validate(
        link_path, target, allow_external=allow_external, archive_symlinks=archive_symlinks
    )


def verify_archive_connection(
    connection: Any,
    *,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
) -> dict[str, Any]:
    from scripts.archive.codex_rehydrate import verify_archive_connection as verify

    return verify(connection, max_blob_bytes=max_blob_bytes, max_text_bytes=max_text_bytes)


def verify_archive(
    archive: Path,
    *,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
) -> dict[str, Any]:
    from scripts.archive.codex_rehydrate import verify_archive as verify

    return verify(archive, max_blob_bytes=max_blob_bytes, max_text_bytes=max_text_bytes)


def validate_inventory(document: dict[str, Any]) -> list[dict[str, Any]]:
    from scripts.archive.cdx_review import validate_inventory as validate

    return validate(document)


def _archive_function_catalog(
    repository: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Index archive source declarations without importing or executing them."""
    from scripts.archive.cdx_preflight import read_source_file

    functions: list[dict[str, Any]] = []
    modules: list[dict[str, Any]] = []
    archive = repository / "scripts" / "archive"
    for path, relative, info in iter_deterministic_tree(archive, set(), set()):
        if path.suffix not in {".py", ".go"}:
            continue
        source_path = f"scripts/archive/{relative}"
        language = "python" if path.suffix == ".py" else "go"
        module: dict[str, Any] = {"path": source_path, "language": language}
        declarations = []
        try:
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("source catalog requires regular files")
            raw = read_source_file(repository, source_path, limit=4 * 1024 * 1024)
            text = raw.decode("utf-8")
            if language == "python":
                tree = ast.parse(text)
                definitions = {
                    node.name: node
                    for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                exports = None
                aliases = {}
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "__all__":
                                value = ast.literal_eval(node.value)
                                if not isinstance(value, (list, tuple)) or any(
                                    not isinstance(name, str) for name in value
                                ):
                                    raise ValueError("invalid source exports")
                                exports = set(value)
                            elif isinstance(target, ast.Name) and isinstance(node.value, ast.Name):
                                if node.value.id in definitions:
                                    aliases[target.id] = (definitions[node.value.id], node.lineno)
                for name, node in definitions.items():
                    signature = f"({ast.unparse(node.args)})"
                    if node.returns is not None:
                        signature += f" -> {ast.unparse(node.returns)}"
                    declarations.append(
                        {
                            "name": name,
                            "signature": signature,
                            "line": node.lineno,
                            "exported": (
                                name in exports if exports is not None else not name.startswith("_")
                            ),
                        }
                    )
                for name, (node, line) in aliases.items():
                    if exports is not None and name in exports:
                        signature = f"({ast.unparse(node.args)})"
                        if node.returns is not None:
                            signature += f" -> {ast.unparse(node.returns)}"
                        declarations.append(
                            {"name": name, "signature": signature, "line": line, "exported": True}
                        )
            else:
                for line, text_line in enumerate(text.splitlines(), 1):
                    match = re.match(
                        r"^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*(\(.*)\s*\{\s*$",
                        text_line,
                    )
                    if match:
                        name, signature = match.groups()
                        declarations.append(
                            {
                                "name": name,
                                "signature": signature.strip(),
                                "line": line,
                                "exported": name[0].isupper(),
                            }
                        )
                module["signature_parser"] = "single_line_go_declarations"
            module.update(
                status="indexed",
                sha256=hashlib.sha256(raw).hexdigest(),
                functions=len(declarations),
            )
            functions.extend(
                {**declaration, "path": source_path, "language": language}
                for declaration in declarations
            )
        except (OSError, ValueError, SyntaxError, UnicodeError, RecursionError):
            module["status"] = "unavailable_or_malformed"
        modules.append(module)
    return (
        sorted(functions, key=lambda row: (row["path"], row["line"], row["name"])),
        sorted(modules, key=lambda row: row["path"]),
    )


def run_cdx_common_preflight(repository_root: Path | None = None) -> dict[str, Any]:
    """Return bounded read-only context, not scanner clearance or full-tree proof."""
    from scripts.archive.cdx_preflight import read_source_file

    root = (repository_root or Path(__file__).resolve().parents[2]).resolve(strict=True)
    functions, modules = _archive_function_catalog(Path(__file__).resolve().parents[2])
    tools: dict[str, Any] = {
        "python": {"present": True, "path": sys.executable, "version": sys.version.split()[0]}
    }
    for name, arguments in (
        ("git", ["--version"]),
        ("detect-secrets", ["--version"]),
        ("gitleaks", ["version"]),
    ):
        executable = shutil.which(name)
        entry: dict[str, Any] = {"present": executable is not None, "path": executable}
        if executable:
            try:
                result = subprocess.run(
                    [executable, *arguments],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=3,
                    cwd=root,
                    env={
                        "PATH": os.environ.get("PATH", ""),
                        "LC_ALL": "C.UTF-8",
                        "PYTHONNOUSERSITE": "1",
                        "PYTHONDONTWRITEBYTECODE": "1",
                    },
                )
                version = result.stdout.strip()
                if result.returncode != 0 or not version or len(version) > 128 or "\n" in version:
                    entry["status"] = "version_unavailable"
                else:
                    entry.update(status="measured", version=version)
            except (OSError, UnicodeError, subprocess.TimeoutExpired):
                entry["status"] = "version_unavailable"
        else:
            entry["status"] = "missing"
        tools[name] = entry
    archive = {}
    for label, name in (
        ("manifest", "MANIFEST.json"),
        ("ledger", "ARCHIVE_LEDGER.jsonl"),
        ("index", "ARCHIVE_INDEX.md"),
    ):
        relative = f".codex/archive/{name}"
        summary: dict[str, Any] = {"path": relative}
        try:
            raw = read_source_file(root, relative, limit=4 * 1024 * 1024)
            summary.update(status="read", bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            if label == "manifest":
                document = _scanner_json(raw.decode("utf-8"))
                if (
                    not isinstance(document, dict)
                    or type(document.get("total_files")) is not int
                    or document["total_files"] < 0
                    or not isinstance(document.get("files"), list)
                    or any(not isinstance(path, str) for path in document["files"])
                ):
                    raise ValueError("invalid manifest summary")
                summary.update(
                    total_files=document.get("total_files"), listed_files=len(document["files"])
                )
            elif label == "ledger":
                count = 0
                for line in io.StringIO(raw.decode("utf-8")):
                    if line.strip():
                        if not isinstance(_scanner_json(line), dict):
                            raise ValueError("invalid ledger summary")
                        count += 1
                summary["records"] = count
            else:
                summary["headings"] = sum(
                    line.startswith("#") for line in raw.decode("utf-8").splitlines()
                )
        except FileNotFoundError:
            summary["status"] = "missing"
        except (OSError, ValueError, UnicodeError, RecursionError):
            summary["status"] = "unavailable_or_malformed"
        archive[label] = summary
    return {
        "schema_version": 1,
        "purpose": "read_only_context_not_secret_clearance",
        "exports": sorted(__all__),
        "functions": functions,
        "modules": modules,
        "tools": tools,
        "archive": archive,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-context", action="store_true", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_cdx_common_preflight()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("CDX common preflight: read-only context; no scanner clearance")
        print(f"Exports: {len(result['exports'])}; functions: {len(result['functions'])}")
        for name, tool in sorted(result["tools"].items()):
            print(f"{name}: {tool.get('version', tool.get('status', 'unavailable'))}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    raise SystemExit(main())
