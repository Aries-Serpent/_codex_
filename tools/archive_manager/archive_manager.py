#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
archive_manager.py — Hybrid code archive orchestrator (v4)
----------------------------------------------------------

New in v4:
- Gzipped tombstones: optionally (re)generate
  * tombstones_code.jsonl.gz
  * tombstones_logs.jsonl.gz
  when --gzip-tombstones is specified on `update` and/or `vacuum`.
- `vacuum` command: summarize and prune tombstones by date.
  * --before YYYY-MM-DD (UTC): drop tombstones strictly older than date
  * --dry-run : show what would be removed, do not modify files
  * --summary : print JSON summary (counts, ranges, unique paths)
  * --gzip-tombstones : regenerate .gz after pruning

Carried from v3:
- Tombstone streams on delete (code vs logs), --workers auto, allow/deny globs, deletion tracking.

Artifacts:
- code_archive.jsonl (+ .gz)
- metadata.sqlite
- code_blobs.parquet + deltas (code_blobs_YYYYMMDD_HHMMSS.parquet)
- tombstones_code.jsonl (+ .gz)
- tombstones_logs.jsonl (+ .gz)
"""

from __future__ import annotations

import argparse
import fnmatch
import glob
import gzip
import hashlib
import json
import logging
import os
import sqlite3
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from typing import Dict, List, Optional, Set, Tuple

# Optional imports for Parquet and querying
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except Exception:
    pa = None
    pq = None

try:
    import duckdb
except Exception:
    duckdb = None

LOG = logging.getLogger("archive_manager")

DEFAULT_EXTS = [
    ".py",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".swift",
    ".m",
    ".mm",
    ".sql",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".md",
    ".rst",
    ".txt",
    ".xml",
    ".html",
    ".css",
    ".sh",
    ".ps1",
    ".bat",
]

DEFAULT_IGNORES = [
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    "out",
    "venv",
    ".venv",
    ".tox",
    ".bundle",
    "target",
    ".next",
    ".nuxt",
    ".serverless",
    ".terraform",
]

LOG_GLOBS = [
    "logs/**",
    "log/**",
    "**/*.log",
    "**/*.log.*",
    "**/*.out",
    "**/*.err",
    "test-output/**",
    "test-results/**",
    "reports/junit*/**",
    "reports/**/junit*",
]

CODELIKE_EXTS = set(DEFAULT_EXTS)
CODELIKE_DIR_GLOBS = [
    "src/**",
    "lib/**",
    "include/**",
    "scripts/**",
    "config/**",
    "configs/**",
    "conf/**",
    "docs/**",
    "doc/**",
    "tests/**",
    "test/**",
]

# ---------------- utils ----------------


def setup_logging(verbosity: int, logfile: str):
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    LOG.setLevel(level)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    LOG.addHandler(ch)

    if logfile:
        from logging.handlers import RotatingFileHandler

        fh = RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=3)
        fh.setFormatter(fmt)
        LOG.addHandler(fh)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def is_ignored_path(rel_path: str, ignores: List[str]) -> bool:
    parts = os.path.normpath(rel_path).split(os.sep)
    for p in parts:
        if p in ignores:
            return True
    return False


def is_probably_text(b: bytes) -> bool:
    return b and (b.find(b"\x00") == -1)


def gzip_rewrite(src: str, dst: str):
    with open(src, "rb") as f_in, gzip.open(dst, "wb") as f_out:
        while True:
            buf = f_in.read(1024 * 1024)
            if not buf:
                break
            f_out.write(buf)


def infer_language_from_ext(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return ext or "txt"


def count_lines(text: str) -> int:
    return text.count("\n") + 1 if text else 0


def parse_workers(val: str) -> int:
    s = str(val).strip().lower()
    if s == "auto":
        try:
            ncpu = os.cpu_count() or 4
        except Exception:
            ncpu = 4
        return min(32, max(4, ncpu * 4))  # I/O-bound heuristic
    try:
        return max(1, int(s))
    except Exception:
        return 1


def iso_utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def parse_date_ymd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def to_posix(rel_path: str) -> str:
    return rel_path.replace(os.sep, "/")


def matches_allowdeny(rel_path: str, allow_globs: List[str], deny_globs: List[str]) -> bool:
    rel = to_posix(rel_path)
    if allow_globs:
        if not any(fnmatch.fnmatch(rel, patt) for patt in allow_globs):
            return False
    if deny_globs and any(fnmatch.fnmatch(rel, patt) for patt in deny_globs):
        return False
    return True


# ---------------- SQLite ----------------


def ensure_sqlite(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS code_metadata (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL UNIQUE,
            language TEXT,
            mime_type TEXT,
            lines INTEGER,
            hash TEXT NOT NULL,
            parquet_row_id INTEGER NOT NULL,
            deleted_at TEXT
        );
    """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_lang ON code_metadata(language);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_hash ON code_metadata(hash);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_deleted ON code_metadata(deleted_at);")
    conn.commit()
    conn.close()


