#!/usr/bin/env python3
"""Verify and rehydrate a content-addressable SQLite archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import stat
import sys
import zlib
from collections import Counter
from contextlib import closing
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

from scripts.archive.cdx_common import (
    DEFAULT_MAX_BLOB_BYTES,
    DEFAULT_MAX_TEXT_BYTES,
    SCHEMA_VERSION,
    compute_merkle_root,
    inspect_text,
)


def _connect_readonly(archive: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(archive.resolve()), safe='/')}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def _decompress(codec: str, payload: bytes, max_size: int | None = None) -> bytes:
    if max_size is not None and max_size < 0:
        raise ValueError("declared content size must not be negative")
    if codec == "zlib":
        if max_size is None:
            return zlib.decompress(payload)
        decoder = zlib.decompressobj()
        content = decoder.decompress(payload, max_size + 1)
        if (
            len(content) > max_size
            or decoder.unconsumed_tail
            or decoder.unused_data
            or not decoder.eof
        ):
            raise ValueError("compressed content exceeds its declared size")
        return content
    if codec == "none":
        return payload
    raise ValueError(f"unsupported archive codec: {codec}")


def _verify_fts_postings(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA query_only = OFF")
    try:
        connection.execute("""
            CREATE VIRTUAL TABLE temp.cdx_expected_fts USING fts5(
                document_type UNINDEXED, symbol_name UNINDEXED, path UNINDEXED, content
            )
            """)
        connection.execute("""
            INSERT INTO temp.cdx_expected_fts(
                rowid, document_type, symbol_name, path, content
            )
            SELECT id, document_type, symbol_name, path, content FROM main.fts_documents
            """)
        connection.execute("""
            CREATE VIRTUAL TABLE temp.cdx_expected_vocab
            USING fts5vocab(cdx_expected_fts, 'instance')
            """)
        connection.execute("""
            CREATE VIRTUAL TABLE temp.cdx_actual_vocab
            USING fts5vocab(main, fts_code_index, 'instance')
            """)
        difference = connection.execute("""
            SELECT EXISTS(
                SELECT term, doc, col, offset FROM temp.cdx_actual_vocab
                EXCEPT
                SELECT term, doc, col, offset FROM temp.cdx_expected_vocab
            ) OR EXISTS(
                SELECT term, doc, col, offset FROM temp.cdx_expected_vocab
                EXCEPT
                SELECT term, doc, col, offset FROM temp.cdx_actual_vocab
            )
            """).fetchone()[0]
        if difference:
            raise ValueError("archive FTS postings are inconsistent")
    finally:
        connection.execute("DROP TABLE IF EXISTS temp.cdx_actual_vocab")
        connection.execute("DROP TABLE IF EXISTS temp.cdx_expected_vocab")
        connection.execute("DROP TABLE IF EXISTS temp.cdx_expected_fts")
        connection.execute("PRAGMA query_only = ON")


def verify_archive_connection(
    connection: sqlite3.Connection,
    *,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
) -> dict[str, Any]:
    if max_blob_bytes <= 0 or max_text_bytes <= 0:
        raise ValueError("size ceilings must be positive")
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise ValueError(f"SQLite integrity check failed: {integrity}")
    decoded_text: dict[str, tuple[str | None, str | None, str | None]] = {}
    for blob in connection.execute("""
            SELECT blob_sha256, codec, raw_size, length(raw_payload) AS payload_size
            FROM content_blobs
            """):
        if (
            blob["raw_size"] < 0
            or blob["raw_size"] > max_blob_bytes
            or blob["payload_size"] > max_blob_bytes + 1024 * 1024
        ):
            raise ValueError(f"content exceeds the configured size ceiling: {blob['blob_sha256']}")
        payload = connection.execute(
            "SELECT raw_payload FROM content_blobs WHERE blob_sha256 = ?",
            (blob["blob_sha256"],),
        ).fetchone()[0]
        content = _decompress(blob["codec"], payload, blob["raw_size"])
        if len(content) != blob["raw_size"]:
            raise ValueError(f"content size mismatch for {blob['blob_sha256']}")
        if hashlib.sha256(content).hexdigest() != blob["blob_sha256"]:
            raise ValueError(f"content digest mismatch for {blob['blob_sha256']}")
        text, encoding, endings = inspect_text(content)
        text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest() if text is not None else None
        decoded_text[blob["blob_sha256"]] = (text_sha256, encoding, endings)
    manifest = connection.execute("SELECT * FROM archive_manifest WHERE id = 1").fetchone()
    if manifest is None:
        raise ValueError("archive manifest is missing")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("archive schema version is not supported")
    if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise ValueError("archive foreign-key check failed")
    invalid_entries = connection.execute("""
            SELECT COUNT(*)
            FROM tree_entries AS t
            LEFT JOIN content_blobs AS b USING (blob_sha256)
            WHERE
                (t.size < 0)
                OR (t.entry_type = 'file' AND
                    (t.blob_sha256 IS NULL OR b.blob_sha256 IS NULL OR t.size != b.raw_size))
                OR (t.entry_type != 'file' AND t.blob_sha256 IS NOT NULL)
                OR (t.entry_type = 'dir' AND (t.size != 0 OR t.symlink_target IS NOT NULL))
                OR (t.entry_type = 'symlink' AND t.symlink_target IS NULL)
            """).fetchone()[0]
    if invalid_entries:
        raise ValueError("archive entry metadata is inconsistent")
    unsafe_mode = connection.execute("""
            SELECT path FROM tree_entries
            WHERE mode < 0 OR mode > 4095 OR (mode & 3072) != 0
            LIMIT 1
            """).fetchone()
    if unsafe_mode is not None:
        raise ValueError("archive contains unsupported setuid/setgid or mode bits")
    for item in connection.execute("""
            SELECT t.entry_id, t.entry_type, t.blob_sha256, t.text_encoding,
                   t.line_endings, t.text_sha256, d.entry_id AS text_entry_id,
                   length(CAST(d.utf8_text AS BLOB)) AS text_size
            FROM tree_entries AS t
            LEFT JOIN text_documents AS d USING (entry_id)
            """):
        expected_text = decoded_text.get(item["blob_sha256"])
        if item["entry_type"] != "file" or expected_text is None:
            if (
                item["text_entry_id"] is not None
                or item["text_sha256"] is not None
                or item["text_encoding"] is not None
                or item["line_endings"] is not None
            ):
                raise ValueError("archive text index is inconsistent")
            continue
        expected_hash, expected_encoding, expected_endings = expected_text
        if expected_hash is None:
            if (
                item["text_entry_id"] is not None
                or item["text_sha256"] is not None
                or item["text_encoding"] is not None
                or item["line_endings"] is not None
            ):
                raise ValueError("archive text index is inconsistent")
            continue
        if item["text_size"] > max_text_bytes:
            raise ValueError("archive text index exceeds the configured size ceiling")
        if (
            item["text_entry_id"] is None
            or item["text_sha256"] != expected_hash
            or item["text_encoding"] != expected_encoding
            or item["line_endings"] != expected_endings
        ):
            raise ValueError("archive text index is inconsistent")
        text = connection.execute(
            "SELECT utf8_text FROM text_documents WHERE entry_id = ?",
            (item["entry_id"],),
        ).fetchone()[0]
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_hash:
            raise ValueError("archive text index is inconsistent")
    for entry in connection.execute("SELECT entry_id, path, entry_type FROM tree_entries"):
        expected_fts: Counter[tuple[str, str, str, str]] = Counter()
        document = connection.execute(
            "SELECT utf8_text FROM text_documents WHERE entry_id = ?",
            (entry["entry_id"],),
        ).fetchone()
        if document is not None:
            text = document["utf8_text"]
            expected_fts[("file", "", entry["path"], text)] += 1
            if Path(entry["path"]).suffix.lower() == ".py":
                lines = text.splitlines()
                for symbol in connection.execute(
                    """
                    SELECT symbol_kind, symbol_name, qualified_name, line_start, line_end
                    FROM ast_symbols WHERE entry_id = ?
                    """,
                    (entry["entry_id"],),
                ):
                    if symbol["symbol_kind"] == "module":
                        continue
                    symbol_name = (
                        symbol["symbol_name"]
                        if symbol["symbol_kind"] == "import"
                        else symbol["qualified_name"]
                    )
                    source_slice = "\n".join(lines[symbol["line_start"] - 1 : symbol["line_end"]])
                    expected_fts[("symbol", symbol_name, entry["path"], source_slice)] += 1
        actual_fts = Counter(
            tuple(row)
            for row in connection.execute(
                """
                SELECT document_type, symbol_name, path, content
                FROM fts_documents WHERE entry_id = ?
                """,
                (entry["entry_id"],),
            )
        )
        if actual_fts != expected_fts:
            raise ValueError("archive search index is inconsistent")
    _verify_fts_postings(connection)
    actual_merkle = compute_merkle_root(connection)
    if actual_merkle != manifest["merkle_root_sha256"]:
        raise ValueError("archive Merkle root mismatch")
    actual_entries = int(connection.execute("SELECT COUNT(*) FROM tree_entries").fetchone()[0])
    actual_blobs = int(connection.execute("SELECT COUNT(*) FROM content_blobs").fetchone()[0])
    if actual_entries != manifest["entry_count"] or actual_blobs != manifest["blob_count"]:
        raise ValueError("archive manifest counts do not match stored data")
    return {
        "integrity_check": integrity,
        "entry_count": actual_entries,
        "blob_count": actual_blobs,
        "merkle_root_sha256": actual_merkle,
    }


def verify_archive(
    archive: Path,
    *,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
) -> dict[str, Any]:
    with closing(_connect_readonly(archive)) as connection:
        return verify_archive_connection(
            connection,
            max_blob_bytes=max_blob_bytes,
            max_text_bytes=max_text_bytes,
        )


def validate_safe_rel_path(path: str) -> PurePosixPath:
    if not path or "\x00" in path or "\\" in path:
        raise ValueError("archive contains an unsafe path")
    if path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        raise ValueError("archive contains an absolute path")
    relative = PurePosixPath(path)
    if any(part in {"", ".", ".."} for part in path.split("/")):
        raise ValueError("archive contains a traversal path")
    return relative


def validate_symlink_target(
    link_path: str,
    target: str,
    *,
    allow_external: bool = False,
    archive_symlinks: set[str] | None = None,
) -> None:
    if not target or "\x00" in target or "\\" in target:
        raise ValueError("archive contains an unsafe symlink target")
    if os.path.isabs(target) or re.match(r"^[A-Za-z]:", target):
        if not allow_external:
            raise ValueError("external symlink target is not allowed")
        return
    if allow_external:
        return
    symlink_paths = archive_symlinks or set()
    components = [part for part in PurePosixPath(link_path).parent.parts if part not in {"", "."}]
    for index in range(len(components)):
        if "/".join(components[: index + 1]) in symlink_paths:
            raise ValueError("archive entry is nested beneath a symlink")
    for part in target.split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if not components:
                raise ValueError("symlink target escapes the destination")
            components.pop()
        else:
            components.append(part)
        resolved = "/".join(components)
        if resolved in symlink_paths:
            raise ValueError("symlink target traverses another archived symlink")


def _destination_path(root: Path, relative: str) -> Path:
    safe = validate_safe_rel_path(relative)
    target = root.joinpath(*safe.parts)
    if (
        root.resolve() not in target.parent.resolve().parents
        and target.parent.resolve() != root.resolve()
    ):
        raise ValueError("archive path escapes the destination")
    return target


def rehydrate_archive(
    archive: Path,
    destination: Path,
    *,
    allow_external_symlinks: bool = False,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
) -> dict[str, Any]:
    verification = verify_archive(
        archive,
        max_blob_bytes=max_blob_bytes,
        max_text_bytes=max_text_bytes,
    )
    if destination.is_symlink():
        raise ValueError("destination must not be a symlink")
    root = destination.resolve()
    if root.exists() and any(root.iterdir()):
        raise FileExistsError("destination must be empty")
    with closing(_connect_readonly(archive)) as connection:
        entries = [
            dict(row)
            for row in connection.execute("SELECT * FROM tree_entries ORDER BY path COLLATE BINARY")
        ]
        symlink_paths = {item["path"] for item in entries if item["entry_type"] == "symlink"}
        for item in entries:
            validate_safe_rel_path(item["path"])
            components = PurePosixPath(item["path"]).parts
            if any(
                "/".join(components[:index]) in symlink_paths for index in range(1, len(components))
            ):
                raise ValueError("archive entry is nested beneath a symlink")
            if item["entry_type"] == "symlink":
                validate_symlink_target(
                    item["path"],
                    item["symlink_target"],
                    allow_external=allow_external_symlinks,
                    archive_symlinks=symlink_paths,
                )
        root.mkdir(parents=True, exist_ok=True)
        directories = [item for item in entries if item["entry_type"] == "dir"]
        files = [item for item in entries if item["entry_type"] == "file"]
        symlinks = [item for item in entries if item["entry_type"] == "symlink"]

        for item in sorted(
            directories, key=lambda value: (value["path"].count("/"), value["path"])
        ):
            path = _destination_path(root, item["path"])
            path.mkdir(parents=True, exist_ok=True)

        for item in files:
            path = _destination_path(root, item["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            blob = connection.execute(
                "SELECT codec, raw_size, raw_payload FROM content_blobs WHERE blob_sha256 = ?",
                (item["blob_sha256"],),
            ).fetchone()
            if blob is None:
                raise ValueError(f"missing content blob for {item['path']}")
            content = _decompress(blob["codec"], blob["raw_payload"], blob["raw_size"])
            if (
                len(content) != blob["raw_size"]
                or hashlib.sha256(content).hexdigest() != item["blob_sha256"]
            ):
                raise ValueError(f"content verification failed for {item['path']}")
            with path.open("xb") as file_handle:
                file_handle.write(content)
            os.chmod(path, item["mode"])
            os.utime(path, ns=(item["mtime_ns"], item["mtime_ns"]))

        for item in symlinks:
            path = _destination_path(root, item["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(item["symlink_target"], path)
            try:
                os.utime(
                    path,
                    ns=(item["mtime_ns"], item["mtime_ns"]),
                    follow_symlinks=False,
                )
            except (NotImplementedError, OSError):
                pass

        for item in sorted(
            directories,
            key=lambda value: (-value["path"].count("/"), value["path"]),
        ):
            path = _destination_path(root, item["path"])
            os.chmod(path, item["mode"])
            os.utime(path, ns=(item["mtime_ns"], item["mtime_ns"]))
    return {"destination": str(root), **verification}


def compare_trees(left: Path, right: Path, *, check_mtime: bool = True) -> dict[str, Any]:
    def inventory(root: Path) -> dict[str, tuple[str, int, int | None, str]]:
        result: dict[str, tuple[str, int, int | None, str]] = {}
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current)
            dirs.sort()
            files.sort()
            for name in list(dirs) + files:
                path = current_path / name
                relative = path.relative_to(root).as_posix()
                info = path.lstat()
                mode = stat.S_IMODE(info.st_mode)
                mtime_ns = info.st_mtime_ns if check_mtime else None
                if stat.S_ISLNK(info.st_mode):
                    result[relative] = ("symlink", mode, mtime_ns, os.readlink(path))
                elif stat.S_ISDIR(info.st_mode):
                    result[relative] = ("dir", mode, mtime_ns, "")
                elif stat.S_ISREG(info.st_mode):
                    digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    result[relative] = ("file", mode, mtime_ns, digest)
        return result

    left_items = inventory(left)
    right_items = inventory(right)
    missing = sorted(left_items.keys() - right_items.keys())
    extra = sorted(right_items.keys() - left_items.keys())
    mismatched = sorted(
        path
        for path in left_items.keys() & right_items.keys()
        if left_items[path] != right_items[path]
    )
    return {
        "identical": not missing and not extra and not mismatched,
        "missing": missing,
        "extra": extra,
        "mismatched": mismatched,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("archive", type=Path)
    verify.add_argument("--max-blob-bytes", type=int, default=DEFAULT_MAX_BLOB_BYTES)
    verify.add_argument("--max-text-bytes", type=int, default=DEFAULT_MAX_TEXT_BYTES)
    extract = commands.add_parser("extract")
    extract.add_argument("archive", type=Path)
    extract.add_argument("destination", type=Path)
    extract.add_argument("--allow-external-symlinks", action="store_true")
    extract.add_argument("--max-blob-bytes", type=int, default=DEFAULT_MAX_BLOB_BYTES)
    extract.add_argument("--max-text-bytes", type=int, default=DEFAULT_MAX_TEXT_BYTES)
    compare = commands.add_parser("compare")
    compare.add_argument("left", type=Path)
    compare.add_argument("right", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "verify":
            result = verify_archive(
                args.archive,
                max_blob_bytes=args.max_blob_bytes,
                max_text_bytes=args.max_text_bytes,
            )
        elif args.command == "extract":
            result = rehydrate_archive(
                args.archive,
                args.destination,
                allow_external_symlinks=args.allow_external_symlinks,
                max_blob_bytes=args.max_blob_bytes,
                max_text_bytes=args.max_text_bytes,
            )
        else:
            result = compare_trees(args.left, args.right)
            if not result["identical"]:
                print(json.dumps(result, sort_keys=True))
                return 1
    except (OSError, sqlite3.Error, ValueError, zlib.error) as exc:
        print(f"archive rehydration failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
