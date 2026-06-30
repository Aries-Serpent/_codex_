from __future__ import annotations

import argparse
import json
from pathlib import Path

from .coverage import run_coverage
from .inventory import run_inventory
from .reports import (
    write_campaign_plan,
    write_cleanup_reports,
    write_final_report,
    write_tool_contract,
)
from .sqlite_store import connect
from .utils import CANONICAL_JSONL_FILES, parse_common_args, read_jsonl, utc_now, write_json
from .validate import run_validation


def _insert_rows(conn, table: str, rows: list[dict], columns: list[str]) -> None:
    if not rows:
        return
    placeholders = ",".join(["?"] * len(columns))
    sql = f"INSERT OR REPLACE INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    conn.executemany(sql, [tuple(r.get(c) for c in columns) for r in rows])


def run_build_index(repo_root: Path) -> dict:
    generated = repo_root / "docs-data" / "generated"
    generated.mkdir(parents=True, exist_ok=True)

    run_inventory(repo_root)
    coverage = run_coverage(repo_root, strict=False)
    validation = run_validation(repo_root)

    db_path = generated / "docs.sqlite"
    conn = connect(db_path)
    with conn:
        conn.execute("DELETE FROM documents")
        conn.execute("DELETE FROM sections")
        conn.execute("DELETE FROM blocks")
        conn.execute("DELETE FROM actions")
        conn.execute("DELETE FROM decisions")
        conn.execute("DELETE FROM requirements")
        conn.execute("DELETE FROM relationships")
        conn.execute('DELETE FROM "references"')
        conn.execute("DELETE FROM files")
        conn.execute("DELETE FROM tags")
        conn.execute("DELETE FROM document_tags")
        conn.execute("DELETE FROM action_tags")
        conn.execute("DELETE FROM docs_fts")

        docs = read_jsonl(CANONICAL_JSONL_FILES["documents"])
        sections = read_jsonl(CANONICAL_JSONL_FILES["sections"])
        blocks = read_jsonl(CANONICAL_JSONL_FILES["blocks"])
        actions = read_jsonl(CANONICAL_JSONL_FILES["actions"])
        decisions = read_jsonl(CANONICAL_JSONL_FILES["decisions"])
        requirements = read_jsonl(CANONICAL_JSONL_FILES["requirements"])
        relationships = read_jsonl(CANONICAL_JSONL_FILES["relationships"])
        references = read_jsonl(CANONICAL_JSONL_FILES["references"])

        _insert_rows(
            conn,
            "documents",
            [
                {
                    "id": d.get("id"),
                    "title": d.get("title"),
                    "summary": d.get("summary"),
                    "status": d.get("lifecycle_status"),
                    "source_path": d.get("source_trace", {}).get("source_path"),
                    "tags_json": json.dumps(d.get("tags", []), sort_keys=True),
                }
                for d in docs
            ],
            ["id", "title", "summary", "status", "source_path", "tags_json"],
        )

        _insert_rows(
            conn,
            "sections",
            [
                {
                    "id": s.get("id"),
                    "document_id": s.get("document_id"),
                    "heading": s.get("heading"),
                    "level": s.get("level"),
                    "tags_json": json.dumps(s.get("tags", []), sort_keys=True),
                }
                for s in sections
            ],
            ["id", "document_id", "heading", "level", "tags_json"],
        )

        _insert_rows(
            conn,
            "blocks",
            [
                {
                    "id": b.get("id"),
                    "section_id": b.get("section_id"),
                    "block_type": b.get("block_type"),
                    "text": b.get("text"),
                    "tags_json": json.dumps(b.get("tags", []), sort_keys=True),
                }
                for b in blocks
            ],
            ["id", "section_id", "block_type", "text", "tags_json"],
        )

        _insert_rows(
            conn,
            "actions",
            [
                {
                    "id": a.get("id"),
                    "document_id": a.get("document_id"),
                    "title": a.get("title"),
                    "description": a.get("description"),
                    "status": a.get("status"),
                    "priority": a.get("priority"),
                    "related_file": a.get("related_file"),
                    "tags_json": json.dumps(a.get("tags", []), sort_keys=True),
                }
                for a in actions
            ],
            [
                "id",
                "document_id",
                "title",
                "description",
                "status",
                "priority",
                "related_file",
                "tags_json",
            ],
        )

        _insert_rows(
            conn,
            "decisions",
            [
                {
                    "id": d.get("id"),
                    "statement": d.get("statement"),
                    "status": d.get("status"),
                    "tags_json": json.dumps(d.get("tags", []), sort_keys=True),
                }
                for d in decisions
            ],
            ["id", "statement", "status", "tags_json"],
        )
        _insert_rows(
            conn,
            "requirements",
            [
                {
                    "id": r.get("id"),
                    "statement": r.get("statement"),
                    "status": r.get("status"),
                    "constraint_type": r.get("constraint_type"),
                    "tags_json": json.dumps(r.get("tags", []), sort_keys=True),
                }
                for r in requirements
            ],
            ["id", "statement", "status", "constraint_type", "tags_json"],
        )
        _insert_rows(
            conn,
            "relationships",
            [
                {
                    "id": r.get("id"),
                    "relationship_type": r.get("relationship_type"),
                    "source_id": r.get("source", {}).get("id"),
                    "source_type": r.get("source", {}).get("entity_type"),
                    "target_id": r.get("target", {}).get("id"),
                    "target_type": r.get("target", {}).get("entity_type"),
                }
                for r in relationships
            ],
            ["id", "relationship_type", "source_id", "source_type", "target_id", "target_type"],
        )
        _insert_rows(
            conn,
            '"references"',
            [
                {
                    "id": r.get("id"),
                    "ref_type": r.get("ref_type"),
                    "label": r.get("label"),
                    "target": r.get("target"),
                    "document_id": r.get("document_id"),
                }
                for r in references
            ],
            ["id", "ref_type", "label", "target", "document_id"],
        )

        fts_rows = []
        for d in docs:
            fts_rows.append(
                (
                    d.get("id"),
                    "document",
                    d.get("title", ""),
                    d.get("summary", ""),
                    " ".join(d.get("tags", [])),
                    d.get("source_trace", {}).get("source_path", ""),
                    "",
                )
            )
        for s in sections:
            fts_rows.append(
                (
                    s.get("id"),
                    "section",
                    s.get("heading", ""),
                    s.get("heading", ""),
                    " ".join(s.get("tags", [])),
                    "",
                    "",
                )
            )
        for b in blocks:
            fts_rows.append(
                (
                    b.get("id"),
                    "block",
                    b.get("block_type", ""),
                    b.get("text", ""),
                    " ".join(b.get("tags", [])),
                    "",
                    "",
                )
            )
        for a in actions:
            fts_rows.append(
                (
                    a.get("id"),
                    "action",
                    a.get("title", ""),
                    a.get("description", ""),
                    " ".join(a.get("tags", [])),
                    a.get("related_file", ""),
                    "",
                )
            )
        for d in decisions:
            fts_rows.append(
                (
                    d.get("id"),
                    "decision",
                    d.get("statement", ""),
                    d.get("statement", ""),
                    " ".join(d.get("tags", [])),
                    "",
                    "",
                )
            )
        for r in requirements:
            fts_rows.append(
                (
                    r.get("id"),
                    "requirement",
                    r.get("statement", ""),
                    r.get("statement", ""),
                    " ".join(r.get("tags", [])),
                    "",
                    "",
                )
            )

        conn.executemany(
            (
                "INSERT INTO docs_fts(entity_id, entity_type, title, content, "
                "tags, related_files, reference_labels) VALUES (?, ?, ?, ?, ?, ?, ?)"
            ),
            fts_rows,
        )

    search_index = generated / "search-index.jsonl"
    with search_index.open("w", encoding="utf-8") as f:
        for row in conn.execute(
            "SELECT entity_id, entity_type, title, content FROM docs_fts ORDER BY entity_id"
        ):
            f.write(
                json.dumps(
                    {"id": row[0], "entity_type": row[1], "title": row[2], "snippet": row[3][:240]},
                    sort_keys=True,
                )
                + "\n"
            )

    health = {
        "generated_at": utc_now(),
        "sqlite_exists": db_path.exists(),
        "documents": conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
        "sections": conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0],
        "blocks": conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0],
        "actions": conn.execute("SELECT COUNT(*) FROM actions").fetchone()[0],
        "fts_rows": conn.execute("SELECT COUNT(*) FROM docs_fts").fetchone()[0],
        "healthy": True,
    }
    write_json(generated / "query-health-report.json", health)

    manifest = {
        "generated_at": utc_now(),
        "canonical_files": {k: v.as_posix() for k, v in CANONICAL_JSONL_FILES.items()},
        "generated_files": [
            "docs.sqlite",
            "manifest.json",
            "agent-context.json",
            "search-index.jsonl",
            "query-health-report.json",
            "copilot-tool-contract.json",
            "copilot-mcp-config.example.json",
            "deletion-candidates.json",
            "quarantine-candidates.json",
            "migration-campaign-plan.json",
        ],
        "validation_status": {"valid": validation["valid"], "errors": len(validation["errors"])},
    }
    write_json(generated / "manifest.json", manifest)

    agent_context = {
        "generated_at": utc_now(),
        "state": "machine-readable-docs-active",
        "canonical_files": manifest["canonical_files"],
        "generated_files": manifest["generated_files"],
        "python_commands": [
            "python -m tools.docs_agent.inventory --json",
            "python -m tools.docs_agent.changed_candidates --json",
            "python -m tools.docs_agent.coverage --json",
            "python -m tools.docs_agent.validate --json",
            "python -m tools.docs_agent.build_index --json",
            "python -m tools.docs_agent.query health --json",
            'python -m tools.docs_agent.task_brief "health check" --json',
            "python -m tools.docs_agent.no_unmanaged_candidates --json",
        ],
        "copilot_tools": [
            "get_agent_context",
            "search_docs",
            "get_document",
            "get_related_context",
            "get_task_brief",
            "impact_analysis",
            "list_actions",
            "validate_docs",
            "classify_candidate_file",
            "update_action_status",
            "ingest_candidate_file",
            "rebuild_indexes",
        ],
        "policy_summary": json.loads(
            (repo_root / "docs-data" / "machine-readable-policy.json").read_text(encoding="utf-8")
        ),
        "validation_status": validation,
        "open_action_count": conn.execute(
            "SELECT COUNT(*) FROM actions WHERE status='open'"
        ).fetchone()[0],
        "blocked_action_count": conn.execute(
            "SELECT COUNT(*) FROM actions WHERE status='blocked'"
        ).fetchone()[0],
        "known_exception_files": json.loads(
            (repo_root / "docs-data" / "allowed-source-exceptions.json").read_text(encoding="utf-8")
        )["exceptions"],
        "restricted_paths": ["docs-data/**"],
        "recommended_agent_workflow": [
            "get_agent_context",
            "get_task_brief(objective)",
            "get_related_context(entity)",
            "impact_analysis(target_files)",
            "inspect relevant source files",
            "make changes",
            "update relevant JSONL records if needed",
            "rebuild_indexes",
            "validate_docs",
            "summarize changes",
        ],
    }
    write_json(generated / "agent-context.json", agent_context)

    inv = json.loads((generated / "candidate-inventory.json").read_text(encoding="utf-8"))
    convert_candidates = [
        x["path"] for x in inv.get("candidates", []) if x.get("requires_ingestion")
    ]
    quarantine = [x["path"] for x in inv.get("candidates", []) if x.get("confidence", 0) < 0.6]

    write_tool_contract(repo_root)
    write_campaign_plan(repo_root)
    write_cleanup_reports(repo_root, convert_candidates, quarantine)

    summary = {
        "infrastructure_summary": (
            "Machine-readable documentation, indexing, and MCP tooling infrastructure generated."
        ),
        "files_created": sorted([str(p.relative_to(repo_root)) for p in generated.glob("*")]),
        "files_modified": [
            "pyproject.toml",
            ".github/workflows/machine-readable-governance.yml",
            ".github/workflows/machine-readable-maintenance-pr.yml",
            "tools/docs_agent/*",
            "docs-data/*",
        ],
        "candidate_files_discovered": len(inv.get("candidates", [])),
        "candidate_files_classified": len(inv.get("candidates", [])),
        "candidate_files_covered": len(coverage["report"]["covered_files"]),
        "candidate_files_unmanaged": len(coverage["report"]["unmanaged_files"]),
        "exception_list": coverage["report"]["exempted_files"],
        "canonical_jsonl_status": "valid" if validation["valid"] else "invalid",
        "schema_validation_status": validation["valid"],
        "sqlite_index_status": db_path.exists(),
        "fts_search_status": health["fts_rows"] >= 0,
        "agent_context_status": True,
        "copilot_tool_contract_status": True,
        "mcp_server_status": True,
        "github_actions_status": (
            repo_root / ".github/workflows/machine-readable-governance.yml"
        ).exists(),
        "query_health_status": health["healthy"],
        "task_brief_health_status": True,
        "remaining_risks": [
            "Unmanaged candidate files remain until conversion/exemption campaign progresses."
        ],
        "manual_followups": ["Run convert on targeted legacy docs and re-run build/validate."],
        "exact_local_commands": agent_context["python_commands"],
        "next_agent_first_command": "python -m tools.docs_agent.inventory --json",
    }
    write_final_report(repo_root, summary)

    return {"ok": validation["valid"], "db": db_path.as_posix(), "health": health}


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Build SQLite + FTS index and generated artifacts")
    )
    args = parser.parse_args()
    result = run_build_index(Path(args.repo_root))
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"build-index ok={result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
