# [Audit]: Status Update Template — Review & Iteration Plan  
> Generated: 2025-11-19 13:13:33 | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Summary
- Verdict: The template at .github/templates/_codex_status_update_template.md is a solid canonical starting point for GitHub Copilot to act on and to produce Status Update audit reports. It already captures S1→S7, scoring components, core principles and useful commands.
- Caveat: For Copilot to reliably "action" the template and return fully-detailed, repeatable iterations, the file must explicitly include a small set of machine-actionable fields, companion JSON schemas, and an iteration playbook. Below I list missing/optional enhancements, then provide a concrete per-iteration plan Copilot can execute.

1) Quick checklist — Does the template contain these minimal requisites?

| Item | Required for Copilot automation? | Present (yes/no / action) |
|------|----------------------------------:|--------------------------|
| Explicit metadata header (metrics_schema_version, template_hash usage) | Yes | If absent: add metrics_schema_version and guidance to compute template_hash |
| Companion JSON schema examples (capabilities_raw/scored/manifest) | Yes | If absent: include JSON snippets (required for deterministic diffs) |
| Per-stage artifacts list with paths & canonical field names | Yes | Ensure paths match workflow.yaml (audit_artifacts/ and reports/) |
| Expected CLI/Make commands & exit codes | Yes | Ensure exit codes mapping to gates present |
| Detector API contract, both v1 & v2 | Optional but highly recommended | Add detect_v2 contract for anchorable evidence ranges |
| Iteration/run playbook (explicit steps Copilot should take) | No / Partial | Add a small step-by-step "Iteration Playbook" (see section 4 below) |
| Acceptance criteria & test checklist for changes | No / Partial | Add per-iteration acceptance criteria (see below) |

If any of the above are not present in the file, Copilot will still be able to produce a report, but automation and multi-iteration governance will be fragile.

2) Gaps & Recommended Additions (short)

| Gap | Location to Add | Severity | Why |
|-----|-----------------|---------:|-----|
| JSON companion artifact requirement (capability_matrix_<ts>.json) | S6 section | Medium | Deterministic diffs & dashboards require a machine-readable companion. |
| metrics_schema_version field | Header / Manifest notes | Low | Tracks metric/contract changes across iterations. |
| Detector v2 contract & loading rules | "Add Detector" section | Medium | Needed to capture evidence ranges and confidence for traceable fixes. |
| Explicit CI gating exit codes mapping | Quality Gates section | Low | Make automation deterministic (CI can interpret codes). |
| Template rendering context keys (pass thresholds & weights) | S6 template guidance | Low | Template currently references weight sum in one place — change to thresholds. |
| Iteration Playbook (step-by-step tasks for Copilot) | New section | High | Required for Copilot to produce "each dedicated iteration" with explicit outputs. |

3) Actionable Iteration Plan — what Copilot should produce for each iteration
(Each "iteration" = a single change & audit run cycle. For each iteration Copilot must produce: artifacts, diffs, a terse changelog, and (when relevant) a PR with code changes and tests.)

Iteration 0 — Baseline capture (first run)
- Goal: produce baseline artifacts and manifest to anchor future diffs.
- Steps for Copilot:
  1. Ensure workflow.yaml exists and points to template path. Validate paths (artifacts_dir, reports_dir).
  2. Run: python scripts/space_traversal/audit_runner.py run
  3. Collect artifacts:
     - audit_artifacts/context_index.json
     - audit_artifacts/facets.json
     - audit_artifacts/capabilities_raw.json
     - audit_artifacts/capabilities_scored.json
     - audit_artifacts/gaps.json
     - reports/capability_matrix_<ts>.md
     - reports/capability_matrix_<ts>.json (companion — add this if missing)
     - audit_run_manifest.json
  4. Validate manifest fields:
     - repo_root_sha, artifacts[].sha, template_hash, weights, metrics_schema_version
  5. Produce Baseline report: add baseline manifest to repo (or to baseline/ folder), and produce a "Baseline Summary" section in report.
- Acceptance criteria:
  - All artifacts exist and compute valid SHA values.
  - capabilities_scored.json must be syntactically valid and contain per-cap components.
  - Determinism smoke: running twice produces identical repo_root_sha and identical capabilities_scored.json (ignoring timestamp).

