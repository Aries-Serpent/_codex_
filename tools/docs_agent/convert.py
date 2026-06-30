from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .utils import (
    CANONICAL_JSONL_FILES,
    parse_common_args,
    read_jsonl,
    relpath,
    source_trace,
    stable_id,
    utc_now,
    write_json,
    write_jsonl,
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
URL_RE = re.compile(r"https?://[^\s)]+")


def _record_document(path: Path, repo_root: Path) -> dict[str, Any]:
    return {
        "id": stable_id("doc", relpath(path, repo_root)),
        "type": "document",
        "schema_version": "1.0.0",
        "title": path.name,
        "summary": f"Converted from {relpath(path, repo_root)}",
        "classification": "legacy_human_documentation",
        "lifecycle_status": "converted_to_jsonl",
        "source_trace": source_trace(path, repo_root),
        "discovered_at": utc_now(),
        "updated_at": utc_now(),
        "tags": ["converted"],
        "confidence": 0.8,
        "related_ids": [],
    }


def _convert_file(path: Path, repo_root: Path) -> dict[str, list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    document = _record_document(path, repo_root)
    sections: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    current_section_id: str | None = None
    for i, line in enumerate(lines, start=1):
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            heading = m.group(2).strip()
            sid = stable_id("sec", relpath(path, repo_root), str(i), heading)
            sections.append(
                {
                    "id": sid,
                    "type": "section",
                    "schema_version": "1.0.0",
                    "document_id": document["id"],
                    "parent_section_id": None,
                    "heading": heading,
                    "level": level,
                    "lifecycle_status": "converted_to_jsonl",
                    "source_trace": {
                        **source_trace(path, repo_root),
                        "source_line_start": i,
                        "source_line_end": i,
                    },
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": [],
                    "confidence": 0.9,
                    "related_ids": [],
                }
            )
            relationships.append(
                {
                    "id": stable_id("rel", document["id"], sid, "owns"),
                    "type": "relationship",
                    "schema_version": "1.0.0",
                    "relationship_type": "document owns section",
                    "source": {"id": document["id"], "entity_type": "document"},
                    "target": {"id": sid, "entity_type": "section"},
                    "lifecycle_status": "validated",
                    "source_trace": source_trace(path, repo_root),
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": [],
                    "confidence": 0.95,
                }
            )
            current_section_id = sid
            continue

        if not line.strip():
            continue

        section_id = current_section_id or stable_id("sec", relpath(path, repo_root), "root")
        if (
            not sections
            or sections[0]["id"] != section_id
            and all(s["id"] != section_id for s in sections)
        ):
            sections.append(
                {
                    "id": section_id,
                    "type": "section",
                    "schema_version": "1.0.0",
                    "document_id": document["id"],
                    "parent_section_id": None,
                    "heading": "root",
                    "level": 1,
                    "lifecycle_status": "converted_to_jsonl",
                    "source_trace": source_trace(path, repo_root),
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": [],
                    "confidence": 0.7,
                    "related_ids": [],
                }
            )

        block_type = "list" if line.lstrip().startswith(("- ", "* ")) else "paragraph"
        bid = stable_id("blk", relpath(path, repo_root), str(i), line.strip())
        blocks.append(
            {
                "id": bid,
                "type": "block",
                "schema_version": "1.0.0",
                "section_id": section_id,
                "block_type": block_type,
                "text": line.strip(),
                "lifecycle_status": "converted_to_jsonl",
                "source_trace": {
                    **source_trace(path, repo_root),
                    "source_line_start": i,
                    "source_line_end": i,
                },
                "discovered_at": utc_now(),
                "updated_at": utc_now(),
                "tags": [],
                "confidence": 0.7,
                "related_ids": [],
            }
        )
        relationships.append(
            {
                "id": stable_id("rel", section_id, bid, "owns"),
                "type": "relationship",
                "schema_version": "1.0.0",
                "relationship_type": "section owns block",
                "source": {"id": section_id, "entity_type": "section"},
                "target": {"id": bid, "entity_type": "block"},
                "lifecycle_status": "validated",
                "source_trace": source_trace(path, repo_root),
                "discovered_at": utc_now(),
                "updated_at": utc_now(),
                "tags": [],
                "confidence": 0.95,
            }
        )

        if line.strip().startswith("- ["):
            checked = "[x]" in line.lower()
            status = "completed" if checked else "open"
            aid = stable_id("act", relpath(path, repo_root), str(i), line.strip())
            actions.append(
                {
                    "id": aid,
                    "type": "action",
                    "schema_version": "1.0.0",
                    "title": line.strip(),
                    "description": line.strip(),
                    "status": status,
                    "priority": "medium",
                    "action_type": "completed task" if checked else "open task",
                    "document_id": document["id"],
                    "related_file": relpath(path, repo_root),
                    "lifecycle_status": "converted_to_jsonl",
                    "source_trace": source_trace(path, repo_root),
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": ["converted"],
                    "confidence": 0.8,
                    "related_ids": [],
                }
            )

        if "decision:" in line.lower():
            decisions.append(
                {
                    "id": stable_id("dec", relpath(path, repo_root), str(i)),
                    "type": "decision",
                    "schema_version": "1.0.0",
                    "statement": line.strip(),
                    "status": "accepted",
                    "requirement_ids": [],
                    "lifecycle_status": "converted_to_jsonl",
                    "source_trace": source_trace(path, repo_root),
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": [],
                    "confidence": 0.7,
                }
            )

        if "must" in line.lower() or "shall" in line.lower() or "required" in line.lower():
            requirements.append(
                {
                    "id": stable_id("req", relpath(path, repo_root), str(i)),
                    "type": "requirement",
                    "schema_version": "1.0.0",
                    "statement": line.strip(),
                    "status": "open",
                    "acceptance_criteria": [],
                    "constraint_type": "rule",
                    "lifecycle_status": "converted_to_jsonl",
                    "source_trace": source_trace(path, repo_root),
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": [],
                    "confidence": 0.7,
                }
            )

        for url in URL_RE.findall(line):
            references.append(
                {
                    "id": stable_id("ref", relpath(path, repo_root), str(i), url),
                    "type": "reference",
                    "schema_version": "1.0.0",
                    "ref_type": "url",
                    "label": url,
                    "target": url,
                    "document_id": document["id"],
                    "lifecycle_status": "validated",
                    "source_trace": source_trace(path, repo_root),
                    "discovered_at": utc_now(),
                    "updated_at": utc_now(),
                    "tags": [],
                    "confidence": 0.95,
                }
            )

    return {
        "documents": [document],
        "sections": sections,
        "blocks": blocks,
        "actions": actions,
        "relationships": relationships,
        "decisions": decisions,
        "requirements": requirements,
        "references": references,
    }


def _merge_into_canonical(records_by_type: dict[str, list[dict[str, Any]]]) -> None:
    for key, path in CANONICAL_JSONL_FILES.items():
        existing = {r.get("id"): r for r in read_jsonl(path)}
        for rec in records_by_type.get(key, []):
            existing[rec["id"]] = rec
        write_jsonl(path, list(existing.values()))


def run_convert(repo_root: Path, paths: list[str]) -> dict:
    converted = []
    map_entries = []
    all_records = {k: [] for k in CANONICAL_JSONL_FILES}

    for p in paths:
        source = (repo_root / p).resolve()
        if not source.exists() or not source.is_file():
            continue
        recs = _convert_file(source, repo_root)
        for key, vals in recs.items():
            all_records[key].extend(vals)
        map_entries.append(
            {
                "source_path": p,
                "document_id": recs["documents"][0]["id"],
                "record_counts": {k: len(v) for k, v in recs.items()},
            }
        )
        converted.append(p)

    _merge_into_canonical(all_records)

    generated = repo_root / "docs-data" / "generated"
    conversion_map = {"generated_at": utc_now(), "entries": map_entries}
    conversion_report = {
        "generated_at": utc_now(),
        "converted_files": converted,
        "total_converted": len(converted),
        "records_generated": {k: len(v) for k, v in all_records.items()},
    }
    write_json(generated / "conversion-map.json", conversion_map)
    write_json(generated / "conversion-report.json", conversion_report)
    return {"ok": True, "converted": len(converted)}


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Convert legacy docs to canonical JSONL")
    )
    parser.add_argument("paths", nargs="*", help="Repository-relative files to ingest")
    args = parser.parse_args()
    result = run_convert(Path(args.repo_root), args.paths)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"converted {result['converted']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
