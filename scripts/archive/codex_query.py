#!/usr/bin/env python3
"""Read-only query and context rendering for `.cdx.sqlite` archives."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import re
import sqlite3
import sys
import zlib
from pathlib import Path
from typing import Any
from urllib.parse import quote
from xml.sax.saxutils import escape

from scripts.archive.cdx_common import (
    DEFAULT_MAX_BLOB_BYTES,
    DEFAULT_MAX_TEXT_BYTES,
)
from scripts.archive.codex_rehydrate import verify_archive_connection


def _xml_safe(value: str) -> str:
    return "".join(
        (
            char
            if ord(char) in (0x9, 0xA, 0xD)
            or 0x20 <= ord(char) <= 0xD7FF
            or 0xE000 <= ord(char) <= 0xFFFD
            or 0x10000 <= ord(char) <= 0x10FFFF
            else "\ufffd"
        )
        for char in value
    )


def _markdown_code_span(value: str) -> str:
    delimiter = "`" * (max((len(run) for run in re.findall(r"`+", value)), default=0) + 1)
    return f"{delimiter} {value} {delimiter}"


def _markdown_fenced_block(content: str) -> str:
    delimiter = "`" * max(
        3,
        max((len(run) for run in re.findall(r"`+", content)), default=0) + 1,
    )
    return f"{delimiter}\n{content}\n{delimiter}"


class CodexArchiveQuery:
    """Open and query a packed archive without permitting database writes."""

    def __init__(
        self,
        archive: Path,
        *,
        max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
        max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
    ):
        if max_blob_bytes <= 0 or max_text_bytes <= 0:
            raise ValueError("size ceilings must be positive")
        self.max_blob_bytes = max_blob_bytes
        self.max_text_bytes = max_text_bytes
        uri = f"file:{quote(str(archive.resolve()), safe='/')}?mode=ro&immutable=1"
        self.connection = sqlite3.connect(uri, uri=True)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA query_only = ON")
        try:
            self.verification = verify_archive_connection(
                self.connection,
                max_blob_bytes=max_blob_bytes,
                max_text_bytes=max_text_bytes,
            )
        except Exception:
            self.connection.close()
            raise

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> CodexArchiveQuery:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get_archive_info(self) -> dict[str, Any]:
        manifest = dict(
            self.connection.execute("SELECT * FROM archive_manifest WHERE id = 1").fetchone()
        )
        manifest["stored_bytes"] = int(
            self.connection.execute(
                "SELECT COALESCE(SUM(length(raw_payload)), 0) FROM content_blobs"
            ).fetchone()[0]
        )
        manifest["original_bytes"] = int(
            self.connection.execute(
                "SELECT COALESCE(SUM(size), 0) FROM tree_entries WHERE entry_type = 'file'"
            ).fetchone()[0]
        )
        manifest["languages"] = {
            extension: count
            for extension, count in sorted(
                self._language_counts().items(), key=lambda item: (-item[1], item[0])
            )
        }
        return manifest

    def _language_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.connection.execute(
            "SELECT path FROM tree_entries WHERE entry_type = 'file'"
        ):
            extension = Path(row["path"]).suffix.lower() or "[no extension]"
            counts[extension] = counts.get(extension, 0) + 1
        return counts

    def list_tree(
        self,
        prefix: str = "",
        *,
        glob: str | None = None,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        values: list[Any] = []
        if prefix:
            normalized = prefix.strip("/")
            if normalized:
                conditions.append("(path = ? OR (path >= ? AND path < ?))")
                values.extend((normalized, normalized + "/", normalized + "0"))
        if glob:
            conditions.append("path GLOB ?")
            values.append(glob)
        if entry_type:
            conditions.append("entry_type = ?")
            values.append(entry_type)
        if language:
            suffix = language if language.startswith(".") else f".{language}"
            conditions.append("path LIKE ?")
            values.append(f"%{suffix}")
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = self.connection.execute(
            f"""
            SELECT path, entry_type, mode, mtime_ns, size, blob_sha256,
                   git_blob_oid, symlink_target, text_encoding, line_endings,
                   text_sha256
            FROM tree_entries {where}
            ORDER BY path COLLATE BINARY
            """,
            values,
        )
        return [dict(row) for row in rows]

    def read_file_bytes(self, path: str) -> bytes:
        row = self.connection.execute(
            """
            SELECT t.size AS entry_size, b.codec, b.raw_size,
                   length(b.raw_payload) AS payload_size, b.blob_sha256
            FROM tree_entries AS t
            JOIN content_blobs AS b USING (blob_sha256)
            WHERE t.path = ? AND t.entry_type = 'file'
            """,
            (path,),
        ).fetchone()
        if row is None:
            raise FileNotFoundError(path)
        if row["raw_size"] < 0:
            raise ValueError(f"content size is negative: {path}")
        if row["entry_size"] != row["raw_size"]:
            raise ValueError(f"content size mismatch: {path}")
        if (
            row["raw_size"] > self.max_blob_bytes
            or row["payload_size"] > self.max_blob_bytes + 1024 * 1024
        ):
            raise ValueError(f"content exceeds the configured size ceiling: {path}")
        payload = self.connection.execute(
            "SELECT raw_payload FROM content_blobs WHERE blob_sha256 = ?",
            (row["blob_sha256"],),
        ).fetchone()[0]
        if row["codec"] == "zlib":
            decoder = zlib.decompressobj()
            content = decoder.decompress(payload, row["raw_size"] + 1)
            if (
                len(content) > row["raw_size"]
                or decoder.unconsumed_tail
                or decoder.unused_data
                or not decoder.eof
            ):
                raise ValueError(f"compressed content exceeds declared size: {path}")
        elif row["codec"] == "none":
            content = bytes(payload)
        else:
            raise ValueError(f"unsupported archive codec: {row['codec']}")
        if len(content) != row["raw_size"]:
            raise ValueError(f"content size mismatch: {path}")
        if hashlib.sha256(content).hexdigest() != row["blob_sha256"]:
            raise ValueError(f"content hash mismatch: {path}")
        return content

    def read_file_text(
        self, path: str, start_line: int | None = None, end_line: int | None = None
    ) -> str:
        row = self.connection.execute(
            """
            SELECT t.size, t.text_sha256,
                   length(CAST(d.utf8_text AS BLOB)) AS text_size
            FROM tree_entries AS t
            JOIN text_documents AS d USING (entry_id)
            WHERE t.path = ? AND t.entry_type = 'file'
            """,
            (path,),
        ).fetchone()
        if row is None:
            raise ValueError(f"file has no indexed text: {path}")
        if row["size"] > self.max_blob_bytes or row["text_size"] > self.max_text_bytes:
            raise ValueError(f"text exceeds the configured size ceiling: {path}")
        text = self.connection.execute(
            """
            SELECT d.utf8_text
            FROM tree_entries AS t
            JOIN text_documents AS d USING (entry_id)
            WHERE t.path = ? AND t.entry_type = 'file'
            """,
            (path,),
        ).fetchone()["utf8_text"]
        if (
            row["text_sha256"] is None
            or hashlib.sha256(text.encode("utf-8")).hexdigest() != row["text_sha256"]
        ):
            raise ValueError(f"text index integrity mismatch: {path}")
        if start_line is None and end_line is None:
            return text
        if start_line is not None and start_line < 1:
            raise ValueError("start_line must be at least 1")
        if end_line is not None and end_line < 1:
            raise ValueError("end_line must be at least 1")
        if start_line is not None and end_line is not None and end_line < start_line:
            raise ValueError("end_line must not precede start_line")
        lines = text.splitlines(keepends=True)
        first = (start_line or 1) - 1
        last = end_line if end_line is not None else len(lines)
        return "".join(lines[first:last])

    def search_fts(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be positive")
        rows = self.connection.execute(
            """
            SELECT path, document_type, symbol_name,
                   snippet(fts_code_index, 3, '«', '»', '…', 12) AS snippet,
                   bm25(fts_code_index, 1.0, 1.0, 1.0, 2.5) AS score
            FROM fts_code_index
            WHERE fts_code_index MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (query, limit),
        )
        return [dict(row) for row in rows]

    def query_symbols(
        self,
        name: str | None = None,
        *,
        kind: str | None = None,
        path: str | None = None,
        decorator: str | None = None,
        base: str | None = None,
        glob: bool = False,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        values: list[Any] = []
        if name:
            if glob:
                conditions.append(
                    "(symbol_name GLOB ? OR qualified_name GLOB ? OR qualified_name GLOB ?)"
                )
                values.extend((name, name, f"*.{name}"))
            else:
                conditions.append(
                    "(symbol_name = ? OR qualified_name = ? OR "
                    "substr(qualified_name, -length(?)) = ?)"
                )
                suffix = f".{name}"
                values.extend((name, name, suffix, suffix))
        if kind:
            conditions.append("symbol_kind = ?")
            values.append(kind)
        if path:
            conditions.append("entry_id IN (SELECT entry_id FROM tree_entries WHERE path = ?)")
            values.append(path)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = self.connection.execute(
            f"""
            SELECT s.symbol_id, t.path, s.parent_symbol_id, s.symbol_kind,
                   s.symbol_name, s.qualified_name, s.signature, s.line_start,
                   s.line_end, s.decorators_json, s.bases_json, s.call_targets_json
            FROM ast_symbols AS s
            JOIN tree_entries AS t USING (entry_id)
            {where}
            ORDER BY t.path, s.line_start, s.symbol_id
            """,
            values,
        )
        result = []
        for row in rows:
            item = dict(row)
            for column in ("decorators_json", "bases_json", "call_targets_json"):
                item[column.removesuffix("_json")] = json.loads(item.pop(column))
            if decorator and decorator not in item["decorators"]:
                continue
            if base and base not in item["bases"]:
                continue
            result.append(item)
        return result

    def query_call_graph(self, symbol: str) -> dict[str, Any]:
        matches = self.query_symbols(symbol)
        if not matches:
            return {"symbol": symbol, "callees": [], "callers": []}
        selected = matches[0]
        callees: list[dict[str, str]] = []
        for target in selected["call_targets"]:
            candidates = self.query_symbols(target)
            for candidate in candidates:
                callees.append(
                    {
                        "path": candidate["path"],
                        "qualified_name": candidate["qualified_name"],
                    }
                )
        callers: list[dict[str, str]] = []
        for row in self.connection.execute("""
            SELECT t.path, s.qualified_name, s.call_targets_json
            FROM ast_symbols AS s
            JOIN tree_entries AS t USING (entry_id)
            """):
            targets = json.loads(row["call_targets_json"])
            direct_match = any(
                candidate["symbol_id"] == selected["symbol_id"]
                for target in targets
                for candidate in self.query_symbols(target)
            )
            owner = selected["qualified_name"].rsplit(".", 1)[0]
            receiver_match = (
                selected["symbol_kind"] in {"method", "async_method"}
                and row["qualified_name"].startswith(f"{owner}.")
                and any(
                    target in {f"self.{selected['symbol_name']}", f"cls.{selected['symbol_name']}"}
                    for target in targets
                )
            )
            if direct_match or receiver_match:
                callers.append({"path": row["path"], "qualified_name": row["qualified_name"]})
        return {
            "symbol": selected["qualified_name"],
            "callees": callees,
            "callers": callers,
        }

    def build_llm_context(
        self,
        *,
        query: str | None = None,
        paths: tuple[str, ...] = (),
        symbols: tuple[str, ...] = (),
        budget_tokens: int = 4000,
        output_format: str = "xml",
    ) -> dict[str, Any]:
        """Build a bounded context using a conservative four-characters/token estimate."""
        if budget_tokens < 1:
            raise ValueError("budget_tokens must be positive")
        if output_format not in {"xml", "markdown"}:
            raise ValueError("output_format must be xml or markdown")
        empty_xml = "<codex_context>\n\n</codex_context>"
        if output_format == "xml" and len(empty_xml) > budget_tokens * 4:
            raise ValueError("budget is too small for the XML context wrapper")
        char_budget = budget_tokens * 4
        entry_sizes = {entry["path"]: entry["size"] for entry in self.list_tree(entry_type="file")}
        omitted: list[str] = []
        included: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        blocks: list[str] = []
        separator = "\n" if output_format == "xml" else "\n\n"
        rendered_chars = len(empty_xml) if output_format == "xml" else 0

        def append_candidate(
            path: str,
            symbol: str,
            *,
            start_line: int | None = None,
            end_line: int | None = None,
            skip_unreadable: bool = False,
        ) -> None:
            nonlocal rendered_chars
            key = (path, symbol)
            if key in seen:
                return
            seen.add(key)
            omitted_name = f"{path}:{symbol}" if symbol else path
            if entry_sizes.get(path, 0) > char_budget:
                omitted.append(omitted_name)
                return
            try:
                content = self.read_file_text(path, start_line, end_line)
            except ValueError:
                if skip_unreadable:
                    return
                raise
            if output_format == "xml":
                block = (
                    f'<file path="{escape(_xml_safe(path), {chr(34): "&quot;"})}"'
                    f' symbol="{escape(_xml_safe(symbol), {chr(34): "&quot;"})}">\n'
                    f"{escape(_xml_safe(content))}\n</file>"
                )
            else:
                metadata = json.dumps(
                    {"path": path, "symbol": symbol},
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                block = (
                    f"### {_markdown_code_span(metadata)}\n\n" f"{_markdown_fenced_block(content)}"
                )
            added_chars = len(block) + (len(separator) if blocks else 0)
            if rendered_chars + added_chars > char_budget:
                omitted.append(omitted_name)
                return
            included.append({"path": path, "symbol": symbol, "content": content})
            blocks.append(block)
            rendered_chars += added_chars

        for symbol in symbols:
            for result in self.query_symbols(symbol):
                append_candidate(
                    result["path"],
                    result["qualified_name"],
                    start_line=result["line_start"],
                    end_line=result["line_end"],
                )
        if query:
            for result in self.search_fts(query, limit=min(budget_tokens, 100)):
                if result["document_type"] == "symbol":
                    symbol_rows = self.query_symbols(result["symbol_name"], path=result["path"])
                    for symbol_row in symbol_rows:
                        append_candidate(
                            result["path"],
                            symbol_row["qualified_name"],
                            start_line=symbol_row["line_start"],
                            end_line=symbol_row["line_end"],
                        )
                else:
                    append_candidate(result["path"], "")
        if paths:
            path_candidates = 0
            for entry in self.list_tree():
                if entry["entry_type"] == "file" and any(
                    fnmatch.fnmatchcase(entry["path"], pattern) for pattern in paths
                ):
                    if entry["size"] > budget_tokens * 4 or path_candidates >= 500:
                        omitted.append(entry["path"])
                        continue
                    append_candidate(entry["path"], "", skip_unreadable=True)
                    path_candidates += 1
        if output_format == "xml":
            rendered = "<codex_context>\n" + "\n".join(blocks) + "\n</codex_context>"
        else:
            rendered = "\n\n".join(blocks)
        used_tokens = math.ceil(len(rendered) / 4)
        return {
            "content": rendered,
            "estimated_tokens": used_tokens,
            "included_items": len(included),
            "omitted_items": omitted,
        }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--max-blob-bytes", type=int, default=DEFAULT_MAX_BLOB_BYTES)
    parser.add_argument("--max-text-bytes", type=int, default=DEFAULT_MAX_TEXT_BYTES)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("info")
    listing = commands.add_parser("list")
    listing.add_argument("--prefix", default="")
    listing.add_argument("--glob")
    listing.add_argument("--type", dest="entry_type", choices=("file", "dir", "symlink"))
    listing.add_argument("--language")
    read = commands.add_parser("read")
    read.add_argument("path")
    read.add_argument("--start-line", type=int)
    read.add_argument("--end-line", type=int)
    read.add_argument("--bytes", action="store_true")
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    symbols = commands.add_parser("symbols")
    symbols.add_argument("name", nargs="?")
    symbols.add_argument("--kind")
    symbols.add_argument("--path")
    symbols.add_argument("--decorator")
    symbols.add_argument("--base")
    symbols.add_argument("--glob", action="store_true")
    callgraph = commands.add_parser("callgraph")
    callgraph.add_argument("symbol")
    context = commands.add_parser("context")
    context.add_argument("--query")
    context.add_argument("--path", action="append", default=[])
    context.add_argument("--symbol", action="append", default=[])
    context.add_argument("--budget-tokens", type=int, default=4000)
    context.add_argument("--format", choices=("xml", "markdown"), default="xml")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result: Any
    try:
        with CodexArchiveQuery(
            args.archive,
            max_blob_bytes=args.max_blob_bytes,
            max_text_bytes=args.max_text_bytes,
        ) as archive:
            if args.command == "info":
                result = archive.get_archive_info()
            elif args.command == "list":
                result = archive.list_tree(
                    args.prefix,
                    glob=args.glob,
                    entry_type=args.entry_type,
                    language=args.language,
                )
            elif args.command == "read":
                if args.bytes:
                    sys.stdout.buffer.write(archive.read_file_bytes(args.path))
                    return 0
                result = archive.read_file_text(args.path, args.start_line, args.end_line)
                print(result, end="" if result.endswith("\n") else "\n")
                return 0
            elif args.command == "search":
                result = archive.search_fts(args.query, args.limit)
            elif args.command == "symbols":
                result = archive.query_symbols(
                    args.name,
                    kind=args.kind,
                    path=args.path,
                    decorator=args.decorator,
                    base=args.base,
                    glob=args.glob,
                )
            elif args.command == "callgraph":
                result = archive.query_call_graph(args.symbol)
            else:
                result = archive.build_llm_context(
                    query=args.query,
                    paths=tuple(args.path),
                    symbols=tuple(args.symbol),
                    budget_tokens=args.budget_tokens,
                    output_format=args.format,
                )
                print(result["content"])
                print(
                    json.dumps(
                        {key: value for key, value in result.items() if key != "content"},
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                )
                return 0
    except (OSError, sqlite3.Error, ValueError, RuntimeError) as exc:
        print(f"archive query failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
