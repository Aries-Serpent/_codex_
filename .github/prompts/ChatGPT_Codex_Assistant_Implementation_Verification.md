# ChatGPT Codex Assistant — Implementation & Verification

Context:
- Repo: Aries-Serpent/_codex_
- Branching convention: audit/<task>-<YYYYMMDD>
- Files to apply: as provided in patchset (audit_runner.py, templates, detectors, coverage_ingest, schemas, tests, Makefile)

Objective:
Implement the patchset and verify full pipeline behavior (unit tests + functional checks). Produce artifacts and a brief verification report.

Strict Step-by-step Instructions for Codex:
1. Create branch: audit/implement-status-update-v2-<YYYYMMDD>.
2. Replace/add files with the exact contents provided in the patchset.
3. Install dependencies: pip install -r requirements.txt (or pip install pyyaml jinja2 pytest).
4. Run unit tests: pytest -q
   - If failures, print failing test names and stack traces and attempt minimal fixes limited to the patched files only.
5. Run baseline audit:
   - Ensure .copilot-space/workflow.yaml metrics_schema_version is "2.0.0".
   - Run: python scripts/space_traversal/audit_runner.py run
6. Confirm artifacts:
   - audit_artifacts/context_index.json
   - audit_artifacts/facets.json
   - audit_artifacts/capabilities_raw.json
   - audit_artifacts/capabilities_scored.json
   - audit_artifacts/gaps.json
   - reports/capability_matrix_<ts>.md
   - reports/capability_matrix_<ts>.json
   - audit_run_manifest.json
7. Validate JSON companion:
   - Validate reports/capability_matrix_<ts>.json against scripts/space_traversal/schemas/capability_matrix.schema.json (use python jsonschema or a minimal structural check).
8. Validate overrides behavior:
   - With an overrides mapping containing a missing alias and workflow.options.fail_on_missing_detector=true, ensure runner exits with code 5.
   - With overrides present and valid aliases, confirm merged canonical id in capabilities_raw.json.
9. Validate detect_v2:
   - Ensure detectors/example_v2.py is loaded and its evidence appears in capabilities_raw.json meta._evidence_v2.
10. Validate coverage ingestion:
    - (If coverage xml is provided) run coverage_ingest.py and ensure S4 blends coverage into tests component.
11. Determinism check:
    - Run the full pipeline twice without changes and confirm repo_root_sha and normalized capabilities_scored.json content are identical (ignore timestamps).
12. Produce verification report (short):
    - Tests run summary
    - Artifacts produced & sample manifest fields
    - Override merge behavior result
    - detect_v2 evidence presence
    - JSON companion validation result
    - Determinism check result

Failure handling:
- If any step fails, produce a concise error summary and suggested minimal code changes (one-liners or small function fixes).

Output:
- A short verification report and list of commands executed + minimal diffs if any post-patch fixes were required.

Notes:
- Avoid network calls during pipeline.
- Respect file read truncation MAX_READ_BYTES.
- Always prefer JSON companion for diffs.


```markdown name=.github/patchsets/README.md
# Patchset: Status Update Pipeline — Ready-to-Implement Changes

This patchset contains the exact file replacements/additions needed for ChatGPT Codex to implement the production-ready Status Update pipeline enhancements:
- Fix template low-threshold rendering
- Add JSON companion output for S6 render
- Apply capability_map.overrides merging and optional missing-detector strict gate
- Support detect_v2 detectors and normalize outputs
- Add coverage ingestion stub
- Add JSON Schema and unit tests
- Add make target for JSON export

Apply these files into the repository paths shown. After applying, run the test suite (pytest) and perform the verification playbook in the Codex prompt.

```

