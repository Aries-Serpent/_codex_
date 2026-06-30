from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .utils import (
    classify_path,
    load_exceptions,
    load_policy,
    parse_common_args,
    relpath,
    requires_ingestion,
    scan_candidate_files,
    utc_now,
    write_json,
)


def run_inventory(repo_root: Path) -> dict:
    policy = load_policy(repo_root)
    exceptions = load_exceptions(repo_root, policy)
    generated_dir = repo_root / "docs-data" / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    candidates = scan_candidate_files(repo_root, policy)

    by_class = Counter()
    by_folder = Counter()
    inventory = []
    markdown_inventory = []

    for path in candidates:
        rp = relpath(path, repo_root)
        cls, confidence = classify_path(rp, exceptions)
        by_class[cls] += 1
        by_folder[rp.split("/")[0]] += 1

        entry = {
            "path": rp,
            "classification": cls,
            "confidence": confidence,
            "extension": path.suffix.lower(),
            "requires_ingestion": requires_ingestion(cls) and rp not in exceptions,
            "exception": rp in exceptions,
            "size_bytes": path.stat().st_size,
        }
        inventory.append(entry)

        if path.suffix.lower() in {".md", ".mdx", ".markdown", ".txt", ".rst"}:
            markdown_inventory.append(entry)

    convert_candidates = [x["path"] for x in inventory if x["requires_ingestion"]]
    exception_candidates = [x["path"] for x in inventory if x["exception"]]
    quarantine_candidates = [
        x["path"] for x in inventory if x["classification"] == "unknown" or x["confidence"] < 0.6
    ]
    deletion_candidates = [
        x["path"]
        for x in inventory
        if x["classification"] in {"legacy_human_documentation", "planning_document", "task_notes"}
        and not x["exception"]
    ]

    existing_scripts = [
        p
        for p in [
            "tools/codex_ingest_md.py",
            "tools/codex_sqlite_align.py",
            "tools/catalog_db.py",
            "scripts/docs_agent/validate_jsonl.py",
            "src/codex/docs_agent/cli.py",
        ]
        if (repo_root / p).exists()
    ]

    existing_workflows = [
        p.name
        for p in sorted((repo_root / ".github" / "workflows").glob("*.yml"))
        if any(k in p.name for k in ["validate", "governance", "docs", "quality", "compliance"])
    ]

    conventions = {
        name: (repo_root / name).exists()
        for name in [
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "poetry.lock",
            "uv.lock",
            "tox.ini",
            "noxfile.py",
            "pytest.ini",
            "ruff.toml",
            "mypy.ini",
            "Makefile",
            "Taskfile",
            ".pre-commit-config.yaml",
        ]
    }

    discovery = {
        "generated_at": utc_now(),
        "total_candidate_files": len(inventory),
        "candidate_files_by_folder": dict(sorted(by_folder.items())),
        "candidate_files_by_classification": dict(sorted(by_class.items())),
        "files_recommended_for_conversion": sorted(convert_candidates),
        "files_recommended_for_exception_handling": sorted(exception_candidates),
        "files_recommended_for_quarantine": sorted(quarantine_candidates),
        "files_recommended_for_deletion_after_conversion": sorted(deletion_candidates),
        "existing_scripts_tools_reused": existing_scripts,
        "existing_workflows_to_update": existing_workflows,
        "detected_python_project_conventions": conventions,
        "unresolved_risks": [
            "Large unmanaged legacy document volume may require staged migration.",
            "Strict enforcement mode will fail until ingestion or exemptions are completed.",
            "Relationship extraction quality depends on source document consistency.",
        ],
        "classification_confidence": {
            x["path"]: x["confidence"] for x in inventory if x["confidence"] < 0.95
        },
    }

    automation = {
        "generated_at": utc_now(),
        "workflow_count": len(list((repo_root / ".github" / "workflows").glob("*.yml"))),
        "workflows": sorted([p.name for p in (repo_root / ".github" / "workflows").glob("*.yml")]),
        "scripts": existing_scripts,
    }

    readiness = {
        "generated_at": utc_now(),
        "conversion_ready": len(convert_candidates),
        "exception_ready": len(exception_candidates),
        "quarantine_needed": len(quarantine_candidates),
        "strict_mode_blocking": len(convert_candidates) > 0,
    }

    write_json(
        generated_dir / "candidate-inventory.json",
        {"generated_at": utc_now(), "candidates": inventory},
    )
    write_json(
        generated_dir / "markdown-inventory.json",
        {"generated_at": utc_now(), "markdown_candidates": markdown_inventory},
    )
    write_json(generated_dir / "codebase-discovery-report.json", discovery)
    write_json(generated_dir / "existing-automation-report.json", automation)
    write_json(generated_dir / "migration-readiness-report.json", readiness)

    return {
        "ok": True,
        "generated": [
            "candidate-inventory.json",
            "markdown-inventory.json",
            "codebase-discovery-report.json",
            "existing-automation-report.json",
            "migration-readiness-report.json",
        ],
        "total_candidates": len(inventory),
    }


def main() -> int:
    parser = parse_common_args(
        argparse.ArgumentParser(description="Inventory candidate documentation files")
    )
    args = parser.parse_args()
    result = run_inventory(Path(args.repo_root))
    if args.json:
        import json

        print(json.dumps(result, sort_keys=True))
    else:
        print(f"inventory complete: {result['total_candidates']} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
