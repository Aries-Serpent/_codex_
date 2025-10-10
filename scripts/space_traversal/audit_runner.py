from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.space_traversal import capability_scoring  # noqa: E402

STAGE_ORDER: List[str] = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
SAFEGUARD_KEYWORDS: Sequence[str] = (
    "sha256",
    "checksum",
    "rng",
    "seed",
    "offline",
    "WANDB_MODE",
)
DEFAULT_WEIGHTS: Mapping[str, float] = {
    "functionality": 0.25,
    "consistency": 0.20,
    "tests": 0.25,
    "safeguards": 0.15,
    "documentation": 0.15,
}
DEFAULT_THRESHOLDS: Mapping[str, float] = {"low": 0.70, "medium": 0.85}
INDEX_TARGETS: Sequence[str] = ("src", "scripts", "docs", "tests")


@dataclass(slots=True)
class AuditConfig:
    repo_root: Path = REPO_ROOT
    artifacts_dir: Path = field(default_factory=lambda: REPO_ROOT / "audit_artifacts")
    reports_dir: Path = field(default_factory=lambda: REPO_ROOT / "reports")
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    thresholds: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_THRESHOLDS))
    safeguards: Sequence[str] = SAFEGUARD_KEYWORDS
    matrix_template: Path = field(
        default_factory=lambda: REPO_ROOT / "templates" / "audit" / "capability_matrix.md.j2"
    )


