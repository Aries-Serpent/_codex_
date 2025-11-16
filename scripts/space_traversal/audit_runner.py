#!/usr/bin/env python
"""
Audit Runner Orchestrator for Copilot Space Traversal Workflow (v1.4.0)

Enhancements (v1.4.0 P5 Integration):
 - Scoring consumes token similarity (token_similarity.json) and coverage stats (coverage_stats.json)
   • consistency := (1 - duplication_ratio) * similarity_index (if available per capability)
   • tests := max(existing_tests_ratio, coverage_percent) (if available per capability)
 - Manifest auto-runs prefix validation (validate_prefixes.py --warn-only) and aggregates its warnings
 - Manifest aggregates security severity classification from security_severity.json (if present)
 - Knobs snapshot preserved (when SUMMARY_ENABLE=1)
 - Safeguards influenced by severity factor (additive/penalty/none modes)

Enhancements (v1.3.0 P3):
 - Aggregate warnings from content_filter_report.json and bundle pointer JSONs
 - Optional knobs snapshot in manifest (via parse_knobs.summarize_effective)
 - Prefix validation warnings integration
 - Add depth gating for configurable recursion control (AUDIT_DEPTH)
 - Integrate knob parsing warnings into manifest
 - Propagate required_patterns into scored artifacts (S4)
 - Compute missing_patterns and write into gaps.json (S5)
 - Emit component_gaps.json with zero components (S5)
 - Add 'validate' command for policy gates (low threshold, missing detectors)
 - Include missing_detectors and thresholds snapshot in manifest (S7)
 - Pass thresholds into render context; template shows true low threshold

Note: Offline only, no network calls. Determinism preserved via sorted traversal and stable merges.
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

# Import knob parser for depth gating
try:
    from scripts.config.parse_knobs import (
        get_depth,
        get_warnings as get_knob_warnings,
        normalize_from_env,
        summarize_effective,
    )
except ImportError:
    # Fallback if not available
    def get_depth():
        return 3, False

    def get_knob_warnings():
        return []

    def normalize_from_env():
        import os as _os
        allowed_prefixes = [
            "CODEX_", "AUDIT_", "CONTENT_FILTER_", "ALLOWLIST_", "PII_",
            "MAX_BUNDLE_", "ARCHIVE_", "BUNDLE_PREFIX_", "AST_",
            "TOKEN_SIMILARITY", "COVERAGE", "SECURITY_SEVERITY", "SEVERITY_",
            "PREFIX_VALIDATE_", "SUMMARY_", "SYNONYM_", "SECRET_CONTEXT_",
            "FEDERATION_", "MANIFEST_EXTENDED_", "COPILOT_", "GITHUB_"
        ]
        filtered = {
            k: v for k, v in _os.environ.items()
            if any(k.startswith(prefix) for prefix in allowed_prefixes)
        }
        return filtered, []
    def summarize_effective(knobs):
        return {k: v for k, v in knobs.items() if v not in (None, "", [], {})}


try:
    from scripts.space_traversal.capability_scoring import (
        aggregate_scores,
        explain_score,
        normalize_weights,
        score_capability,
    )
except Exception:
    try:
        from capability_scoring import (  # type: ignore
            aggregate_scores,
            explain_score,
            normalize_weights,
            score_capability,
        )
    except Exception:
        print("Failed to import capability_scoring utilities.", file=sys.stderr)
        sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader

    import yaml
except ImportError:
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    sys.exit(1)

# Local validators for gate checks
try:
    from scripts.space_traversal.validators import (
        check_low_threshold,
        check_missing_detectors,
        emit_summary,
    )
except Exception:  # pragma: no cover - fallback for direct execution
    try:
        from validators import (  # type: ignore
            check_low_threshold,
            check_missing_detectors,
            emit_summary,
        )
    except Exception:
        sys.path.append(str(Path(__file__).resolve().parent))
        try:
            from validators import (  # type: ignore
                check_low_threshold,
                check_missing_detectors,
                emit_summary,
            )
        except Exception:
            check_low_threshold = check_missing_detectors = emit_summary = None  # type: ignore

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
    # Codex-specific additions (v1.4.0)
    "deterministic",
    "reproduce",
    "manifest",
    "baseline",
    "secret",
    "sanitize",
]
VERSION = "1.4.0"
EVIDENCE_TRUNCATION_LIMIT = 50  # applied when depth < 4

SKIP_DIR_PREFIXES = (
    ".git/",
    ".venv/",
    "venv/",
    ".tox/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".cache/",
    "node_modules/",
    "dist/",
    "build/",
    "audit_artifacts/",
    "reports/",
)


def _should_skip_path(rel_path: str) -> bool:
    """Return True when the relative path matches a vendor/cache prefix."""

    if not rel_path:
        return False

    for prefix in SKIP_DIR_PREFIXES:
        base = prefix.rstrip("/")
        if rel_path == base:
            return True
        if rel_path.startswith(prefix):
            return True
        if base and rel_path.startswith(f"{base}/"):
            return True
        if base and base in rel_path.split("/"):
            return True
    return False


DOCS_SYNONYMS_MAP: Dict[str, List[str]] = {
    "checkpointing": ["ckpt", "checkpointing", "checkpoints"],
    "tokenization": ["tokenizer", "tokenize", "bpe", "sentencepiece"],
    "training-engine": ["trainer", "training", "train"],
    "evaluation-metrics": ["metrics", "eval", "perplexity", "accuracy", "loss"],
    "data-pipeline": ["dataset", "dataloader", "loader", "ingest", "preprocess"],
    "safety-security": ["sanitize", "redact", "secret", "security", "baseline"],
    "logging-tracking": ["tracking", "mlflow", "wandb", "tensorboard", "log"],
    "configuration": ["config", "hydra", "omegaconf", "yaml"],
    # Codex-specific additions (v1.4.0)
    "ml-serving": ["serve", "api", "inference", "predict", "fastapi"],
    "inference-serving": ["serve", "api", "inference", "predict", "fastapi"],
    "status-reporting": ["status", "audit", "report", "codex_status"],
    "archival": ["archive", "bundle", "manifest", "pointer"],
}


def _expand_doc_tokens(domain: str, base_tokens: List[str]) -> set[str]:
    """Expand a list of domain tokens with known synonyms and simple variants."""

    tokens = {t.lower() for t in base_tokens}
    for synonym in DOCS_SYNONYMS_MAP.get(domain, []):
        tokens.add(synonym.lower())

    # naive pluralisation – good enough for the audit heuristics
    pluralised = {f"{t}s" for t in tokens if not t.endswith("s")}
    tokens.update(pluralised)
    return tokens


def _docs_score(domain: str, docs_cache: Dict[str, str], base_tokens: List[str]) -> float:
    """Compute a lightweight documentation coverage score for a domain."""

    if not docs_cache:
        return 0.0

    expanded_tokens = _expand_doc_tokens(domain, base_tokens)
    hits = 0
    for text in docs_cache.values():
        lowered = text.lower()
        if any(token in lowered for token in expanded_tokens):
            hits += 1

    return hits / max(len(docs_cache), 1)


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
    with open(CFG_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


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


# ---------------------------------------------------------------------------
# Depth Gated Traversal
# ---------------------------------------------------------------------------
def iter_paths_depth(root: Path, max_depth: int) -> List[Path]:
    """
    Deterministic depth-limited traversal.
    Depth definition:
      root depth = 0
      root/subdir depth = 1
    """
    result: List[Path] = []
    stack = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        entries = sorted(current.iterdir(), key=lambda p: p.name)
        for e in entries:
            rel = e.relative_to(root).as_posix()
            if _should_skip_path(rel):
                continue
            if e.is_dir():
                if depth + 1 <= max_depth:
                    stack.append((e, depth + 1))
            else:
                result.append(e)
    return sorted(result, key=lambda p: p.as_posix())


# ---------------------------------------------------------------------------
# Stage Implementations
# ---------------------------------------------------------------------------
def stage_s1_index(cfg):
    # Get depth configuration
    depth, depth_warning_issued = get_depth()
    depth_warnings = get_knob_warnings()

    out_dir = Path(cfg["output"]["artifacts_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    files_meta = []
    all_paths = iter_paths_depth(ROOT, depth)
    for p in all_paths:
        rel = p.relative_to(ROOT).as_posix()
        if _should_skip_path(rel):
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
        "depth": depth,
    }
    (out_dir / "context_index.json").write_text(json.dumps(idx, indent=2), encoding="utf-8")
    (out_dir / "_depth_warnings.json").write_text(json.dumps(depth_warnings), encoding="utf-8")
    return idx


DOMAIN_PATTERNS = {
    "checkpoint": re.compile(r"checkpoint", re.I),
    "token": re.compile(r"tokeniz", re.I),
    "train": re.compile(r"train", re.I),
    "eval": re.compile(r"eval", re.I),
    "data": re.compile(r"data", re.I),
    "safety": re.compile(r"safety|saniti", re.I),
    "logging": re.compile(r"log|tracking", re.I),
    "config": re.compile(r"config|hydra", re.I),
    # Codex Extensions (v1.4.0)
    "serve": re.compile(r"serve|inference|api", re.I),
    "secret": re.compile(r"secret|baseline|redact", re.I),
    "status": re.compile(r"status|audit|report", re.I),
    "archive": re.compile(r"archive|bundle|manifest", re.I),
}


def stage_s2_facets(cfg, context_idx):
    facets = {k: [] for k in DOMAIN_PATTERNS}
    for f in context_idx["files"]:
        for key, rx in DOMAIN_PATTERNS.items():
            if rx.search(f["path"]):
                facets[key].append(f["path"])
    payload = {
        "generated": time.time(),
        "facets": facets,
        "version": VERSION,
        "depth": context_idx.get("depth"),
    }
    out = Path(cfg["output"]["artifacts_dir"]) / "facets.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


# Static baseline capability inference rules
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
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                warn(f"Failed loading detector {py.name}: {e}")
                continue
            if hasattr(module, "detect") and callable(module.detect):
                sig = inspect.signature(module.detect)
                if len(sig.parameters) == 1:
                    funcs.append(module.detect)
                else:
                    warn(f"Detector {py.name} has invalid signature; skipping.")
    return funcs


REQUIRED_DET_FIELDS = {"id", "evidence_files", "found_patterns", "required_patterns"}


def validate_detector_output(det: dict, src: str) -> bool:
    """Validate detector output structure with detailed error messages."""
    missing = REQUIRED_DET_FIELDS - det.keys()
    if missing:
        warn(f"Detector {src} missing fields {sorted(missing)}; skipping.")
        return False
    if not isinstance(det.get("evidence_files", []), list):
        warn(f"Detector {src} evidence_files must be a list; skipping.")
        return False
    if not isinstance(det.get("found_patterns", []), list):
        warn(f"Detector {src} found_patterns must be a list; skipping.")
        return False
    if not isinstance(det.get("required_patterns", []), list):
        warn(f"Detector {src} required_patterns must be a list; skipping.")
        return False
    return True


def apply_overrides(capabilities: List[dict], cfg: dict) -> List[dict]:
    """Apply capability_map.overrides to merge alias IDs into canonical ones."""
    overrides = cfg.get("capability_map", {}).get("overrides", {})
    if not overrides:
        return capabilities

    # Build reverse alias map: alias -> canonical
    alias_to_canon = {}
    for canon, aliases in overrides.items():
        for a in aliases:
            alias_to_canon[a] = canon

    merged: Dict[str, dict] = {}
    for cap in capabilities:
        cid = cap["id"]
        canon = alias_to_canon.get(cid, cid)
        target = merged.setdefault(
            canon,
            {
                "id": canon,
                "evidence_files": [],
                "found_patterns": [],
                "required_patterns": [],
                "meta": {},
            },
        )
        target["evidence_files"].extend(cap.get("evidence_files", []))
        target["found_patterns"].extend(cap.get("found_patterns", []))
        target["required_patterns"].extend(cap.get("required_patterns", []))
        # shallow-merge meta
        target["meta"].update(cap.get("meta", {}))

    # Deduplicate & sort lists
    for cap in merged.values():
        cap["evidence_files"] = sorted(set(cap["evidence_files"]))
        cap["found_patterns"] = sorted(set(cap["found_patterns"]))
        cap["required_patterns"] = sorted(set(cap["required_patterns"]))
    return sorted(merged.values(), key=lambda c: c["id"])


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
        evidence_files = sorted(set(evidence_files))
        # Truncate evidence list if depth restriction active
        depth = facets.get("depth", 4)
        if depth < 4 and len(evidence_files) > EVIDENCE_TRUNCATION_LIMIT:
            evidence_files = evidence_files[:EVIDENCE_TRUNCATION_LIMIT]
        capabilities.append(
            {
                "id": rule["id"],
                "evidence_files": evidence_files,
                "found_patterns": sorted(pattern_hits),
                "required_patterns": rule["required_patterns"],
            }
        )
    # Dynamic detectors
    if cfg.get("capability_map", {}).get("dynamic", False):
        context_idx_path = out_dir / "context_index.json"
        if not context_idx_path.exists():
            warn("context_index.json missing for dynamic detectors; re-run S1")
        else:
            ctx_index = json.loads(context_idx_path.read_text())
            dynamic_funcs = load_dynamic_detectors()
            for func in dynamic_funcs:
                try:
                    det = func(ctx_index)
                except Exception as e:
                    warn(f"Detector {func} raised: {e}")
                    continue
                if not isinstance(det, dict) or "id" not in det:
                    warn(
                        f"Invalid detector return structure from {getattr(func, '__name__', 'unknown')}; skipping."
                    )
                    continue
                if not validate_detector_output(det, getattr(func, "__name__", "unknown")):
                    continue
                for key in ["evidence_files", "found_patterns", "required_patterns"]:
                    det.setdefault(key, [])
                evidence_files = sorted(set(det["evidence_files"]))
                depth = facets.get("depth", 4)
                if depth < 4 and len(evidence_files) > EVIDENCE_TRUNCATION_LIMIT:
                    evidence_files = evidence_files[:EVIDENCE_TRUNCATION_LIMIT]
                capabilities.append(
                    {
                        "id": det["id"],
                        "evidence_files": evidence_files,
                        "found_patterns": sorted(set(det["found_patterns"])),
                        "required_patterns": det["required_patterns"],
                        "meta": det.get("meta", {}),
                    }
                )
    capabilities = sorted(capabilities, key=lambda c: c["id"])

    # Apply capability overrides to merge aliases
    capabilities = apply_overrides(capabilities, cfg)
    out_file = out_dir / "capabilities_raw.json"
    out_file.write_text(
        json.dumps(
            {"generated": time.time(), "capabilities": capabilities, "version": VERSION}, indent=2
        ),
        encoding="utf-8",
    )
    return capabilities


def duplication_ratio(evidence_files: List[str]) -> float:
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


def docs_score(cap_id: str, file_cache: Dict[str, str]) -> float:
    docs = [p for p in file_cache if p.startswith("docs/") or p.endswith(".md")]
    token = cap_id.split("-")[0]
    hits = sum(1 for p in docs if token in file_cache[p].lower())
    if not docs:
        return 0.0
    return min(1.0, hits / max(3, len(docs) * 0.1))


def _compute_missing_patterns(capability: Dict[str, Any]) -> List[str]:
    required = set(capability.get("required_patterns", []) or [])
    found = set(capability.get("found_patterns", []) or [])
    return sorted(required - found)


# ---------------------- P5: External Metrics Loaders ------------------------
def _load_similarity_map(artifacts_dir: Path) -> Dict[str, float]:
    if os.getenv("TOKEN_SIMILARITY_ENABLE", "0") not in {"1", "true", "TRUE"}:
        return {}
    f = artifacts_dir / "token_similarity.json"
    if not f.exists():
        return {}
    try:
        data = json.loads(f.read_text())
        return {
            e["id"]: float(e.get("similarity_index", 1.0)) for e in data.get("capabilities", [])
        }
    except Exception as e:
        warn(f"Failed to load token_similarity.json: {e}")
        return {}


def _load_coverage_map(artifacts_dir: Path) -> Dict[str, float]:
    if os.getenv("COVERAGE_ENABLE", "0") not in {"1", "true", "TRUE"}:
        return {}
    f = artifacts_dir / "coverage_stats.json"
    if not f.exists():
        return {}
    try:
        data = json.loads(f.read_text())
        return {
            e["id"]: float(e.get("coverage_percent", 0.0)) for e in data.get("capabilities", [])
        }
    except Exception as e:
        warn(f"Failed to load coverage_stats.json: {e}")
        return {}


def _load_severity_info(artifacts_dir: Path) -> Dict[str, Any]:
    if os.getenv("SECURITY_SEVERITY_ENABLE", "0") not in {"1", "true", "TRUE", "on", "ON"}:
        return {}
    f = artifacts_dir / "security_severity.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text())
    except Exception as e:
        warn(f"Failed to load security_severity.json: {e}")
        return {}


def _severity_multiplier(sev_info: Dict[str, Any]) -> float:
    mode = os.getenv("SEVERITY_MULTIPLIER_MODE", "additive")
    if not sev_info:
        return 1.0
    counts = sev_info.get("counts", {})
    weights = sev_info.get("weights", {})
    high = counts.get("high", 0) * weights.get("high", 0.05)
    med = counts.get("medium", 0) * weights.get("medium", 0.02)
    low = counts.get("low", 0) * weights.get("low", 0.01)
    if mode == "penalty":
        factor = 1 - (high + med * 0.5 + low * 0.25)
        return max(0.75, factor)
    if mode == "none":
        return 1.0
    # additive default
    factor = 1 + (high + med + low)
    return min(1.25, factor)


def stage_s4_scoring(cfg, raw_caps):
    raw_weights = dict(cfg["weights"])
    total_w = float(sum(raw_weights.values()))
    warnings: List[str] = []
    try:
        w_norm = normalize_weights(raw_weights)
    except ValueError as exc:
        raise ValueError("workflow.yaml weights must sum to a positive value") from exc
    if abs(total_w - 1.0) > 1e-9:
        warnings.append(f"weights_normalized_from:{total_w}")

    caps = (cfg.get("scoring", {}) or {}).get("component_caps", {}) or {}
    if not isinstance(caps, dict):
        caps = {}

    def cap_value(key: str) -> float:
        try:
            return float(caps.get(key, 1.0))
        except Exception:
            return 1.0

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])

    # Load external metrics (optional; per-capability id maps)
    similarity_map = _load_similarity_map(artifacts_dir)
    coverage_map = _load_coverage_map(artifacts_dir)
    severity_info = _load_severity_info(artifacts_dir)
    sev_factor = _severity_multiplier(severity_info)

    file_cache: Dict[str, str] = {}
    for cap in raw_caps:
        for ef in cap["evidence_files"]:
            if ef not in file_cache:
                file_cache[ef] = read_file_text_safe(ROOT / ef)
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        file_cache.setdefault(rel, read_file_text_safe(p))

    scored: List[Dict[str, Any]] = []
    for cap in raw_caps:
        cap_id = cap["id"]
        functionality = len(cap["found_patterns"]) / max(1, len(cap["required_patterns"]))

        # P5: Consistency with similarity
        base_consistency = 1.0 - duplication_ratio(cap["evidence_files"])
        similarity_index = similarity_map.get(cap_id, 1.0)
        consistency = max(0.0, min(1.0, base_consistency * similarity_index))

        # P5: Tests with coverage
        base_tests = estimate_test_depth(cap_id, cap["evidence_files"])
        coverage_percent = coverage_map.get(cap_id, 0.0)
        tests = max(base_tests, coverage_percent)

        # P5: Safeguards with severity influence
        safeguards = safeguard_score(cap["evidence_files"], file_cache)
        safeguards = min(1.0, safeguards * sev_factor)

        documentation = docs_score(cap_id, file_cache)
        raw_components = {
            "functionality": max(0.0, min(1.0, functionality)),
            "consistency": max(0.0, min(1.0, consistency)),
            "tests": max(0.0, min(1.0, tests)),
            "safeguards": max(0.0, min(1.0, safeguards)),
            "documentation": max(0.0, min(1.0, documentation)),
        }
        components = {k: min(v, cap_value(k)) for k, v in raw_components.items()}
        score_val = round(score_capability(components, w_norm), 4)

        scored_item: Dict[str, Any] = {
            "id": cap["id"],
            "components": components,
            "score": score_val,
            "evidence_files": cap["evidence_files"],
            "found_patterns": cap["found_patterns"],
            "required_patterns": cap.get("required_patterns", []),
            "missing_patterns": _compute_missing_patterns(cap),
        }
        if isinstance(cap.get("meta"), dict):
            scored_item["meta"] = cap["meta"]
        scored.append(scored_item)

    explanations = aggregate_scores(scored, w_norm)
    by_id = {e["id"]: e for e in explanations}
    for item in scored:
        detail = by_id.get(item["id"])
        if detail:
            item["score"] = detail["score"]
            item["partials"] = detail["partials"]

    payload = {
        "generated": time.time(),
        "capabilities": scored,
        "version": VERSION,
        "weights": w_norm,
        "warnings": warnings,
    }
    out = artifacts_dir / "capabilities_scored.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return scored


def stage_s5_gaps(cfg, scored_caps):
    thresholds = cfg["scoring"]["thresholds"]
    overrides = (cfg.get("capability_map", {}) or {}).get("overrides") or {}
    low: List[Dict[str, Any]] = []
    component_gaps: List[Dict[str, Any]] = []

    for capability in scored_caps:
        comps = capability.get("components", {}) or {}
        enriched = dict(capability)
        enriched["missing_patterns"] = capability.get(
            "missing_patterns"
        ) or _compute_missing_patterns(capability)
        if comps:
            primary_component = min(comps, key=lambda key: comps[key])
            enriched["primary_deficit"] = primary_component
        else:
            primary_component = None

        if capability["score"] < thresholds["low"]:
            low.append(enriched)

        zero_components = sorted([key for key, value in comps.items() if value == 0.0])
        component_entry: Dict[str, Any] = {
            "id": capability["id"],
            "zero_components": zero_components,
        }
        if primary_component is not None:
            component_entry["primary_deficit"] = {
                "component": primary_component,
                "value": float(comps.get(primary_component, 0.0)),
            }
        component_gaps.append(component_entry)

    present_ids = {cap["id"] for cap in scored_caps}
    missing_detectors = sorted(set(overrides.keys()) - present_ids)

    payload = {
        "generated": time.time(),
        "low_maturity": low,
        "missing_detectors": missing_detectors,
        "summary": {
            "low_count": len(low),
            "missing_detectors_count": len(missing_detectors),
            "zero_components_total": sum(len(entry["zero_components"]) for entry in component_gaps),
        },
        "thresholds": thresholds,
        "version": VERSION,
    }

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    (artifacts_dir / "gaps.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    component_payload = {
        "generated": time.time(),
        "component_gaps": component_gaps,
        "version": VERSION,
    }
    (artifacts_dir / "component_gaps.json").write_text(
        json.dumps(component_payload, indent=2),
        encoding="utf-8",
    )
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
    return out_file


def stage_s6_render(cfg, scored_caps, gaps):
    weights = cfg["weights"]
    scored_file = Path(cfg["output"]["artifacts_dir"]) / "capabilities_scored.json"
    if scored_file.exists():
        try:
            saved = json.loads(scored_file.read_text(encoding="utf-8"))
            if isinstance(saved.get("weights"), dict):
                weights = saved["weights"]
        except Exception:
            pass

    context = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "capabilities": scored_caps,
        "gaps": gaps["low_maturity"],
        "gap_summary": gaps.get("summary", {}),
        "missing_detectors": gaps.get("missing_detectors", []),
        "weights": weights,
        "thresholds": cfg["scoring"]["thresholds"],
    }
    return render_template(cfg, context)


def _aggregate_external_warnings(artifacts_dir: Path) -> List[str]:
    """Aggregate warnings from external sources (filter, pointers, prefix validation, severity)."""
    warnings: List[str] = []
    # Content filter report
    cfr = artifacts_dir / "content_filter_report.json"
    if cfr.exists():
        try:
            data = json.loads(cfr.read_text())
            warnings.extend(data.get("warnings", []))
            if "error" in data:
                warnings.append(f"filter_error:{data['error']}")
        except Exception as e:
            warnings.append(f"filter_report_parse_fail:{e}")
    # Latest pointer in bundles
    bundles = Path("audit_artifacts") / "bundles"
    if bundles.exists():
        ptrs = sorted(bundles.glob("*.pointer.json"))
        if ptrs:
            try:
                pdata = json.loads(ptrs[-1].read_text())
                warnings.extend(pdata.get("warnings", []))
            except Exception as e:
                warnings.append(f"pointer_parse_fail:{e}")
    # Prefix validation report
    pvr = artifacts_dir / "prefix_validation_report.json"
    if pvr.exists():
        try:
            vdata = json.loads(pvr.read_text())
            if vdata.get("violations"):
                warnings.append(f"prefix_violations:{len(vdata['violations'])}")
        except Exception as e:
            warnings.append(f"prefix_report_parse_fail:{e}")
    # P5: Secret severity classification note (counts only as warning if high)
    sev = artifacts_dir / "security_severity.json"
    if sev.exists():
        try:
            sdata = json.loads(sev.read_text())
            hi = sdata.get("counts", {}).get("high", 0)
            if hi:
                warnings.append(f"secrets_high:{hi}")
        except Exception as e:
            warnings.append(f"security_severity_parse_fail:{e}")
    return warnings


def _auto_prefix_validate(artifacts_dir: Path, warnings: List[str]):
    """
    P5: Auto-run prefix validator in warn-only mode; embeds a report for manifest.
    """
    if os.getenv("BUNDLE_PREFIX_MODE", "0") not in {"1", "true", "TRUE"}:
        return
    if os.getenv("PREFIX_VALIDATE_AUTO", "1") not in {"1", "true", "TRUE"}:
        return
    script = ROOT / "scripts" / "archive" / "validate_prefixes.py"
    if not script.exists():
        return
    try:
        # Prefer importing to capture report deterministically
        module_path = str(ROOT / "scripts" / "archive" / "validate_prefixes.py")
        spec = importlib.util.spec_from_file_location("validate_prefixes", module_path)
        validate_prefixes_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validate_prefixes_mod)
        report = validate_prefixes_mod.validate_prefixes(Path("audit_artifacts"))
        (artifacts_dir / "prefix_validation_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        if report.get("violations"):
            warnings.append(f"prefix_violations:{len(report['violations'])}")
    except Exception as e:
        warnings.append(f"prefix_validator_failed:{e}")


def stage_s7_manifest(cfg):
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    manifest = {
        "timestamp": time.time(),
        "version": VERSION,
        "repo_root_sha": _sha256_bytes(
            json.dumps(
                sorted([f.as_posix() for f in ROOT.rglob("*") if f.is_file()]), sort_keys=True
            ).encode()
        ),
        "artifacts": [],
        "weights": cfg["weights"],
        "warnings": [],
    }

    for p in artifacts_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        manifest["artifacts"].append({"name": p.name, "sha": _sha256_file(p)})

    tpl_dir = Path(cfg["output"]["matrix_template"]).parent
    concat = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concat += t.read_bytes()
    manifest["template_hash"] = _sha256_bytes(concat)

    # Collect internal warnings
    for wfile in ["_scoring_warnings.json", "_depth_warnings.json"]:
        wf = artifacts_dir / wfile
        if wf.exists():
            try:
                manifest["warnings"].extend(json.loads(wf.read_text()))
            except Exception:
                pass

    # P5: Auto prefix validation
    _auto_prefix_validate(artifacts_dir, manifest["warnings"])

    # Collect external warnings
    manifest["warnings"].extend(_aggregate_external_warnings(artifacts_dir))

    # Optional knobs snapshot
    try:
        knobs, warns = normalize_from_env()
        if knobs:
            manifest["knobs_effective"] = summarize_effective(knobs)
        if warns:
            manifest["warnings"].extend(warns)
    except Exception:
        pass

    # P5: Knobs summary sidecar
    if os.getenv("SUMMARY_ENABLE", "1") in {"1", "true", "TRUE"}:
        env_knobs = {
            k: v
            for k, v in os.environ.items()
            if any(
                k.startswith(prefix)
                for prefix in [
                    "TOKEN_SIMILARITY",
                    "COVERAGE",
                    "SECURITY_SEVERITY",
                    "SEVERITY_",
                    "BUNDLE_PREFIX_MODE",
                    "PREFIX_VALIDATE_AUTO",
                    "SUMMARY_ENABLE",
                ]
            )
        }
        (artifacts_dir / "knobs_effective.json").write_text(
            json.dumps(env_knobs, indent=2), encoding="utf-8"
        )

    out = ROOT / "audit_run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------------------
# Ancillary Commands: diff, explain, validate
# ---------------------------------------------------------------------------
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
                        caps.append({"id": parts[0], "score": float(parts[1])})
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

    weights = normalize_weights(cfg["weights"])
    explanation = explain_score(target, weights)

    print(f"Explain: {cap_id}")
    for k, part in explanation["partials"].items():
        print(
            f"  {k:14s} "
            f"value={part['component_value']:.4f} "
            f"weight={part['weight']:.3f} "
            f"contribution={part['contribution']:.4f}"
        )
    print(f"  Total score: {explanation['score']:.4f}")


def command_validate(cfg):
    if any(func is None for func in (check_low_threshold, check_missing_detectors, emit_summary)):
        print(
            "Validation helpers unavailable; ensure validators module is accessible.",
            file=sys.stderr,
        )
        sys.exit(2)

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    gaps_path = artifacts_dir / "gaps.json"
    scored_path = artifacts_dir / "capabilities_scored.json"

    if not gaps_path.exists() or not scored_path.exists():
        print("Missing artifacts. Run full pipeline before validate.", file=sys.stderr)
        sys.exit(2)

    low_count, low_list = check_low_threshold(gaps_path)  # type: ignore[arg-type]
    overrides = (cfg.get("capability_map", {}) or {}).get("overrides") or {}
    missing = check_missing_detectors(scored_path, overrides)  # type: ignore[arg-type]
    summary = emit_summary(low_list, missing, cfg["scoring"]["thresholds"])  # type: ignore[arg-type]

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as handle:
            handle.write(summary + "\n")

    print(summary)

    failed = False
    if cfg.get("options", {}).get("fail_on_low_maturity", False) and low_count > 0:
        failed = True
    if cfg.get("options", {}).get("fail_on_missing_detector", False) and missing:
        failed = True
    if failed:
        sys.exit(4)


def run_full(cfg):
    ctx = stage_s1_index(cfg)
    facets = stage_s2_facets(cfg, ctx)
    raw = stage_s3_capabilities(cfg, facets)
    scored = stage_s4_scoring(cfg, raw)
    gaps = stage_s5_gaps(cfg, scored)
    stage_s6_render(cfg, scored, gaps)
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
        facets = (
            json.loads(facets_file.read_text())
            if facets_file.exists()
            else stage_s2_facets(cfg, idx)
        )
        stage_s3_capabilities(cfg, facets)
    elif stage_id == "S4":
        raw = json.loads((artifacts_dir / "capabilities_raw.json").read_text())["capabilities"]
        stage_s4_scoring(cfg, raw)
    elif stage_id == "S5":
        scored = json.loads((artifacts_dir / "capabilities_scored.json").read_text())[
            "capabilities"
        ]
        stage_s5_gaps(cfg, scored)
    elif stage_id == "S6":
        scored = json.loads((artifacts_dir / "capabilities_scored.json").read_text())[
            "capabilities"
        ]
        gaps = json.loads((artifacts_dir / "gaps.json").read_text())
        stage_s6_render(cfg, scored, gaps)
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

    run_p = sub.add_parser("run", help="Run full pipeline")
    run_p.add_argument(
        "--artifacts-dir",
        help="Override artifacts output directory",
    )
    stage_p = sub.add_parser("stage", help="Run a single stage")
    stage_p.add_argument("stage_id", help="Stage code (S1..S7)")
    stage_p.add_argument(
        "--artifacts-dir",
        help="Override artifacts output directory",
    )
    diff_p = sub.add_parser("diff", help="Diff two report or score files")
    diff_p.add_argument("--old", required=True, help="Old report/JSON path")
    diff_p.add_argument("--new", required=True, help="New report/JSON path")
    exp_p = sub.add_parser("explain", help="Explain a capability's score")
    exp_p.add_argument("capability", help="Capability ID to explain")
    sub.add_parser("validate", help="Validate policy gates (low threshold, detectors)")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    cfg = load_config()
    artifacts_override = getattr(args, "artifacts_dir", None)
    if artifacts_override:
        cfg.setdefault("output", {})["artifacts_dir"] = artifacts_override
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
