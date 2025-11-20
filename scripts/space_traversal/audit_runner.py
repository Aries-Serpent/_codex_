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
import copy
import hashlib
import importlib.util
import inspect
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

try:
    from jinja2 import Environment, FileSystemLoader
    import yaml
except ImportError:
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
MAX_READ_BYTES = 200_000
SAFEGUARD_KEYWORDS = [
    "sha256",
    "checksum",
    "rng",
    "seed",
    "offline",
    "WANDB_MODE",
    # MCP-specific safeguards
    "confirm",
    "dry_run",
    "RateLimitExceeded",
    "Unauthorized",
    "ValidationError",
]
VERSION = "1.1.0"
METRICS_SCHEMA_VERSION = "2.0.0"

# Import scoring helpers (P1)
try:
    from scripts.space_traversal import capability_scoring
except Exception:
    capability_scoring = None  # fallback handled in runtime paths

# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------
def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()

def load_config() -> dict:
    """
    Load YAML config and allow optional override of SAFEGUARD_KEYWORDS
    via workflow.yaml:safeguards.keywords. This keeps backward compatibility.
    """
    global SAFEGUARD_KEYWORDS
    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    # Optional safeguard keyword overrides (P3)
    extra = cfg.get("safeguards", {}).get("keywords")
    if extra and isinstance(extra, list) and extra:
        SAFEGUARD_KEYWORDS = list(extra)
    return cfg

def read_file_text_safe(p: Path) -> str:
    if p.suffix.lower() not in SAFE_TEXT_EXT:
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except Exception:
        return ""

def warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)

def info(msg: str):
    print(f"[INFO] {msg}")

def merge_capability_entries(target: Dict[str, Any] | None, source: Dict[str, Any], canonical_id: str) -> Dict[str, Any]:
    """Merge two capability entries ensuring unique fields are combined."""

    def _sorted_unique(values):
        return sorted(set(values))

    if target is None:
        merged = copy.deepcopy(source)
    else:
        merged = copy.deepcopy(target)
        merged.setdefault("meta", {})

    merged["id"] = canonical_id
    merged.setdefault("evidence_files", [])
    merged.setdefault("found_patterns", [])
    merged.setdefault("required_patterns", [])

    merged["evidence_files"] = _sorted_unique(merged["evidence_files"] + source.get("evidence_files", []))
    merged["found_patterns"] = _sorted_unique(merged["found_patterns"] + source.get("found_patterns", []))
    merged["required_patterns"] = _sorted_unique(merged["required_patterns"] + source.get("required_patterns", []))

    src_meta = source.get("meta") or {}
    if src_meta:
        merged_meta = merged.setdefault("meta", {})
        for key, value in src_meta.items():
            merged_meta[key] = value

    return merged

