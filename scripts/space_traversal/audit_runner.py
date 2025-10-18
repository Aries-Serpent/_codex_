#!/usr/bin/env python
"""
Audit Runner Orchestrator for Copilot Space Traversal Workflow (v1.1.0)

This file includes:
- S3→S4 meta propagation (capability 'meta' carried into scored payload)
- Optional component caps (cfg.scoring.component_caps) applied before weighting
- Optional duplication heuristic switch (cfg.scoring.dup.heuristic):
    - "simple" uses file-stem duplication ratio (default)
    - "token_similarity" uses dup_similarity.estimate() if present, else fallback
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
    from jinja2 import Environment, FileSystemLoader

    import yaml
except ImportError:
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    sys.exit(1)

# Try scoring utilities
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

# Optional token-similarity duplication heuristic
try:
    from scripts.space_traversal import dup_similarity  # type: ignore
except Exception:  # pragma: no cover
    dup_similarity = None  # dynamic import guard

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
MAX_READ_BYTES = 200_000
SAFEGUARD_KEYWORDS = ["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE"]
VERSION = "1.1.0"

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


def stage_s1_index(cfg):
    out_dir = Path(cfg["output"]["artifacts_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    files_meta = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(rel.startswith(prefix) for prefix in SKIP_DIR_PREFIXES):
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
    funcs: List[Callable] = []
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


def _expand_doc_tokens(capability_id: str, keywords: List[str] | None) -> List[str]:
    base = [capability_id.split("-")[0]] if not keywords else list(keywords)
    syns = DOCS_SYNONYMS_MAP.get(capability_id, [])
    seeds = [t.lower() for t in (base + syns)]
    variants: set[str] = set()
    for t in seeds:
        t = t.strip().lower()
        if not t:
            continue
        variants.add(t)
        if t.endswith("es"):
            variants.add(t[:-2])
        if t.endswith("s"):
            variants.add(t[:-1])
        else:
            variants.add(t + "s")
            variants.add(t + "es")
    return sorted(variants)


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
    capabilities: List[Dict[str, Any]] = []
    # Static rules
    for rule in BASE_CAPABILITY_RULES:
        evidence_files: List[str] = []
        for facet in rule["facet_keys"]:
            evidence_files.extend(facets["facets"].get(facet, []))
        pattern_hits: set[str] = set()
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
                # No meta for static rules
            }
        )
    # Dynamic detectors
    if cfg.get("capability_map", {}).get("dynamic", False):
        dynamic_funcs = load_dynamic_detectors()
        context_idx_path = out_dir / "context_index.json"
        if not context_idx_path.exists():
            warn("context_index.json missing for dynamic detectors; re-run S1")
        else:
            ctx_index = json.loads(context_idx_path.read_text(encoding="utf-8"))
            for func in dynamic_funcs:
                try:
                    det = func(ctx_index)
                except Exception as e:
                    warn(f"Detector {func} raised: {e}")
                    continue
                if not isinstance(det, dict) or "id" not in det:
                    warn("Invalid detector return structure; skipping.")
                    continue
                for key in ["evidence_files", "found_patterns", "required_patterns"]:
                    det.setdefault(key, [])
                capabilities.append(
                    {
                        "id": det["id"],
                        "evidence_files": sorted(set(det["evidence_files"])),
                        "found_patterns": sorted(set(det["found_patterns"])),
                        "required_patterns": det["required_patterns"],
                        "meta": det.get("meta", {}),  # carry meta forward
                    }
                )
    # Sorting & write
    capabilities = sorted(capabilities, key=lambda c: c["id"])
    out_file = out_dir / "capabilities_raw.json"
    out_file.write_text(
        json.dumps(
            {"generated": time.time(), "capabilities": capabilities, "version": VERSION}, indent=2
        ),
        encoding="utf-8",
    )
    return capabilities


def _duplication_ratio_simple(evidence_files: List[str]) -> float:
    stems = [Path(f).stem for f in evidence_files]
    if not stems:
        return 0.0
    counts: Dict[str, int] = {}
    for s in stems:
        counts[s] = counts.get(s, 0) + 1
    dup = sum(c - 1 for c in counts.values() if c > 1)
    return min(1.0, dup / max(1, len(stems)))


def _duplication_ratio(cfg: dict, evidence_files: List[str]) -> float:
    """Switchable duplication heuristic with safe fallback."""
    heuristic = (cfg.get("scoring", {}) or {}).get("dup", {}).get("heuristic", "simple")
    if heuristic == "token_similarity" and dup_similarity is not None:
        try:
            return dup_similarity.estimate(evidence_files, ROOT)  # type: ignore[attr-defined]
        except Exception as e:  # pragma: no cover
            warn(f"dup_similarity failed ({e}); falling back to simple heuristic")
    return _duplication_ratio_simple(evidence_files)


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


def stage_s4_scoring(cfg, raw_caps):
    # Normalize weights
    raw_weights = dict(cfg["weights"])
    total_w = float(sum(raw_weights.values()))
    warnings: List[str] = []
    try:
        w_norm = normalize_weights(raw_weights)
    except ValueError as exc:
        raise ValueError("workflow.yaml weights must sum to a positive value") from exc
    if abs(total_w - 1.0) > 1e-9:
        warnings.append(f"weights_normalized_from:{total_w}")

    # Component caps (optional)
    caps = (cfg.get("scoring", {}) or {}).get("component_caps", {}) or {}
    if not isinstance(caps, dict):
        caps = {}

    def cap_value(key: str) -> float:
        # Any missing key defaults to 1.0 (no suppression)
        try:
            return float(caps.get(key, 1.0))
        except Exception:
            return 1.0

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    file_cache: Dict[str, str] = {}
    # Preload evidence & docs into cache
    for cap in raw_caps:
        for ef in cap["evidence_files"]:
            if ef not in file_cache:
                file_cache[ef] = read_file_text_safe(ROOT / ef)
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        file_cache.setdefault(rel, read_file_text_safe(p))

    scored: List[Dict[str, Any]] = []
    for cap in raw_caps:
        functionality = len(cap["found_patterns"]) / max(1, len(cap["required_patterns"]))
        consistency = 1.0 - _duplication_ratio(cfg, cap["evidence_files"])
        tests = estimate_test_depth(cap["id"], cap["evidence_files"])
        safeguards = safeguard_score(cap["evidence_files"], file_cache)
        documentation = docs_score(cap["id"], file_cache)
        # Clamp to [0,1] then apply component caps
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
        }
        # S3→S4 meta propagation (if present)
        if isinstance(cap.get("meta"), dict):
            scored_item["meta"] = cap["meta"]
        scored.append(scored_item)

    # Attach explanation partials
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
    low = []
    for c in scored_caps:
        if c["score"] < thresholds["low"]:
            comps = c.get("components", {}) or {}
            c_enriched = dict(c)
            if comps:
                c_enriched["primary_deficit"] = min(comps, key=lambda k: comps[k])
            low.append(c_enriched)
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
    return out_file


def stage_s6_render(cfg, scored_caps, gaps):
    # Prefer normalized weights saved by S4
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
        "weights": weights,
    }
    return render_template(cfg, context)


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

    # Template hash
    tpl_dir = Path(cfg["output"]["matrix_template"]).parent
    concat = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concat += t.read_bytes()
    manifest["template_hash"] = _sha256_bytes(concat)

    # Inject effective weights/warnings from scored payload
    scored_file = artifacts_dir / "capabilities_scored.json"
    if scored_file.exists():
        try:
            scored_payload = json.loads(scored_file.read_text(encoding="utf-8"))
            if isinstance(scored_payload.get("weights"), dict):
                manifest["weights"] = scored_payload["weights"]
            if isinstance(scored_payload.get("warnings"), list):
                manifest["warnings"].extend([str(w) for w in scored_payload["warnings"]])
        except Exception:
            pass

    out = ROOT / "audit_run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def load_capabilities_from_any(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data: Dict[str, Any] = {}
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
    return {c["id"]: c.get("score") for c in data.get("capabilities", [])}


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
    data = json.loads(scored_file.read_text(encoding="utf-8"))
    cap_id = args.capability
    target = next((c for c in data["capabilities"] if c["id"] == cap_id), None)
    if not target:
        print(f"Capability {cap_id} not found.", file=sys.stderr)
        sys.exit(2)
    weights = data.get("weights") or dict(cfg["weights"])
    total_w = float(sum(weights.values()))
    if abs(total_w - 1.0) > 1e-9:
        warn(f"Weights normalized in explain view from {total_w}")
    try:
        w_norm = normalize_weights(weights)  # type: ignore[arg-type]
    except ValueError as exc:
        raise ValueError("workflow.yaml weights must sum to a positive value") from exc
    partials = target.get("partials") if isinstance(target.get("partials"), dict) else None
    score_value = target.get("score", 0.0)
    if partials is None:
        explanation = explain_score(target, w_norm)
        partials = explanation["partials"]
        score_value = explanation["score"]
    print(f"Explain: {cap_id}")
    for key in w_norm:
        details = partials.get(key, {})
        component_value = float(details.get("component_value", target["components"].get(key, 0.0)))
        weight = float(details.get("weight", w_norm[key]))
        contribution = float(details.get("contribution", component_value * weight))
        print(
            f"  {key:14s} value={component_value:.4f} weight={weight:.3f} contribution={contribution:.4f}"
        )
    print(f"  Total score: {float(score_value):.4f}")


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
        scored_payload = json.loads((artifacts_dir / "capabilities_scored.json").read_text())
        scored = scored_payload["capabilities"]
        gaps = json.loads((artifacts_dir / "gaps.json").read_text())
        stage_s6_render(cfg, scored, gaps)
    elif stage_id == "S7":
        stage_s7_manifest(cfg)
    else:
        print("Unknown stage ID", file=sys.stderr)
        sys.exit(2)


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
