#!/usr/bin/env python
"""
Audit Runner Orchestrator for Copilot Space Traversal Workflow (v1.1.0)

Additions (v1.1.0):
 - Dynamic detector loading from detectors/ directory
 - 'diff' command for comparing score JSON or matrix markdown files
 - 'explain' command for per-capability score breakdown
 - Improved determinism & weight normalization warnings
 - Manifest warnings field
 - Optional regression failure exit code (YAML options)

Stages:
 S1 Index               -> context_index.json
 S2 Facet Grouping      -> facets.json
 S3 Capability Extract  -> capabilities_raw.json
 S4 Scoring             -> capabilities_scored.json
 S5 Gap Analysis        -> gaps.json
 S6 Render Markdown     -> capability_matrix_<timestamp>.md
 S7 Manifest            -> audit_run_manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader
except ImportError:  # pragma: no cover - runtime guard
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
MAX_READ_BYTES = 200_000
SAFEGUARD_KEYWORDS = ["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE"]
VERSION = "1.1.0"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config() -> dict:
    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def read_file_text_safe(path: Path) -> str:
    if path.suffix.lower() not in SAFE_TEXT_EXT:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except Exception:  # pragma: no cover - best effort
        return ""


def warn(msg: str) -> None:
    print(f"[WARN] {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


DOMAIN_PATTERNS = {
    "checkpoint": re.compile(r"checkpoint", re.I),
    "token": re.compile(r"tokeniz", re.I),
    "train": re.compile(r"train", re.I),
    "eval": re.compile(r"eval", re.I),
    "data": re.compile(r"data", re.I),
    "safety": re.compile(r"safety|saniti", re.I),
    "logging": re.compile(r"log|tracking", re.I),
    "config": re.compile(r"config|hydra", re.I),
}


BASE_CAPABILITY_RULES = [
    {
        "id": "checkpointing",
        "facet_keys": ["checkpoint"],
        "required_patterns": ["save_checkpoint", "load"],
        "docs_keywords": ["checkpoint"],
    },
    {
        "id": "tokenization",
        "facet_keys": ["token"],
        "required_patterns": ["tokenizer", "encode"],
        "docs_keywords": ["token"],
    },
    {
        "id": "training-engine",
        "facet_keys": ["train"],
        "required_patterns": ["train", "epoch"],
        "docs_keywords": ["train"],
    },
    {
        "id": "evaluation-metrics",
        "facet_keys": ["eval"],
        "required_patterns": ["metric", "perplexity"],
        "docs_keywords": ["metric"],
    },
    {
        "id": "data-pipeline",
        "facet_keys": ["data"],
        "required_patterns": ["split", "loader"],
        "docs_keywords": ["data"],
    },
    {
        "id": "safety-security",
        "facet_keys": ["safety"],
        "required_patterns": ["secret", "sanitize"],
        "docs_keywords": ["safety"],
    },
    {
        "id": "logging-tracking",
        "facet_keys": ["logging"],
        "required_patterns": ["log", "mlflow"],
        "docs_keywords": ["log"],
    },
    {
        "id": "configuration",
        "facet_keys": ["config"],
        "required_patterns": ["config", "hydra"],
        "docs_keywords": ["config"],
    },
]

# Map capability id -> docs keywords to improve doc token scoring
DOCS_KEYWORDS_MAP = {rule["id"]: rule.get("docs_keywords", []) for rule in BASE_CAPABILITY_RULES}

# Optional synonyms to widen doc token search per capability (simple variants; offline-safe)
DOCS_SYNONYMS_MAP: Dict[str, List[str]] = {
    "checkpointing": ["ckpt", "checkpointing", "checkpoints"],
    "tokenization": ["tokenizer", "tokenize", "bpe", "sentencepiece"],
    "training-engine": ["trainer", "training"],
    "evaluation-metrics": ["metrics", "eval", "perplexity", "accuracy", "loss"],
    "data-pipeline": ["dataset", "dataloader", "loader", "ingest", "preprocess"],
    "safety-security": ["sanitize", "redact", "secret", "security"],
    "logging-tracking": ["tracking", "mlflow", "wandb", "tensorboard", "log"],
    "configuration": ["config", "hydra", "omegaconf", "yaml"],
}


def _expand_doc_tokens(capability_id: str, keywords: List[str] | None) -> List[str]:
    """
    Build a deterministic set of tokens for docs scoring:
      - explicit keywords (if provided) else leading token from capability id
      - capability-specific synonyms (DOCS_SYNONYMS_MAP)
      - naive plural/singular variants (add/remove 's'/'es')
    """

    base = [capability_id.split("-")[0]] if not keywords else list(keywords)
    syns = DOCS_SYNONYMS_MAP.get(capability_id, [])
    seeds = [t.lower() for t in (base + syns)]
    variants: set[str] = set()
    for t in seeds:
        t = t.strip().lower()
        if not t:
            continue
        variants.add(t)
        # naive pluralization/singularization variants
        if t.endswith("es"):
            variants.add(t[:-2])
        if t.endswith("s"):
            variants.add(t[:-1])
        else:
            variants.add(t + "s")
            variants.add(t + "es")
    return sorted(variants)


def stage_s1_index(cfg: dict) -> dict:
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    files_meta: List[dict] = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if (
            rel.startswith(".git/")
            or rel.startswith("audit_artifacts/")
            or rel.startswith("reports/")
        ):
            continue
        size = path.stat().st_size
        sha = _sha256_file(path) if size < 2_000_000 else None
        files_meta.append(
            {
                "path": rel,
                "ext": path.suffix.lower(),
                "size": size,
                "sha": sha,
            }
        )
    payload = {
        "generated": time.time(),
        "count": len(files_meta),
        "files": files_meta,
        "version": VERSION,
    }
    (artifacts_dir / "context_index.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload


def stage_s2_facets(cfg: dict, context_idx: dict) -> dict:
    facets = {key: [] for key in DOMAIN_PATTERNS}
    for file_info in context_idx["files"]:
        for key, pattern in DOMAIN_PATTERNS.items():
            if pattern.search(file_info["path"]):
                facets[key].append(file_info["path"])
    payload = {
        "generated": time.time(),
        "facets": facets,
        "version": VERSION,
    }
    (Path(cfg["output"]["artifacts_dir"]) / "facets.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload


def _read_file_cache(paths: List[str]) -> Dict[str, str]:
    cache: Dict[str, str] = {}
    for rel in paths:
        if rel not in cache:
            cache[rel] = read_file_text_safe(ROOT / rel)
    return cache


def _load_dynamic_detectors() -> List[Callable[[dict], dict]]:
    detectors_dir = ROOT / "scripts" / "space_traversal" / "detectors"
    funcs: List[Callable[[dict], dict]] = []
    if not detectors_dir.exists():
        return funcs
    for module_path in sorted(detectors_dir.glob("*.py")):
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as exc:  # pragma: no cover - plugin guard
                warn(f"Failed loading detector {module_path.name}: {exc}")
                continue
            detect_fn = getattr(module, "detect", None)
            if callable(detect_fn):
                sig = inspect.signature(detect_fn)
                if len(sig.parameters) == 1:
                    funcs.append(detect_fn)
                else:
                    warn(f"Detector {module_path.name} has invalid signature; skipping")
    return funcs


def stage_s3_capabilities(cfg: dict, facets: dict) -> List[dict]:
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    capabilities: List[dict] = []
    for rule in BASE_CAPABILITY_RULES:
        evidence_files: List[str] = []
        for facet_key in rule["facet_keys"]:
            evidence_files.extend(facets["facets"].get(facet_key, []))
        evidence_files = sorted(set(evidence_files))
        cache = _read_file_cache(evidence_files)
        pattern_hits = {
            pattern
            for pattern in rule["required_patterns"]
            if any(pattern in cache.get(path, "") for path in evidence_files)
        }
        capabilities.append(
            {
                "id": rule["id"],
                "evidence_files": evidence_files,
                "found_patterns": sorted(pattern_hits),
                "required_patterns": rule["required_patterns"],
            }
        )
    if cfg.get("capability_map", {}).get("dynamic"):
        detectors = _load_dynamic_detectors()
        context_path = artifacts_dir / "context_index.json"
        if not context_path.exists():
            warn("context_index.json missing for dynamic detectors; re-run S1")
        else:
            index_payload = json.loads(context_path.read_text(encoding="utf-8"))
            for detect_fn in detectors:
                try:
                    detector_result = detect_fn(index_payload)
                except Exception as exc:  # pragma: no cover - plugin guard
                    warn(f"Detector {detect_fn} raised: {exc}")
                    continue
                if not isinstance(detector_result, dict) or "id" not in detector_result:
                    warn("Invalid detector return structure; skipping")
                    continue
                for field in ("evidence_files", "found_patterns", "required_patterns"):
                    detector_result.setdefault(field, [])
                capabilities.append(
                    {
                        "id": detector_result["id"],
                        "evidence_files": sorted(set(detector_result["evidence_files"])),
                        "found_patterns": sorted(set(detector_result["found_patterns"])),
                        "required_patterns": detector_result["required_patterns"],
                        "meta": detector_result.get("meta", {}),
                    }
                )
    capabilities = sorted(capabilities, key=lambda item: item["id"])
    payload = {
        "generated": time.time(),
        "capabilities": capabilities,
        "version": VERSION,
    }
    (artifacts_dir / "capabilities_raw.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return capabilities


def _duplication_ratio(evidence_files: List[str]) -> float:
    stems = [Path(path).stem for path in evidence_files]
    if not stems:
        return 0.0
    counts: Dict[str, int] = {}
    for stem in stems:
        counts[stem] = counts.get(stem, 0) + 1
    duplicates = sum(value - 1 for value in counts.values() if value > 1)
    return min(1.0, duplicates / max(1, len(stems)))


def _estimate_test_depth(capability_id: str, evidence_files: List[str]) -> float:
    test_paths = [path for path in evidence_files if path.startswith("tests/")]
    token = capability_id.split("-")[0]
    tests_dir = ROOT / "tests"
    if tests_dir.exists():
        for candidate in sorted(tests_dir.rglob("*.py")):
            if token in candidate.name.lower():
                test_paths.append(candidate.relative_to(ROOT).as_posix())
    unique = {path for path in test_paths}
    if not evidence_files:
        return 0.0
    return min(1.0, len(unique) / len(set(evidence_files)))


def _safeguard_score(evidence_files: List[str], cache: Dict[str, str]) -> float:
    hits = 0
    for keyword in SAFEGUARD_KEYWORDS:
        if any(keyword in cache.get(path, "") for path in evidence_files):
            hits += 1
    return hits / len(SAFEGUARD_KEYWORDS) if SAFEGUARD_KEYWORDS else 0.0


def _docs_score(
    capability_id: str, cache: Dict[str, str], keywords: List[str] | None = None
) -> float:
    """
    Compute documentation score using capability-specific keywords when available.
    Falls back to the leading token of the capability ID.
    """

    docs = [path for path in cache if path.startswith("docs/") or path.endswith(".md")]
    tokens = _expand_doc_tokens(capability_id, keywords)
    hits = 0
    for path in docs:
        text = cache[path].lower()
        if any(token in text for token in tokens):
            hits += 1
    if not docs:
        return 0.0
    return min(1.0, hits / max(3, len(docs) * 0.1))


def stage_s4_scoring(cfg: dict, capabilities: List[dict]) -> List[dict]:
    weights = dict(cfg["weights"])
    total_weight = sum(weights.values())
    warnings: List[str] = []
    if abs(total_weight - 1.0) > 1e-9:
        warnings.append(f"weights_normalized_from:{total_weight}")
        weights = {key: value / total_weight for key, value in weights.items()}
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    cache: Dict[str, str] = {}
    # Optional component clamps (e.g., cap documentation influence at 0.9)
    component_caps: Dict[str, float] = (cfg.get("scoring", {}) or {}).get(
        "component_caps", {}
    ) or {}
    for capability in capabilities:
        for path in capability["evidence_files"]:
            cache.setdefault(path, read_file_text_safe(ROOT / path))
    for doc_path in sorted(ROOT.rglob("*.md")):
        rel = doc_path.relative_to(ROOT).as_posix()
        cache.setdefault(rel, read_file_text_safe(doc_path))
    scored: List[dict] = []
    for capability in capabilities:
        components = {
            "functionality": len(capability["found_patterns"])
            / max(1, len(capability["required_patterns"])),
            "consistency": 1.0 - _duplication_ratio(capability["evidence_files"]),
            "tests": _estimate_test_depth(capability["id"], capability["evidence_files"]),
            "safeguards": _safeguard_score(capability["evidence_files"], cache),
            "documentation": _docs_score(
                capability["id"], cache, DOCS_KEYWORDS_MAP.get(capability["id"])
            ),
        }
        # Apply per-component caps if configured
        if component_caps:
            components = {k: min(v, component_caps.get(k, 1.0)) for k, v in components.items()}
        score = sum(components[key] * weights[key] for key in weights)
        scored.append(
            {
                "id": capability["id"],
                "components": components,
                "score": round(score, 4),
                "evidence_files": capability["evidence_files"],
                "found_patterns": capability["found_patterns"],
            }
        )
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "capabilities_scored.json").write_text(
        json.dumps(
            {"generated": time.time(), "capabilities": scored, "version": VERSION}, indent=2
        ),
        encoding="utf-8",
    )
    (artifacts_dir / "_scoring_warnings.json").write_text(json.dumps(warnings), encoding="utf-8")
    return scored


def stage_s5_gaps(cfg: dict, scored_caps: List[dict]) -> dict:
    low_threshold = cfg["scoring"]["thresholds"]["low"]
    low: List[dict] = []
    for capability in scored_caps:
        if capability["score"] >= low_threshold:
            continue
        components = capability.get("components", {}) or {}
        enriched = dict(capability)
        if components:
            primary_deficit = min(components, key=lambda key: components[key])
            enriched["primary_deficit"] = primary_deficit
        low.append(enriched)
    payload = {
        "generated": time.time(),
        "low_maturity": low,
        "version": VERSION,
    }
    (Path(cfg["output"]["artifacts_dir"]) / "gaps.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload


def _render_template(cfg: dict, context: dict) -> Path:
    template_path = Path(cfg["output"]["matrix_template"])
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    concatenated = b""
    for tpl in sorted(template_path.parent.glob("*.j2")):
        concatenated += tpl.read_bytes()
    context["template_hash"] = _sha256_bytes(concatenated)
    output = template.render(**context)
    reports_dir = Path(cfg["output"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_file = reports_dir / f"capability_matrix_{stamp}.md"
    out_file.write_text(output, encoding="utf-8")
    return out_file


def stage_s6_render(cfg: dict, scored_caps: List[dict], gaps: dict) -> Path:
    context = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "capabilities": scored_caps,
        "gaps": gaps["low_maturity"],
        "weights": cfg["weights"],
    }
    return _render_template(cfg, context)


def stage_s7_manifest(cfg: dict) -> dict:
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    manifest = {
        "timestamp": time.time(),
        "version": VERSION,
        "repo_root_sha": _sha256_bytes(
            json.dumps(
                sorted([path.as_posix() for path in ROOT.rglob("*") if path.is_file()]),
                sort_keys=True,
            ).encode("utf-8")
        ),
        "artifacts": [],
        "weights": cfg["weights"],
        "warnings": [],
    }
    for path in artifacts_dir.glob("*.json"):
        if path.name.startswith("_"):
            continue
        manifest["artifacts"].append({"name": path.name, "sha": _sha256_file(path)})
    template_dir = Path(cfg["output"]["matrix_template"]).parent
    concatenated = b""
    for tpl in sorted(template_dir.glob("*.j2")):
        concatenated += tpl.read_bytes()
    manifest["template_hash"] = _sha256_bytes(concatenated)
    warn_file = artifacts_dir / "_scoring_warnings.json"
    if warn_file.exists():
        manifest["warnings"].extend(json.loads(warn_file.read_text(encoding="utf-8")))
    (ROOT / "audit_run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _load_capabilities_from_any(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(text)
        capabilities = data.get("capabilities", [])
    else:
        capabilities = []
        lines = text.splitlines()
        in_table = False
        for line in lines:
            if line.strip().startswith("| ID | Score"):
                in_table = True
                continue
            if in_table:
                if not line.strip().startswith("|"):
                    break
                parts = [part.strip() for part in line.strip().split("|")[1:-1]]
                if len(parts) >= 2 and parts[0] != "----":
                    try:
                        capabilities.append({"id": parts[0], "score": float(parts[1])})
                    except ValueError:
                        pass
        data = {"capabilities": capabilities}
    return {cap["id"]: cap.get("score") for cap in data.get("capabilities", [])}


def command_diff(args: argparse.Namespace, cfg: dict) -> None:
    old_path = Path(args.old)
    new_path = Path(args.new)
    if not old_path.exists() or not new_path.exists():
        print("One of the diff paths does not exist.", file=sys.stderr)
        sys.exit(2)
    old_caps = _load_capabilities_from_any(old_path)
    new_caps = _load_capabilities_from_any(new_path)
    all_ids = sorted(set(old_caps) | set(new_caps))
    regressions: List[tuple[str, float]] = []
    print("ID,OLD,NEW,DELTA")
    for capability_id in all_ids:
        old_score = old_caps.get(capability_id)
        new_score = new_caps.get(capability_id)
        if old_score is None or new_score is None:
            delta = "NA"
        else:
            delta_value = new_score - old_score
            delta = f"{delta_value:+.4f}"
            if cfg.get("options", {}).get("fail_on_score_regression"):
                threshold = float(cfg["options"].get("regression_delta_threshold", 0.0))
                if delta_value < -abs(threshold):
                    regressions.append((capability_id, delta_value))
        print(f"{capability_id},{old_score},{new_score},{delta}")
    if regressions:
        warn(f"Score regressions detected: {regressions}")
        sys.exit(3)


def command_explain(args: argparse.Namespace, cfg: dict) -> None:
    scored_file = Path(cfg["output"]["artifacts_dir"]) / "capabilities_scored.json"
    if not scored_file.exists():
        print("Scored file missing. Run stage S4 first.", file=sys.stderr)
        sys.exit(2)
    data = json.loads(scored_file.read_text(encoding="utf-8"))
    capability_id = args.capability
    target = next((cap for cap in data["capabilities"] if cap["id"] == capability_id), None)
    if not target:
        print(f"Capability {capability_id} not found.", file=sys.stderr)
        sys.exit(2)
    weights = dict(cfg["weights"])
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 1e-9:
        weights = {key: value / total_weight for key, value in weights.items()}
        warn(f"Weights normalized in explain view from {total_weight}")
    components = target["components"]
    print(f"Explain: {capability_id}")
    for key, value in components.items():
        weight = weights[key]
        print(
            f"  {key:14s} value={value:.4f} weight={weight:.3f} contribution={(value * weight):.4f}"
        )
    print(f"  Total score: {target['score']:.4f}")


def run_full(cfg: dict) -> None:
    context_idx = stage_s1_index(cfg)
    facets = stage_s2_facets(cfg, context_idx)
    capabilities = stage_s3_capabilities(cfg, facets)
    scored = stage_s4_scoring(cfg, capabilities)
    gaps = stage_s5_gaps(cfg, scored)
    stage_s6_render(cfg, scored, gaps)
    stage_s7_manifest(cfg)
    info("Audit complete.")


def run_stage(cfg: dict, stage_id: str) -> None:
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    context_path = artifacts_dir / "context_index.json"
    facets_path = artifacts_dir / "facets.json"
    if stage_id == "S1":
        stage_s1_index(cfg)
    elif stage_id == "S2":
        context_idx = (
            json.loads(context_path.read_text(encoding="utf-8"))
            if context_path.exists()
            else stage_s1_index(cfg)
        )
        stage_s2_facets(cfg, context_idx)
    elif stage_id == "S3":
        context_idx = (
            json.loads(context_path.read_text(encoding="utf-8"))
            if context_path.exists()
            else stage_s1_index(cfg)
        )
        facets = (
            json.loads(facets_path.read_text(encoding="utf-8"))
            if facets_path.exists()
            else stage_s2_facets(cfg, context_idx)
        )
        stage_s3_capabilities(cfg, facets)
    elif stage_id == "S4":
        raw = json.loads((artifacts_dir / "capabilities_raw.json").read_text(encoding="utf-8"))[
            "capabilities"
        ]
        stage_s4_scoring(cfg, raw)
    elif stage_id == "S5":
        scored = json.loads(
            (artifacts_dir / "capabilities_scored.json").read_text(encoding="utf-8")
        )["capabilities"]
        stage_s5_gaps(cfg, scored)
    elif stage_id == "S6":
        scored = json.loads(
            (artifacts_dir / "capabilities_scored.json").read_text(encoding="utf-8")
        )["capabilities"]
        gaps = json.loads((artifacts_dir / "gaps.json").read_text(encoding="utf-8"))
        stage_s6_render(cfg, scored, gaps)
    elif stage_id == "S7":
        stage_s7_manifest(cfg)
    else:
        print("Unknown stage ID", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Capability Audit Runner")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="Run full pipeline")
    stage_parser = sub.add_parser("stage", help="Run a single stage")
    stage_parser.add_argument("stage_id", help="Stage code (S1..S7)")
    diff_parser = sub.add_parser("diff", help="Diff two report or score files")
    diff_parser.add_argument("--old", required=True)
    diff_parser.add_argument("--new", required=True)
    explain_parser = sub.add_parser("explain", help="Explain a capability's score")
    explain_parser.add_argument("capability")
    args = parser.parse_args()
    cfg = load_config()
    os.makedirs(cfg["output"]["artifacts_dir"], exist_ok=True)
    if args.command == "run":
        run_full(cfg)
    elif args.command == "stage":
        run_stage(cfg, args.stage_id)
    elif args.command == "diff":
        command_diff(args, cfg)
    elif args.command == "explain":
        command_explain(args, cfg)
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
