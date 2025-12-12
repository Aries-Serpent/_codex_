#!/usr/bin/env python
"""
Audit Runner Orchestrator — v1.5.0 (Space Traversal Workflow)

Capability audit pipeline for the _codex_ ML platform implementing the
Space Traversal Workflow v1.5.x specification.

Features:
 - S1-S7 pipeline stages with deterministic ordering and hashing
 - Dynamic detector loading from scripts/space_traversal/detectors/*.py
 - 5-component weighted scoring (functionality, consistency, tests, safeguards, documentation)
 - Coverage augmentation via coverage_map.json
 - Token-similarity duplication heuristic (configurable)
 - Policy validation via `validate` command
 - Trend aggregation (when enabled)
 - Manifest integrity chain with SHA256 hashes
 - v1.5.x: Trend database storage and queries
 - v1.5.x: Historical comparison with regression detection
 - v1.5.x: ASCII and HTML visualization dashboards

Commands:
 - run: Execute full pipeline (S1→S7)
 - stage <S1-S7>: Execute single stage
 - explain <cap-id>: Break down capability score
 - diff --old <a> --new <b>: Compare two audit runs
 - validate: Check quality gates (low maturity, missing detectors)
 - store-trend: Store current audit in trend database (v1.5.0)
 - show-trend <cap-id>: Show trend for a capability (v1.5.0)
 - check-regressions: Check for score regressions (v1.5.0)
 - compare-runs: Compare two audit runs with detailed analysis (v1.5.1)
 - dashboard: Generate HTML dashboard (v1.5.2)

Config: .copilot-space/workflow.yaml
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import hashlib
import time
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Any, Callable

# Try to import optional modules for enhanced features
try:
    from scripts.space_traversal import dup_similarity
    HAS_DUP_SIMILARITY = True
except ImportError:
    HAS_DUP_SIMILARITY = False

try:
    from scripts.space_traversal import coverage_ingest
    HAS_COVERAGE_INGEST = True
except ImportError:
    HAS_COVERAGE_INGEST = False

try:
    from scripts.space_traversal import trend_aggregator
    HAS_TREND_AGGREGATOR = True
except ImportError:
    HAS_TREND_AGGREGATOR = False

# v1.5.x trend database imports
try:
    from scripts.space_traversal.trend_db import TrendDatabase, create_snapshot_from_artifacts
    HAS_TREND_DB = True
except ImportError:
    HAS_TREND_DB = False

try:
    from scripts.space_traversal import trend_compare
    HAS_TREND_COMPARE = True
except ImportError:
    HAS_TREND_COMPARE = False

try:
    from scripts.space_traversal import viz_ascii
    HAS_VIZ_ASCII = True
except ImportError:
    HAS_VIZ_ASCII = False

try:
    from scripts.space_traversal import viz_html
    HAS_VIZ_HTML = True
except ImportError:
    HAS_VIZ_HTML = False

try:
    from scripts.space_traversal import viz_cli_builder
    HAS_VIZ_CLI_BUILDER = True
except ImportError:
    HAS_VIZ_CLI_BUILDER = False

try:
    from scripts.space_traversal import viz_api_collection
    HAS_VIZ_API_COLLECTION = True
except ImportError:
    HAS_VIZ_API_COLLECTION = False

try:
    from scripts.space_traversal import viz_swagger
    HAS_VIZ_SWAGGER = True
except ImportError:
    HAS_VIZ_SWAGGER = False

def import_yaml_from_sitepackages():
    """Import yaml from site-packages, avoiding local directory shadowing."""
    import sys
    import os
    original = list(sys.path)
    try:
        # Remove current directory and repository root from sys.path to avoid local shadowing
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        filtered = [p for p in sys.path if p and os.path.abspath(p) != repo_root and os.path.abspath(p) != '']
        sys.path = filtered
        import yaml  # noqa
        return yaml
    finally:
        sys.path = original

try:
    yaml = import_yaml_from_sitepackages()
    from jinja2 import Environment, FileSystemLoader
except Exception:
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    raise

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
CFG_PATHS = [
    ROOT / ".copilot-space" / "workflow.yaml",
    ROOT / "workflow.yaml",
]
SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
MAX_READ_BYTES = 200_000
# Expanded safeguard keywords per v1.4.0 spec - sorted for determinism
SAFEGUARD_KEYWORDS = [
    "baseline",
    "checksum",
    "deterministic",
    "manifest",
    "offline",
    "reproduce",
    "rng",
    "sanitize",
    "seed",
    "secret",
    "sha256",
    "WANDB_MODE",
]
VERSION = "1.5.0"

# Quality gate option keys (v1.4.0)
OPT_FAIL_ON_LOW_MATURITY = "fail_on_low_maturity"
OPT_FAIL_ON_MISSING_DETECTOR = "fail_on_missing_detector"
OPT_FAIL_ON_SCORE_REGRESSION = "fail_on_score_regression"
OPT_REGRESSION_DELTA_THRESHOLD = "regression_delta_threshold"

# Exit codes for quality gates
EXIT_LOW_MATURITY = 4
EXIT_MISSING_DETECTOR = 5
EXIT_REGRESSION = 3
EXIT_MISSING_ARTIFACTS = 2

# ---------------------------------------------------------------------------
# Utilities
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
    for p in CFG_PATHS:
        if p.exists():
            with open(p, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh)
                # ensure required output keys exist
                cfg.setdefault("output", {})
                cfg["output"].setdefault("artifacts_dir", "audit_artifacts")
                cfg["output"].setdefault("reports_dir", "reports")
                return cfg
    raise FileNotFoundError(f"Workflow config not found at any of: {CFG_PATHS}")

def read_file_text_safe(p: Path) -> str:
    if not p.exists() or p.suffix.lower() not in SAFE_TEXT_EXT:
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except Exception:
        return ""

def warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)

def info(msg: str):
    print(f"[INFO] {msg}")

# ---------------------------------------------------------------------------
# Config access helpers (robust to top-level vs nested config shapes)
# ---------------------------------------------------------------------------
def _get_matrix_template(cfg: dict) -> str:
    """
    Return the configured matrix template path.
    Accepts either:
      - cfg["output"]["matrix_template"]
      - cfg["matrix_template"] (top-level)
    """
    if not isinstance(cfg, dict):
        raise KeyError("cfg must be a dict")
    out = cfg.get("output") or {}
    mt = out.get("matrix_template")
    if mt:
        return mt
    mt2 = cfg.get("matrix_template")
    if mt2:
        return mt2
    raise KeyError("matrix_template not found in config. Provide either 'output.matrix_template' or top-level 'matrix_template'")

def _get_reports_dir(cfg: dict) -> str:
    """
    Return the configured reports directory.
    Accepts cfg["output"]["reports_dir"] or top-level cfg["reports_dir"].
    """
    out = cfg.get("output") or {}
    return out.get("reports_dir") or cfg.get("reports_dir") or "reports"

def _get_artifacts_dir(cfg: dict) -> str:
    out = cfg.get("output") or {}
    return out.get("artifacts_dir") or cfg.get("artifacts_dir") or "audit_artifacts"

# ---------------------------------------------------------------------------
# Deterministic file filter used by S1 and S7 (keep consistent)
# ---------------------------------------------------------------------------
def _iter_repo_files():
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT).as_posix()
        # filter out audit outputs & git metadata
        if rel.startswith(".git/") or rel.startswith("audit_artifacts/") or rel.startswith("reports/"):
            continue
        yield p

# ---------------------------------------------------------------------------
# Detector loader & normalizer (safe-loading with logs)
# ---------------------------------------------------------------------------
def load_dynamic_detectors() -> List[Callable]:
    detectors_dir = ROOT / "scripts" / "space_traversal" / "detectors"
    funcs = []
    if not detectors_dir.exists():
        return funcs
    for py in sorted(detectors_dir.glob("*.py")):
        try:
            spec = importlib.util.spec_from_file_location(py.stem, py)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Execute module in isolated namespace; warn about side-effects
                try:
                    spec.loader.exec_module(module)
                except Exception as e:
                    warn(f"Detector module {py.name} raised during import: {e} — skipping.")
                    continue
                # Prefer detect_v2 then detect
                if hasattr(module, "detect_v2") and callable(module.detect_v2):
                    funcs.append(module.detect_v2)
                    info(f"Loaded detect_v2 from {py.name}")
                elif hasattr(module, "detect") and callable(module.detect):
                    funcs.append(module.detect)
                    info(f"Loaded detect from {py.name}")
                else:
                    warn(f"No usable detector function in {py.name}; skipping.")
        except Exception as e:
            warn(f"Failed to load detector {py.name}: {e}")
    return funcs

def _normalize_detector_output(det: dict) -> dict:
    if not isinstance(det, dict) or "id" not in det:
        raise ValueError("Detector output must be dict with 'id'")
    meta = det.get("meta", {}) or {}
    docs_keywords = det.get("docs_keywords") or []
    normalized_docs_keywords = sorted({kw.lower() for kw in docs_keywords}) if docs_keywords else []
    if "evidence" in det:
        evidence_list = det.get("evidence", [])
        evidence_files = [e.get("path") for e in evidence_list if isinstance(e, dict) and e.get("path")]
        meta["_evidence_v2"] = evidence_list
    else:
        evidence_files = det.get("evidence_files") or []
    return {
        "id": det["id"],
        "evidence_files": sorted(set(evidence_files)),
        "found_patterns": sorted(set(det.get("found_patterns", []))),
        "required_patterns": det.get("required_patterns", []),
        "docs_keywords": normalized_docs_keywords,
        "meta": meta,
    }

# ---------------------------------------------------------------------------
# Stages S1..S7 (implementation unchanged except for template lookup usage)
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
    # v1.4.0 additions
    "serve": re.compile(r"serve|inference|api", re.I),
    "secret": re.compile(r"secret|baseline|redact", re.I),
    "status": re.compile(r"status|audit|report", re.I),
    "archive": re.compile(r"archive|bundle|manifest", re.I),
}

BASE_CAPABILITY_RULES = [
    {"id": "checkpointing", "facet_keys": ["checkpoint"], "required_patterns": ["save_checkpoint", "load"], "docs_keywords": ["checkpoint"]},
    {"id": "tokenization", "facet_keys": ["token"], "required_patterns": ["tokenizer", "encode"], "docs_keywords": ["token"]},
    {"id": "training-engine", "facet_keys": ["train"], "required_patterns": ["train", "epoch"], "docs_keywords": ["train"]},
    {"id": "evaluation-metrics", "facet_keys": ["eval"], "required_patterns": ["metric", "perplexity"], "docs_keywords": ["metric"]},
    {"id": "data-pipeline", "facet_keys": ["data"], "required_patterns": ["split", "loader"], "docs_keywords": ["data"]},
    {"id": "safety-security", "facet_keys": ["safety"], "required_patterns": ["secret", "sanitize"], "docs_keywords": ["safety"]},
    {"id": "logging-tracking", "facet_keys": ["logging"], "required_patterns": ["log", "mlflow"], "docs_keywords": ["log"]},
    {"id": "configuration", "facet_keys": ["config"], "required_patterns": ["config", "hydra"], "docs_keywords": ["config"]},
]

def stage_s1_index(cfg):
    out_dir = Path(_get_artifacts_dir(cfg))
    out_dir.mkdir(parents=True, exist_ok=True)
    files_meta = []
    for p in _iter_repo_files():
        rel = p.relative_to(ROOT).as_posix()
        ext = p.suffix.lower()
        size = p.stat().st_size
        sha = _sha256_file(p) if size < 2_000_000 else None
        files_meta.append({"path": rel, "ext": ext, "size": size, "sha": sha})
    idx = {"generated": time.time(), "count": len(files_meta), "files": files_meta, "version": VERSION}
    (out_dir / "context_index.json").write_text(json.dumps(idx, indent=2), encoding="utf-8")
    return idx

def stage_s2_facets(cfg, context_idx):
    facets = {k: [] for k in DOMAIN_PATTERNS}
    for f in context_idx["files"]:
        for key, rx in DOMAIN_PATTERNS.items():
            if rx.search(f["path"]):
                facets[key].append(f["path"])
    payload = {"generated": time.time(), "facets": facets, "version": VERSION}
    out = Path(_get_artifacts_dir(cfg)) / "facets.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

def stage_s3_capabilities(cfg, facets):
    out_dir = Path(_get_artifacts_dir(cfg))
    out_dir.mkdir(parents=True, exist_ok=True)
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
        capabilities.append({
            "id": rule["id"],
            "evidence_files": sorted(set(evidence_files)),
            "found_patterns": sorted(pattern_hits),
            "required_patterns": rule["required_patterns"],
            "docs_keywords": rule.get("docs_keywords", []),
            "meta": {},
        })
    # Dynamic detectors
    if cfg.get("capability_map", {}).get("dynamic", False):
        dynamic_funcs = load_dynamic_detectors()
        ctx_path = Path(_get_artifacts_dir(cfg)) / "context_index.json"
        if not ctx_path.exists():
            warn("context_index.json missing for dynamic detectors; re-run S1")
        else:
            ctx_index = json.loads(ctx_path.read_text())
            for func in dynamic_funcs:
                try:
                    det = func(ctx_index)
                except Exception as e:
                    warn(f"Detector {func} raised: {e}")
                    continue
                try:
                    normalized = _normalize_detector_output(det)
                except Exception as e:
                    warn(f"Detector {func} returned invalid shape: {e}")
                    continue
                capabilities.append(normalized)
    # Apply overrides merging (canonical <- aliases)
    overrides = cfg.get("capability_map", {}).get("overrides", {}) or {}
    if overrides:
        by_id = {c["id"]: c for c in capabilities}
        merged = {}
        missing_refs = []
        missing_by_canonical: Dict[str, List[str]] = {}
        for canonical, aliases in overrides.items():
            base = by_id.get(
                canonical,
                {
                    "id": canonical,
                    "evidence_files": [],
                    "found_patterns": [],
                    "required_patterns": [],
                    "docs_keywords": [],
                    "meta": {},
                },
            )
            base_from_existing = canonical in by_id
            alias_contributed = False
            for alias in aliases:
                if alias not in by_id:
                    missing_refs.append(alias)
                    missing_by_canonical.setdefault(canonical, []).append(alias)
                    continue
                a = by_id[alias]
                alias_contributed = True
                base["evidence_files"] = sorted(set(base.get("evidence_files", []) + a.get("evidence_files", [])))
                base["found_patterns"] = sorted(set(base.get("found_patterns", []) + a.get("found_patterns", [])))
                base["required_patterns"] = sorted(set(base.get("required_patterns", []) + a.get("required_patterns", [])))
                base["docs_keywords"] = sorted(set(base.get("docs_keywords", []) + a.get("docs_keywords", [])))
                base.setdefault("meta", {})
                base["meta"].setdefault("_aliases", [])
                if alias not in base["meta"]["_aliases"]:
                    base["meta"]["_aliases"].append(alias)
            if missing_by_canonical.get(canonical):
                base.setdefault("meta", {})
                base["meta"].setdefault("missing_detectors", [])
                for missing_alias in missing_by_canonical[canonical]:
                    if missing_alias not in base["meta"]["missing_detectors"]:
                        base["meta"]["missing_detectors"].append(missing_alias)
                base["meta"]["missing_detectors"] = sorted(base["meta"]["missing_detectors"])
            # ensure deterministic ordering of alias list
            if "meta" in base and "_aliases" in base["meta"]:
                base["meta"]["_aliases"] = sorted(base["meta"]["_aliases"])
            if not base_from_existing and not alias_contributed and not missing_by_canonical.get(canonical):
                # Avoid fabricating an empty capability when nothing real was merged
                continue
            merged[canonical] = base
        referenced = set(sum((aliases for aliases in overrides.values()), []))
        remaining = {k: v for k, v in by_id.items() if k not in referenced and k not in merged}
        capabilities = list(remaining.values()) + list(merged.values())
        if missing_refs:
            warn(f"Missing detector references in overrides: {missing_refs}")
            if cfg.get("options", {}).get("fail_on_missing_detector", False):
                sys.exit(5)
    # Sort capabilities deterministically
    capabilities = sorted(capabilities, key=lambda c: c["id"])
    out_file = Path(_get_artifacts_dir(cfg)) / "capabilities_raw.json"
    out_file.write_text(json.dumps({"generated": time.time(), "capabilities": capabilities, "version": VERSION}, indent=2), encoding="utf-8")
    return capabilities

def duplication_ratio(evidence_files: List[str], file_cache: Dict[str, str] = None, cfg: dict = None) -> float:
    """
    Compute duplication ratio using configured heuristic.
    
    Supports two modes:
    - simple: Original stem-based duplication (default, backward compatible)
    - token_similarity: Enhanced token-based similarity using dup_similarity module
    
    Args:
        evidence_files: List of evidence file paths
        file_cache: Optional file content cache (for token_similarity mode)
        cfg: Optional config dict (to determine heuristic mode)
    
    Returns:
        Duplication ratio in [0, 1]
    """
    # Determine heuristic mode
    heuristic = "simple"  # Default for backward compatibility
    if cfg:
        dup_cfg = cfg.get("scoring", {}).get("dup", {})
        heuristic = dup_cfg.get("heuristic", "simple")
    
    # Simple mode (original behavior)
    if heuristic == "simple" or file_cache is None:
        stems = [Path(f).stem for f in evidence_files]
        if not stems:
            return 0.0
        counts = {}
        for s in stems:
            counts[s] = counts.get(s, 0) + 1
        dup = sum(c - 1 for c in counts.values() if c > 1)
        return min(1.0, dup / max(1, len(stems)))
    
    # Token similarity mode
    if heuristic == "token_similarity":
        if not HAS_DUP_SIMILARITY:
            warn("dup_similarity module not available, falling back to simple mode")
            # Fallback code (same as below)
            stems = [Path(f).stem for f in evidence_files]
            if not stems:
                return 0.0
            counts = {}
            for s in stems:
                counts[s] = counts.get(s, 0) + 1
            dup = sum(c - 1 for c in counts.values() if c > 1)
            return min(1.0, dup / max(1, len(stems)))
        
        try:
            # Get parameters from config
            dup_cfg = cfg.get("scoring", {}).get("dup", {})
            threshold = dup_cfg.get("threshold", 0.7)
            max_pairwise = dup_cfg.get("max_pairwise", 1000)
            max_tokens = dup_cfg.get("max_tokens_per_file", 1000)
            
            return dup_similarity.duplication_ratio_token_similarity(
                evidence_files,
                file_cache,
                threshold=threshold,
                max_pairwise=max_pairwise,
                max_tokens_per_file=max_tokens
            )
        except Exception as e:
            warn(f"Failed to use token_similarity heuristic: {e}, falling back to simple")
            # Fallback to simple mode
            stems = [Path(f).stem for f in evidence_files]
            if not stems:
                return 0.0
            counts = {}
            for s in stems:
                counts[s] = counts.get(s, 0) + 1
            dup = sum(c - 1 for c in counts.values() if c > 1)
            return min(1.0, dup / max(1, len(stems)))
    
    # Unknown heuristic, use simple
    warn(f"Unknown duplication heuristic '{heuristic}', using simple")
    stems = [Path(f).stem for f in evidence_files]
    if not stems:
        return 0.0
    counts = {}
    for s in stems:
        counts[s] = counts.get(s, 0) + 1
    dup = sum(c - 1 for c in counts.values() if c > 1)
    return min(1.0, dup / max(1, len(stems)))

def estimate_test_depth(cap_id: str, evidence_files: List[str]) -> float:
    test_files = [f for f in evidence_files if f.startswith("tests/")]
    token = cap_id.split("-")[0]
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

DOCS_EXCLUDE_PREFIXES = (
    "reports/",
    "audit_artifacts/",
)

DOCS_INCLUDE_PREFIXES = (
    "docs/",
)

DOCS_STANDALONE_FILES = {
    "README.md",
}

DOCS_SYNONYMS_MAP = {
    "checkpointing": ["ckpt", "checkpointing", "checkpoints"],
    "tokenization": ["tokenizer", "tokenize", "bpe", "sentencepiece"],
    "training-engine": ["trainer", "training", "train"],
    "evaluation-metrics": ["metrics", "eval", "perplexity", "accuracy", "loss"],
    "data-pipeline": ["dataset", "dataloader", "loader", "ingest", "preprocess"],
    "safety-security": ["sanitize", "redact", "secret", "security", "baseline"],
    "logging-tracking": ["tracking", "mlflow", "wandb", "tensorboard", "log"],
    "configuration": ["config", "hydra", "omegaconf", "yaml"],
    "ml-serving": ["serve", "api", "inference", "predict", "fastapi"],
    "inference-serving": ["serve", "api", "inference", "predict", "fastapi"],
    "status-reporting": ["status", "audit", "report", "codex_status"],
    "archival-bundling": ["archive", "bundle", "manifest", "pointer"],
}


def _expand_doc_tokens(cap_id: str, docs_keywords: List[str]) -> set[str]:
    tokens = set()
    base = (cap_id or "").split("-")[0].lower()
    seeds = [base] if base else []
    seeds.extend(docs_keywords or [])
    for tok in seeds:
        if not tok:
            continue
        t = tok.lower()
        tokens.add(t)
        tokens.add(t.replace("-", " "))
        if not t.endswith("s"):
            tokens.add(f"{t}s")
    synonyms = DOCS_SYNONYMS_MAP.get(cap_id, []) + DOCS_SYNONYMS_MAP.get(base, [])
    for syn in synonyms:
        s = syn.lower()
        tokens.add(s)
        if not s.endswith("s"):
            tokens.add(f"{s}s")
    return tokens


def _docs_score(cap_id: str, file_cache: Dict[str, str], docs_keywords: List[str]) -> float:
    tokens = _expand_doc_tokens(cap_id, docs_keywords)

    def _is_doc(path: str) -> bool:
        if not path.endswith(".md"):
            return False
        if any(path.startswith(prefix) for prefix in DOCS_EXCLUDE_PREFIXES):
            return False
        if any(path.startswith(prefix) for prefix in DOCS_INCLUDE_PREFIXES):
            return True
        return path in DOCS_STANDALONE_FILES

    docs = [p for p in file_cache if _is_doc(p)]
    if not docs:
        return 0.0
    hits = 0
    for p in docs:
        text = file_cache.get(p, "").lower()
        if any(tok in text for tok in tokens):
            hits += 1
    return min(1.0, hits / max(3, len(docs) * 0.1))


def docs_score(cap_id: str, file_cache: Dict[str, str], docs_keywords: List[str] | None = None) -> float:
    return _docs_score(cap_id, file_cache, docs_keywords or [])

def stage_s4_scoring(cfg, raw_caps):
    try:
        from scripts.space_traversal import capability_scoring as cs
    except Exception:
        cs = None

    weights = cfg["weights"]
    total_w = sum(weights.values())
    warnings = []
    if abs(total_w - 1.0) > 1e-9:
        warnings.append(f"weights_normalized_from:{total_w}")
        if cs:
            weights = cs.normalize_weights(weights)
        else:
            weights = {k: v / total_w for k, v in weights.items()}

    artifacts_dir = Path(_get_artifacts_dir(cfg))
    file_cache = {}
    for cap in raw_caps:
        for ef in cap.get("evidence_files", []):
            if ef not in file_cache:
                file_cache[ef] = read_file_text_safe(ROOT / ef)
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        if rel not in file_cache:
            file_cache[rel] = read_file_text_safe(p)

    # Discover and parse coverage if enabled
    cov_map = {}
    if HAS_COVERAGE_INGEST:
        try:
            discovered_cov = coverage_ingest.discover_and_parse_coverage(cfg, artifacts_dir)
            if discovered_cov:
                cov_map = discovered_cov
        except Exception as e:
            warn(f"Coverage discovery failed: {e}")
    
    # Fallback: check for existing coverage_map.json
    if not cov_map:
        cov_path = artifacts_dir / "coverage_map.json"
        if cov_path.exists():
            try:
                cov_map = json.loads(cov_path.read_text())
            except Exception:
                warn("Failed to read coverage_map.json; ignoring coverage augmentation.")

    scored = []
    for cap in raw_caps:
        functionality = len(cap.get("found_patterns", [])) / max(1, len(cap.get("required_patterns", [])))
        consistency = 1.0 - duplication_ratio(cap.get("evidence_files", []), file_cache, cfg)
        tests = estimate_test_depth(cap.get("id"), cap.get("evidence_files", []))
        if cov_map:
            vals = []
            for ef in cap.get("evidence_files", []):
                if ef in cov_map:
                    vals.append(cov_map[ef].get("percent", 0.0))
            if vals:
                coverage_value = sum(vals) / len(vals)
                tests = max(tests, coverage_value)
        safeguards = safeguard_score(cap.get("evidence_files", []), file_cache)
        documentation = docs_score(cap.get("id"), file_cache, cap.get("docs_keywords", []))
        
        # Round components to 6 decimals for determinism
        components = {
            "functionality": round(functionality, 6),
            "consistency": round(consistency, 6),
            "tests": round(tests, 6),
            "safeguards": round(safeguards, 6),
            "documentation": round(documentation, 6),
        }
        if cs:
            score = cs.score_capability(components, weights)
            explanation = cs.explain_score({"id": cap.get("id"), "components": components}, weights)
        else:
            score = sum(components[k] * weights[k] for k in weights)
            explanation = {"id": cap.get("id"), "score": round(score, 6), "partials": {}}
        
        # Normalize for deterministic output: sort lists, round floats
        try:
            components_norm = {k: round(float(v), 6) for k, v in components.items()}
        except (ValueError, TypeError) as e:
            # Fallback: keep original values if conversion fails
            components_norm = components
            print(f"Warning: Could not normalize components for {cap.get('id')}: {e}", file=sys.stderr)
        scored.append({
            "id": cap.get("id"),
            "components": components_norm,
            "score": round(float(score), 6),
            "evidence_files": sorted(cap.get("evidence_files", [])),
            "found_patterns": sorted(cap.get("found_patterns", [])),
            "meta": cap.get("meta", {}),
            "explain": explanation
        })

    # Sort capabilities by id for determinism
    scored = sorted(scored, key=lambda x: x["id"])

    out = artifacts_dir / "capabilities_scored.json"
    # Use sort_keys and consistent separators for deterministic JSON output
    out.write_text(json.dumps({"generated": time.time(), "capabilities": scored, "version": VERSION}, 
                              indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    (artifacts_dir / "_scoring_warnings.json").write_text(json.dumps(warnings), encoding="utf-8")
    return scored

def stage_s5_gaps(cfg, scored_caps):
    """
    Stage S5: Gap Analysis
    
    Produces:
    - gaps.json: Low maturity capabilities (score < threshold)
    - component_gaps.json: Detailed component-level gaps analysis
    """
    thresholds = cfg["scoring"]["thresholds"]
    low_threshold = thresholds.get("low", 0.70)
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    
    low = []
    component_gaps = []
    
    for c in scored_caps:
        # Check for low maturity
        if c["score"] < low_threshold:
            low.append(c)
        
        # Analyze component-level gaps
        components = c.get("components", {})
        cap_id = c.get("id", "unknown")
        
        # Identify zero or low components
        zero_components = [k for k, v in components.items() if v == 0.0]
        low_components = [k for k, v in components.items() if 0.0 < v < 0.5]
        
        # Check for missing patterns
        found_patterns = set(c.get("found_patterns", []))
        required_patterns = set(c.get("required_patterns", []))
        missing_patterns = list(required_patterns - found_patterns)
        
        # Check for missing detectors in meta
        meta = c.get("meta", {})
        missing_detectors = meta.get("missing_detectors", [])
        
        if zero_components or low_components or missing_patterns or missing_detectors:
            component_gaps.append({
                "id": cap_id,
                "score": c["score"],
                "zero_components": sorted(zero_components),
                "low_components": sorted(low_components),
                "missing_patterns": sorted(missing_patterns),
                "missing_detectors": sorted(missing_detectors),
            })
    
    # Sort for determinism
    low = sorted(low, key=lambda x: (x["score"], x["id"]))
    component_gaps = sorted(component_gaps, key=lambda x: (x["score"], x["id"]))
    
    # Write gaps.json
    payload = {
        "generated": time.time(),
        "low_maturity": low,
        "low_threshold": low_threshold,
        "version": VERSION
    }
    out = artifacts_dir / "gaps.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    
    # Write component_gaps.json (v1.4.0 enhancement)
    component_payload = {
        "generated": time.time(),
        "component_gaps": component_gaps,
        "total_capabilities": len(scored_caps),
        "total_with_gaps": len(component_gaps),
        "version": VERSION
    }
    component_out = artifacts_dir / "component_gaps.json"
    component_out.write_text(json.dumps(component_payload, indent=2, sort_keys=True), encoding="utf-8")
    
    return payload

def render_template(cfg, context):
    # Resolve matrix template path robustly (top-level or nested under output)
    tpl_path = _get_matrix_template(cfg)
    tpl_dir = Path(tpl_path).parent
    env = Environment(loader=FileSystemLoader(str(tpl_dir)), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(Path(tpl_path).name)
    concatenated = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concatenated += t.read_bytes()
    context["template_hash"] = _sha256_bytes(concatenated)
    output = template.render(**context)
    reports_dir = Path(_get_reports_dir(cfg))
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    md_out = reports_dir / f"capability_matrix_{stamp}.md"
    json_out = reports_dir / f"capability_matrix_{stamp}.json"
    md_out.write_text(output, encoding="utf-8")
    comp = {
        "timestamp": context.get("timestamp"),
        "metrics_schema_version": cfg.get("metrics_schema_version", "2.0.0"),
        "template_hash": context["template_hash"],
        "weights": cfg["weights"],
        "scoring_thresholds": cfg.get("scoring", {}).get("thresholds", {}),
        "capabilities": sorted(context.get("capabilities", []), key=lambda c: c["id"]),
        "gaps": context.get("gaps", [])
    }
    json_out.write_text(json.dumps(comp, indent=2, sort_keys=True), encoding="utf-8")
    return md_out, json_out

def write_daily_status_issue(cfg, context, report_path: Path):
    """
    Produce a daily status issue body alongside the matrix report.

    This keeps the audit pipeline self-contained while enabling schedulers
    (e.g., nightly/cron workflows) to pick up the issue text directly from
    the reports directory and create an issue automatically.
    """
    reports_dir = Path(_get_reports_dir(cfg))
    reports_dir.mkdir(parents=True, exist_ok=True)
    date_str = time.strftime("%Y-%m-%d")
    issue_path = reports_dir / f"codex_status_update_{date_str}.md"

    # Sort ascending to surface the lowest-maturity items first.
    gaps = sorted(context.get("gaps", []), key=lambda g: g.get("score", 0.0))
    low_threshold = context.get("scoring", {}).get("thresholds", {}).get("low")
    low_threshold_display = low_threshold if low_threshold is not None else "n/a"
    total_caps = len(context.get("capabilities", []))
    report_ref = report_path
    if report_path.exists():
        try:
            report_ref = report_path.relative_to(ROOT)
        except ValueError:
            pass

    lines = [
        f"# [Daily Audit Status] {date_str}",
        "",
        f"- Generated: {context.get('timestamp')}",
        f"- Capabilities scored: {total_caps}",
        f"- Low maturity (< {low_threshold_display}): {len(gaps)}",
        f"- Matrix report: {report_ref}",
        "- Manifest (after S7): audit_run_manifest.json",
        "",
        "## Low Maturity Focus",
    ]
    if gaps:
        for g in gaps:
            lines.append(f"- {g.get('id')} — score {g.get('score'):.2f}")
    else:
        lines.append("No low-maturity capabilities detected.")

    lines.extend(
        [
            "",
            "## Next Steps",
            "- Review gaps above and plan remediation.",
            "- If acceptable, promote report and manifest to baseline.",
        ]
    )
    issue_path.write_text("\n".join(lines), encoding="utf-8")
    return issue_path

def stage_s6_render(cfg, scored_caps, gaps):
    context = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "capabilities": scored_caps,
        "gaps": gaps.get("low_maturity", []),
        "weights": cfg["weights"],
        "scoring": cfg.get("scoring", {}),
    }
    result = render_template(cfg, context)
    issue_path = write_daily_status_issue(cfg, context, result[0])
    info(f"Daily status issue body written to {issue_path}")
    # Backward compatibility: still return the same tuple from render_template.
    return result

def stage_s7_manifest(cfg):
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    files_for_hash = [p.relative_to(ROOT).as_posix() for p in _iter_repo_files()]
    repo_root_sha = _sha256_bytes(json.dumps(sorted(files_for_hash)).encode())
    try:
        from scripts.space_traversal import capability_scoring as cs
    except Exception:
        cs = None

    weights = cfg["weights"]
    total_w = sum(weights.values())
    normalized_weights = dict(weights)
    if total_w > 0 and abs(total_w - 1.0) > 1e-9:
        normalized_weights = cs.normalize_weights(weights) if cs else {k: v / total_w for k, v in weights.items()}

    manifest = {
        "timestamp": time.time(),
        "version": VERSION,
        "repo_root_sha": repo_root_sha,
        "artifacts": [],
        "weights": cfg["weights"],
        "normalized_weights": normalized_weights,
        "warnings": [],
        "metrics_schema_version": cfg.get("metrics_schema_version", "2.0.0"),
    }
    # Sort artifacts by name for determinism
    json_artifacts = sorted(artifacts_dir.glob("*.json"), key=lambda path: path.name)
    for p in json_artifacts:
        if p.name.startswith("_"):
            continue
        manifest["artifacts"].append({
            "name": p.name,
            "sha": _sha256_file(p),
            "size": p.stat().st_size,
            "format": "json",
            "generated_at": p.stat().st_mtime
        })
    
    # Add coverage_stats if coverage_map.json exists (v1.4.0 enhanced)
    cov_map_path = artifacts_dir / "coverage_map.json"
    if cov_map_path.exists():
        try:
            cov_data = json.loads(cov_map_path.read_text())
            percents = []
            for entry in cov_data.values():
                pct = entry.get("percent")
                if isinstance(pct, (int, float)):
                    percents.append(float(pct))
            percents = sorted(percents)
            if percents:
                manifest["coverage_stats"] = {
                    "total_files": len(percents),
                    "min_percent": round(percents[0], 6),
                    "max_percent": round(percents[-1], 6),
                    "avg_percent": round(sum(percents) / len(percents), 6),
                }
            else:
                manifest["coverage_stats"] = {
                    "total_files": 0,
                    "min_percent": 0.0,
                    "max_percent": 0.0,
                    "avg_percent": 0.0,
                }
        except Exception as e:
            manifest.setdefault("warnings", []).append(f"coverage_stats_error: {e}")
    
    tpl_dir = Path(_get_matrix_template(cfg)).parent
    concat = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concat += t.read_bytes()
    manifest["template_hash"] = _sha256_bytes(concat)
    warn_file = artifacts_dir / "_scoring_warnings.json"
    if warn_file.exists():
        manifest["warnings"].extend(json.loads(warn_file.read_text()))
    
    # Write manifest with sorted keys for determinism
    out = ROOT / "audit_run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest

# diff & explain functions
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
                if len(parts) >= 2 and parts[0] != "----":
                    try:
                        caps.append({
                            "id": parts[0],
                            "score": float(parts[1]),
                        })
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
        sys.exit(EXIT_MISSING_ARTIFACTS)
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
            if cfg.get("options", {}).get(OPT_FAIL_ON_SCORE_REGRESSION, False):
                threshold = cfg["options"].get(OPT_REGRESSION_DELTA_THRESHOLD, 0.0)
                if delta_val < -abs(threshold):
                    regressions.append((cid, delta_val))
        print(f"{cid},{o},{n},{delta}")
    if regressions:
        warn(f"Score regressions detected: {regressions}")
        sys.exit(EXIT_REGRESSION)

def command_explain(args, cfg):
    scored_file = Path(_get_artifacts_dir(cfg)) / "capabilities_scored.json"
    if not scored_file.exists():
        print("Scored file missing. Run stage S4 first.", file=sys.stderr)
        sys.exit(2)
    data = json.loads(scored_file.read_text())
    cap_id = args.capability
    target = next((c for c in data["capabilities"] if c["id"] == cap_id), None)
    if not target:
        print(f"Capability {cap_id} not found.", file=sys.stderr)
        sys.exit(2)
    weights = cfg["weights"]
    total_w = sum(weights.values())
    if abs(total_w - 1.0) > 1e-9:
        weights = {k: v / total_w for k, v in weights.items()}
        warn(f"Weights normalized in explain view from {total_w}")
    components = target["components"]
    print(f"Explain: {cap_id}")
    for k, v in components.items():
        w = weights.get(k, 0.0)
        print(f"  {k:14s} value={v:.4f} weight={w:.3f} contribution={(v*w):.4f}")
    explain_dir = Path(_get_artifacts_dir(cfg)) / "explain"
    if explain_dir.exists():
        explain_file = explain_dir / f"{cap_id}.json"
        if explain_file.exists():
            print(f"Explain JSON: {explain_file}")
    print(f"  Total score: {target['score']:.4f}")


def command_validate(cfg):
    """
    Validate policy gates per v1.4.0 spec.
    
    Checks:
    - fail_on_low_maturity: Non-zero exit if any capability score < thresholds.low
    - fail_on_missing_detector: Non-zero exit if detector in overrides is missing
    
    Exit Codes:
    - 0: All validations pass
    - EXIT_LOW_MATURITY (4): Low maturity capability detected
    - EXIT_MISSING_DETECTOR (5): Missing detector detected
    """
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    scored_file = artifacts_dir / "capabilities_scored.json"
    gaps_file = artifacts_dir / "gaps.json"
    
    if not scored_file.exists():
        print("capabilities_scored.json missing. Run audit pipeline first.", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    
    scored_data = json.loads(scored_file.read_text())
    capabilities = scored_data.get("capabilities", [])
    
    options = cfg.get("options", {})
    thresholds = cfg.get("scoring", {}).get("thresholds", {})
    low_threshold = thresholds.get("low", 0.70)
    
    violations = []
    
    # Check for low maturity
    if options.get(OPT_FAIL_ON_LOW_MATURITY, False):
        low_maturity = [c for c in capabilities if c.get("score", 0) < low_threshold]
        if low_maturity:
            for cap in low_maturity:
                violations.append(f"LOW_MATURITY: {cap['id']} score={cap['score']:.4f} < {low_threshold}")
    
    # Check for missing detectors
    if options.get(OPT_FAIL_ON_MISSING_DETECTOR, False):
        overrides = cfg.get("capability_map", {}).get("overrides", {})
        capability_ids = {c["id"] for c in capabilities}
        for canonical, aliases in overrides.items():
            if canonical not in capability_ids:
                # Check if any alias contributed
                aliases_found = [a for a in aliases if a in capability_ids]
                if not aliases_found:
                    # Check if capability has missing_detectors in meta
                    cap = next((c for c in capabilities if c["id"] == canonical), None)
                    if cap and cap.get("meta", {}).get("missing_detectors"):
                        violations.append(f"MISSING_DETECTOR: {canonical} has missing alias detectors: {cap['meta']['missing_detectors']}")
    
    # Report results
    if violations:
        print("Validation FAILED:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        
        # Determine exit code using constants
        has_low = any("LOW_MATURITY" in v for v in violations)
        has_missing = any("MISSING_DETECTOR" in v for v in violations)
        
        if has_low:
            sys.exit(EXIT_LOW_MATURITY)
        elif has_missing:
            sys.exit(EXIT_MISSING_DETECTOR)
        else:
            sys.exit(1)
    else:
        print("Validation PASSED: All quality gates satisfied.")
        # Also print summary
        print(f"  - Capabilities scored: {len(capabilities)}")
        if gaps_file.exists():
            gaps_data = json.loads(gaps_file.read_text())
            low_count = len(gaps_data.get("low_maturity", []))
            print(f"  - Low maturity (< {low_threshold}): {low_count}")
        print(f"  - fail_on_low_maturity: {options.get('fail_on_low_maturity', False)}")
        print(f"  - fail_on_missing_detector: {options.get('fail_on_missing_detector', False)}")


# ---------------------------------------------------------------------------
# v1.5.x Trend Commands
# ---------------------------------------------------------------------------
def cmd_store_trend(args, cfg):
    """Store current audit results in trend database."""
    import subprocess
    
    if not HAS_TREND_DB:
        print("Trend database module not available. Install dependencies.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    
    # Check if scored capabilities exist
    scored_path = artifacts_dir / "capabilities_scored.json"
    if not scored_path.exists():
        print(f"No capabilities_scored.json found at {scored_path}. Run audit first.", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    
    # Get git info
    git_commit = None
    git_branch = None
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        git_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git information is optional; proceed if unavailable (e.g., not a git repo or git not installed)
        pass
    
    # Get database path from config
    trends_cfg = cfg.get("trends", {})
    db_path = trends_cfg.get("database_path", str(artifacts_dir / "trends.db"))
    
    # Create and store snapshot
    db = TrendDatabase(db_path)
    snapshot = create_snapshot_from_artifacts(
        artifacts_dir, git_commit, git_branch
    )
    run_id = db.store_snapshot(snapshot)
    
    print(f"Stored audit snapshot: {run_id}")
    print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snapshot.timestamp))}")
    print(f"  Capabilities: {len(snapshot.capabilities)}")
    print(f"  Git: {git_branch}@{git_commit[:8] if git_commit else 'N/A'}")
    print(f"  Database: {db_path}")


def cmd_show_trend(args, cfg):
    """Show trend for a capability."""
    if not HAS_TREND_DB:
        print("Trend database module not available.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    trends_cfg = cfg.get("trends", {})
    db_path = trends_cfg.get("database_path", str(artifacts_dir / "trends.db"))
    
    if not Path(db_path).exists():
        print(f"No trend database found at {db_path}. Run 'store-trend' first.", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    
    db = TrendDatabase(db_path)
    trend = db.get_trend(args.capability, limit=args.limit, branch=args.branch)
    
    if not trend:
        print(f"No trend data for {args.capability}")
        return
    
    from datetime import datetime
    
    print(f"\nTrend for: {args.capability}")
    print("-" * 60)
    print(f"{'Timestamp':<20} {'Score':>8} {'Δ':>8} {'Branch':<15}")
    print("-" * 60)
    
    prev_score = None
    for entry in reversed(trend):
        score = entry["score"]
        delta = f"{score - prev_score:+.3f}" if prev_score is not None else "—"
        ts = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
        branch = entry["git_branch"] or "—"
        print(f"{ts:<20} {score:>8.3f} {delta:>8} {branch:<15}")
        prev_score = score
    
    # Show sparkline if viz_ascii available
    if HAS_VIZ_ASCII and len(trend) > 1:
        scores = [t["score"] for t in reversed(trend)]
        spark = viz_ascii.sparkline(scores, width=40)
        print(f"\nSparkline: {spark}")


def cmd_check_regressions(args, cfg):
    """Check for score regressions."""
    if not HAS_TREND_DB:
        print("Trend database module not available.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    trends_cfg = cfg.get("trends", {})
    db_path = trends_cfg.get("database_path", str(artifacts_dir / "trends.db"))
    
    if not Path(db_path).exists():
        print(f"No trend database found at {db_path}. Run 'store-trend' first.", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    
    db = TrendDatabase(db_path)
    regressions = db.get_regressions(
        threshold=args.threshold,
        lookback_runs=args.lookback,
    )
    
    if not regressions:
        print("✅ No regressions detected")
        return 0
    
    print(f"⚠️  {len(regressions)} regression(s) detected:\n")
    for reg in regressions:
        severity_icon = "🔴" if reg["severity"] == "high" else "🟡"
        print(f"{severity_icon} {reg['capability_id']}")
        print(f"   Current: {reg['current_score']:.3f}")
        print(f"   Previous avg: {reg['previous_avg']:.3f}")
        print(f"   Delta: {reg['delta']:+.3f}")
        print()
    
    # Return non-zero exit code if high severity regressions
    if any(r["severity"] == "high" for r in regressions):
        return 1
    return 0


def cmd_compare_runs(args, cfg):
    """Compare two audit runs with detailed analysis."""
    if not HAS_TREND_COMPARE:
        print("Trend compare module not available.", file=sys.stderr)
        sys.exit(2)
    
    old_path = Path(args.old)
    new_path = Path(args.new)
    
    if not old_path.exists():
        print(f"Old file not found: {old_path}", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    if not new_path.exists():
        print(f"New file not found: {new_path}", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    
    results = trend_compare.compare_runs(old_path, new_path, threshold=args.threshold)
    
    # Generate report if output specified
    if args.output:
        output_path = Path(args.output)
        trend_compare.generate_comparison_report(results, output_path)
        print(f"Comparison report written to: {output_path}")
    
    # Print summary
    regressions = [r for r in results if r.is_regression]
    improvements = [r for r in results if r.delta > 0.02]
    
    print(f"\nComparison: {old_path.name} → {new_path.name}")
    print("-" * 50)
    print(f"Total capabilities: {len(results)}")
    print(f"Regressions: {len(regressions)}")
    print(f"Improvements: {len(improvements)}")
    
    if regressions:
        print("\n⚠️  Regressions:")
        for r in sorted(regressions, key=lambda x: x.delta)[:5]:
            print(f"  {r.capability_id}: {r.old_score:.3f} → {r.new_score:.3f} ({r.delta:+.3f})")
    
    if improvements:
        print("\n✅ Improvements:")
        for r in sorted(improvements, key=lambda x: -x.delta)[:5]:
            print(f"  {r.capability_id}: {r.old_score:.3f} → {r.new_score:.3f} ({r.delta:+.3f})")
    
    return 1 if any(r.regression_severity == "high" for r in regressions) else 0


def cmd_dashboard(args, cfg):
    """Generate HTML dashboard."""
    if not HAS_VIZ_HTML:
        print("Visualization HTML module not available.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    scored_path = artifacts_dir / "capabilities_scored.json"
    
    if not scored_path.exists():
        print(f"No capabilities_scored.json found. Run audit first.", file=sys.stderr)
        sys.exit(EXIT_MISSING_ARTIFACTS)
    
    # Load capabilities
    with open(scored_path, encoding="utf-8") as f:
        scored_data = json.load(f)
    capabilities = scored_data.get("capabilities", [])
    
    # Load trend data if available
    trend_data = []
    if HAS_TREND_DB:
        trends_cfg = cfg.get("trends", {})
        db_path = trends_cfg.get("database_path", str(artifacts_dir / "trends.db"))
        if Path(db_path).exists():
            db = TrendDatabase(db_path)
            # Get average scores per run
            with __import__('sqlite3').connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT r.timestamp, AVG(cs.score) as avg_score
                    FROM capability_scores cs
                    JOIN audit_runs r ON cs.run_id = r.run_id
                    GROUP BY r.run_id
                    ORDER BY r.timestamp DESC
                    LIMIT 30
                """)
                for row in cursor.fetchall():
                    trend_data.append({"timestamp": row[0], "avg_score": row[1]})
    
    # Get regressions if available
    regressions = []
    if HAS_TREND_DB and Path(db_path).exists():
        db = TrendDatabase(db_path)
        regressions = db.get_regressions()
    
    # Determine output path
    output_path = Path(args.output) if args.output else artifacts_dir / "dashboard.html"
    
    # Generate dashboard
    repo_name = cfg.get("repo_name", "Repository")
    viz_html.generate_dashboard(
        capabilities=capabilities,
        trend_data=trend_data,
        output_path=output_path,
        repo_name=repo_name,
        version=VERSION,
        regressions=regressions,
    )
    
    print(f"Dashboard generated: {output_path}")