```jinja name=templates/audit/capability_matrix.md.j2 url=https://github.com/Aries-Serpent/_codex_/blob/main/templates/audit/capability_matrix.md.j2
# [Report]: Capability Matrix  
> Generated: {{ timestamp }} | Author: audit_system  
 Roles: [Primary: Automated Auditor], [Secondary: Provenance Engine]  Energy: 5  

## 1. Summary
Total Capabilities: {{ capabilities|length }}
Low Maturity (< {{ scoring.thresholds.low }}) : {{ gaps|length }}

## 2. Capability Scores
| ID | Score | Functionality | Consistency | Tests | Safeguards | Docs | Evidence Count |
|----|-------|--------------:|------------:|------:|-----------:|-----:|---------------:|
{% for cap in capabilities -%}
| {{ cap.id }} | {{ "%.2f"|format(cap.score) }} | {{ "%.2f"|format(cap.components.functionality) }} | {{ "%.2f"|format(cap.components.consistency) }} | {{ "%.2f"|format(cap.components.tests) }} | {{ "%.2f"|format(cap.components.safeguards) }} | {{ "%.2f"|format(cap.components.documentation) }} | {{ cap.evidence_files|length }} |
{% endfor %}

## 3. Low Maturity Focus
{% if gaps %}
| ID | Score | Primary Deficit |
|----|-------|-----------------|
{% for g in gaps -%}
{# Pick smallest numeric component #}
| {{ g.id }} | {{ "%.2f"|format(g.score) }} | {% set comp = (g.components|dictsort(false, 'value'))[0][0] %}{{ comp }} |
{% endfor %}
{% else %}
All capabilities meet minimum thresholds.
{% endif %}

## 4. Weight Reference
| Component | Weight |
|-----------|-------:|
{% for k,v in weights.items() -%}
| {{ k }} | {{ "%.2f"|format(v) }} |
{% endfor %}

## 5. Capability Detail Sections
{% for cap in capabilities %}
### {{ cap.id }}
Score: {{ "%.4f"|format(cap.score) }}

Components:
- Functionality: {{ cap.components.functionality }}
- Consistency: {{ cap.components.consistency }}
- Tests: {{ cap.components.tests }}
- Safeguards: {{ cap.components.safeguards }}
- Documentation: {{ cap.components.documentation }}

Patterns Found: {{ cap.found_patterns|join(", ") if cap.found_patterns else "None" }}

Evidence Files (first 10):
	```
{% for f in cap.evidence_files[:10] -%}
{{ f }}
{% endfor %}
	```
{% endfor %}

## 6. Appendix
| Field | Description |
|-------|-------------|
| template_hash | Hash of concatenated Jinja templates |
| generation_strategy | Weighted component aggregation |
| scoring_components | functionality, consistency, tests, safeguards, documentation |

Embedded Template SHA256: {{ template_hash|default("UNKNOWN") }}

*End of Matrix*
```

