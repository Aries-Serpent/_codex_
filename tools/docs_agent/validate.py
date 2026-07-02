from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import pathname2url

import jsonschema
from jsonschema import RefResolver

from .utils import CANONICAL_JSONL_FILES, parse_common_args, read_jsonl, utc_now, write_json


def _load_schemas(repo_root: Path) -> dict[str, dict[str, Any]]:
    schema_dir = repo_root / "docs-data" / "schemas"
    schemas: dict[str, dict[str, Any]] = {}
    for p in sorted(schema_dir.glob("*.schema.json")):
        schemas[p.name.replace(".schema.json", "")] = json.loads(p.read_text(encoding="utf-8"))
    return schemas


def _create_resolver(repo_root: Path) -> RefResolver:
    """Create a RefResolver that can handle relative schema references."""
    schema_dir = repo_root / "docs-data" / "schemas"
    
    # Load all schemas into a store for resolution
    store: dict[str, dict[str, Any]] = {}
    
    # First pass: load all schemas with their correct URIs
    for p in sorted(schema_dir.glob("*.schema.json")):
        schema_content = json.loads(p.read_text(encoding="utf-8"))
        filename = p.name
        
        # Store the schema under its canonical filename (e.g., "reference.schema.json")
        store[filename] = schema_content
        
        # Also store under the file:// URL form that's used in the $id field
        # This allows resolution of references like "./reference.schema.json#/$defs/source_trace"
        store[f"file:///docs-data/schemas/{filename}"] = schema_content
    
    # Create a base URL that matches the schema directory
    # This is important so relative references work correctly
    base_url = "file:///docs-data/schemas/"
    
    return RefResolver(base_url, {}, store=store)


def run_validation(repo_root: Path) -> dict[str, Any]:
    schemas = _load_schemas(repo_root)
    resolver = _create_resolver(repo_root)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    all_records: dict[str, dict[str, Any]] = {}
    ids_seen: set[str] = set()
    by_type: dict[str, list[dict[str, Any]]] = {k: [] for k in CANONICAL_JSONL_FILES}

    for key, path in CANONICAL_JSONL_FILES.items():
        for row in read_jsonl(path):
            rid = row.get("id")
            if rid in ids_seen:
                errors.append({"type": "duplicate_id", "id": rid, "file": path.as_posix()})
            ids_seen.add(rid)
            all_records[rid] = row
            by_type[key].append(row)

            schema = schemas.get(key.rstrip("s"))
            if schema:
                try:
                    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
                    validator.validate(row)
                except jsonschema.ValidationError as exc:
                    errors.append(
                        {
                            "type": "schema_validation",
                            "id": rid,
                            "message": exc.message,
                            "file": path.as_posix(),
                        }
                    )

    def exists(rid: str | None) -> bool:
        return bool(rid) and rid in all_records

    for s in by_type["sections"]:
        if not exists(s.get("document_id")):
            errors.append(
                {"type": "orphaned_section", "id": s.get("id"), "document_id": s.get("document_id")}
            )
    for b in by_type["blocks"]:
        if not exists(b.get("section_id")):
            errors.append(
                {"type": "orphaned_block", "id": b.get("id"), "section_id": b.get("section_id")}
            )
    for a in by_type["actions"]:
        did = a.get("document_id")
        if did and not exists(did):
            errors.append({"type": "orphaned_action", "id": a.get("id"), "document_id": did})
    for d in by_type["decisions"]:
        for rid in d.get("requirement_ids", []):
            if not exists(rid):
                errors.append(
                    {"type": "orphaned_decision", "id": d.get("id"), "requirement_id": rid}
                )
    for r in by_type["requirements"]:
        if r.get("status") not in {"open", "satisfied", "blocked", "deprecated"}:
            errors.append(
                {"type": "invalid_lifecycle_status", "id": r.get("id"), "status": r.get("status")}
            )
    for rel in by_type["relationships"]:
        s = rel.get("source", {}).get("id")
        t = rel.get("target", {}).get("id")
        if not exists(s):
            errors.append({"type": "broken_relationship", "id": rel.get("id"), "missing": s})
        if not exists(t):
            errors.append({"type": "broken_relationship", "id": rel.get("id"), "missing": t})
    for ref in by_type["references"]:
        target = ref.get("target", "")
        if ref.get("ref_type") == "url" and not str(target).startswith(("http://", "https://")):
            warnings.append({"type": "unresolved_reference", "id": ref.get("id"), "target": target})

    generated = repo_root / "docs-data" / "generated"
    manifest_path = generated / "manifest.json"
    stale = []
    if not manifest_path.exists():
        stale.append("manifest.json")
    expected_generated = [
        "docs.sqlite",
        "manifest.json",
        "agent-context.json",
        "search-index.jsonl",
        "query-health-report.json",
    ]
    for name in expected_generated:
        if not (generated / name).exists():
            stale.append(name)

    report = {
        "generated_at": utc_now(),
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {"records": len(all_records), "errors": len(errors), "warnings": len(warnings)},
        "stale_generated_files": sorted(set(stale)),
        "orphaned_records": [e for e in errors if "orphaned" in e.get("type", "")],
        "broken_relationships": [e for e in errors if e.get("type") == "broken_relationship"],
    }
    write_json(generated / "validation-report.json", report)
    return report


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Validate canonical JSONL records")
    )
    args = parser.parse_args()
    report = run_validation(Path(args.repo_root))
    if args.json:
        print(json.dumps({"ok": report["valid"], "errors": len(report["errors"])}, sort_keys=True))
    else:
        print(f"valid={report['valid']} errors={len(report['errors'])}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