def cmd_cli_builder(args, cfg):
    """Generate CLI builder HTML interface."""
    if not HAS_VIZ_CLI_BUILDER:
        print("CLI builder module not available.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    output_path = Path(args.output) if args.output else artifacts_dir / "cli_builder.html"
    repo_name = cfg.get("repo_name", "Repository")
    
    viz_cli_builder.generate_cli_builder(
        output_path=output_path,
        repo_name=repo_name,
        version=VERSION,
    )
    
    print(f"CLI builder generated: {output_path}")


def cmd_api_collection(args, cfg):
    """Generate API collection HTML interface with adjusters."""
    if not HAS_VIZ_API_COLLECTION:
        print("API collection module not available.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    output_path = Path(args.output) if args.output else artifacts_dir / "api_collection.html"
    repo_name = cfg.get("repo_name", "Repository")
    
    viz_api_collection.generate_api_collection(
        output_path=output_path,
        repo_name=repo_name,
        version=VERSION,
    )
    
    print(f"API collection generated: {output_path}")


def cmd_swagger_docs(args, cfg):
    """Generate Swagger/OpenAPI-style documentation HTML."""
    if not HAS_VIZ_SWAGGER:
        print("Swagger docs module not available.", file=sys.stderr)
        sys.exit(2)
    
    artifacts_dir = Path(_get_artifacts_dir(cfg))
    output_path = Path(args.output) if args.output else artifacts_dir / "api_docs.html"
    repo_name = cfg.get("repo_name", "Repository")
    
    viz_swagger.generate_swagger_docs(
        output_path=output_path,
        repo_name=repo_name,
        version=VERSION,
    )
    
    print(f"Swagger API docs generated: {output_path}")


# orchestrator
def run_full(cfg):
    ctx = stage_s1_index(cfg)
    facets = stage_s2_facets(cfg, ctx)
    raw = stage_s3_capabilities(cfg, facets)
    scored = stage_s4_scoring(cfg, raw)
    gaps = stage_s5_gaps(cfg, scored)
    stage_s6_render(cfg, scored, gaps)
    stage_s7_manifest(cfg)
    
    # Optional: Run trend aggregation if enabled in config
    trends_cfg = cfg.get("trends", {})
    if trends_cfg.get("enabled", False) and HAS_TREND_AGGREGATOR:
        try:
            artifacts_dir = Path(_get_artifacts_dir(cfg))
            reports_dir = Path(_get_reports_dir(cfg))
            lookback_days = trends_cfg.get("lookback_days", None)
            
            info("Running trend aggregation...")
            trend_data = trend_aggregator.aggregate_trends(
                artifacts_dir, reports_dir, lookback_days, None
            )
            
            # Generate report
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = artifacts_dir / "trends" / f"trend_report_{timestamp}.md"
            trend_aggregator.generate_trend_report(trend_data, output_path)
            info(f"Trend report generated: {output_path}")
        except Exception as e:
            warn(f"Trend aggregation failed: {e}")
    elif trends_cfg.get("enabled", False) and not HAS_TREND_AGGREGATOR:
        warn("Trends enabled but trend_aggregator module not available")
    
    # v1.5.0: Auto-store in trend database if enabled
    if trends_cfg.get("auto_store", False) and HAS_TREND_DB:
        try:
            import subprocess
            artifacts_dir = Path(_get_artifacts_dir(cfg))
            db_path = trends_cfg.get("database_path", str(artifacts_dir / "trends.db"))
            
            # Get git info
            git_commit = None
            git_branch = None
            try:
                git_commit = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
                ).strip()
                git_branch = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True, stderr=subprocess.DEVNULL
                ).strip()
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                # It's OK if git info is unavailable (e.g., not a git repo); leave commit/branch as None.
                warn(f"Could not retrieve git info: {e}")
            
            db = TrendDatabase(db_path)
            snapshot = create_snapshot_from_artifacts(artifacts_dir, git_commit, git_branch)
            run_id = db.store_snapshot(snapshot)
            info(f"Stored audit snapshot in trend database: {run_id[:8]}...")
        except Exception as e:
            warn(f"Auto-store trend failed: {e}")
    
    info("Audit complete.")