def sqlite_upsert_rows(
    db_path: str, rows: List[Tuple[str, str, Optional[str], int, str, int, Optional[str]]]
):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO code_metadata (path, language, mime_type, lines, hash, parquet_row_id, deleted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            language=excluded.language,
            mime_type=excluded.mime_type,
            lines=excluded.lines,
            hash=excluded.hash,
            parquet_row_id=excluded.parquet_row_id,
            deleted_at=excluded.deleted_at
    """,
        rows,
    )
    conn.commit()
    conn.close()


def sqlite_fetch_hash_map(db_path: str) -> Dict[str, str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT path, hash FROM code_metadata WHERE deleted_at IS NULL")
    out = dict(cur.fetchall())
    conn.close()
    return out


def sqlite_active_paths(db_path: str) -> Set[str]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT path FROM code_metadata WHERE deleted_at IS NULL")
    out = {r[0] for r in cur.fetchall()}
    conn.close()
    return out


def sqlite_mark_deleted(db_path: str, paths: Set[str], ts: str):
    if not paths:
        return 0
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executemany(
        "UPDATE code_metadata SET deleted_at=? WHERE path=? AND (deleted_at IS NULL OR deleted_at='')",
        [(ts, p) for p in paths],
    )
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes


def sqlite_fetch_info_for_paths(
    db_path: str, paths: Set[str]
) -> Dict[str, Tuple[Optional[str], Optional[int], Optional[str]]]:
    if not paths:
        return {}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    qmarks = ",".join("?" for _ in paths)
    cur.execute(
        f"SELECT path, language, lines, hash FROM code_metadata WHERE path IN ({qmarks})",
        tuple(paths),
    )
    out = {}
    for path, lang, lines, h in cur.fetchall():
        out[path] = (lang, lines, h)
    conn.close()
    return out


def sqlite_max_row_id(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT MAX(parquet_row_id) FROM code_metadata")
    res = cur.fetchone()
    conn.close()
    return int(res[0]) if res and res[0] is not None else 0


# ---------------- scanning ----------------


def scan_files(root: str, exts: List[str], ignores: List[str]) -> List[str]:
    root = os.path.abspath(root)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignores]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if exts and os.path.splitext(fn)[1].lower() not in exts:
                continue
            if is_ignored_path(os.path.relpath(full, root), ignores):
                continue
            files.append(full)
    return files


def read_text_file(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as f:
            b = f.read()
        if not is_probably_text(b):
            return None
        return b.decode("utf-8", errors="ignore")
    except Exception as e:
        LOG.warning(f"Failed reading {path}: {e}")
        return None


# ---------------- parquet ----------------


def write_parquet_rows(rows: List[Tuple[int, str]], out_file: str, compression: str = "zstd"):
    if pa is None or pq is None:
        raise RuntimeError("pyarrow is required for Parquet operations")
    table = pa.Table.from_pydict(
        {
            "parquet_row_id": [rid for rid, _ in rows],
            "content": [content for _, content in rows],
        }
    )
    pq.write_table(table, out_file, compression=compression)


def list_parquet_deltas(base_file: str, deltas_dir: str) -> List[str]:
    pattern = os.path.join(deltas_dir, "code_blobs_*.parquet")
    files = sorted(glob.glob(pattern))
    if base_file and os.path.exists(base_file):
        files = [base_file] + [f for f in files if os.path.abspath(f) != os.path.abspath(base_file)]
    return files


# ---------------- classification & JSONL helpers ----------------


def classify_deleted_path(rel_path: str) -> str:
    posix = to_posix(rel_path)
    if any(fnmatch.fnmatch(posix, patt) for patt in LOG_GLOBS):
        return "logs"
    ext = os.path.splitext(posix)[1].lower()
    if ext in CODELIKE_EXTS:
        return "code"
    if any(fnmatch.fnmatch(posix, patt) for patt in CODELIKE_DIR_GLOBS):
        return "code"
    return "code"


def append_jsonl(path: str, records: List[dict]):
    if not records:
        return
    with open(path, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------- workers ----------------


def process_file(args_tuple):
    path, root, allow_globs, deny_globs = args_tuple
    rel_path = os.path.relpath(path, root)
    if not matches_allowdeny(rel_path, allow_globs, deny_globs):
        return None
    content = read_text_file(path)
    if content is None:
        return None
    h = sha256_hex(content)
    lang = infer_language_from_ext(path)
    lines = count_lines(content)
    return (rel_path, lang, None, lines, h, content)


# ---------------- commands ----------------


def cmd_build(args):
    root = args.root
    exts = [e if e.startswith(".") else f".{e}" for e in (args.exts or [])] or DEFAULT_EXTS
    ignores = DEFAULT_IGNORES
    jsonl_path = args.jsonl
    sqlite_path = args.sqlite
    parquet_base = args.parquet
    gzip_jsonl = args.gzip_jsonl
    overwrite = args.force
    allow_globs = args.allow_globs or []
    deny_globs = args.deny_globs or []
    workers = parse_workers(args.workers)

    for p in [jsonl_path, sqlite_path, parquet_base, jsonl_path + ".gz"]:
        if os.path.exists(p) and not overwrite:
            raise SystemExit(f"Refusing to overwrite existing {p}. Use --force to allow.")

    ensure_sqlite(sqlite_path)

    LOG.info(f"Scanning {root} ...")
    candidates = scan_files(root, exts, ignores)
    LOG.info(f"Found {len(candidates)} candidate files (pre-glob filters); workers={workers}")

    jsonl_records, sqlite_rows, parquet_rows = [], [], []
    row_id, processed = 1, 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(process_file, (p, root, allow_globs, deny_globs)) for p in candidates
        ]
        for fut in as_completed(futures):
            res = fut.result()
            if not res:
                continue
            rel_path, lang, mime, lines, h, content = res
            jsonl_records.append({"path": rel_path, "language": lang, "content": content})
            sqlite_rows.append((rel_path, lang, mime, lines, h, row_id, None))
            parquet_rows.append((row_id, content))
            row_id += 1
            processed += 1
            if processed % 500 == 0:
                LOG.info(f" processed {processed} files...")

    LOG.info(f"Writing JSONL → {jsonl_path}")
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        for rec in jsonl_records:
            tmp.write(json.dumps(rec, ensure_ascii=False) + "\n")
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name
    os.replace(tmp_path, jsonl_path)

    if gzip_jsonl:
        LOG.info(f"Gzipping JSONL → {jsonl_path}.gz")
        gzip_rewrite(jsonl_path, jsonl_path + ".gz")

    LOG.info(f"Writing SQLite → {sqlite_path}")
    sqlite_upsert_rows(sqlite_path, sqlite_rows)

    LOG.info(f"Writing Parquet base → {parquet_base}")
    write_parquet_rows(parquet_rows, parquet_base, compression=args.parquet_compression)

    LOG.info(f"BUILD complete: files={processed}")


def cmd_update(args):
    root = args.root
    exts = [e if e.startswith(".") else f".{e}" for e in (args.exts or [])] or DEFAULT_EXTS
    ignores = DEFAULT_IGNORES
    jsonl_path = args.jsonl
    sqlite_path = args.sqlite
    parquet_base = args.parquet
    deltas_dir = args.deltas_dir or os.path.dirname(parquet_base) or "."
    gzip_jsonl = args.gzip_jsonl
    allow_globs = args.allow_globs or []
    deny_globs = args.deny_globs or []
    workers = parse_workers(args.workers)
    track_deletes = bool(args.track_deletes)
    tomb_code = args.tombstones_code
    tomb_logs = args.tombstones_logs
    gzip_tombs = args.gzip_tombstones

    if not (
        os.path.exists(jsonl_path) and os.path.exists(sqlite_path) and os.path.exists(parquet_base)
    ):
        raise SystemExit(
            "Missing required artifacts. Run build first (JSONL, SQLite, Parquet base)."
        )

    ensure_sqlite(sqlite_path)
    existing_hash = sqlite_fetch_hash_map(sqlite_path)
    next_row_id = sqlite_max_row_id(sqlite_path)

    LOG.info(f"Scanning for changes in {root} ... (workers={workers})")
    candidates = scan_files(root, exts, ignores)

    changed = 0
    sqlite_rows, parquet_rows, jsonl_updates = [], [], []
    current_paths: Set[str] = set()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(process_file, (p, root, allow_globs, deny_globs)) for p in candidates
        ]
        for fut in as_completed(futures):
            res = fut.result()
            if not res:
                continue
            rel_path, lang, mime, lines, h, content = res
            current_paths.add(rel_path)
            if existing_hash.get(rel_path) == h:
                continue
            next_row_id += 1
            sqlite_rows.append((rel_path, lang, mime, lines, h, next_row_id, None))
            parquet_rows.append((next_row_id, content))
            jsonl_updates.append({"path": rel_path, "language": lang, "content": content})
            changed += 1

    deleted_marked = 0
    tomb_records_code, tomb_records_logs = [], []

    if track_deletes:
        active = sqlite_active_paths(sqlite_path)
        domain_active = {p for p in active if matches_allowdeny(p, allow_globs, deny_globs)}
        missing_new = domain_active - current_paths
        if missing_new:
            ts = iso_utc_now()
            deleted_marked = sqlite_mark_deleted(sqlite_path, missing_new, ts)
            info = sqlite_fetch_info_for_paths(sqlite_path, missing_new)
            for p in sorted(missing_new):
                lang, lines, h = info.get(p, (None, None, None))
                cat = classify_deleted_path(p)
                rec = {
                    "ts": ts,
                    "path": p,
                    "category": cat,
                    "language": lang,
                    "lines": lines,
                    "last_known_hash": h,
                    "event": "deleted",
                }
                (tomb_records_logs if cat == "logs" else tomb_records_code).append(rec)

    if not changed and deleted_marked == 0:
        LOG.info("No changes detected.")
        return

    if jsonl_updates:
        LOG.info(f"Appending {len(jsonl_updates)} records → {jsonl_path}")
        with open(jsonl_path, "a", encoding="utf-8") as f:
            for rec in jsonl_updates:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if gzip_jsonl:
            LOG.info(f"Regenerating gzip → {jsonl_path}.gz")
            gzip_rewrite(jsonl_path, jsonl_path + ".gz")

    if sqlite_rows:
        LOG.info(f"Upserting {len(sqlite_rows)} rows → {sqlite_path}")
        sqlite_upsert_rows(sqlite_path, sqlite_rows)

    if parquet_rows:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        delta_file = os.path.join(deltas_dir, f"code_blobs_{ts}.parquet")
        LOG.info(f"Writing Parquet delta → {delta_file}")
        write_parquet_rows(parquet_rows, delta_file, compression=args.parquet_compression)

    # Write tombstones
    wrote_tombs = False
    if tomb_records_code:
        LOG.info(f"Appending {len(tomb_records_code)} tombstones → {tomb_code}")
        append_jsonl(tomb_code, tomb_records_code)
        wrote_tombs = True
    if tomb_records_logs:
        LOG.info(f"Appending {len(tomb_records_logs)} tombstones → {tomb_logs}")
        append_jsonl(tomb_logs, tomb_records_logs)
        wrote_tombs = True

    # Gzip tombstones if requested
    if gzip_tombs and wrote_tombs:
        if os.path.exists(tomb_code):
            LOG.info(f"Gzipping tombstones → {tomb_code}.gz")
            gzip_rewrite(tomb_code, tomb_code + ".gz")
        if os.path.exists(tomb_logs):
            LOG.info(f"Gzipping tombstones → {tomb_logs}.gz")
            gzip_rewrite(tomb_logs, tomb_logs + ".gz")

    LOG.info(f"UPDATE complete: changed_files={changed}, deleted_marked={deleted_marked}")


def cmd_compact(args):
    if pa is None or pq is None:
        raise SystemExit("pyarrow is required for compaction")
    base = args.parquet
    deltas_dir = args.deltas_dir or os.path.dirname(base) or "."
    files = list_parquet_deltas(base, deltas_dir)
    if not files:
        LOG.info("No Parquet files found to compact.")
        return
    tmp_out = base + ".tmp"
    LOG.info(f"Compacting {len(files)} files → {tmp_out}")
    first = pq.ParquetFile(files[0])
    schema = first.schema_arrow
    writer = pq.ParquetWriter(tmp_out, schema=schema, compression=args.parquet_compression)
    try:
        for f in files:
            LOG.info(f" + {os.path.basename(f)}")
            pf = pq.ParquetFile(f)
            for batch in pf.iter_batches():
                tbl = pa.Table.from_batches([batch], schema=schema)
                writer.write_table(tbl)
    finally:
        writer.close()
    os.replace(tmp_out, base)
    removed = 0
    for f in files[1:]:
        try:
            os.remove(f)
            removed += 1
        except Exception as e:
            LOG.warning(f"Failed to remove {f}: {e}")
    LOG.info(
        f"COMPACT complete: merged={len(files)} removed_deltas={removed} → base={os.path.basename(base)}"
    )


def cmd_query(args):
    if duckdb is None:
        raise SystemExit("duckdb is required for query mode")
    con = duckdb.connect(database=":memory:")
    con.execute(f"ATTACH '{args.sqlite}' AS meta (TYPE SQLITE)")
    base = args.parquet
    deltas_dir = args.deltas_dir or os.path.dirname(base) or "."
    files = list_parquet_deltas(base, deltas_dir)
    if not files:
        raise SystemExit("No Parquet files available for query.")
    parquet_list_sql = ", ".join([f"'{f}'" for f in files])
    default_sql = f"""
        SELECT
          m.path, m.language, m.lines,
          LENGTH(c.content) AS code_size,
          SUBSTR(c.content, 1, 160) AS snippet
        FROM meta.code_metadata m
        JOIN read_parquet([{parquet_list_sql}]) c
          ON m.parquet_row_id = c.parquet_row_id
        WHERE m.deleted_at IS NULL
        ORDER BY m.lines DESC
        LIMIT 20;
    """
    sql = args.sql if args.sql else default_sql
    LOG.debug("Executing SQL:\n" + sql)
    df = con.execute(sql).fetchdf()
    print(df.to_json(orient="records", force_ascii=False, indent=2))


def iter_jsonl(path: str):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def summarize_tombstones(paths: List[str]) -> dict:
    total = 0
    by_cat, by_day, paths_set = {}, {}, set()
    oldest, newest = None, None
    for p in paths:
        for rec in iter_jsonl(p):
            total += 1
            paths_set.add(rec.get("path"))
            cat = rec.get("category") or "unknown"
            by_cat[cat] = by_cat.get(cat, 0) + 1
            ts = rec.get("ts")
            if ts:
                day = ts[:10]
                by_day[day] = by_day.get(day, 0) + 1
                if oldest is None or ts < oldest:
                    oldest = ts
                if newest is None or ts > newest:
                    newest = ts
    return {
        "total": total,
        "unique_paths": len(paths_set),
        "by_category": by_cat,
        "by_day": by_day,
        "oldest": oldest,
        "newest": newest,
    }


def prune_tombstones(path: str, before_date: date) -> tuple:
    """Rewrite JSONL in place keeping only records with ts >= before_date. Returns (kept, pruned)."""
    if not os.path.exists(path):
        return (0, 0)
    kept, pruned = 0, 0
    tmp = path + ".tmp"
    cutoff = before_date.strftime("%Y-%m-%d")
    with open(path, "r", encoding="utf-8") as fin, open(tmp, "w", encoding="utf-8") as fout:
        for line in fin:
            try:
                rec = json.loads(line)
                ts = (rec.get("ts") or "")[:10]
                if ts and ts < cutoff:
                    pruned += 1
                    continue
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                kept += 1
            except Exception:
                # keep unparsable
                fout.write(line)
                kept += 1
    os.replace(tmp, path)
    return (kept, pruned)


def cmd_vacuum(args):
    tomb_code = args.tombstones_code
    tomb_logs = args.tombstones_logs
    do_summary = args.summary
    do_gzip = args.gzip_tombstones
    dry_run = args.dry_run
    before = parse_date_ymd(args.before) if args.before else None

    paths = [p for p in [tomb_code, tomb_logs] if os.path.exists(p)]

    if do_summary:
        summary = summarize_tombstones(paths)
        print(json.dumps({"summary": summary}, indent=2))
        if before is None:
            return  # only summarize

    if before is None:
        raise SystemExit("--before YYYY-MM-DD is required unless --summary is provided.")

    # Prune
    results = {}
    for p in paths:
        if dry_run:
            sim_kept = sim_pruned = 0
            cutoff = before.strftime("%Y-%m-%d")
            for rec in iter_jsonl(p):
                ts = (rec.get("ts") or "")[:10]
                if ts and ts < cutoff:
                    sim_pruned += 1
                else:
                    sim_kept += 1
            results[p] = {"kept": sim_kept, "pruned": sim_pruned, "dry_run": True}
        else:
            kept, pruned = prune_tombstones(p, before)
            results[p] = {"kept": kept, "pruned": pruned, "dry_run": False}

    print(json.dumps({"vacuum": results, "cutoff": before.strftime("%Y-%m-%d")}, indent=2))

    # Regzip
    if do_gzip and not dry_run:
        for p in [tomb_code, tomb_logs]:
            if os.path.exists(p):
                LOG.info(f"Gzipping tombstones → {p}.gz")
                gzip_rewrite(p, p + ".gz")


def cmd_verify(args):
    """Check that all active parquet_row_id are present in Parquet (base + deltas)."""
    if duckdb is None:
        raise SystemExit("duckdb is required for verify mode")
    con = duckdb.connect(database=":memory:")
    con.execute(f"ATTACH '{args.sqlite}' AS meta (TYPE SQLITE)")
    base = args.parquet
    deltas_dir = args.deltas_dir or os.path.dirname(base) or "."
    files = list_parquet_deltas(base, deltas_dir)
    if not files:
        raise SystemExit("No Parquet files available for verify.")
    parquet_list_sql = ", ".join([f"'{f}'" for f in files])
    counts = con.execute(
        f"""
        WITH active AS (
          SELECT parquet_row_id FROM meta.code_metadata WHERE deleted_at IS NULL
        ),
        present AS (
          SELECT DISTINCT parquet_row_id FROM read_parquet([{parquet_list_sql}])
        )
        SELECT
          (SELECT COUNT(*) FROM active) AS active_count,
          (SELECT COUNT(*) FROM present) AS present_count,
          (SELECT COUNT(*) FROM active a
             WHERE a.parquet_row_id NOT IN (SELECT parquet_row_id FROM present)) AS missing_count
    """
    ).fetchone()
    missing_ids = con.execute(
        f"""
        SELECT parquet_row_id
        FROM meta.code_metadata
        WHERE deleted_at IS NULL
          AND parquet_row_id NOT IN (SELECT parquet_row_id FROM read_parquet([{parquet_list_sql}]))
        ORDER BY parquet_row_id
        LIMIT 50
    """
    ).fetchall()
    print(
        json.dumps(
            {
                "active_count": counts[0],
                "present_count": counts[1],
                "missing_count": counts[2],
                "sample_missing_row_ids": [r[0] for r in missing_ids],
            },
            indent=2,
        )
    )


# ---------------- CLI ----------------


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Hybrid code archive orchestrator (JSONL + SQLite + Parquet + Tombstones)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common(p):
        p.add_argument("--root", default=".", help="Root folder to scan (for build/update)")
        p.add_argument(
            "--exts",
            nargs="*",
            help="Extensions to include (e.g., py,js,ts,json,yaml). Default: a sane set.",
        )
        p.add_argument(
            "--allow-globs",
            nargs="*",
            help="Only include files matching any of these globs (relative to root).",
        )
        p.add_argument(
            "--deny-globs",
            nargs="*",
            help="Exclude files matching any of these globs (relative to root).",
        )
        p.add_argument(
            "--workers", default="1", help="Number of worker threads for file I/O (int or 'auto')."
        )
        p.add_argument("--jsonl", default="code_archive.jsonl", help="Path to JSONL (append-only).")
        p.add_argument("--sqlite", default="metadata.sqlite", help="Path to SQLite metadata DB.")
        p.add_argument("--parquet", default="code_blobs.parquet", help="Path to base Parquet file.")
        p.add_argument(
            "--deltas-dir", default=".", help="Directory where Parquet delta files live."
        )
        p.add_argument(
            "--parquet-compression",
            default="zstd",
            choices=["zstd", "snappy", "gzip", "none"],
            help="Parquet compression codec.",
        )
        p.add_argument(
            "-v", "--verbose", action="count", default=0, help="Increase verbosity (-v, -vv)."
        )
        p.add_argument("--logfile", default="archive_manager.log", help="Log file path (rotating).")

    p_build = sub.add_parser("build", help="Fresh build of JSONL + SQLite + base Parquet")
    add_common(p_build)
    p_build.add_argument(
        "--gzip-jsonl", action="store_true", help="Also write code_archive.jsonl.gz"
    )
    p_build.add_argument(
        "--force", action="store_true", help="Overwrite existing outputs if present."
    )
    p_build.set_defaults(func=cmd_build)

    p_update = sub.add_parser(
        "update",
        help="Detect changes and write JSONL appends + SQLite upserts + Parquet delta (+ tombstones on delete)",
    )
    add_common(p_update)
    p_update.add_argument(
        "--gzip-jsonl", action="store_true", help="Regenerate compressed JSONL after append."
    )
    p_update.add_argument(
        "--track-deletes",
        action="store_true",
        help="Mark missing files as deleted in SQLite and write tombstones.",
    )
    p_update.add_argument(
        "--tombstones-code",
        default="tombstones_code.jsonl",
        help="JSONL for tombstones (code/docs/tests/configs).",
    )
    p_update.add_argument(
        "--tombstones-logs",
        default="tombstones_logs.jsonl",
        help="JSONL for tombstones (logs/test logs).",
    )
    p_update.add_argument(
        "--gzip-tombstones",
        action="store_true",
        help="Also (re)generate tombstones_code.jsonl.gz and tombstones_logs.jsonl.gz if anything was appended.",
    )
    p_update.set_defaults(func=cmd_update)

    p_compact = sub.add_parser(
        "compact", help="Merge Parquet base + deltas into a fresh optimized base"
    )
    add_common(p_compact)
    p_compact.set_defaults(func=cmd_compact)

    p_query = sub.add_parser("query", help="Run DuckDB SQL joining SQLite + Parquet")
    add_common(p_query)
    p_query.add_argument(
        "--sql", help="SQL string to execute (DuckDB). If omitted, runs a sample query."
    )
    p_query.set_defaults(func=cmd_query)

    p_verify = sub.add_parser(
        "verify",
        help="Check referential integrity between SQLite and Parquet row_ids (active rows only)",
    )
    add_common(p_verify)
    p_verify.set_defaults(func=cmd_verify)

    p_vacuum = sub.add_parser("vacuum", help="Summarize and prune tombstone JSONL streams")
    p_vacuum.add_argument(
        "--tombstones-code", default="tombstones_code.jsonl", help="Path to code tombstones JSONL."
    )
    p_vacuum.add_argument(
        "--tombstones-logs", default="tombstones_logs.jsonl", help="Path to logs tombstones JSONL."
    )
    p_vacuum.add_argument(
        "--before", help="Prune tombstones with ts < YYYY-MM-DD (UTC). If omitted, only summarize."
    )
    p_vacuum.add_argument(
        "--summary", action="store_true", help="Print JSON summary of tombstones."
    )
    p_vacuum.add_argument(
        "--dry-run", action="store_true", help="Simulate pruning without modifying files."
    )
    p_vacuum.add_argument(
        "--gzip-tombstones",
        action="store_true",
        help="Regenerate .gz after pruning (when not dry-run).",
    )
    p_vacuum.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity (-v, -vv)."
    )
    p_vacuum.add_argument(
        "--logfile", default="archive_manager.log", help="Log file path (rotating)."
    )
    p_vacuum.set_defaults(func=cmd_vacuum)

    args = parser.parse_args(argv)
    setup_logging(getattr(args, "verbose", 0), getattr(args, "logfile", "archive_manager.log"))
    if hasattr(args, "parquet_compression") and args.parquet_compression == "none":
        args.parquet_compression = None
    args.func(args)


if __name__ == "__main__":
    main()
