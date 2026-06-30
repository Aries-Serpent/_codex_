from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from .relationships import traverse_related
from .utils import parse_common_args


def _db(repo_root: Path) -> sqlite3.Connection:
    return sqlite3.connect(repo_root / "docs-data" / "generated" / "docs.sqlite")


def query_health(repo_root: Path) -> dict[str, Any]:
    p = repo_root / "docs-data" / "generated" / "query-health-report.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    with _db(repo_root) as conn:
        return {
            "healthy": True,
            "documents": conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
        }


def query_search(repo_root: Path, text: str, limit: int) -> dict[str, Any]:
    with _db(repo_root) as conn:
        rows = conn.execute(
            (
                "SELECT entity_id, entity_type, title, content "
                "FROM docs_fts WHERE docs_fts MATCH ? LIMIT ?"
            ),
            (text, limit),
        ).fetchall()
        if not rows:
            rows = conn.execute(
                (
                    "SELECT entity_id, entity_type, title, content FROM docs_fts "
                    "WHERE content LIKE ? OR title LIKE ? LIMIT ?"
                ),
                (f"%{text}%", f"%{text}%", limit),
            ).fetchall()
    return {
        "query": text,
        "results": [
            {
                "id": r[0],
                "entity_type": r[1],
                "title": r[2],
                "snippet": (r[3] or "")[:240],
                "relevance": 1.0,
            }
            for r in rows
        ],
    }


def query_document(repo_root: Path, document_id: str) -> dict[str, Any]:
    with _db(repo_root) as conn:
        doc = conn.execute(
            "SELECT id, title, summary, source_path FROM documents WHERE id=?", (document_id,)
        ).fetchone()
        sections = conn.execute(
            "SELECT id, heading, level FROM sections WHERE document_id=? ORDER BY level",
            (document_id,),
        ).fetchall()
        action_rows = conn.execute(
            "SELECT id, title, status FROM actions WHERE document_id=?", (document_id,)
        ).fetchall()
    return {
        "document": (
            None
            if not doc
            else {"id": doc[0], "title": doc[1], "summary": doc[2], "source_path": doc[3]}
        ),
        "sections": [{"id": s[0], "heading": s[1], "level": s[2]} for s in sections],
        "actions": [{"id": a[0], "title": a[1], "status": a[2]} for a in action_rows],
    }


def query_table(repo_root: Path, table: str, limit: int = 100) -> dict[str, Any]:
    with _db(repo_root) as conn:
        rows = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()
        cols = [d[0] for d in conn.execute(f"SELECT * FROM {table} LIMIT 1").description]
    return {"table": table, "rows": [dict(zip(cols, r)) for r in rows]}


def query_related(repo_root: Path, entity_id: str, depth: int) -> dict[str, Any]:
    with _db(repo_root) as conn:
        rels = conn.execute(
            (
                "SELECT id, relationship_type, source_id, source_type, "
                "target_id, target_type FROM relationships"
            )
        ).fetchall()
    rel_rows = [
        {
            "id": r[0],
            "relationship_type": r[1],
            "source_id": r[2],
            "source_type": r[3],
            "target_id": r[4],
            "target_type": r[5],
        }
        for r in rels
    ]
    return {"entity_id": entity_id, "paths": traverse_related(entity_id, rel_rows, depth)}


def query_impact(repo_root: Path, files: list[str]) -> dict[str, Any]:
    with _db(repo_root) as conn:
        docs = (
            conn.execute(
                "SELECT id, title, source_path FROM documents WHERE source_path IN ({})".format(
                    ",".join("?" * len(files)) if files else "''"
                ),
                tuple(files),
            ).fetchall()
            if files
            else []
        )
        doc_ids = [d[0] for d in docs]
        actions = []
        requirements = []
        decisions = []
        if doc_ids:
            q = ",".join("?" * len(doc_ids))
            actions = conn.execute(
                f"SELECT id, title, status FROM actions WHERE document_id IN ({q})", tuple(doc_ids)
            ).fetchall()
            requirements = conn.execute("SELECT id, statement, status FROM requirements").fetchall()
            decisions = conn.execute("SELECT id, statement, status FROM decisions").fetchall()
    return {
        "changed_files": files,
        "affected_documents": [{"id": d[0], "title": d[1], "source_path": d[2]} for d in docs],
        "affected_actions": [{"id": a[0], "title": a[1], "status": a[2]} for a in actions],
        "affected_decisions": [{"id": d[0], "statement": d[1], "status": d[2]} for d in decisions],
        "affected_requirements": [
            {"id": r[0], "statement": r[1], "status": r[2]} for r in requirements
        ],
        "required_checks": [
            "python -m tools.docs_agent.validate --json",
            "python -m tools.docs_agent.build_index --json",
        ],
    }


def main() -> int:
    parser = parse_common_args(argparse.ArgumentParser(description="Query docs sqlite index"))
    sub = parser.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("health")
    h.add_argument("--json", action="store_true")
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true")

    d = sub.add_parser("document")
    d.add_argument("document_id")
    d.add_argument("--json", action="store_true")

    sec = sub.add_parser("section")
    sec.add_argument("--limit", type=int, default=100)
    sec.add_argument("--json", action="store_true")

    act = sub.add_parser("actions")
    act.add_argument("--limit", type=int, default=100)
    act.add_argument("--json", action="store_true")

    dec = sub.add_parser("decisions")
    dec.add_argument("--limit", type=int, default=100)
    dec.add_argument("--json", action="store_true")

    req = sub.add_parser("requirements")
    req.add_argument("--limit", type=int, default=100)
    req.add_argument("--json", action="store_true")

    rel = sub.add_parser("related")
    rel.add_argument("entity_id")
    rel.add_argument("--depth", type=int, default=2)
    rel.add_argument("--json", action="store_true")

    imp = sub.add_parser("impact")
    imp.add_argument("files", nargs="*")
    imp.add_argument("--json", action="store_true")

    args = parser.parse_args()
    repo_root = Path(args.repo_root)
    if args.cmd == "health":
        result = query_health(repo_root)
    elif args.cmd == "search":
        result = query_search(repo_root, args.query, args.limit)
    elif args.cmd == "document":
        result = query_document(repo_root, args.document_id)
    elif args.cmd == "section":
        result = query_table(repo_root, "sections", args.limit)
    elif args.cmd == "actions":
        result = query_table(repo_root, "actions", args.limit)
    elif args.cmd == "decisions":
        result = query_table(repo_root, "decisions", args.limit)
    elif args.cmd == "requirements":
        result = query_table(repo_root, "requirements", args.limit)
    elif args.cmd == "related":
        result = query_related(repo_root, args.entity_id, args.depth)
    elif args.cmd == "impact":
        result = query_impact(repo_root, args.files)
    else:
        raise RuntimeError("unknown command")

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