```python name=scripts/space_traversal/audit_runner.py url=https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/audit_runner.py
#!/usr/bin/env python
"""
Audit Runner Orchestrator for Copilot Space Traversal Workflow (v1.2.0)

Key enhancements:
 - detect_v2() detector support
 - capability_map.overrides merging and optional fail_on_missing_detector gate
 - JSON companion output for S6 (reports/capability_matrix_<ts>.json)
 - Pass scoring.thresholds.low into template context
 - metrics_schema_version recorded in manifest
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

ROOT = Path(__file__).resolve().parents[2]
CFG_PATH = ROOT / ".copilot-space" / "workflow.yaml"
SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
MAX_READ_BYTES = 200_000
SAFEGUARD_KEYWORDS = ["sha256", "checksum", "rng", "seed", "offline", "WANDB_MODE"]
VERSION = "1.2.0"

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
# Pipeline stages
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

# Baseline static rules
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
            # Prefer detect_v2
            if hasattr(module, "detect_v2") and callable(module.detect_v2):
                funcs.append(module.detect_v2)
            elif hasattr(module, "detect") and callable(module.detect):
                funcs.append(module.detect)
            else:
                warn(f"No usable detector function in {py.name}; skipping.")
    return funcs

def _normalize_detector_output(det: dict) -> dict:
    # Normalize both v1 and v2 detector outputs to canonical shape
    if "evidence" in det:
        evidence_files = [e.get("path") for e in det.get("evidence", []) if e.get("path")]
        meta = det.get("meta", {})
        meta["_evidence_v2"] = det.get("evidence", [])
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
                normalized = _normalize_detector_output(det)
                capabilities.append(normalized)
    # Apply overrides merging
    overrides = cfg.get("capability_map", {}).get("overrides", {}) or {}
    if overrides:
        by_id = {c["id"]: c for c in capabilities}
        merged = {}
        missing_refs = []
        for canonical, aliases in overrides.items():
            base = by_id.get(canonical, {"id": canonical, "evidence_files": [], "found_patterns": [], "required_patterns": []})
            for alias in aliases:
                if alias not in by_id:
                    missing_refs.append(alias)
                    continue
                a = by_id[alias]
                base["evidence_files"] = sorted(set(base.get("evidence_files", []) + a.get("evidence_files", [])))
                base["found_patterns"] = sorted(set(base.get("found_patterns", []) + a.get("found_patterns", [])))
                base["required_patterns"] = sorted(set(base.get("required_patterns", []) + a.get("required_patterns", [])))
            merged[canonical] = base
        remaining = {k: v for k, v in by_id.items() if k not in sum((aliases for aliases in overrides.values()), []) and k not in merged}
        capabilities = list(remaining.values()) + list(merged.values())
        if missing_refs and cfg.get("options", {}).get("fail_on_missing_detector", False):
            warn(f"Missing detector references in overrides: {missing_refs}")
            sys.exit(5)
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

    artifacts_dir = Path(cfg["output"]["artifacts_dir"])
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
        cov_map = {}
        cov_path = artifacts_dir / "coverage_map.json"
        if cov_path.exists():
            cov_map = json.loads(cov_path.read_text())
        coverage_value = None
        if cov_map:
            vals = []
            for ef in cap.get("evidence_files", []):
                if ef in cov_map:
                    vals.append(cov_map[ef].get("percent", 0.0))
            if vals:
                coverage_value = sum(vals) / len(vals)
                tests = max(tests, coverage_value)
        safeguards = safeguard_score(cap.get("evidence_files", []), file_cache)
        documentation = docs_score(cap.get("id"), file_cache)
        components = {
            "functionality": functionality,
            "consistency": consistency,
            "tests": tests,
            "safeguards": safeguards,
            "documentation": documentation,
        }

        if cs:
            score = cs.score_capability(components, weights)
            explanation = cs.explain_score({"id": cap.get("id"), "components": components}, weights)
        else:
            score = sum(components[k] * weights[k] for k in weights)
            explanation = {"id": cap.get("id"), "score": round(score, 4), "partials": {}}

        scored.append({
            "id": cap.get("id"),
            "components": components,
            "score": round(score, 4),
            "evidence_files": cap.get("evidence_files", []),
            "found_patterns": cap.get("found_patterns", []),
            "explain": explanation
        })

    out = artifacts_dir / "capabilities_scored.json"
    out.write_text(json.dumps({"generated": time.time(), "capabilities": scored, "version": VERSION}, indent=2), encoding="utf-8")
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

def stage_s6_render(cfg, scored_caps, gaps):
    context = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "capabilities": scored_caps,
        "gaps": gaps["low_maturity"],
        "weights": cfg["weights"],
        "scoring": cfg.get("scoring", {}),
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
        "warnings": [],
        "metrics_schema_version": cfg.get("metrics_schema_version", "2.0.0"),
        "baseline_manifest_ref": cfg.get("baseline_manifest_ref", None)
    }
    for p in artifacts_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        manifest["artifacts"].append({
            "name": p.name,
            "sha": _sha256_file(p),
            "size": p.stat().st_size,
            "format": "json",
            "generated_at": p.stat().st_mtime
        })
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

# ---------------------------------------------------------------------------
# diff & explain (prefers JSON companion)
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
                if len(parts) >= 8 and parts[0] != "----":
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
    old_map = load_capabilities_from_any(Path(args.old))
    new_map = load_capabilities_from_any(Path(args.new))
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
    explain_dir = Path(cfg["output"]["artifacts_dir"]) / "explain"
    explain_file = explain_dir / f"{cap_id}.json"
    if explain_file.exists():
        print(f"Explain JSON: {explain_file}")
    print(f"  Total score: {target['score']:.4f}")

# ---------------------------------------------------------------------------
# Orchestration
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
```

