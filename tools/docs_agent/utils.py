from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCS_DATA_DIR = ROOT / "docs-data"
GENERATED_DIR = DOCS_DATA_DIR / "generated"
SCHEMAS_DIR = DOCS_DATA_DIR / "schemas"

CANONICAL_JSONL_FILES = {
    "documents": DOCS_DATA_DIR / "documents.jsonl",
    "sections": DOCS_DATA_DIR / "sections.jsonl",
    "blocks": DOCS_DATA_DIR / "blocks.jsonl",
    "actions": DOCS_DATA_DIR / "actions.jsonl",
    "relationships": DOCS_DATA_DIR / "relationships.jsonl",
    "decisions": DOCS_DATA_DIR / "decisions.jsonl",
    "requirements": DOCS_DATA_DIR / "requirements.jsonl",
    "references": DOCS_DATA_DIR / "references.jsonl",
}

DEFAULT_IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
    ".next",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

DEFAULT_CANDIDATE_EXTENSIONS = [
    ".md",
    ".mdx",
    ".markdown",
    ".txt",
    ".rst",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".jsonl",
]

CLASSIFICATIONS = {
    "legacy_human_documentation",
    "planning_document",
    "roadmap",
    "architecture_note",
    "decision_record",
    "implementation_spec",
    "runbook",
    "developer_guide",
    "task_notes",
    "changelog",
    "release_notes",
    "repository_readme",
    "policy_file",
    "agent_instruction",
    "configuration",
    "schema",
    "canonical_machine_readable_record",
    "generated_machine_readable_artifact",
    "workflow_file",
    "exception_candidate",
    "ignored_dependency_or_build_file",
    "unknown",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    return parser


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def sha1_file(path: Path) -> str | None:
    try:
        return hashlib.sha1(path.read_bytes()).hexdigest()
    except Exception:
        return None


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return Path(os.path.relpath(path.resolve(), root.resolve())).as_posix()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in sorted(records, key=lambda r: r.get("id", "")):
            f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def load_policy(repo_root: Path) -> dict[str, Any]:
    policy_path = repo_root / "docs-data" / "machine-readable-policy.json"
    policy = load_json(policy_path, default={})
    if not policy:
        policy = {
            "candidate_extensions": DEFAULT_CANDIDATE_EXTENSIONS,
            "ignored_paths": [],
            "enforcement": {"default_mode": "strict", "fail_on_unmanaged_candidates": True},
            "allowed_exceptions_file": "docs-data/allowed-source-exceptions.json",
        }
    return policy


def load_exceptions(repo_root: Path, policy: dict[str, Any]) -> set[str]:
    exc_file = policy.get("allowed_exceptions_file", "docs-data/allowed-source-exceptions.json")
    data = load_json(repo_root / exc_file, default={"exceptions": []})
    return {
        item["path"]
        for item in data.get("exceptions", [])
        if isinstance(item, dict) and "path" in item
    }


def _is_ignored_by_glob(path: str, ignored_globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in ignored_globs)


def scan_candidate_files(repo_root: Path, policy: dict[str, Any]) -> list[Path]:
    candidate_exts = set(policy.get("candidate_extensions", DEFAULT_CANDIDATE_EXTENSIONS))
    ignored_globs = policy.get("ignored_paths", [])
    results: list[Path] = []
    for base, dirs, files in os.walk(repo_root):
        base_path = Path(base)
        rel_base = relpath(base_path, repo_root)
        dirs[:] = [
            d
            for d in dirs
            if d not in DEFAULT_IGNORED_DIRS
            and not _is_ignored_by_glob(f"{rel_base}/{d}", ignored_globs)
        ]
        for name in files:
            p = base_path / name
            rp = relpath(p, repo_root)
            if rp.startswith(".."):
                continue
            if _is_ignored_by_glob(rp, ignored_globs):
                continue
            if p.suffix.lower() in candidate_exts:
                results.append(p)
    return sorted(results)


def classify_path(path: str, exceptions: set[str], exempted_paths: list[str] | None = None) -> tuple[str, float]:
    name = Path(path).name.lower()

    if path in exceptions:
        return "exception_candidate", 1.0
    
    # Check if path matches any exempted glob patterns from policy
    if exempted_paths:
        for pattern in exempted_paths:
            if fnmatch.fnmatch(path, pattern):
                return "exception_candidate", 1.0
    
    if path.startswith("docs-data/generated/"):
        return "generated_machine_readable_artifact", 1.0
    if path.startswith("docs-data/") and (
        path.endswith(".jsonl") or path.startswith("docs-data/schemas/")
    ):
        return "canonical_machine_readable_record", 1.0
    if path.startswith(".github/workflows/"):
        return "workflow_file", 1.0
    if path.startswith(".github/instructions/") or name == "agents.md":
        return "agent_instruction", 0.95
    if name == "readme.md":
        return "repository_readme", 0.95
    if "changelog" in name:
        return "changelog", 0.95
    if "release" in name and "note" in name:
        return "release_notes", 0.9
    if "roadmap" in name:
        return "roadmap", 0.9
    if "architecture" in name:
        return "architecture_note", 0.9
    if "runbook" in name:
        return "runbook", 0.9
    if "guide" in name:
        return "developer_guide", 0.85
    if any(k in name for k in ["plan", "phase", "task", "todo", "checklist"]):
        return "planning_document", 0.8
    if "decision" in name or "adr" in name:
        return "decision_record", 0.8
    if path.endswith((".yml", ".yaml", ".toml")):
        return "configuration", 0.95
    if "schema" in name and path.endswith(".json"):
        return "schema", 0.95
    if path.endswith((".json", ".jsonl")):
        return "configuration", 0.75
    if path.endswith((".md", ".mdx", ".markdown", ".txt", ".rst")):
        return "legacy_human_documentation", 0.7
    return "unknown", 0.4


def requires_ingestion(classification: str) -> bool:
    return classification in {
        "legacy_human_documentation",
        "planning_document",
        "roadmap",
        "architecture_note",
        "decision_record",
        "implementation_spec",
        "runbook",
        "developer_guide",
        "task_notes",
        "changelog",
        "release_notes",
        "repository_readme",
        "policy_file",
        "agent_instruction",
    }


def source_trace(path: Path, root: Path) -> dict[str, Any]:
    return {
        "source_path": relpath(path, root),
        "source_line_start": None,
        "source_line_end": None,
        "source_sha1": sha1_file(path),
    }