Iteration 1 — Enforce capability_map.overrides & missing-detector gate
- Goal: Apply workflow overrides merging and fail when overrides reference missing detectors when configured to do so.
- Steps for Copilot:
  1. Modify audit_runner.py stage_s3_capabilities to:
     - Read cfg["capability_map"]["overrides"] and apply alias/merge semantics: for each canonical ID map, merge evidence and pattern lists.
     - Add a validation: if overrides reference IDs not present in produced capabilities and cfg.options.fail_on_missing_detector == True, exit with CI code 5.
  2. Add unit tests (tests/audit/test_overrides.py) that:
     - Simulate a small context_index and facets; assert merge behavior.
     - Assert exit code when missing detector referenced.
  3. Run S3→S7, produce diff vs baseline and include change summary.
- Acceptance criteria:
  - overrides applied and visible in capabilities_raw.json and capabilities_scored.json.
  - CI exit code behavior enforced when option set.

Iteration 2 — Add JSON companion for matrix & deterministic render
- Goal: Ensure S6 writes both markdown and capability_matrix_<ts>.json for deterministic diffs and dashboards.
- Steps for Copilot:
  1. Update render_template / stage_s6_render to:
     - Write reports/capability_matrix_<ts>.json containing all fields used in markdown: capabilities array, gaps, weights, template_hash, timestamp.
     - Use stable sorting for capabilities array (by id).
  2. Update template context to include scoring.thresholds.low and pass weights normalized.
  3. Update Makefile (space.mk) to include a `space-audit-export-json` target (optional).
- Acceptance criteria:
  - reports/capability_matrix_<ts>.json exists and validates against a small JSON schema included in repo (scripts/space_traversal/schemas/capability_matrix.schema.json).
  - Diff CLI uses JSON companion by default (prefer JSON diff for CI).

Iteration 3 — Hook capability_scoring.py functions & add score_explain JSON
- Goal: Remove scoring duplication and make explain results machine-readable.
- Steps for Copilot:
  1. Refactor stage_s4_scoring to call capability_scoring.normalize_weights, score_capability, explain_score.
  2. Write an explain artifact for each capability (explain/<cap_id>.json) containing partials and contributions.
  3. Update CLI explain to emit the JSON path as well as human output.
- Acceptance criteria:
  - audit_artifacts/explain/<cap>.json exists for all capabilities.
  - explain command prints path + concise human-readable breakdown.

Iteration 4 — Detector v2 & evidence anchors
- Goal: Upgrade detectors to support evidence ranges, confidence and excerpt fields.
- Steps for Copilot:
  1. Add detect_v2 loader in load_dynamic_detectors: prefer detect_v2 when present and normalize to capabilities_raw schema including evidence objects with ranges & confidence.
  2. Update capability JSON schema to accept evidence objects (path, sha, ranges, confidence).
  3. Provide a sample detector in scripts/space_traversal/detectors/example_v2.py and unit tests for parsing ranges.
- Acceptance criteria:
  - capabilities_raw.json and capabilities_scored.json include evidence ranges for any detector emitting ranges.
  - Jinja render includes first evidence anchor excerpt.

Iteration 5 — Coverage ingestion (optional medium)
- Goal: Compute m.tests.coverage using coverage.xml mapping.
- Steps for Copilot:
  1. Add scripts/space_traversal/coverage_ingest.py to parse Cobertura/coverage.py xml into audit_artifacts/coverage_map.json.
  2. stage_s4_scoring should use coverage_map.json when present to calculate tests component (m.tests.coverage), fallback to estimate_test_depth when absent.
  3. Add CI config knob scoring.sources.coverage in workflow.yaml to enable.
- Acceptance criteria:
  - If coverage_map.json present, capabilities_scored.json tests component includes "coverage": <float>.
  - Tests for mapping correctness for sample coverage file.