def run_stage(cfg, stage_id: str):
    artifacts_dir = Path(_get_artifacts_dir(cfg))
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
        facets = json.loads(facets_file.read_text()) if facets_file.exists() else stage_s2_facets(cfg, idx)
        stage_s3_capabilities(cfg, facets)
    elif stage_id == "S4":
        raw = json.loads((artifacts_dir / "capabilities_raw.json").read_text())["capabilities"]
        stage_s4_scoring(cfg, raw)
    elif stage_id == "S5":
        scored = json.loads((artifacts_dir / "capabilities_scored.json").read_text())["capabilities"]
        stage_s5_gaps(cfg, scored)
    elif stage_id == "S6":
        scored = json.loads((artifacts_dir / "capabilities_scored.json").read_text())["capabilities"]
        gaps = json.loads((artifacts_dir / "gaps.json").read_text())
        stage_s6_render(cfg, scored, gaps)
    elif stage_id == "S7":
        stage_s7_manifest(cfg)
    elif stage_id == "TRENDS":
        # Optional trend aggregation stage
        if not HAS_TREND_AGGREGATOR:
            warn("trend_aggregator module not available")
            sys.exit(2)
        
        try:
            reports_dir = Path(_get_reports_dir(cfg))
            trends_cfg = cfg.get("trends", {})
            lookback_days = trends_cfg.get("lookback_days", None)
            
            trend_data = trend_aggregator.aggregate_trends(
                artifacts_dir, reports_dir, lookback_days, None
            )
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = artifacts_dir / "trends" / f"trend_report_{timestamp}.md"
            trend_aggregator.generate_trend_report(trend_data, output_path)
            info(f"Trend report generated: {output_path}")
        except Exception as e:
            warn(f"Trend aggregation failed: {e}")
            sys.exit(2)
    else:
        print("Unknown stage ID", file=sys.stderr)
        sys.exit(2)

