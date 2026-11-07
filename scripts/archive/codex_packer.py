#!/usr/bin/env python3
"""Build a deterministic, content-addressable SQLite snapshot of a directory."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import os
import sqlite3
import stat
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any

from scripts.archive.cdx_common import (
    DEFAULT_DENIED_GLOBS,
    DEFAULT_MAX_BLOB_BYTES,
    SCHEMA_SQL,
    SCHEMA_VERSION,
    compute_merkle_root,
    git_blob_oids,
    inspect_text,
    iter_deterministic_tree,
    run_secret_scanners,
)


def _insert_fts_document(
    connection: sqlite3.Connection,
    entry_id: int,
    document_type: str,
    symbol_name: str,
    path: str,
    content: str,
) -> None:
    connection.execute(
        """
        INSERT INTO fts_documents(entry_id, document_type, symbol_name, path, content)
        VALUES (?, ?, ?, ?, ?)
        """,
        (entry_id, document_type, symbol_name, path, content),
    )


def _ast_symbols(
    connection: sqlite3.Connection,
    entry_id: int,
    path: str,
    text: str,
) -> None:
    try:
        module = ast.parse(text, filename=path)
    except (SyntaxError, ValueError, TypeError):
        return
    lines = text.splitlines()
    module_name = Path(path).stem
    cursor = connection.execute(
        """
        INSERT INTO ast_symbols(
            entry_id, parent_symbol_id, symbol_kind, symbol_name, qualified_name,
            signature, line_start, line_end, decorators_json, bases_json,
            call_targets_json
        ) VALUES (?, NULL, 'module', ?, ?, NULL, 1, ?, '[]', '[]', '[]')
        """,
        (entry_id, module_name, module_name, max(1, len(lines))),
    )
    if cursor.lastrowid is None:
        raise sqlite3.DatabaseError("failed to insert module symbol")
    module_id = cursor.lastrowid

    def save_symbol(
        node: ast.AST,
        parent_id: int,
        parent_name: str,
        inside_class: bool,
    ) -> int:
        if isinstance(node, ast.ClassDef):
            name = node.name
            kind = "class"
            signature = None
            bases = [ast.unparse(base) for base in node.bases]
            decorators = [ast.unparse(item) for item in node.decorator_list]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            kind = (
                "async_method"
                if isinstance(node, ast.AsyncFunctionDef) and inside_class
                else (
                    "method"
                    if inside_class
                    else "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
                )
            )
            args = ast.unparse(node.args)
            signature = (
                f"{'async ' if isinstance(node, ast.AsyncFunctionDef) else ''}def {name}({args})"
            )
            if node.returns is not None:
                signature += f" -> {ast.unparse(node.returns)}"
            bases = []
            decorators = [ast.unparse(item) for item in node.decorator_list]
        else:
            return parent_id

        qualified_name = f"{parent_name}.{name}" if parent_name else name
        calls = sorted(
            {ast.unparse(call.func) for call in ast.walk(node) if isinstance(call, ast.Call)}
        )
        start = int(getattr(node, "lineno", 1))
        end = int(getattr(node, "end_lineno", start))
        cursor = connection.execute(
            """
            INSERT INTO ast_symbols(
                entry_id, parent_symbol_id, symbol_kind, symbol_name, qualified_name,
                signature, line_start, line_end, decorators_json, bases_json,
                call_targets_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                parent_id,
                kind,
                name,
                qualified_name,
                signature,
                start,
                end,
                json.dumps(decorators, ensure_ascii=False),
                json.dumps(bases, ensure_ascii=False),
                json.dumps(calls, ensure_ascii=False),
            ),
        )
        if cursor.lastrowid is None:
            raise sqlite3.DatabaseError("failed to insert AST symbol")
        symbol_id = cursor.lastrowid
        source_slice = "\n".join(lines[start - 1 : end])
        _insert_fts_document(connection, entry_id, "symbol", qualified_name, path, source_slice)
        for child in getattr(node, "body", []):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                save_symbol(
                    child,
                    symbol_id,
                    qualified_name,
                    inside_class or isinstance(node, ast.ClassDef),
                )
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                import_name = (
                    child.module or ""
                    if isinstance(child, ast.ImportFrom)
                    else ", ".join(alias.name for alias in child.names)
                )
                import_start = int(getattr(child, "lineno", 1))
                import_end = int(getattr(child, "end_lineno", import_start))
                connection.execute(
                    """
                    INSERT INTO ast_symbols(
                        entry_id, parent_symbol_id, symbol_kind, symbol_name,
                        qualified_name, signature, line_start, line_end,
                        decorators_json, bases_json, call_targets_json
                    ) VALUES (?, ?, 'import', ?, ?, NULL, ?, ?, '[]', '[]', '[]')
                    """,
                    (
                        entry_id,
                        symbol_id,
                        import_name,
                        f"{qualified_name}.{import_name}",
                        import_start,
                        import_end,
                    ),
                )
                _insert_fts_document(
                    connection,
                    entry_id,
                    "symbol",
                    import_name,
                    path,
                    "\n".join(lines[import_start - 1 : import_end]),
                )
        return symbol_id

    for node in module.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            save_symbol(node, module_id, module_name, False)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            import_name = (
                node.module or ""
                if isinstance(node, ast.ImportFrom)
                else ", ".join(alias.name for alias in node.names)
            )
            start = int(getattr(node, "lineno", 1))
            end = int(getattr(node, "end_lineno", start))
            connection.execute(
                """
                INSERT INTO ast_symbols(
                    entry_id, parent_symbol_id, symbol_kind, symbol_name,
                    qualified_name, signature, line_start, line_end,
                    decorators_json, bases_json, call_targets_json
                ) VALUES (?, ?, 'import', ?, ?, NULL, ?, ?, '[]', '[]', '[]')
                """,
                (entry_id, module_id, import_name, f"{module_name}.{import_name}", start, end),
            )
            _insert_fts_document(
                connection,
                entry_id,
                "symbol",
                import_name,
                path,
                "\n".join(lines[start - 1 : end]),
            )