4) Copilot Playbook — How to action the template and produce each dedicated iteration
- For each iteration requested by maintainers, Copilot must:
  1. Open an issue (draft) describing the change (title, problem statement, files to change).
  2. Create a branch named audit/<short-task>-<yyyymmdd>.
  3. Make minimal edits to the target files with clear commit messages and tests added under tests/.
  4. Run minimal audit steps locally using the runner (or CI step simulation) and produce the artifacts in a temporary subtree (audit_artifacts_temp/) to avoid overwriting baseline.
  5. Attach artifacts and diff summary to the PR and in the PR description include:
     - Baseline vs new avg_score Δ
     - Files changed & line count
     - Acceptance test results
  6. Request a review from owners listed in template (owner labels or CODEOWNERS).
- Example PR title: "audit: enable overrides merge + missing-detector strict gate"
- Example PR body skeleton (Copilot should fill):
  - Summary
  - Changes made (files & key functions)
  - How to test locally
  - Acceptance criteria (pass/fail)
  - Artifacts attached: urls to capabilities_scored.json and manifest

5) Required additions to the template (copyable snippets)
- Add metrics_schema_version to header and manifest guidance:
  - "metrics_schema_version: 2.0.0 — increment when any metric formula or artifact schema changes."
- Add companion JSON write guidance under S6:
  - "Always write reports/capability_matrix_<ts>.json with canonical ordering and a JSON schema (scripts/space_traversal/schemas/). Use the JSON for diffs in CI."
- Add PR & iteration checklist snippet (short) that Copilot will use before opening PRs.

6) Acceptance Criteria for the final template to be "Copilot-actionable"
- Machine fields included: metrics_schema_version, template_hash usage guidance, JSON companion schema examples, detector v2 contract, CI exit code mapping.
- Per-iteration playbook included with explicit commands, expected artifacts, and acceptance tests.
- Example detectors and unit tests present to demonstrate expected behavior.
- Template and workflow.yaml cross-validated (paths consistent).

7) Suggested small edits to commit now (PR-quick wins)
| Change | Target file | Rationale |
|--------|-------------|----------|
| Replace "Low Maturity (< {{ (weights.functionality + weights.consistency) | round(2) }} heuristic)" with "Low Maturity (< {{ scoring.thresholds.low }})" | templates/capability_matrix.md.j2 | Avoid confusion and align with workflow.yaml |
| Add JSON companion write in stage_s6_render | scripts/space_traversal/audit_runner.py | Deterministic diffs |
| Add metrics_schema_version to audit_run_manifest.json | stage_s7_manifest in audit_runner.py | Metric evolution tracking |

8) If you want, next actions I can perform for you
- Produce the exact patch (diff) for:
  - templates/capability_matrix.md.j2 change (Low Maturity line).
  - audit_runner.py: write JSON companion and apply overrides merging in stage_s3.
  - Add a sample detector_v2 and coverage_ingest stub.
- Generate unit tests for overrides and companion JSON writer.
- Draft PR descriptions and issue content.

Conclusion
- The file is a valid and useful pointer for GitHub Copilot. To make it fully actionable and reliable across iterations, add the small set of machine-actionable fields and the "Iteration Playbook" described above. Once those additions are in place (I can produce the patches), Copilot can be instructed to run each iteration, create PRs, produce artifacts, and report back with deterministic, review-ready audit updates.

```markdown name=capability_matrix.md.j2 url=https://github.com/Aries-Serpent/_codex_/blob/main/templates/audit/capability_matrix.md.j2
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

```makefile name=space.mk url=https://github.com/Aries-Serpent/_codex_/blob/main/space.mk
# Copilot Space Audit Workflow Makefile (v1.1.1)

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