```python name=scripts/space_traversal/coverage_ingest.py url=https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/coverage_ingest.py
#!/usr/bin/env python3
"""
Coverage ingestion stub (Cobertura / coverage.py XML -> coverage_map.json)

Produces:
  audit_artifacts/coverage_map.json
{
  "<path>": {
     "covered_lines": [1,2,3],
     "percent": 0.42
  },
  ...
}
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import sys

ROOT = Path(__file__).resolve().parents[2]

def parse_coverage_xml(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    cov = {}
    for cls in root.findall(".//class"):
        filename = cls.get("filename")
        lines = []
        for ln in cls.findall(".//line"):
            num = ln.get("number")
            hits = ln.get("hits")
            if num is not None and hits is not None and int(hits) > 0:
                lines.append(int(num))
        if filename:
            cov[filename] = {"covered_lines": sorted(set(lines))}
    for f, data in cov.items():
        try:
            full_path = ROOT / f
            total_lines = sum(1 for _ in open(full_path, "r", encoding="utf-8", errors="ignore"))
            data["percent"] = len(data["covered_lines"]) / max(1, total_lines)
        except Exception:
            data["percent"] = 0.0
    return cov

def write_coverage_map(out_path: Path, cov_map: dict):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cov_map, indent=2), encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("Usage: coverage_ingest.py <coverage_xml_path>", file=sys.stderr)
        sys.exit(2)
    xml_in = Path(sys.argv[1])
    if not xml_in.exists():
        print("Coverage xml not found", file=sys.stderr)
        sys.exit(2)
    cov_map = parse_coverage_xml(xml_in)
    out = Path.cwd() / "audit_artifacts" / "coverage_map.json"
    write_coverage_map(out, cov_map)
    print(f"Wrote coverage map to {out}")

if __name__ == "__main__":
    main()
```

```python name=scripts/space_traversal/detectors/example_v2.py url=https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/detectors/example_v2.py
def detect_v2(file_index: dict) -> dict:
    """
    Example detector v2 that returns evidence with ranges and confidence.
    Minimal illustrative detector.
    """
    files = [f["path"] for f in file_index.get("files", []) if f["path"].endswith(".py")]
    evidence = []
    for p in files:
        if "serve" in p.lower() or "checkpoint" in p.lower():
            evidence.append({
                "path": p,
                "sha": None,
                "ranges": [{"start_line": 1, "end_line": 40}],
                "confidence": 0.9,
                "excerpt": None
            })
    return {
        "id": "example-evidence-v2",
        "evidence": evidence,
        "found_patterns": ["serve", "checkpoint"],
        "required_patterns": ["serve"],
        "meta": {"detector_version": "v2", "source": "example_v2"}
    }
```

```json name=scripts/space_traversal/schemas/capability_matrix.schema.json url=https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/schemas/capability_matrix.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Capability Matrix",
  "type": "object",
  "required": ["timestamp", "capabilities", "weights", "template_hash", "metrics_schema_version"],
  "properties": {
    "timestamp": {"type": "string"},
    "metrics_schema_version": {"type": "string"},
    "template_hash": {"type": "string"},
    "weights": {"type": "object"},
    "capabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "score", "components"],
        "properties": {
          "id": {"type": "string"},
          "score": {"type": "number"},
          "components": {"type": "object"},
          "evidence_files": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

```python name=tests/audit/test_overrides.py url=https://github.com/Aries-Serpent/_codex_/blob/main/tests/audit/test_overrides.py
"""
Unit tests for overrides merging and missing-detector strict gate
"""
import json
from pathlib import Path
import pytest

from scripts.space_traversal import audit_runner as runner

def make_cfg(tmp_path):
    cfg = {
        "output": {"artifacts_dir": str(tmp_path)},
        "weights": {"functionality":0.25,"consistency":0.2,"tests":0.25,"safeguards":0.15,"documentation":0.15},
        "capability_map": {"dynamic": False, "overrides": {"merged-cap": ["alias-a"]}},
        "options": {"fail_on_missing_detector": False},
        "scoring": {"thresholds": {"low": 0.7, "medium": 0.85}},
        "matrix_template": "templates/audit/capability_matrix.md.j2",
        "metrics_schema_version": "2.0.0"
    }
    return cfg