def timestamp() -> str:
    return (
        _dt.datetime.now(tz=_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> MutableMapping[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)


def load_indexed_files(config: AuditConfig) -> List[Dict[str, Any]]:
    index_path = config.artifacts_dir / "index.json"
    if not index_path.exists():
        raise FileNotFoundError("S1 index.json not found; run stage S1 first")
    index_data = read_json(index_path)
    return index_data.get("files", [])


def stage_index(config: AuditConfig) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    for target in INDEX_TARGETS:
        root = config.repo_root / target
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(config.repo_root)
            if any(part.startswith(".") for part in rel.parts):
                continue
            rel_path = rel.as_posix()
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            record = {
                "path": rel_path,
                "size": size,
                "sha256": sha256_file(path),
                "extension": path.suffix.lower(),
                "category": infer_category(rel_path),
            }
            records.append(record)
    records.sort(key=lambda item: item["path"])
    payload = {
        "generated_at": timestamp(),
        "repo_root": str(config.repo_root),
        "file_count": len(records),
        "total_bytes": sum(r["size"] for r in records),
        "files": records,
    }
    output_path = config.artifacts_dir / "index.json"
    write_json(output_path, payload)
    return {"artifact": str(output_path), "file_count": len(records)}


def infer_category(rel_path: str) -> str:
    if rel_path.startswith("tests/") or "/tests/" in rel_path or rel_path.endswith("_test.py"):
        return "tests"
    if rel_path.startswith("docs/") or rel_path.startswith("documentation/"):
        return "docs"
    if rel_path.startswith("scripts/"):
        return "scripts"
    if rel_path.startswith("src/"):
        return "src"
    return "other"


def stage_facets(config: AuditConfig) -> Dict[str, Any]:
    files = load_indexed_files(config)
    by_extension: Dict[str, Dict[str, Any]] = {}
    doc_paths: List[str] = []
    test_paths: List[str] = []
    for entry in files:
        ext = entry.get("extension", "") or "<none>"
        bucket = by_extension.setdefault(ext, {"count": 0, "total_bytes": 0})
        bucket["count"] += 1
        bucket["total_bytes"] += entry.get("size", 0)
        if entry.get("category") == "docs":
            doc_paths.append(entry["path"])
        if entry.get("category") == "tests":
            test_paths.append(entry["path"])
    payload = {
        "generated_at": timestamp(),
        "by_extension": by_extension,
        "docs": {"count": len(doc_paths), "paths": sorted(doc_paths)},
        "tests": {"count": len(test_paths), "paths": sorted(test_paths)},
        "summary": {
            "file_count": len(files),
            "doc_ratio": len(doc_paths) / len(files) if files else 0.0,
            "test_ratio": len(test_paths) / len(files) if files else 0.0,
        },
    }
    output_path = config.artifacts_dir / "facets.json"
    write_json(output_path, payload)
    return {"artifact": str(output_path), "extensions": len(by_extension)}


def load_detectors() -> List[Callable[[Mapping[str, Any]], Mapping[str, Any]]]:
    detectors_dir = SCRIPT_DIR / "detectors"
    loaded: List[Callable[[Mapping[str, Any]], Mapping[str, Any]]] = []
    if not detectors_dir.exists():
        return loaded
    for module_path in sorted(detectors_dir.glob("*.py")):
        if module_path.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(
            f"audit_detector_{module_path.stem}", module_path
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        detect_fn = getattr(module, "detect", None)
        if callable(detect_fn):
            loaded.append(detect_fn)
    return loaded


def stage_capabilities(config: AuditConfig) -> Dict[str, Any]:
    index_payload = {
        "files": load_indexed_files(config),
    }
    capabilities: List[Dict[str, Any]] = []
    for detect_fn in load_detectors():
        try:
            result = detect_fn(index_payload)
        except Exception as exc:  # noqa: BLE001
            capabilities.append(
                {
                    "id": getattr(detect_fn, "__name__", "unknown"),
                    "error": str(exc),
                    "evidence_files": [],
                    "found_patterns": [],
                    "required_patterns": [],
                    "meta": {"status": "error"},
                }
            )
            continue
        if not isinstance(result, Mapping):
            continue
        capability = dict(result)
        capability.setdefault("id", getattr(detect_fn, "__name__", "unknown"))
        capability.setdefault("evidence_files", [])
        capability.setdefault("found_patterns", [])
        capability.setdefault("required_patterns", [])
        capability.setdefault("meta", {})
        capabilities.append(capability)
    payload = {
        "generated_at": timestamp(),
        "capabilities": capabilities,
    }
    output_path = config.artifacts_dir / "capabilities_raw.json"
    write_json(output_path, payload)
    return {"artifact": str(output_path), "capability_count": len(capabilities)}


def build_components(
    capability: Mapping[str, Any],
    config: AuditConfig,
    index: List[Mapping[str, Any]],
    facets: Mapping[str, Any],
) -> Dict[str, float]:
    evidence_files: Sequence[str] = capability.get("evidence_files", []) or []
    required_patterns: Sequence[str] = capability.get("required_patterns", []) or []
    found_patterns: Sequence[str] = capability.get("found_patterns", []) or []

    if required_patterns:
        functionality = len(set(found_patterns)) / len(set(required_patterns))
    else:
        functionality = 1.0 if evidence_files else 0.0
    functionality = max(0.0, min(1.0, functionality))

    unique_evidence = len(set(evidence_files))
    total_evidence = len(evidence_files)
    if total_evidence:
        duplicate_ratio = (total_evidence - unique_evidence) / total_evidence
        consistency = max(0.0, 1.0 - duplicate_ratio)
    else:
        consistency = 1.0

    test_hits = 0
    for rel_path in evidence_files:
        lower = rel_path.lower()
        if "test" in lower or "tests/" in lower:
            test_hits += 1
    tests_component = (
        min(1.0, test_hits / total_evidence)
        if total_evidence
        else facets.get("tests", {}).get("count", 0) > 0
    )
    tests_component = float(tests_component)

    safeguard_hits = set()
    for rel_path in evidence_files:
        path = config.repo_root / rel_path
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        lower_text = text.lower()
        for keyword in config.safeguards:
            if keyword.lower() in lower_text:
                safeguard_hits.add(keyword)
    safeguards_component = (
        len(safeguard_hits) / len(config.safeguards) if config.safeguards else 0.0
    )

    docs_info = facets.get("docs", {})
    doc_paths: Sequence[str] = docs_info.get("paths", []) if isinstance(docs_info, Mapping) else []
    doc_hits = 0
    needle = str(capability.get("id", "")).replace("_", " ").lower()
    if needle:
        for rel_path in doc_paths:
            doc_path = config.repo_root / rel_path
            try:
                text = doc_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if needle in text.lower():
                doc_hits += 1
    documentation_component = min(1.0, doc_hits / max(1, len(doc_paths))) if doc_paths else 0.0

    return {
        "functionality": float(functionality),
        "consistency": float(consistency),
        "tests": float(tests_component),
        "safeguards": float(safeguards_component),
        "documentation": float(documentation_component),
    }


def stage_scoring(config: AuditConfig) -> Dict[str, Any]:
    raw_path = config.artifacts_dir / "capabilities_raw.json"
    facets_path = config.artifacts_dir / "facets.json"
    if not raw_path.exists() or not facets_path.exists():
        raise FileNotFoundError("Run stages S2 and S3 before scoring")
    raw_payload = read_json(raw_path)
    facets_payload = read_json(facets_path)
    index_records = load_indexed_files(config)

    scored_capabilities: List[Dict[str, Any]] = []
    normalized_weights = capability_scoring.normalize_weights(config.weights)

    for capability in raw_payload.get("capabilities", []):
        components = build_components(capability, config, index_records, facets_payload)
        cap_with_components = dict(capability)
        cap_with_components["components"] = components
        explanation = capability_scoring.explain_score(cap_with_components, normalized_weights)
        explanation["components"] = components
        explanation["meta"] = capability.get("meta", {})
        explanation["evidence_files"] = capability.get("evidence_files", [])
        explanation["required_patterns"] = capability.get("required_patterns", [])
        explanation["found_patterns"] = capability.get("found_patterns", [])
        scored_capabilities.append(explanation)

    payload = {
        "generated_at": timestamp(),
        "weights": normalized_weights,
        "capabilities": scored_capabilities,
    }
    output_path = config.artifacts_dir / "capabilities_scored.json"
    write_json(output_path, payload)
    return {"artifact": str(output_path), "capability_count": len(scored_capabilities)}


def stage_gaps(config: AuditConfig) -> Dict[str, Any]:
    scored_path = config.artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        raise FileNotFoundError("Run stage S4 before gap analysis")
    scored_payload = read_json(scored_path)
    threshold = float(config.thresholds.get("low", 0.0))
    gaps = [
        cap for cap in scored_payload.get("capabilities", []) if cap.get("score", 0.0) < threshold
    ]
    payload = {
        "generated_at": timestamp(),
        "threshold": threshold,
        "gaps": gaps,
    }
    output_path = config.artifacts_dir / "capability_gaps.json"
    write_json(output_path, payload)
    return {"artifact": str(output_path), "gap_count": len(gaps)}


def render_markdown_matrix(scored_payload: Mapping[str, Any]) -> str:
    lines = [
        "# Capability Matrix",
        "",
        "| Capability | Score | Functionality | Consistency | Tests | Safeguards | Documentation |",
        "|------------|-------|--------------|-------------|-------|------------|-----------------|",
    ]
    for capability in scored_payload.get("capabilities", []):
        components = capability.get("components", {})
        line = "| {id} | {score:.2f} | {functionality:.2f} | {consistency:.2f} | {tests:.2f} | {safeguards:.2f} | {documentation:.2f} |".format(
            id=capability.get("id", "unknown"),
            score=float(capability.get("score", 0.0)),
            functionality=float(components.get("functionality", 0.0)),
            consistency=float(components.get("consistency", 0.0)),
            tests=float(components.get("tests", 0.0)),
            safeguards=float(components.get("safeguards", 0.0)),
            documentation=float(components.get("documentation", 0.0)),
        )
        lines.append(line)
    lines.append("")
    lines.append("Generated at: " + scored_payload.get("generated_at", timestamp()))
    return "\n".join(lines)


def stage_render(config: AuditConfig) -> Dict[str, Any]:
    scored_path = config.artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        raise FileNotFoundError("Run stage S4 before rendering")
    scored_payload = read_json(scored_path)

    content = render_markdown_matrix(scored_payload)
    reports_dir = config.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / "capability_matrix.md"
    output_path.write_text(content, encoding="utf-8")
    return {"artifact": str(output_path)}


def collect_artifacts(root: Path, base: Path) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    if not root.exists():
        return collected
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(base)
        collected.append(
            {
                "path": rel.as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return collected


def git_head(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def stage_manifest(config: AuditConfig) -> Dict[str, Any]:
    artifacts = collect_artifacts(config.artifacts_dir, config.repo_root)
    reports = collect_artifacts(config.reports_dir, config.repo_root)
    payload = {
        "generated_at": timestamp(),
        "repo_root": str(config.repo_root),
        "git_head": git_head(config.repo_root),
        "artifacts": artifacts,
        "reports": reports,
    }
    output_path = config.reports_dir / "audit_manifest.json"
    write_json(output_path, payload)
    return {"artifact": str(output_path), "artifacts": len(artifacts), "reports": len(reports)}


STAGE_IMPLEMENTATIONS: Dict[str, Callable[[AuditConfig], Dict[str, Any]]] = {
    "S1": stage_index,
    "S2": stage_facets,
    "S3": stage_capabilities,
    "S4": stage_scoring,
    "S5": stage_gaps,
    "S6": stage_render,
    "S7": stage_manifest,
}


def run_stage(stage_id: str, config: AuditConfig | None = None) -> Dict[str, Any]:
    config = config or AuditConfig()
    normalized = stage_id.strip().upper()
    if normalized not in STAGE_IMPLEMENTATIONS:
        raise ValueError(f"Unknown stage id: {stage_id}")
    return STAGE_IMPLEMENTATIONS[normalized](config)


def run_all(config: AuditConfig | None = None) -> List[Dict[str, Any]]:
    config = config or AuditConfig()
    results: List[Dict[str, Any]] = []
    for stage_id in STAGE_ORDER:
        result = run_stage(stage_id, config)
        results.append({"stage": stage_id, **result})
    return results


def command_run(_: argparse.Namespace) -> int:
    results = run_all()
    for result in results:
        stage_id = result.pop("stage")
        print(f"[audit] {stage_id} -> {json.dumps(result, sort_keys=True)}")
    return 0


def command_stage(args: argparse.Namespace) -> int:
    result = run_stage(args.stage)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def command_explain(args: argparse.Namespace) -> int:
    scored_path = AuditConfig().artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        print("No scored capabilities found. Run stage S4 first.", file=sys.stderr)
        return 2
    payload = read_json(scored_path)
    needle = args.capability.lower()
    for capability in payload.get("capabilities", []):
        if str(capability.get("id", "")).lower() == needle:
            print(json.dumps(capability, indent=2, sort_keys=True))
            return 0
    print(f"Capability '{args.capability}' not found in scored output.", file=sys.stderr)
    return 1


def command_diff(args: argparse.Namespace) -> int:
    old_payload = read_json(Path(args.old))
    new_payload = read_json(Path(args.new))
    old_scores = {
        cap.get("id"): cap.get("score", 0.0) for cap in old_payload.get("capabilities", [])
    }
    new_scores = {
        cap.get("id"): cap.get("score", 0.0) for cap in new_payload.get("capabilities", [])
    }
    ids = sorted(set(old_scores) | set(new_scores))
    changes: List[Dict[str, Any]] = []
    for cap_id in ids:
        changes.append(
            {
                "id": cap_id,
                "old": float(old_scores.get(cap_id, 0.0)),
                "new": float(new_scores.get(cap_id, 0.0)),
                "delta": float(new_scores.get(cap_id, 0.0) - old_scores.get(cap_id, 0.0)),
            }
        )
    print(json.dumps({"changes": changes}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Copilot Space audit runner")
    sub = parser.add_subparsers(dest="command", required=True)

    sub_run = sub.add_parser("run", help="Execute S1–S7 in order")
    sub_run.set_defaults(func=command_run)

    sub_stage = sub.add_parser("stage", help="Execute a single stage")
    sub_stage.add_argument("stage", help="Stage identifier (e.g., S4)")
    sub_stage.set_defaults(func=command_stage)

    sub_explain = sub.add_parser("explain", help="Explain a scored capability")
    sub_explain.add_argument("capability", help="Capability identifier")
    sub_explain.set_defaults(func=command_explain)

    sub_diff = sub.add_parser("diff", help="Compare two scored capability files")
    sub_diff.add_argument("old", help="Path to baseline capabilities_scored.json")
    sub_diff.add_argument("new", help="Path to new capabilities_scored.json")
    sub_diff.set_defaults(func=command_diff)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 2
    return func(args)


def stage_entry(stage_id: str) -> Dict[str, Any]:
    return run_stage(stage_id)


def stage(stage_id: str) -> Dict[str, Any]:
    return run_stage(stage_id)


if __name__ == "__main__":
    raise SystemExit(main())