```yaml name=workflow.yaml url=https://github.com/Aries-Serpent/_codex_/blob/main/.copilot-space/workflow.yaml
version: 1.1.0
stages:
  - id: index
    script: audit_runner.py
    entry: stage
    args: ["S1"]
  - id: facets
    script: audit_runner.py
    entry: stage
    args: ["S2"]
  - id: capabilities
    script: audit_runner.py
    entry: stage
    args: ["S3"]
  - id: scoring
    script: audit_runner.py
    entry: stage
    args: ["S4"]
  - id: gaps
    script: audit_runner.py
    entry: stage
    args: ["S5"]
  - id: render
    script: audit_runner.py
    entry: stage
    args: ["S6"]
  - id: manifest
    script: audit_runner.py
    entry: stage
    args: ["S7"]

weights:
  functionality: 0.25
  consistency: 0.20
  tests: 0.25
  safeguards: 0.15
  documentation: 0.15

scoring:
  thresholds:
    low: 0.70
    medium: 0.85

capability_map:
  overrides:
    training-engine: ["train_loop", "functional_training"]
  dynamic: true

output:
  reports_dir: reports
  artifacts_dir: audit_artifacts
  matrix_template: templates/audit/capability_matrix.md.j2

options:
  # When true, diff command exit code is non-zero if any capability score drops.
  fail_on_score_regression: true
  # Minimum absolute delta to consider a regression (if above flag enabled).
  regression_delta_threshold: 0.02
  # When true, missing detectors referenced in capability_map.overrides will fail the run.
  fail_on_missing_detector: true

# Metrics schema version for artifacts produced by this workflow
metrics_schema_version: "2.0.0"
```

```python name=scripts/space_traversal/detectors/example_v2.py url=https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/detectors/example_v2.py
def detect_v2(file_index: dict) -> dict:
    """
    Example detector v2 that returns evidence with ranges and confidence.
    This is a minimal illustrative detector — real detectors should inspect file contents.
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
    # Support both coverage.py and Cobertura by searching for <class> / <lines>
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
    # compute percent crude
    for f, data in cov.items():
        # attempt to read file length
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

```json
name=scripts/space_traversal/schemas/capability_matrix.schema.json
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

