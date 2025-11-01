#!/usr/bin/env python
"""
Audit Runner Orchestrator for Copilot Space Traversal Workflow (v1.2.0)

Enhancements (v1.2.0):
 - Propagate required_patterns into scored artifacts (S4)
 - Compute missing_patterns and write into gaps.json (S5)
 - Emit component_gaps.json with zero components (S5)
 - Add 'validate' command for policy gates (low threshold, missing detectors)
 - Include missing_detectors and thresholds snapshot in manifest (S7)
 - Pass thresholds into render context; template shows true low threshold
"""
from __future__ import annotations
import argparse, json, os, re, sys, hashlib, time, importlib.util, inspect
from pathlib import Path
from typing import Dict, List, Any, Callable

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Missing dependencies. Install via: pip install pyyaml jinja2", file=sys.stderr)
    sys.exit(1)

# Local validators
try:
    from .validators import (
        check_low_threshold,
        check_missing_detectors,
        emit_summary,
    )
except Exception:
    # fallback for direct execution
    sys.path.append(str(Path(__file__).resolve().parent))
    from validators import (
        check_low_threshold,
        check_missing_detectors,
        emit_summary,
    )

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
MAX_READ_BYTES = 200_000
SAFEGUARD_KEYWORDS = ["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE"]
VERSION = "1.2.0"

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
# Stage Implementations
# ---------------------------------------------------------------------------
def stage_s1_index(cfg):
    out_dir = Path(cfg["output"]["artifacts_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    files_meta = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(".git/") or rel.startswith("audit_artifacts/") or rel.startswith("reports/"):
            continue
        ext = p.suffix.lower()
        size = p.stat().st_size
        sha = _sha256_file(p) if size < 2_000_000 else None
        files_meta.append({"path": rel, "ext": ext, "size": size, "sha": sha})
    idx = {"generated": time.time(), "count": len(files_meta), "files": files_meta, "version": VERSION}
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

# Static baseline capability inference rules
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
        capabilities.append({
            "id": rule["id"],
            "evidence_files": sorted(set(evidence_files)),
            "found_patterns": sorted(pattern_hits),
            "required_patterns": rule["required_patterns"],
        })
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
                for key in ["evidence_files", "found_patterns", "required_patterns"]:
                    det.setdefault(key, [])
                capabilities.append({
                    "id": det["id"],
                    "evidence_files": sorted(set(det["evidence_files"])),
                    "found_patterns": sorted(set(det["found_patterns"])),
                    "required_patterns": det["required_patterns"],
                    "meta": det.get("meta", {}),
                })
    capabilities = sorted(capabilities, key=lambda c: c["id"])
    out_file = out_dir / "capabilities_raw.json"
    out_file.write_text(json.dumps({"generated": time.time(), "capabilities": capabilities, "version": VERSION}, indent=2), encoding="utf-8")
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

def stage_s4_scoring(cfg, raw_caps):
    weights = cfg["weights"]
    total_w = sum(weights.values())
    warnings = []
    if abs(total_w - 1.0) > 1e-9:
        warnings.append(f"weights_normalized_from:{total_w}")
        weights = {k: v / total_w for k, v in weights.items()}

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    file_cache: Dict[str, str] = {}
    for cap in raw_caps:
        for ef in cap["evidence_files"]:
            if ef not in file_cache:
                file_cache[ef] = read_file_text_safe(ROOT / ef)
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        if rel not in file_cache:
            file_cache[rel] = read_file_text_safe(p)

    scored = []
    for cap in raw_caps:
        functionality = len(cap["found_patterns"]) / max(1, len(cap["required_patterns"]))
        consistency = 1.0 - duplication_ratio(cap["evidence_files"])
        tests = estimate_test_depth(cap["id"], cap["evidence_files"])
        safeguards = safeguard_score(cap["evidence_files"], file_cache)
        documentation = docs_score(cap["id"], file_cache)
        components = {
            "functionality": functionality,
            "consistency": consistency,
            "tests": tests,
            "safeguards": safeguards,
            "documentation": documentation,
        }
        score = sum(components[k] * weights[k] for k in weights)
        missing_patterns = _compute_missing_patterns(cap)
        scored.append({
            "id": cap["id"],
            "components": components,
            "score": round(score, 4),
            "evidence_files": cap["evidence_files"],
            "found_patterns": cap["found_patterns"],
            "required_patterns": cap.get("required_patterns", []),
            "missing_patterns": missing_patterns,
        })

    out = artifacts_dir / "capabilities_scored.json"
    out.write_text(json.dumps({"generated": time.time(), "capabilities": scored, "version": VERSION}, indent=2), encoding="utf-8")
    (artifacts_dir / "_scoring_warnings.json").write_text(json.dumps(warnings), encoding="utf-8")
    return scored

def _compute_missing_patterns(cap: dict) -> List[str]:
    req = set(cap.get("required_patterns", []))
    found = set(cap.get("found_patterns", []))
    return sorted(req - found)

def stage_s5_gaps(cfg, scored_caps):
    thresholds = cfg["scoring"]["thresholds"]
    low = []
    for c in scored_caps:
        if c["score"] < thresholds["low"]:
            entry = dict(c)
            entry["missing_patterns"] = _compute_missing_patterns(c)
            low.append(entry)
    # component gaps (zeros and primary deficit)
    component_gaps = []
    for c in scored_caps:
        comps = c.get("components", {})
        zeros = sorted([k for k, v in comps.items() if v == 0.0])
        if zeros:
            component_gaps.append({"id": c["id"], "zero_components": zeros})

    # missing detectors (overrides ids not present)
    overrides = (cfg.get("capability_map", {}) or {}).get("overrides") or {}
    present_ids = {c["id"] for c in scored_caps}
    missing_detectors = sorted(set(overrides.keys()) - present_ids)

    payload = {
        "generated": time.time(),
        "low_maturity": low,
        "missing_detectors": missing_detectors,
        "summary": {
            "low_count": len(low),
            "zeros_count": sum(len(x["zero_components"]) for x in component_gaps),
        },
        "version": VERSION,
    }
    out_dir = Path(cfg["output"]["artifacts_dir"])
    (out_dir / "gaps.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "component_gaps.json").write_text(json.dumps({"component_gaps": component_gaps, "version": VERSION}, indent=2), encoding="utf-8")
    return payload

def render_template(cfg, context):
    tpl_path = cfg["output"]["matrix_template"]
    tpl_dir = Path(tpl_path).parent
    env = Environment(loader=FileSystemLoader(str(tpl_dir)), autoescape=False, trim_blocks=True, lstrip_blocks=True)
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
    context = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "capabilities": scored_caps,
        "gaps": gaps["low_maturity"],
        "weights": cfg["weights"],
        "thresholds": cfg["scoring"]["thresholds"],
    }
    return render_template(cfg, context)

def stage_s7_manifest(cfg):
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    manifest = {
        "timestamp": time.time(),
        "version": VERSION,
        "repo_root_sha": _sha256_bytes(json.dumps(sorted([f.as_posix() for f in ROOT.rglob('*') if f.is_file()]), sort_keys=True).encode()),
        "artifacts": [],
        "weights": cfg["weights"],
        "thresholds": cfg["scoring"]["thresholds"],
        "warnings": []
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

    warn_file = artifacts_dir / "_scoring_warnings.json"
    if warn_file.exists():
        manifest["warnings"].extend(json.loads(warn_file.read_text()))

    # include missing_detectors list for provenance
    gaps_path = artifacts_dir / "gaps.json"
    if gaps_path.exists():
        try:
            gaps = json.loads(gaps_path.read_text())
            manifest["missing_detectors"] = gaps.get("missing_detectors", [])
        except Exception:
            manifest["missing_detectors"] = []

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
    weights = cfg["weights"]
    total_w = sum(weights.values())
    if abs(total_w - 1.0) > 1e-9:
        weights = {k: v / total_w for k, v in weights.items()}
        warn(f"Weights normalized in explain view from {total_w}")
    components = target["components"]
    print(f"Explain: {cap_id}")
    for k, v in components.items():
        w = weights[k]
        print(f"  {k:14s} value={v:.4f} weight={w:.3f} contribution={(v*w):.4f}")
    print(f"  Total score: {target['score']:.4f}")

def command_validate(cfg):
    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
    gaps_path = artifacts_dir / "gaps.json"
    scored_path = artifacts_dir / "capabilities_scored.json"

    if not gaps_path.exists() or not scored_path.exists():
        print("Missing artifacts. Run full pipeline or required stages first.", file=sys.stderr)
        sys.exit(2)

    low_count, low_list = check_low_threshold(str(gaps_path))
    missing = check_missing_detectors(str(scored_path), (cfg.get("capability_map", {}) or {}).get("overrides") or {})
    summary = emit_summary(low_list, missing, cfg["scoring"]["thresholds"])

    # Always emit job summary text if env is set
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        with open(step_summary, "a", encoding="utf-8") as fh:
            fh.write(summary + "\n")

    # Print to stdout for logs
    print(summary)

    failed = False
    if cfg.get("options", {}).get("fail_on_low_maturity", False) and low_count > 0:
        failed = True
    if cfg.get("options", {}).get("fail_on_missing_detector", False) and missing:
        failed = True
    if failed:
        sys.exit(4)

# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
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
    context_idx = (artifacts_dir / "context_index.json")
    facets_file = (artifacts_dir / "facets.json")
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
    sub.add_parser("validate", help="Validate gates (low threshold, missing detectors)")

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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