def apply_overrides(
    capabilities: List[Dict[str, Any]],
    overrides: Dict[str, List[str]],
    fail_on_missing: bool = False,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Apply capability override mappings.

    Returns merged capabilities plus missing detector aliases.
    """
    cap_map: Dict[str, Dict[str, Any]] = {cap["id"]: cap for cap in capabilities}
    missing: List[str] = []

    for canonical_id, alias_list in overrides.items():
        target_entry = cap_map.get(canonical_id)
        used_aliases: List[str] = []
        missing_aliases: List[str] = []
        for alias in alias_list or []:
            alias_entry = cap_map.pop(alias, None)
            if alias_entry:
                target_entry = merge_capability_entries(target_entry, alias_entry, canonical_id)
                used_aliases.append(alias)
            else:
                missing_aliases.append(alias)

        if missing_aliases:
            missing.extend(f"{canonical_id}::{alias}" for alias in missing_aliases)

        if target_entry:
            target_entry = merge_capability_entries(target_entry, target_entry, canonical_id)
            meta = target_entry.setdefault("meta", {})
            if used_aliases:
                meta.setdefault("override_aliases", [])
                meta["override_aliases"] = sorted(set(meta["override_aliases"]) | set(used_aliases))
            cap_map[canonical_id] = target_entry

    merged_caps = sorted(cap_map.values(), key=lambda c: c["id"])
    if fail_on_missing and missing:
        warn(f"Missing override detectors: {missing}")
        raise SystemExit(5)

    return merged_caps, missing

# ---------------------------------------------------------------------------
# Stage Implementations
# ---------------------------------------------------------------------------
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

def load_dynamic_detectors() -> List[Callable]:
    detectors_dir = ROOT / "scripts" / "space_traversal" / "detectors"
    funcs = []
    if not detectors_dir.exists():
        return funcs
    for py in sorted(detectors_dir.glob("*.py")):
        spec = importlib.util.spec_from_file_location(py.stem, py)
        if not spec or not spec.loader:
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            warn(f"Failed loading detector {py.name}: {e}")
            continue
        if hasattr(module, "detect_v2") and callable(module.detect_v2):
            funcs.append(module.detect_v2)
        elif hasattr(module, "detect") and callable(module.detect):
            funcs.append(module.detect)
        else:
            warn(f"No usable detector function in {py.name}; skipping.")
    return funcs

def _normalize_detector_output(det: dict) -> dict:
    if "evidence" in det:
        normalized = []
        evidence_files = []
        for entry in det.get("evidence", []):
            if isinstance(entry, dict):
                path = entry.get("path")
                if path:
                    evidence_files.append(path)
                normalized.append(entry)
            elif isinstance(entry, str):
                evidence_files.append(entry)
                normalized.append({"path": entry})
        meta = det.get("meta", {})
        meta["_evidence_v2"] = normalized
    else:
        evidence_files = det.get("evidence_files", [])
        meta = det.get("meta", {})
    return {
        "id": det["id"],
        "evidence_files": sorted(set(evidence_files)),
        "found_patterns": sorted(set(det.get("found_patterns", []))),
        "required_patterns": det.get("required_patterns", []),
        "meta": meta,
    }

def stage_s1_index(cfg):
    out_dir = Path(cfg["output"]["artifacts_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    files_meta = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if (
            rel.startswith(".git/")
            or rel.startswith("audit_artifacts/")
            or rel.startswith("reports/")
        ):
            continue
        ext = p.suffix.lower()
        size = p.stat().st_size
        sha = _sha256_file(p) if size < 2_000_000 else None
        files_meta.append({"path": rel, "ext": ext, "size": size, "sha": sha})
    idx = {
        "generated": time.time(),
        "count": len(files_meta),
        "files": files_meta,
        "version": VERSION,
    }
    (out_dir / "context_index.json").write_text(json.dumps(idx, indent=2), encoding="utf-8")
    return idx

def stage_s2_facets(cfg, context_idx):
    facets = {k: [] for k in DOMAIN_PATTERNS}
    for f in context_idx["files"]:
        for key, rx in DOMAIN_PATTERNS.items():
            if rx.search(f["path"]):
                facets[key].append(f["path"])
    payload = {"generated": time.time(), "facets": facets, "version": VERSION}
    out = Path(cfg["output"]["artifacts_dir"]) / "facets.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

def stage_s3_capabilities(cfg, facets):
    out_dir = Path(cfg["output"]["artifacts_dir"])
    file_cache: Dict[str, str] = {}
    capabilities = []
    # Static rules
    for rule in BASE_CAPABILITY_RULES:
        evidence_files = []
        for facet in rule["facet_keys"]:
            evidence_files.extend(facets["facets"].get(facet, []))
        pattern_hits = set()
        for ef in evidence_files:
            fp = ROOT / ef
            if ef not in file_cache:
                file_cache[ef] = read_file_text_safe(fp)
            txt = file_cache[ef]
            for pat in rule["required_patterns"]:
                if pat in txt:
                    pattern_hits.add(pat)
        capabilities.append(
            {
                "id": rule["id"],
                "evidence_files": sorted(set(evidence_files)),
                "found_patterns": sorted(pattern_hits),
                "required_patterns": rule["required_patterns"],
            }
        )
    # Dynamic detectors
    if cfg.get("capability_map", {}).get("dynamic", False):
        dynamic_funcs = load_dynamic_detectors()
        context_idx_path = out_dir / "context_index.json"
        if not context_idx_path.exists():
            warn("context_index.json missing for dynamic detectors; re-run S1")
        else:
            ctx_index = json.loads(context_idx_path.read_text())
            for func in dynamic_funcs:
                try:
                    det = func(ctx_index)
                except Exception as e:
                    warn(f"Detector {func} raised: {e}")
                    continue
                if not isinstance(det, dict) or "id" not in det:
                    warn("Invalid detector return structure; skipping.")
                    continue
                capabilities.append(_normalize_detector_output(det))

    overrides_cfg = cfg.get("capability_map", {}).get("overrides", {})
    fail_on_missing = cfg.get("options", {}).get("fail_on_missing_detector", False)
    missing_detectors: List[str] = []
    if overrides_cfg:
        capabilities, missing_detectors = apply_overrides(capabilities, overrides_cfg, fail_on_missing)

    out_file = out_dir / "capabilities_raw.json"
    out_file.write_text(
        json.dumps(
            {
                "generated": time.time(),
                "capabilities": capabilities,
                "missing_detectors": missing_detectors,
                "version": VERSION,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"capabilities": capabilities, "missing_detectors": missing_detectors}

def duplication_ratio(evidence_files: List[str]) -> float:
    stems = [Path(f).stem for f in evidence_files]
    if not stems:
        return 0.0
    counts = {}
    for s in stems:
        counts[s] = counts.get(s, 0) + 1
    dup = sum(c - 1 for c in counts.values() if c > 1)
    return min(1.0, dup / max(1, len(stems)))

def load_coverage_map(*paths: Path) -> Dict[str, float]:
    """Load coverage percentages, supporting legacy and new filenames.

    The first readable path wins to preserve deterministic behavior while
    maintaining compatibility with historical artifacts (coverage_stats.json)
    and the newer coverage_map.json produced by coverage_ingest.
    """

    def _load(path: Path) -> Dict[str, float]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text())
        except Exception as exc:
            warn(f"Unable to parse coverage map {path}: {exc}")
            return {}
        coverage = {}
        for entry in data.get("capabilities", []):
            cid = entry.get("id")
            percent = entry.get("coverage_percent")
            if cid is None or percent is None:
                continue
            try:
                coverage[cid] = float(percent)
            except (TypeError, ValueError):
                continue
        return coverage

    for p in paths:
        coverage = _load(p)
        if coverage:
            return coverage
    return {}

def estimate_test_depth(cap_id: str, evidence_files: List[str]) -> float:
    test_files = [f for f in evidence_files if f.startswith("tests/")]
    token = cap_id.split("-")[0]
    # Add external test files referencing the token
    tests_dir = ROOT / "tests"
    if tests_dir.exists():
        for candidate in sorted(tests_dir.rglob("*.py")):
            if token in candidate.name.lower():
                test_files.append(candidate.relative_to(ROOT).as_posix())
    uniq = {f for f in test_files}
    if not evidence_files:
        return 0.0
    ratio = len(uniq) / len(set(evidence_files))
    return min(1.0, ratio)

def safeguard_score(evidence_files: List[str], file_cache: Dict[str, str]) -> float:
    hits = 0
    for kw in SAFEGUARD_KEYWORDS:
        if any(kw in file_cache.get(f, "") for f in evidence_files):
            hits += 1
    return hits / len(SAFEGUARD_KEYWORDS) if SAFEGUARD_KEYWORDS else 0.0

def docs_score(cap_id: str, file_cache: Dict[str, str]) -> float:
    """
    Prefer docs/ and top-level README-like markdown files for documentation scoring.
    Exclude audit_artifacts and logs to reduce noise (P3 tuning).
    """
    docs = []
    for p in file_cache:
        if p.startswith("audit_artifacts/") or p.startswith("logs/"):
            continue
        if p.startswith("docs/"):
            docs.append(p)
        elif p.count("/") == 0 and p.endswith(".md"):
            docs.append(p)
        elif p.endswith(".md") and p.startswith("_codex"):
            docs.append(p)
    token = cap_id.split("-")[0]
    hits = sum(1 for p in docs if token in file_cache[p].lower())
    if not docs:
        return 0.0
    return min(1.0, hits / max(3, len(docs) * 0.1))

def stage_s4_scoring(cfg, raw_payload):
    """
    P1: Centralize scoring logic by using capability_scoring helpers where available.
    - Normalize weights via capability_scoring.normalize_weights
    - Use capability_scoring.score_capability for aggregation (clamps applied in helper)
    - Preserve warnings file behavior for manifest
    """
    raw_caps = raw_payload["capabilities"]
    missing_detectors = raw_payload.get("missing_detectors", [])
    weights_cfg = cfg["weights"]
    total_w = sum(weights_cfg.values())
    warnings = []
    if abs(total_w - 1.0) > 1e-9:
        warnings.append(f"weights_normalized_from:{total_w}")

    if capability_scoring:
        try:
            weights_norm = capability_scoring.normalize_weights(weights_cfg)
        except Exception:
            weights_norm = ({k: v / total_w for k, v in weights_cfg.items()} if total_w > 0 else weights_cfg)
    else:
        weights_norm = ({k: v / total_w for k, v in weights_cfg.items()} if total_w > 0 else weights_cfg)

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    coverage_map = load_coverage_map(
        artifacts_dir / "coverage_map.json", artifacts_dir / "coverage_stats.json"
    )
    file_cache = {}
    for cap in raw_caps:
        for ef in cap.get("evidence_files", []):
            if ef not in file_cache:
                file_cache[ef] = read_file_text_safe(ROOT / ef)
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        if rel not in file_cache:
            file_cache[rel] = read_file_text_safe(p)

    scored = []
    for cap in raw_caps:
        functionality = len(cap.get("found_patterns", [])) / max(1, len(cap.get("required_patterns", [])))
        consistency = 1.0 - duplication_ratio(cap.get("evidence_files", []))
        tests = estimate_test_depth(cap.get("id"), cap.get("evidence_files", []))
        tests = max(tests, coverage_map.get(cap.get("id"), 0.0))
        safeguards = safeguard_score(cap.get("evidence_files", []), file_cache)
        documentation = docs_score(cap.get("id"), file_cache)
        missing_patterns = sorted([pat for pat in cap.get("required_patterns", []) if pat not in cap.get("found_patterns", [])])
        components = {
            "functionality": functionality,
            "consistency": consistency,
            "tests": tests,
            "safeguards": safeguards,
            "documentation": documentation,
        }

        if capability_scoring:
            score = capability_scoring.score_capability(components, weights_norm)
            try:
                explanation = capability_scoring.explain_score({"id": cap.get("id"), "components": components}, weights_norm)
            except Exception:
                explanation = {"id": cap.get("id"), "score": 0.0, "partials": {}}
        else:
            clamped = {k: max(0.0, min(1.0, v)) for k, v in components.items()}
            score = sum(clamped[k] * weights_norm.get(k, 0.0) for k in weights_norm)
            explanation = {"id": cap.get("id"), "score": round(score, 4), "partials": {}}

        scored.append(
            {
                "id": cap.get("id"),
                "components": components,
                "score": round(score, 4),
                "evidence_files": cap.get("evidence_files", []),
                "found_patterns": cap.get("found_patterns", []),
                "required_patterns": cap.get("required_patterns", []),
                "missing_patterns": missing_patterns,
                "meta": cap.get("meta", {}),
            }
        )

    out = artifacts_dir / "capabilities_scored.json"
    out.write_text(
        json.dumps(
            {
                "generated": time.time(),
                "capabilities": scored,
                "missing_detectors": missing_detectors,
                "version": VERSION,
            },
            indent=2,
        ),
        encoding="utf-8"
    )
    (artifacts_dir / "_scoring_warnings.json").write_text(json.dumps(warnings), encoding="utf-8")
    return scored

def stage_s5_gaps(cfg, scored_caps):
    thresholds = cfg["scoring"]["thresholds"]
    low = []
    for c in scored_caps:
        if c["score"] < thresholds["low"]:
            low.append(c)
    payload = {"generated": time.time(), "low_maturity": low, "version": VERSION}
    out = Path(cfg["output"]["artifacts_dir"]) / "gaps.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

def render_template(cfg, context):
    tpl_path = cfg["output"]["matrix_template"]
    tpl_dir = Path(tpl_path).parent
    env = Environment(
        loader=FileSystemLoader(str(tpl_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(Path(tpl_path).name)
    concatenated = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concatenated += t.read_bytes()
    context["template_hash"] = _sha256_bytes(concatenated)
    output = template.render(**context)
    reports_dir = Path(cfg["output"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_file = reports_dir / f"capability_matrix_{stamp}.md"
    out_file.write_text(output, encoding="utf-8")
    return out_file, stamp

def classify_level(score: float, thresholds: Dict[str, float]) -> str:
    low = thresholds.get("low", 0.0)
    medium = thresholds.get("medium", low)
    if score < low:
        return "low"
    if score < medium:
        return "medium"
    return "high"

def build_json_companion_payload(context: Dict[str, Any], markdown_name: str) -> Dict[str, Any]:
    thresholds = context["thresholds"]
    payload = {
        "schema_version": METRICS_SCHEMA_VERSION,
        "generated_at": context["timestamp"],
        "markdown_report": markdown_name,
        "weights": context["weights"],
        "thresholds": thresholds,
        "missing_detectors": context.get("missing_detectors", []),
        "capabilities": [],
        "gaps": context["gaps"],
    }
    for cap in context["capabilities"]:
        payload["capabilities"].append(
            {
                "id": cap["id"],
                "score": cap["score"],
                "level": classify_level(cap["score"], thresholds),
                "components": cap["components"],
                "evidence_count": len(cap.get("evidence_files", [])),
                "missing_patterns": cap.get("missing_patterns", []),
                "meta": cap.get("meta", {}),
            }
        )
    return payload

def render_json_companion(cfg, context, stamp: str, markdown_path: Path):
    payload = build_json_companion_payload(context, markdown_path.name)
    reports_dir = Path(cfg["output"]["reports_dir"])
    json_path = reports_dir / f"capability_matrix_{stamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json_path

def stage_s6_render(cfg, scored_caps, gaps, raw_payload):
    context = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "capabilities": scored_caps,
        "gaps": gaps["low_maturity"],
        "weights": cfg["weights"],
        "thresholds": cfg["scoring"]["thresholds"],
        "missing_detectors": raw_payload.get("missing_detectors", []),
    }
    markdown_path, stamp = render_template(cfg, context)
    json_path = render_json_companion(cfg, context, stamp, markdown_path)
    return markdown_path, json_path

def stage_s7_manifest(cfg):
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    manifest = {
        "timestamp": time.time(),
        "version": VERSION,
        "metrics_schema_version": METRICS_SCHEMA_VERSION,
        "repo_root_sha": _sha256_bytes(
            json.dumps(
                sorted([f.as_posix() for f in ROOT.rglob("*") if f.is_file()]), sort_keys=True
            ).encode()
        ),
        "artifacts": [],
        "reports": [],
        "weights": cfg["weights"],
        "warnings": [],
    }

    # Add normalized weights for transparency (P2)
    try:
        if capability_scoring:
            manifest["normalized_weights"] = capability_scoring.normalize_weights(cfg["weights"])
        else:
            total_w = sum(cfg["weights"].values())
            if total_w > 0:
                manifest["normalized_weights"] = {k: v / total_w for k, v in cfg["weights"].items()}
            else:
                manifest["normalized_weights"] = cfg["weights"]
    except Exception as e:
        warn(f"Could not compute normalized_weights for manifest: {e}")

    for p in artifacts_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        rel_path = p.resolve().relative_to(ROOT)
        manifest["artifacts"].append(
            {
                "name": p.name,
                "path": rel_path.as_posix(),
                "sha": _sha256_file(p),
                "size": p.stat().st_size,
                "format": p.suffix.lstrip("."),
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(p.stat().st_mtime)),
            }
        )

    reports_dir = Path(cfg["output"]["reports_dir"])
    if reports_dir.exists():
        for report in sorted(reports_dir.glob("capability_matrix_*.*")):
            rel = report.resolve().relative_to(ROOT)
            manifest["reports"].append(
                {
                    "name": report.name,
                    "path": rel.as_posix(),
                    "sha": _sha256_file(report),
                    "size": report.stat().st_size,
                    "format": report.suffix.lstrip("."),
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(report.stat().st_mtime)),
                }
            )

    tpl_dir = Path(cfg["output"]["matrix_template"]).parent
    concat = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concat += t.read_bytes()
    manifest["template_hash"] = _sha256_bytes(concat)

    warn_file = artifacts_dir / "_scoring_warnings.json"
    if warn_file.exists():
        manifest["warnings"].extend(json.loads(warn_file.read_text()))

    out = ROOT / "audit_run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest

def load_capabilities_from_any(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = {}
    if path.suffix == ".json":
        data = json.loads(text)
        caps = data.get("capabilities", [])
    else:
        lines = text.splitlines()
        caps = []
        in_table = False
        for ln in lines:
            if ln.strip().startswith("| ID | Score"):
                in_table = True
                continue
            if in_table:
                if not ln.strip().startswith("|"):
                    break
                parts = [p.strip() for p in ln.strip().split("|")[1:-1]]
                if len(parts) >= 8 and parts[0] != "----":
                    try:
                        caps.append(
                            {
                                "id": parts[0],
                                "score": float(parts[1]),
                            }
                        )
                    except ValueError:
                        pass
        data["capabilities"] = caps
    mapping = {c["id"]: c.get("score") for c in data.get("capabilities", [])}
    return mapping

def command_diff(args, cfg):
    old_path = Path(args.old)
    new_path = Path(args.new)
    if not old_path.exists() or not new_path.exists():
        print("One of the diff paths does not exist.", file=sys.stderr)
        sys.exit(2)
    old_map = load_capabilities_from_any(old_path)
    new_map = load_capabilities_from_any(new_path)
    all_ids = sorted(set(old_map) | set(new_map))
    regressions = []
    print("ID,OLD,NEW,DELTA")
    for cid in all_ids:
        o = old_map.get(cid)
        n = new_map.get(cid)
        if o is None or n is None:
            delta = "NA"
        else:
            delta_val = n - o
            delta = f"{delta_val:+.4f}"
            if cfg.get("options", {}).get("fail_on_score_regression", False):
                threshold = cfg["options"].get("regression_delta_threshold", 0.0)
                if delta_val < -abs(threshold):
                    regressions.append((cid, delta_val))
        print(f"{cid},{o},{n},{delta}")
    if regressions:
        warn(f"Score regressions detected: {regressions}")
        sys.exit(3)

def command_explain(args, cfg):
    scored_file = Path(cfg["output"]["artifacts_dir"]) / "capabilities_scored.json"
    if not scored_file.exists():
        print("Scored file missing. Run stage S4 first.", file=sys.stderr)
        sys.exit(2)
    data = json.loads(scored_file.read_text())
    cap_id = args.capability
    target = next((c for c in data["capabilities"] if c["id"] == cap_id), None)
    if not target:
        print(f"Capability {cap_id} not found.", file=sys.stderr)
        sys.exit(2)
    weights_cfg = cfg["weights"]
    if capability_scoring:
        try:
            explanation = capability_scoring.explain_score(target, weights_cfg)
            print(f"Explain: {cap_id}")
            for k, v in explanation["partials"].items():
                print(f"  {k:14s} value={v['component_value']:.4f} weight={v['weight']:.3f} contribution={v['contribution']:.4f}")
            print(f"  Total score: {explanation['score']:.4f}")
            return
        except Exception:
            pass
    total_w = sum(weights_cfg.values())
    if abs(total_w - 1.0) > 1e-9:
        weights = {k: v / total_w for k, v in weights_cfg.items()}
        warn(f"Weights normalized in explain view from {total_w}")
    else:
        weights = weights_cfg
    components = target["components"]
    print(f"Explain: {cap_id}")
    for k, v in components.items():
        w = weights[k]
        print(f"  {k:14s} value={v:.4f} weight={w:.3f} contribution={(v*w):.4f}")
    print(f"  Total score: {target['score']:.4f}")

# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def run_full(cfg):
    ctx = stage_s1_index(cfg)
    facets = stage_s2_facets(cfg, ctx)
    raw_payload = stage_s3_capabilities(cfg, facets)
    scored = stage_s4_scoring(cfg, raw_payload)
    gaps = stage_s5_gaps(cfg, scored)
    stage_s6_render(cfg, scored, gaps, raw_payload)
    stage_s7_manifest(cfg)
    info("Audit complete.")

def run_stage(cfg, stage_id: str):
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    context_idx = artifacts_dir / "context_index.json"
    facets_file = artifacts_dir / "facets.json"
    if stage_id == "S1":
        stage_s1_index(cfg)
    elif stage_id == "S2":
        idx = json.loads(context_idx.read_text()) if context_idx.exists() else stage_s1_index(cfg)
        stage_s2_facets(cfg, idx)
    elif stage_id == "S3":
        idx = json.loads(context_idx.read_text()) if context_idx.exists() else stage_s1_index(cfg)
        facets = (json.loads(facets_file.read_text()) if facets_file.exists() else stage_s2_facets(cfg, idx))
        stage_s3_capabilities(cfg, facets)
    elif stage_id == "S4":
        raw = json.loads((artifacts_dir / "capabilities_raw.json").read_text())
        stage_s4_scoring(cfg, raw)
    elif stage_id == "S5":
        scored = json.loads((artifacts_dir / "capabilities_scored.json").read_text())["capabilities"]
        stage_s5_gaps(cfg, scored)
    elif stage_id == "S6":
        scored_blob = json.loads((artifacts_dir / "capabilities_scored.json").read_text())
        scored = scored_blob["capabilities"]
        gaps = json.loads((artifacts_dir / "gaps.json").read_text())
        raw_payload = json.loads((artifacts_dir / "capabilities_raw.json").read_text())
        if "missing_detectors" not in raw_payload and "missing_detectors" in scored_blob:
            raw_payload["missing_detectors"] = scored_blob["missing_detectors"]
        stage_s6_render(cfg, scored, gaps, raw_payload)
    elif stage_id == "S7":
        stage_s7_manifest(cfg)
    else:
        print("Unknown stage ID", file=sys.stderr)
        sys.exit(2)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Capability Audit Runner")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("run", help="Run full pipeline")
    stage_p = sub.add_parser("stage", help="Run a single stage")
    stage_p.add_argument("stage_id", help="Stage code (S1..S7)")
    diff_p = sub.add_parser("diff", help="Diff two report or score files")
    diff_p.add_argument("--old", required=True, help="Old report/JSON path")
    diff_p.add_argument("--new", required=True, help="New report/JSON path")
    exp_p = sub.add_parser("explain", help="Explain a capability's score")
    exp_p.add_argument("capability", help="Capability ID to explain")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

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

if __name__ == "__main__":
    main()