def _create_scanned_snapshot(
    source: Path,
    snapshot: Path,
    *,
    max_file_bytes: int,
    max_blob_bytes: int,
    exclude: tuple[str, ...],
    allow_large: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    snapshot.mkdir()
    metadata: dict[str, dict[str, Any]] = {}
    denied_globs = DEFAULT_DENIED_GLOBS | set(exclude)
    directories: list[tuple[Path, dict[str, Any]]] = []
    for path, relative, info in iter_deterministic_tree(source, denied_globs=denied_globs):
        try:
            relative.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("archive paths must be valid UTF-8") from exc
        if any(fnmatch.fnmatchcase(relative, pattern) for pattern in exclude):
            continue
        target = snapshot / relative
        mode = stat.S_IMODE(info.st_mode)
        if mode & (stat.S_ISUID | stat.S_ISGID):
            raise ValueError("setuid and setgid modes are not supported")
        entry: dict[str, Any] = {
            "entry_type": "",
            "mode": mode,
            "mtime_ns": info.st_mtime_ns,
            "snapshot_mtime_ns": None,
            "size": 0,
            "blob_sha256": None,
            "symlink_target": None,
        }
        if stat.S_ISDIR(info.st_mode):
            target.mkdir(parents=True, exist_ok=True)
            entry["entry_type"] = "dir"
            directories.append((target, entry))
        elif stat.S_ISLNK(info.st_mode):
            link_target = os.readlink(path)
            try:
                link_target.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise ValueError("symlink targets must be valid UTF-8") from exc
            os.symlink(link_target, target)
            try:
                os.utime(
                    target,
                    ns=(info.st_mtime_ns, info.st_mtime_ns),
                    follow_symlinks=False,
                )
            except (NotImplementedError, OSError):
                # Preserve the snapshot when symlink timestamp updates are unsupported.
                pass
            entry["entry_type"] = "symlink"
            entry["symlink_target"] = link_target
            entry["size"] = len(os.fsencode(link_target))
            entry["snapshot_mtime_ns"] = target.lstat().st_mtime_ns
        elif stat.S_ISREG(info.st_mode):
            if info.st_size > max_file_bytes and not any(
                fnmatch.fnmatchcase(relative, pattern) for pattern in allow_large
            ):
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as source_file, target.open("xb") as target_file:
                for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                    size += len(chunk)
                    if size > max_blob_bytes:
                        raise ValueError("file exceeds the configured blob size ceiling")
                    digest.update(chunk)
                    target_file.write(chunk)
            os.chmod(target, mode)
            os.utime(target, ns=(info.st_mtime_ns, info.st_mtime_ns))
            entry["entry_type"] = "file"
            entry["size"] = size
            entry["blob_sha256"] = digest.hexdigest()
            entry["snapshot_mtime_ns"] = target.stat().st_mtime_ns
        else:
            continue
        metadata[relative] = entry
    for path, entry in sorted(
        directories, key=lambda item: (-item[0].as_posix().count("/"), item[0].as_posix())
    ):
        os.chmod(path, entry["mode"])
        os.utime(path, ns=(entry["mtime_ns"], entry["mtime_ns"]))
        entry["snapshot_mtime_ns"] = path.stat().st_mtime_ns
    return metadata


def pack_archive(
    source: Path,
    output: Path,
    *,
    max_file_bytes: int = 8 * 1024 * 1024,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    exclude: tuple[str, ...] = (),
    allow_large: tuple[str, ...] = (),
    finding_dispositions: Path | None = None,
    finding_inventory: Path | None = None,
) -> dict[str, Any]:
    root = source.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("source must be a directory")
    try:
        root.name.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("source directory name must be valid UTF-8") from exc
    output_path = output.absolute()
    if output_path.is_symlink() or output_path == root or root in output_path.parents:
        raise ValueError("archive output must be outside the source directory")
    destination = output_path.parent.resolve() / output_path.name
    if destination == root or root in destination.parents:
        raise ValueError("archive output must be outside the source directory")
    if max_file_bytes < 0 or max_blob_bytes <= 0:
        raise ValueError("file and blob size limits must be non-negative")
    blob_ids = git_blob_oids(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cdx-pack-") as work_dir:
        snapshot = Path(work_dir) / "tree"
        metadata = _create_scanned_snapshot(
            root,
            snapshot,
            max_file_bytes=max_file_bytes,
            max_blob_bytes=max_blob_bytes,
            exclude=exclude,
            allow_large=allow_large,
        )
        run_secret_scanners(
            snapshot,
            finding_dispositions,
            finding_inventory,
            root,
        )
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
        )
        os.close(fd)
        temp_path = Path(temp_name)
        try:
            connection = sqlite3.connect(temp_path)
            try:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.executescript(SCHEMA_SQL)
                seen: set[str] = set()
                for path, relative, info in iter_deterministic_tree(snapshot):
                    if relative not in metadata or relative in seen:
                        raise RuntimeError("scanned snapshot changed during packing")
                    seen.add(relative)
                    expected = metadata[relative]
                    mode = stat.S_IMODE(info.st_mode)
                    if (
                        mode != expected["mode"]
                        or info.st_mtime_ns != expected["snapshot_mtime_ns"]
                    ):
                        raise RuntimeError("scanned snapshot metadata changed during packing")
                    mtime_ns = expected["mtime_ns"]
                    if stat.S_ISDIR(info.st_mode):
                        if expected["entry_type"] != "dir":
                            raise RuntimeError("scanned snapshot type changed during packing")
                        connection.execute(
                            """
                            INSERT INTO tree_entries(path, entry_type, mode, mtime_ns, size)
                            VALUES (?, 'dir', ?, ?, 0)
                            """,
                            (relative, mode, mtime_ns),
                        )
                        continue
                    if stat.S_ISLNK(info.st_mode):
                        target = os.readlink(path)
                        if (
                            expected["entry_type"] != "symlink"
                            or target != expected["symlink_target"]
                        ):
                            raise RuntimeError("scanned snapshot link changed during packing")
                        connection.execute(
                            """
                            INSERT INTO tree_entries(
                                path, entry_type, mode, mtime_ns, size, symlink_target
                            ) VALUES (?, 'symlink', ?, ?, ?, ?)
                            """,
                            (relative, mode, mtime_ns, expected["size"], target),
                        )
                        continue
                    if not stat.S_ISREG(info.st_mode) or expected["entry_type"] != "file":
                        raise RuntimeError("scanned snapshot type changed during packing")
                    raw = path.read_bytes()
                    blob_sha = hashlib.sha256(raw).hexdigest()
                    if len(raw) != expected["size"] or blob_sha != expected["blob_sha256"]:
                        raise RuntimeError("scanned snapshot content changed during packing")
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO content_blobs(
                            blob_sha256, codec, raw_size, raw_payload
                        ) VALUES (?, 'zlib', ?, ?)
                        """,
                        (blob_sha, len(raw), zlib.compress(raw, level=9)),
                    )
                    text, encoding, endings = inspect_text(raw)
                    text_sha256 = (
                        hashlib.sha256(text.encode("utf-8")).hexdigest()
                        if text is not None
                        else None
                    )
                    cursor = connection.execute(
                        """
                        INSERT INTO tree_entries(
                            path, entry_type, mode, mtime_ns, size, blob_sha256,
                            git_blob_oid, text_encoding, line_endings, text_sha256
                        ) VALUES (?, 'file', ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            relative,
                            mode,
                            mtime_ns,
                            len(raw),
                            blob_sha,
                            blob_ids.get(relative),
                            encoding,
                            endings,
                            text_sha256,
                        ),
                    )
                    if cursor.lastrowid is None:
                        raise sqlite3.DatabaseError("failed to insert tree entry")
                    entry_id = cursor.lastrowid
                    if text is not None:
                        connection.execute(
                            "INSERT INTO text_documents(entry_id, utf8_text) VALUES (?, ?)",
                            (entry_id, text),
                        )
                        _insert_fts_document(connection, entry_id, "file", "", relative, text)
                        if path.suffix.lower() == ".py":
                            _ast_symbols(connection, entry_id, relative, text)

                if seen != metadata.keys():
                    raise RuntimeError("scanned snapshot changed during packing")
                merkle_root = compute_merkle_root(connection)
                entry_count = int(
                    connection.execute("SELECT COUNT(*) FROM tree_entries").fetchone()[0]
                )
                blob_count = int(
                    connection.execute("SELECT COUNT(*) FROM content_blobs").fetchone()[0]
                )
                connection.execute(
                    """
                    INSERT INTO archive_manifest(
                        id, schema_version, source_root, source_of_truth,
                        merkle_root_sha256, entry_count, blob_count
                    ) VALUES (1, ?, ?, 'working_tree_bytes', ?, ?, ?)
                    """,
                    (SCHEMA_VERSION, root.name, merkle_root, entry_count, blob_count),
                )
                connection.execute("INSERT INTO fts_code_index(fts_code_index) VALUES ('optimize')")
                connection.execute(
                    "INSERT INTO fts_code_index(fts_code_index, rank) "
                    "VALUES ('integrity-check', 1)"
                )
                connection.execute("PRAGMA optimize")
                connection.commit()
                connection.execute("VACUUM")
                check = connection.execute("PRAGMA integrity_check").fetchone()[0]
                if check != "ok":
                    raise sqlite3.DatabaseError(f"integrity_check failed: {check}")
            finally:
                connection.close()
            with temp_path.open("rb") as archive_file:
                os.fsync(archive_file.fileno())
            os.replace(temp_path, destination)
        except BaseException:
            temp_path.unlink(missing_ok=True)
            raise
    return {
        "output": str(destination),
        "entry_count": entry_count,
        "blob_count": blob_count,
        "merkle_root_sha256": merkle_root,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-file-bytes", type=int, default=8 * 1024 * 1024)
    parser.add_argument("--max-blob-bytes", type=int, default=DEFAULT_MAX_BLOB_BYTES)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--allow-large", action="append", default=[])
    parser.add_argument("--finding-dispositions", type=Path)
    parser.add_argument("--finding-inventory", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = pack_archive(
            args.source,
            args.output,
            max_file_bytes=args.max_file_bytes,
            max_blob_bytes=args.max_blob_bytes,
            exclude=tuple(args.exclude),
            allow_large=tuple(args.allow_large),
            finding_dispositions=args.finding_dispositions,
            finding_inventory=args.finding_inventory,
        )
    except (OSError, RuntimeError, sqlite3.Error, ValueError) as exc:
        print(f"archive pack failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
