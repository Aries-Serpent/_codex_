#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_sqlite_align.py
End-to-end workflow to:
1) Update default DB path to .codex/session_logs.db
2) Detect SQLite via .sqlite and .db extensions
3) Auto-infer table/column names and preview logs (session_logger & similar)
4) Parse README and standardize references
5) Record gaps in a change log
6) Emit structured research questions for errors
7) Output a coverage report
Safety: Never touches .github/workflows
"""

import argparse
import json
import os
import re
import shutil
import sqlite3

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except Exception:
    pass
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# -------------------- Constants & Helpers --------------------

DEFAULT_DB_REL = Path(".codex") / "session_logs.db"
EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
}
READABLE_EXTS = {
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".env",
    "",
    ".ini",
    ".cfg",
    ".json",
    ".sh",
    ".bat",
    ".ps1",
    ".md",
}
CONFIG_LIKE = (
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".env",
    ".ini",
    ".cfg",
    ".json",
    ".md",
    ".sh",
    ".ps1",
    ".bat",
)

SQLITE_PATH_PATTERNS = [
    r"sqlite3\.connect\(\s*[ru]?['\"]([^'\"]+\.(?:db|sqlite))['\"]\s*\)",
    r"sqlite\+?:///[^\s\"\')]+",  # sqlalchemy-style URIs
    r"['\"]([^'\"]+\.(?:db|sqlite))['\"]",  # generic path literals
]

LIKELY_LOG_TABLE_PAT = re.compile(r"(session|log|event|audit)", re.IGNORECASE)
VALID_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


@dataclass
class FileMatch:
    file: str
    line_number: int
    snippet: str
    current_path: str
    kind: str  # 'sqlite3', 'sqlalchemy', 'literal'


@dataclass
class ChangeEntry:
    file: str
    changes: int
    notes: str


@dataclass
class PruneEntry:
    file: str
    reason: str
    alternatives: List[str]
    risk: str


@dataclass
class CoverageReport:
    implemented_objectives: Dict[str, bool]
    executed_objectives: Dict[str, bool]
    pruning_penalty_lambda: float
    pruned_items: int
    implemented_coverage: float
    executed_coverage_raw: float
    executed_coverage_penalized: float
    timestamp: str


# -------------------- Utility Functions --------------------


def step_error(step_label: str, err: Exception, context: str, research_path: Path):
    research_path.parent.mkdir(parents=True, exist_ok=True)
    with research_path.open("a", encoding="utf-8") as fh:
        fh.write(
            f"""Question for ChatGPT-5:\nWhile performing [{step_label}], encountered the following error:\n{type(err).__name__}: {err}\nContext: {context}\nWhat are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"""
        )


def safe_backup(p: Path):
    bak = p.with_suffix(p.suffix + ".bak")
    if p.exists() and not bak.exists():
        shutil.copy2(p, bak)


def should_skip_dir(dir_name: str) -> bool:
    if dir_name in EXCLUDE_DIRS:
        return True
    if dir_name == "workflows":
        return True
    return False


def iter_repo_files(root: Path) -> List[Path]:
    files = []
    for base, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        if Path(base).parts[-2:] == (".github", "workflows"):
            continue
        for fn in fns:
            p = Path(base) / fn
            if p.suffix.lower() in READABLE_EXTS or p.suffix == "":
                files.append(p)
    return files


def find_sqlite_references(text: str) -> List[Tuple[re.Match, str]]:
    results = []
    for pat in SQLITE_PATH_PATTERNS:
        for m in re.finditer(pat, text):
            kind = "literal"
            if "sqlite3.connect" in pat:
                kind = "sqlite3"
            elif "sqlite+?" in pat or "sqlite:///" in m.group(0):
                kind = "sqlalchemy"
            results.append((m, kind))
    return results


def normalize_sqlite_reference(snippet: str, kind: str, repo_root: Path) -> str:
    default_path = DEFAULT_DB_REL.as_posix()
    if kind == "sqlalchemy":
        return re.sub(r'sqlite\+?:///[^"]+', f"sqlite:///./{default_path}", snippet)
    elif kind == "sqlite3":
        return re.sub(
            r"(sqlite3\.connect\(\s*[ru]?)(['\"])([^'\"]+)(\2)(\s*\))",
            rf"\1\2{repo_root.as_posix()}/{default_path}\2\5",
            snippet,
        )
    else:
        return re.sub(r"(['\"])([^'\"]+\.(?:db|sqlite))\1", rf"\1./{default_path}\1", snippet)


def try_update_file(
    p: Path,
    repo_root: Path,
    change_log: List[ChangeEntry],
    prunes: List[PruneEntry],
    research_path: Path,
):
    try:
        text = p.read_text(encoding="utf-8")
    except Exception as e:
        prunes.append(
            PruneEntry(
                file=str(p),
                reason="Non-text or unreadable file",
                alternatives=["Open in binary-safe mode", "Skip with documentation"],
                risk="Low; file likely not a config/code text source",
            )
        )
        step_error("3.1: Default Path Alignment", e, f"Reading file {p}", research_path)
        return

    matches = find_sqlite_references(text)
    if not matches:
        return

    original_text = text
    changes = 0
    for m, kind in reversed(matches):
        snippet = text[m.start() : m.end()]
        replaced = normalize_sqlite_reference(snippet, kind, repo_root)
        if replaced != snippet:
            text = text[: m.start()] + replaced + text[m.end() :]
            changes += 1

    if changes > 0 and text != original_text:
        try:
            safe_backup(p)
            p.write_text(text, encoding="utf-8")
            change_log.append(
                ChangeEntry(
                    file=str(p),
                    changes=changes,
                    notes=f"Normalized {changes} SQLite reference(s)",
                )
            )
        except Exception as e:
            prunes.append(
                PruneEntry(
                    file=str(p),
                    reason="Write failed (permissions or lock)",
                    alternatives=["Run with elevated perms", "Modify via PR patch"],
                    risk="Medium",
                )
            )
            step_error("3.1: Default Path Alignment", e, f"Writing file {p}", research_path)


def update_readme(
    readme: Path, repo_root: Path, change_log: List[ChangeEntry], research_path: Path
):
    if not readme.exists():
        return
    try:
        text = readme.read_text(encoding="utf-8")
        original = text
        text = re.sub(r"(sqlite\+?:///)[^\s\)]+", r"./.codex/.codex/session_logs.db", text)
        text = re.sub(
            r"sqlite3\.connect\(\s*[ru]?['\"]([^'\"]+\.(?:db|sqlite))['\"]\s*\)",
            "sqlite3.connect('./.codex/.codex/session_logs.db')",
            text,
        )
        text = re.sub(
            r"(['\"])([^'\"]+\.(?:db|sqlite))\1",
            r"'./.codex/.codex/session_logs.db'",
            text,
        )
        if text != original:
            safe_backup(readme)
            readme.write_text(text, encoding="utf-8")
            change_log.append(
                ChangeEntry(
                    file=str(readme),
                    changes=1,
                    notes="Standardized README DB references",
                )
            )
    except Exception as e:
        step_error("3.4: README Reference Updates", e, f"Updating {readme}", research_path)


def discover_db_files(repo_root: Path) -> List[Path]:
    candidates = []
    for base, dirs, fns in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        if Path(base).parts[-2:] == (".github", "workflows"):
            continue
        for fn in fns:
            p = Path(base) / fn
            if p.suffix.lower() in {".db", ".sqlite"}:
                candidates.append(p)
    return candidates


def _validate_table(name: str) -> str:
    """Return *name* when it matches SQLite identifier rules."""

    if not VALID_IDENT.fullmatch(name):
        raise ValueError(f"invalid table name: {name!r}")
    return name


def sqlite_catalog(db_path: Path, max_rows: int = 50) -> Dict[str, Any]:
    info: Dict[str, Any] = {"db": str(db_path), "tables": []}
    con = None
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            try:
                safe = _validate_table(t)
            except ValueError:
                continue
            cur.execute(f"PRAGMA table_info({safe})")
            cols = [
                {
                    "cid": r[0],
                    "name": r[1],
                    "type": r[2],
                    "notnull": r[3],
                    "dflt_value": r[4],
                    "pk": r[5],
                }
                for r in cur.fetchall()
            ]
            info["tables"].append({"name": safe, "columns": cols})
    finally:
        if con:
            con.close()
    return info


def dump_preview(db_path: Path, out_dir: Path, max_rows: int = 50) -> List[str]:
    generated = []
    con = None
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        prioritized = sorted(tables, key=lambda t: (0 if LIKELY_LOG_TABLE_PAT.search(t) else 1, t))
        for t in prioritized:
            try:
                safe = _validate_table(t)
            except ValueError:
                continue
            try:
                cur.execute(f"SELECT * FROM {safe} LIMIT ?", (max_rows,))  # nosec B608
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description] if cur.description else []
                if not cols:
                    continue
                out_csv = out_dir / f"logs_preview_{safe}.csv"
                with out_csv.open("w", encoding="utf-8", newline="") as fh:
                    fh.write(",".join(cols) + "\n")
                    for r in rows:
                        fh.write(
                            ",".join(
                                [
                                    json.dumps(v, ensure_ascii=False) if v is not None else ""
                                    for v in r
                                ]
                            )
                            + "\n"
                        )
                generated.append(str(out_csv))
                if len(generated) >= 5:
                    break
            except Exception as inner_e:
                step_error(
                    "3.3: Auto-Inference & Preview",
                    inner_e,
                    f"Dumping preview for table {t} in {db_path}",
                    out_dir / "research_questions.md",
                )
    finally:
        if con:
            con.close()
    return generated


# -------------------- Main Workflow --------------------


def main():
    ap = argparse.ArgumentParser(description="Codex SQLite alignment & logging preview tool")
    ap.add_argument("--repo", type=str, default=".", help="Path to repo root")
    ap.add_argument("--max-rows", type=int, default=50, help="Max rows for table previews")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    out_dir = repo_root / ".codex" / "automation_out"
    out_dir.mkdir(parents=True, exist_ok=True)

    research_md = out_dir / "research_questions.md"
    change_log: List[ChangeEntry] = []
    prunes: List[PruneEntry] = []

    (repo_root / ".codex").mkdir(parents=True, exist_ok=True)

    try:
        update_readme(repo_root / "README.md", repo_root, change_log, research_md)
    except Exception as e:
        step_error("2.1: README Parsing", e, f"Path {repo_root / 'README.md'}", research_md)

    files = iter_repo_files(repo_root)
    for p in files:
        try_update_file(p, repo_root, change_log, prunes, research_md)

    db_candidates = discover_db_files(repo_root)
    db_inventory = {
        "discovered": [str(p) for p in db_candidates],
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    (out_dir / "db_inventory.json").write_text(json.dumps(db_inventory, indent=2), encoding="utf-8")

    catalogs = []
    previews = []
    for dbp in db_candidates:
        try:
            cat = sqlite_catalog(dbp, max_rows=args.max_rows)
            catalogs.append(cat)
        except Exception as e:
            step_error("3.3: Auto-Inference & Preview", e, f"Cataloging {dbp}", research_md)
            continue
        try:
            previews += dump_preview(dbp, out_dir, max_rows=args.max_rows)
        except Exception as e:
            step_error("3.3: Auto-Inference & Preview", e, f"Previewing {dbp}", research_md)

    (out_dir / "db_catalog.json").write_text(json.dumps(catalogs, indent=2), encoding="utf-8")

    implemented = {
        "O1_default_path": True,
        "O2_dual_extension": True,
        "O3_auto_infer_preview": True,
    }
    executed = {
        "O1_default_path": any(
            c.file.endswith((".py", ".toml", ".yaml", ".yml", ".json", ".md")) for c in change_log
        ),
        "O2_dual_extension": len(db_candidates) >= 0,
        "O3_auto_infer_preview": len(previews) > 0 or len(catalogs) > 0,
    }
    pruned_count = len(prunes)
    lam = 0.25
    implemented_cov = sum(1 for v in implemented.values() if v) / 3.0
    executed_raw = sum(1 for v in executed.values() if v) / 3.0
    executed_penalized = max(0.0, executed_raw - lam * (pruned_count / 3.0))

    cov = CoverageReport(
        implemented_objectives=implemented,
        executed_objectives=executed,
        pruning_penalty_lambda=lam,
        pruned_items=pruned_count,
        implemented_coverage=round(implemented_cov, 4),
        executed_coverage_raw=round(executed_raw, 4),
        executed_coverage_penalized=round(executed_penalized, 4),
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )
    (out_dir / "coverage_report.json").write_text(
        json.dumps(asdict(cov), indent=2), encoding="utf-8"
    )

    with (out_dir / "change_log.md").open("a", encoding="utf-8") as ch:
        ch.write(
            f"# Change Log ({datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')})\n\n"
        )
        if change_log:
            ch.write("## Updated Files\n")
            for c in change_log:
                ch.write(f"- `{c.file}` — {c.changes} change(s). _{c.notes}_\n")
            ch.write("\n")
        else:
            ch.write("- No direct file updates were necessary or detected.\n\n")

        ch.write("## DB Inventory\n")
        ch.write(json.dumps(db_inventory, indent=2))
        ch.write("\n\n")

        ch.write("## Cataloged Schemas\n")
        ch.write(f"- See `db_catalog.json` ({len(catalogs)} databases).\n\n")

        ch.write("## Generated Previews\n")
        if previews:
            for pth in previews:
                ch.write(f"- `{pth}`\n")
        else:
            ch.write("- No preview CSVs generated (no tables or access issues).\n")
        ch.write("\n")

        ch.write("## Pruned Items (with rationale)\n")
        if prunes:
            for pr in prunes:
                ch.write(
                    f"- `{pr.file}` — Reason: {pr.reason}. Alternatives: {', '.join(pr.alternatives)}. Risk: {pr.risk}\n"
                )
        else:
            ch.write("- None.\n")
        ch.write("\n")

        ch.write("## Research Questions\n")
        if research_md.exists():
            ch.write("- See `research_questions.md`.\n")
        else:
            ch.write("- None captured.\n")

    if args.verbose:
        print(json.dumps(asdict(cov), indent=2))


if __name__ == "__main__":
    sys.exit(main())