```python name=scripts/space_traversal/audit_runner.py url=https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/audit_runner.py
#!/usr/bin/env python
"""
Audit Runner Orchestrator for Copilot Space Traversal Workflow (v1.2.0)

Key changes in this patched runner:
 - Support detect_v2() detectors and normalize outputs
 - Apply capability_map.overrides merging (S3) and optional fail_on_missing_detector
 - Write JSON companion (reports/capability_matrix_<ts>.json) in S6 render
 - Pass scoring.thresholds.low into Jinja context and include metrics_schema_version in manifest
 - Improved manifest artifact entries with size/format/generated_at
"""
from __future__ import annotations
import argparse, json, os, re, sys, hashlib, time, importlib.util, inspect, difflib
from pathlib import Path
from typing import Dict, List, Any, Callable

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader
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
# Stage Implementations (mostly unchanged except noted)
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
            # Prefer detect_v2 if present; otherwise detect
            if hasattr(module, "detect_v2") and callable(module.detect_v2):
                funcs.append(module.detect_v2)
            elif hasattr(module, "detect") and callable(module.detect):
                funcs.append(module.detect)
            else:
                warn(f"No usable detector function in {py.name}; skipping.")
    return funcs

def _normalize_detector_output(det: dict) -> dict:
    """
    Normalize detector output to a common shape with keys:
     - id, evidence_files, found_patterns, required_patterns, meta
    For detect_v2 -> evidence objects are flattened to evidence_files while preserving 'evidence' in meta
    """
    if "evidence" in det:  # v2 detector
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
    # Apply overrides merging (aliasing)
    overrides = cfg.get("capability_map", {}).get("overrides", {}) or {}
    if overrides:
        # Build index by id
        by_id = {c["id"]: c for c in capabilities}
        merged = {}
        missing_refs = []
        # For each canonical id in overrides, merge listed aliases into canonical
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
        # Keep capabilities not referenced by overrides and add merged entries
        remaining = {k: v for k, v in by_id.items() if k not in sum((aliases for aliases in overrides.values()), []) and k not in merged}
        capabilities = list(remaining.values()) + list(merged.values())
        # If configured to fail on missing detector references, exit
        if missing_refs and cfg.get("options", {}).get("fail_on_missing_detector", False):
            warn(f"Missing detector references in overrides: {missing_refs}")
            sys.exit(5)
    # Sorting & write
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
    docs = [p for p in file_cache if p.startswith("docs/") or p.endswith(".md")]
    token = cap_id.split("-")[0]
    hits = sum(1 for p in docs if token in file_cache[p].lower())
    if not docs:
        return 0.0
    # scale factor: ensure small doc sets still get reasonable credit
    return min(1.0, hits / max(3, len(docs) * 0.1))

def stage_s4_scoring(cfg, raw_caps):
    # Use capability_scoring utilities if available
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
    # Preload evidence & docs
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
        # coverage augmentation if coverage_map exists
        cov_map = {}
        cov_path = artifacts_dir / "coverage_map.json"
        if cov_path.exists():
            cov_map = json.loads(cov_path.read_text())
        coverage_value = None
        if cov_map:
            # compute simple average coverage across evidence files present in cov_map
            vals = []
            for ef in cap.get("evidence_files", []):
                if ef in cov_map:
                    vals.append(cov_map[ef].get("percent", 0.0))
            if vals:
                coverage_value = sum(vals) / len(vals)
                # blend coverage into tests metric (conservative)
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
            # fallback
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
    # write warnings (temp) for manifest stage
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
    # Add template hash into context if available
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
    # Write machine companion JSON in canonical ordering
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
    # Pass scores thresholds into template context for correct rendering
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
        if p.name.startswith("_"):  # internal warnings file
            continue
        manifest["artifacts"].append({
            "name": p.name,
            "sha": _sha256_file(p),
            "size": p.stat().st_size,
            "format": "json",
            "generated_at": p.stat().st_mtime
        })

    # Add template hash
    tpl_dir = Path(cfg["output"]["matrix_template"]).parent
    concat = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concat += t.read_bytes()
    manifest["template_hash"] = _sha256_bytes(concat)

    # Scoring warnings
    warn_file = artifacts_dir / "_scoring_warnings.json"
    if warn_file.exists():
        manifest["warnings"].extend(json.loads(warn_file.read_text()))

    out = ROOT / "audit_run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest

# ---------------------------------------------------------------------------
# Ancillary Commands: diff & explain (unchanged except JSON companion preference)
# ---------------------------------------------------------------------------
def load_capabilities_from_any(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = {}
    if path.suffix == ".json":
        data = json.loads(text)
        caps = data.get("capabilities", [])
    else:
        # naive markdown table parsing for scores section
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
        # embed in synthetic structure
        data["capabilities"] = caps
    # build id->score map
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
    # Also print path to JSON explain if present
    explain_dir = Path(cfg["output"]["artifacts_dir"]) / "explain"
    explain_file = explain_dir / f"{cap_id}.json"
    if explain_file.exists():
        print(f"Explain JSON: {explain_file}")
    print(f"  Total score: {target['score']:.4f}")

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

    run_p = sub.add_parser("run", help="Run full pipeline")
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

```python name=tests/audit/test_overrides.py
"""
Unit tests for overrides merging and missing-detector strict gate
"""
import json
import os
import tempfile
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
    # create a fake facets input
    facets = {"generated": 0, "facets": {"train": ["src/train/foo.py"], "checkpoint": ["src/ckpt/a.py"]}, "version": "1"}
    cfg = make_cfg(tmp_path)
    # write a simple context file expected by stage_s3 dynamic (not used)
    idx = {"generated":0,"count":0,"files":[]}
    (Path(cfg["output"]["artifacts_dir"]) / "context_index.json").parent.mkdir(parents=True, exist_ok=True)
    (Path(cfg["output"]["artifacts_dir"]) / "context_index.json").write_text(json.dumps(idx))
    caps = runner.stage_s3_capabilities(cfg, facets)
    # after merging, 'merged-cap' should exist (even if base lacks evidence)
    ids = [c["id"] for c in caps]
    assert "merged-cap" in ids

def test_missing_detector_strict_fails(tmp_path, monkeypatch):
    cfg = make_cfg(tmp_path)
    cfg["options"]["fail_on_missing_detector"] = True
    # set overrides referencing non-existent detector alias
    cfg["capability_map"]["overrides"] = {"canonical": ["nonexistent-alias"]}
    facets = {"generated": 0, "facets": {}}
    # stage_s3 should exit with sys.exit(5) when missing refs and option enabled
    with pytest.raises(SystemExit) as exc:
        runner.stage_s3_capabilities(cfg, facets)
    assert exc.value.code == 5
```

```python name=tests/audit/test_json_companion.py
"""
Test that stage_s6_render writes a JSON companion file with expected schema keys
"""
import json
import tempfile
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