def main():
    parser = argparse.ArgumentParser(description="Capability Audit Runner v1.5.x")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="Run full pipeline")
    stage_p = sub.add_parser("stage", help="Run a single stage")
    stage_p.add_argument("stage_id", help="Stage code (S1..S7, TRENDS)")
    diff_p = sub.add_parser("diff", help="Diff two report or score files")
    diff_p.add_argument("--old", required=True, help="Old report/JSON path")
    diff_p.add_argument("--new", required=True, help="New report/JSON path")
    exp_p = sub.add_parser("explain", help="Explain a capability's score")
    exp_p.add_argument("capability", help="Capability ID to explain")
    sub.add_parser("validate", help="Validate policy gates (low maturity, missing detectors)")
    
    # v1.5.0 trend commands
    sub.add_parser("store-trend", help="Store current audit in trend database (v1.5.0)")
    
    show_trend_p = sub.add_parser("show-trend", help="Show trend for a capability (v1.5.0)")
    show_trend_p.add_argument("capability", help="Capability ID to show trend for")
    show_trend_p.add_argument("--limit", type=int, default=30, help="Number of entries to show")
    show_trend_p.add_argument("--branch", help="Filter by git branch")
    
    check_reg_p = sub.add_parser("check-regressions", help="Check for score regressions (v1.5.0)")
    check_reg_p.add_argument("--threshold", type=float, default=0.02, help="Regression threshold")
    check_reg_p.add_argument("--lookback", type=int, default=5, help="Number of runs to compare")
    
    # v1.5.1 comparison commands
    compare_p = sub.add_parser("compare-runs", help="Compare two audit runs with detailed analysis (v1.5.1)")
    compare_p.add_argument("--old", required=True, help="Old capabilities_scored.json path")
    compare_p.add_argument("--new", required=True, help="New capabilities_scored.json path")
    compare_p.add_argument("--output", help="Output path for comparison report")
    compare_p.add_argument("--threshold", type=float, default=0.02, help="Regression threshold")
    
    # v1.5.2 dashboard command
    dashboard_p = sub.add_parser("dashboard", help="Generate HTML dashboard (v1.5.2)")
    dashboard_p.add_argument("--output", help="Output path for dashboard HTML")
    
    # v1.5.3 CLI builder command
    cli_builder_p = sub.add_parser("cli-builder", help="Generate interactive CLI builder HTML (v1.5.3)")
    cli_builder_p.add_argument("--output", help="Output path for CLI builder HTML")
    
    # v1.5.4 API collection command
    api_collection_p = sub.add_parser("api-collection", help="Generate API collection HTML with adjusters (v1.5.4)")
    api_collection_p.add_argument("--output", help="Output path for API collection HTML")
    
    # v1.5.4 Swagger docs command
    swagger_p = sub.add_parser("api-docs", help="Generate Swagger/OpenAPI-style API documentation (v1.5.4)")
    swagger_p.add_argument("--output", help="Output path for API docs HTML")
    
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
    elif args.command == "validate":
        command_validate(cfg)
    elif args.command == "store-trend":
        cmd_store_trend(args, cfg)
    elif args.command == "show-trend":
        cmd_show_trend(args, cfg)
    elif args.command == "check-regressions":
        exit_code = cmd_check_regressions(args, cfg)
        sys.exit(exit_code)
    elif args.command == "compare-runs":
        exit_code = cmd_compare_runs(args, cfg)
        sys.exit(exit_code)
    elif args.command == "dashboard":
        cmd_dashboard(args, cfg)
    elif args.command == "cli-builder":
        cmd_cli_builder(args, cfg)
    elif args.command == "api-collection":
        cmd_api_collection(args, cfg)
    elif args.command == "api-docs":
        cmd_swagger_docs(args, cfg)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