def test_overrides_merging(tmp_path):
    facets = {"generated": 0, "facets": {"train": ["src/train/foo.py"], "checkpoint": ["src/ckpt/a.py"]}, "version": "1"}
    cfg = make_cfg(tmp_path)
    idx = {"generated":0,"count":0,"files":[]}
    Path(cfg["output"]["artifacts_dir"]).mkdir(parents=True, exist_ok=True)
    (Path(cfg["output"]["artifacts_dir"]) / "context_index.json").write_text(json.dumps(idx))
    caps = runner.stage_s3_capabilities(cfg, facets)
    ids = [c["id"] for c in caps]
    assert "merged-cap" in ids

def test_missing_detector_strict_fails(tmp_path):
    cfg = make_cfg(tmp_path)
    cfg["options"]["fail_on_missing_detector"] = True
    cfg["capability_map"]["overrides"] = {"canonical": ["nonexistent-alias"]}
    facets = {"generated": 0, "facets": {}}
    with pytest.raises(SystemExit) as exc:
        runner.stage_s3_capabilities(cfg, facets)
    assert exc.value.code == 5
```

```python name=tests/audit/test_json_companion.py url=https://github.com/Aries-Serpent/_codex_/blob/main/tests/audit/test_json_companion.py
"""
Test that stage_s6_render writes a JSON companion file with expected schema keys
"""
import json
from pathlib import Path
from scripts.space_traversal import audit_runner as runner

def make_cfg(tmp_path):
    return {
        "output": {"artifacts_dir": str(tmp_path / "audit_artifacts"), "reports_dir": str(tmp_path / "reports")},
        "weights": {"functionality":0.25,"consistency":0.2,"tests":0.25,"safeguards":0.15,"documentation":0.15},
        "scoring": {"thresholds": {"low": 0.7, "medium": 0.85}},
        "matrix_template": "templates/audit/capability_matrix.md.j2",
        "metrics_schema_version": "2.0.0"
    }

def test_json_companion_written(tmp_path):
    cfg = make_cfg(tmp_path)
    scored = [{"id":"a","components":{"functionality":1.0,"consistency":1.0,"tests":0.0,"safeguards":0.0,"documentation":0.0},"score":0.6,"evidence_files":[], "found_patterns": []}]
    gaps = {"low_maturity": []}
    md, js = runner.render_template(cfg, {"timestamp": "x", "capabilities": scored, "gaps": [], "weights": cfg["weights"], "scoring": cfg["scoring"]})
    assert js.exists()
    data = json.loads(js.read_text())
    assert "capabilities" in data
    assert data["metrics_schema_version"] == "2.0.0"
```

```makefile name=space.mk url=https://github.com/Aries-Serpent/_codex_/blob/main/space.mk
# Copilot Space Audit Workflow Makefile (v1.2.0)

SPACE_PY ?= python
RUNNER ?= scripts/space_traversal/audit_runner.py

.PHONY: space-audit
space-audit:
	$(SPACE_PY) $(RUNNER) run

.PHONY: space-audit-fast
space-audit-fast:
	$(SPACE_PY) $(RUNNER) stage S1
	$(SPACE_PY) $(RUNNER) stage S3
	$(SPACE_PY) $(RUNNER) stage S4
	$(SPACE_PY) $(RUNNER) stage S6

.PHONY: space-audit-export-json
space-audit-export-json:
	$(SPACE_PY) $(RUNNER) stage S6

.PHONY: space-explain
space-explain:
	@if [ -z "$(cap)" ]; then echo "Usage: make space-explain cap=<capability_id>"; exit 2; fi
	$(SPACE_PY) $(RUNNER) explain $(cap)

.PHONY: space-diff
space-diff:
	@if [ -z "$(old)" ] || [ -z "$(new)" ]; then echo "Usage: make space-diff old=<old> new=<new>"; exit 2; fi
	$(SPACE_PY) $(RUNNER) diff --old $(old) --new $(new)

.PHONY: space-clean
space-clean:
	rm -rf audit_artifacts audit_run_manifest.json reports/capability_matrix_*.md reports/capability_matrix_*.json
```
