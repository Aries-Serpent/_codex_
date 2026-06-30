from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .actions import update_action_status as update_action_status_impl
from .build_index import run_build_index
from .convert import run_convert
from .query import query_document, query_impact, query_related, query_search, query_table
from .task_brief import run_task_brief
from .utils import classify_path, load_exceptions, load_policy
from .validate import run_validation


def get_agent_context(repo_root: Path) -> dict[str, Any]:
    p = repo_root / "docs-data" / "generated" / "agent-context.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def search_docs(
    repo_root: Path,
    query: str,
    entity_types: list[str] | None = None,
    statuses: list[str] | None = None,
    tags: list[str] | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    result = query_search(repo_root, query, limit)
    if entity_types:
        result["results"] = [r for r in result["results"] if r.get("entity_type") in entity_types]
    return result


def get_document(
    repo_root: Path,
    document_id: str,
    include_sections: bool = True,
    include_blocks: bool = True,
    include_actions: bool = True,
    include_relationships: bool = True,
) -> dict[str, Any]:
    doc = query_document(repo_root, document_id)
    if not include_sections:
        doc["sections"] = []
    if not include_actions:
        doc["actions"] = []
    return doc


def get_related_context(
    repo_root: Path, entity_type: str, entity_id: str, depth: int = 2
) -> dict[str, Any]:
    return query_related(repo_root, entity_id, depth)


def get_task_brief(
    repo_root: Path,
    objective: str,
    include_actions: bool = True,
    include_files: bool = True,
    include_decisions: bool = True,
    include_requirements: bool = True,
    include_validation: bool = True,
) -> dict[str, Any]:
    data = run_task_brief(repo_root, objective)
    if not include_actions:
        data["open_actions"] = []
        data["blocked_actions"] = []
    if not include_files:
        data["related_files"] = []
    if not include_decisions:
        data["known_decisions"] = []
    if not include_requirements:
        data["known_requirements"] = []
    if not include_validation:
        data["validation_commands"] = []
    return data


def impact_analysis(
    repo_root: Path, changed_files: list[str], target_files: list[str] | None = None
) -> dict[str, Any]:
    files = changed_files + (target_files or [])
    return query_impact(repo_root, files)


def list_actions(
    repo_root: Path,
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
    tags: list[str] | None = None,
    related_file: str | None = None,
    related_document: str | None = None,
) -> dict[str, Any]:
    rows = query_table(repo_root, "actions", 500).get("rows", [])
    if status:
        rows = [r for r in rows if r.get("status") == status]
    if priority:
        rows = [r for r in rows if r.get("priority") == priority]
    if related_file:
        rows = [r for r in rows if r.get("related_file") == related_file]
    if related_document:
        rows = [r for r in rows if r.get("document_id") == related_document]
    return {"actions": rows}


def validate_docs(repo_root: Path, scope: str | None = None) -> dict[str, Any]:
    report = run_validation(repo_root)
    return {
        "valid": report["valid"],
        "errors": report["errors"],
        "warnings": report["warnings"],
        "stale_generated_files": report["stale_generated_files"],
        "orphaned_records": report["orphaned_records"],
        "broken_references": report["broken_relationships"],
    }


def rebuild_indexes(
    repo_root: Path, validate_before: bool = True, validate_after: bool = True
) -> dict[str, Any]:
    before = validate_docs(repo_root) if validate_before else None
    result = run_build_index(repo_root)
    after = validate_docs(repo_root) if validate_after else None
    return {
        "generated_files": [
            "docs.sqlite",
            "manifest.json",
            "agent-context.json",
            "search-index.jsonl",
            "query-health-report.json",
        ],
        "query_health_status": result["health"],
        "validation_summary": {"before": before, "after": after},
    }


def update_action_status(
    repo_root: Path, action_id: str, status: str, evidence: str, changed_by: str
) -> dict[str, Any]:
    updated = update_action_status_impl(action_id, status, evidence, changed_by)
    return {
        "updated_action_record": updated.get("action"),
        "files_modified": ["docs-data/actions.jsonl"],
        "required_followup_validation": [
            "python -m tools.docs_agent.validate --json",
            "python -m tools.docs_agent.build_index --json",
        ],
    }


def classify_candidate_file(repo_root: Path, path: str) -> dict[str, Any]:
    policy = load_policy(repo_root)
    exceptions = load_exceptions(repo_root, policy)
    classification, confidence = classify_path(path, exceptions)
    return {
        "path": path,
        "candidate_classification": classification,
        "requires_ingestion": classification
        not in {
            "generated_machine_readable_artifact",
            "canonical_machine_readable_record",
            "configuration",
            "workflow_file",
            "schema",
            "exception_candidate",
        },
        "existing_coverage_status": "unknown",
        "recommended_action": (
            "ingest"
            if classification.startswith("legacy") or classification == "planning_document"
            else "review"
        ),
        "confidence": confidence,
    }


def ingest_candidate_file(
    repo_root: Path, path: str, ingestion_mode: str = "append"
) -> dict[str, Any]:
    result = run_convert(repo_root, [path])
    return {
        "generated_records": result,
        "source_trace": {"source_path": path},
        "conversion_warnings": [],
        "validation_status": validate_docs(repo_root),
    }


TOOLS = {
    "get_agent_context": get_agent_context,
    "search_docs": search_docs,
    "get_document": get_document,
    "get_related_context": get_related_context,
    "get_task_brief": get_task_brief,
    "impact_analysis": impact_analysis,
    "list_actions": list_actions,
    "validate_docs": validate_docs,
    "rebuild_indexes": rebuild_indexes,
    "update_action_status": update_action_status,
    "classify_candidate_file": classify_candidate_file,
    "ingest_candidate_file": ingest_candidate_file,
}
