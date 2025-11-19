# [Audit]: Status Update — Comprehensive Canonical Template (v2.0.0)
> Generated: 2025-11-19 13:00:38 | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose: single canonical Status Update audit report template that merges: (a) the previously generated v1.2.0 template, (b) the Enhancement & Instrumentation Plan (v1.2.0-enhance), and (c) the concrete implementation details found in the repository attachments (audit_runner.py, Traversal_Workflow.md, workflow.yaml, capability_scoring.py, templates/capability_matrix.j2, Usage_Guide.md, etc.). This file explicitly lists measurable, reportable, trackable artifacts and the schema & methods required to produce an ideal, deterministic, auditable report for S1→S7 runs.

Release: v2.0.0 — includes detector v2 support, coverage ingestion, token-similarity dedupe, richer manifest, metrics versioning, and mapping to repo implementation.

--- 

Verification Summary (mapping of template sections → repository/source artifacts)
- Pipeline stages (S1–S7): adopted from Traversal_Workflow.md and audit_runner.py (stage_* functions).
- Scoring defaults & weight normalization: from Traversal_Workflow.md and capability_scoring.py + audit_runner.py stage_s4_scoring.
- Duplicate heuristic: original stem-based implementation in audit_runner.py (duplication_ratio) + planned token-similarity (enhancement).
- Safeguard keywords: SAFEGUARD_KEYWORDS constant in audit_runner.py; template references included.
- Key commands / Makefile targets: mapped from space.mk and Usage_Guide.md.
- Config schema & flags: from workflow.yaml (weights, stages, capability_map.dynamic, overrides, options.*).
- Template rendering & template_hash: render_template and template concatenation in audit_runner.py and capability_matrix.md.j2 (note: template currently has a minor inconsistency — corrected below).
- Determinism checks, manifest fields: stage_s7_manifest in audit_runner.py and Traversal_Workflow.md.
- Detector API & dynamic loading: audit_runner.py load_dynamic_detectors + enhancements (detector v2 contract proposed).
- Coverage ingestion, token-similarity, enhanced safeguards: proposed in enhancement plan and added as explicit instrumentation points below.

If any section below diverges from the repository, it is intentional (explicitly marked) and accompanied by a recommended patch.

---

Table of Contents (for automation & machines)
- Header metadata
- Executive Summary (KPI Snapshot)
- Artifact Inventory (S1–S7)
- Metrics Catalog (definitions, formulas, provenance)
- Capability Matrix (render + JSON companion)
- Gaps & Action Items (prioritized)
- Quality Gates & CI semantics (exit codes)
- Determinism & Integrity Checks
- Measurement Methods & Sampling Rules
- Instrumentation Points & Implementation Hooks
- Data Schemas (capabilities_raw.json, capabilities_scored.json, manifest)
- Detector API (v1 & v2 compatibility)
- Dashboard recommendations & aggregation
- Pre-commit & Release Checklist
- Appendix: mapping to repo files / diffs and suggested small PRs

---

## 0. Header Metadata (machine + human)
| Field | Type | Example / Notes |
|-------|------|-----------------|
| report_type | str | "Status Update Audit" |
| generated_at | timestamp | 2025-11-19 13:00:38 UTC |
| run_id | str | UUID or timestamp |
| runner_version | semver | e.g., "1.2.0" or current audit_runner.py VERSION |
| repo | str | Aries-Serpent/_codex_ |
| workspace_root_sha | sha256 | canonicalized repo listing hash (see Determinism) |
| template_hash | sha256 | concatenated Jinja bytes hash |
| config_ref | path | .copilot-space/workflow.yaml (include version) |
| artifacts_dir | path | audit_artifacts/ |
| reports_dir | path | reports/ |
| metrics_schema_version | semver | e.g., "2.0.0" (update when metrics change) |

---

## 1. Executive Summary (KPI Snapshot)
- One-line top-level statement and 1-row KPI table (both human and machine JSON companion).

| KPI | Value | Target / Threshold | Status |
|-----|------:|-------------------:|:------:|
| Capabilities assessed | <int> | — | ok/warn/fail |
| Avg capability score | 0.00 | ≥ 0.85 (green) | green/amber/red |
| Capabilities below `low` threshold | <int> | 0 | pass/fail |
| Score regressions | <int> | 0 | pass/fail |
| Weight normalization applied | yes/no | no | warn/fine |
| Template hash drift | changed/unchanged | unchanged | warn/fine |
| Determinism check | identical runs | pass/fail | pass/fail |
| CI gate status | code | 0 (ok) / >0 (fail) | |

Short narrative (free text): summarize major regressions, new detected capabilities, confidence (see m.confidence.cap), and top 3 action items with owners and ETA.

---

## 2. Artifact Inventory (S1–S7) — canonical fields
List S1–S7 artifacts including sizes, SHAs, and key metrics. For automation include machine JSON with same fields.

| Stage | ID | Artifact Path | Size (bytes) | SHA256 | Key Metrics |
|------:|----:|---------------|-------------:|--------|------------|
| S1 | context_index.json | audit_artifacts/context_index.json | | sha | file_count, indexed_size |
| S2 | facets.json | audit_artifacts/facets.json | | sha | facet_counts per domain |
| S3 | capabilities_raw.json | audit_artifacts/capabilities_raw.json | | sha | capabilities_count, dynamic_detectors_loaded |
| S4 | capabilities_scored.json | audit_artifacts/capabilities_scored.json | | sha | avg_score, score_histogram, avg_confidence |
| S5 | gaps.json | audit_artifacts/gaps.json | | sha | low_maturity_count |
| S6 | capability_matrix | reports/capability_matrix_<ts>.md + .json | | sha | template_hash embedded |
| S7 | audit_run_manifest.json | audit_run_manifest.json | | sha | repo_root_sha, template_hash, warnings |

Provenance: each artifact should include generated timestamp and generator (script path + git commit/sha if available).

---

## 3. Metrics Catalog (measurable, formula, provenance)
Each metric must include: id, name, formula, numerator, denominator, canonical function, artifact source, sampling notes, owner.

| Metric ID | Name | Formula | Source Artifact | Owner |
|----------|------|--------|-----------------|------|
| m.functionality | Functionality | (#found_patterns) / max(1,#required_patterns) | capabilities_raw.json | dev-team |
| m.consistency | Consistency | 1 - m.dup_ratio | capabilities_raw.json | infra |
| m.dup_ratio | Duplicate Ratio (stem) | sum(max(0,count(stem)-1)) / max(1,len(evidence_files)) | capabilities_raw.json | infra |
| m.dup.token_sim | Duplicate Ratio (token-sim) | normalized minhash/ngram similarity → mapped to [0,1] | internal token index (audit_artifacts/) | infra (planned v1.2.x) |
| m.tests.files | Test File Ratio | (# unique test files referencing cap) / max(1,#evidence_files) | tests/ + evidence mapping | qa |
| m.tests.coverage | Test Coverage Ratio | covered_lines_in_evidence / total_lines_in_evidence | coverage_map.json (coverage ingestion) | qa (planned v1.3.x) |
| m.safeguards.breadth | Safeguard Breadth | (# distinct safeguard families with ≥1 hit) / total_families | file contents + SAFEGUARD_KEYWORDS | security |
| m.safeguards.density | Safeguard Density | Σ(keyword_hits_in_evidence) / Σ(total_tokens_in_evidence) | file cache | security |
| m.docs_density | Documentation Density | (# doc files mentioning token) / scaled_corpus_factor | docs/ + markdown files | docs |
| m.confidence.cap | Capability Confidence | weighted mean of component confidences (if provided) | capabilities_scored.json | audit |
| m.capability_score | Composite Score | Σ(weight_i * component_i) (weights normalized) | capabilities_scored.json | audit |
| m.avg_score | Average Score | mean(m.capability_score) | capabilities_scored.json | product |
| m.low_count | Low Maturity Count | Count(cap where score < scoring.thresholds.low) | capabilities_scored.json | product |
| m.template_drift | Template Drift | template_hash != baseline.template_hash | manifest | release |

Canonical function references:
- capability scoring: scripts/space_traversal/capability_scoring.py::score_capability and audit_runner.py::stage_s4_scoring.
- duplication (stem): audit_runner.py::duplication_ratio.
- safegaurd keywords: audit_runner.py SAFE... constant and safeguard_score().

Versioning: metrics_schema_version in manifest must be incremented when any metric formula or provenance changes.

---

## 4. Capability Matrix (render + machine companion)
Render: capability_matrix_<ts>.md (Jinja). Companion: capability_matrix_<ts>.json (full structured object for dashboards and diffs).

Human table columns:
| ID | Score | Func | Consist | Tests | Safeguards | Docs | Evidence Count | Primary Deficit |
|----|------:|-----:|--------:|------:|-----------:|-----:|---------------:|-----------------|

Primary Deficit: component with lowest (component_value * normalized_weight) contribution; include per-cap score_confidence if present.

Companion JSON artifact schema snippet (capability entry):
{
  "id": "checkpointing",
  "components": {
    "functionality": {"value":0.90,"confidence":0.95},
    "consistency": {"value":0.92,"confidence":0.9},
    "tests": {"value":0.6,"coverage":0.42,"confidence":0.8},
    "safeguards": {"value":0.7,"density":0.002,"confidence":0.85},
    "documentation": {"value":0.8,"anchor_score":0.6,"confidence":0.8}
  },
  "score": 0.8285,
  "score_confidence": 0.86,
  "found_patterns": ["save_checkpoint","load"],
  "evidence": [
     {"path":"src/io/checkpoint.py","sha":"<sha>","ranges":[{"start":120,"end":142}],"confidence":0.9}
  ],
  "meta": {"detector":"static_rule","last_seen":1700000000}
}

Note: companion JSON enables deterministic diffs and dashboards (audit_runner.py currently writes only markdown; enhancement recommends writing the JSON companion per render — see Instrumentation Points).

---

## 5. Gaps & Action Items (prioritized, traceable)
Structured table and ISSUE templates (machine-friendly).

| Priority | Capability ID | Score | Primary Deficit | Evidence Samples | Suggested Action | Assignee | ETA |
|--------:|---------------|------:|-----------------|------------------|------------------|---------|-----|
| 1 | training-engine | 0.42 | tests | src/train/loop.py | Add unit tests & CI coverage; add examples | @owner | 2025-12-05 |

Accept criteria: changes increase target metric (e.g., m.tests.coverage >= 0.5) and pass determinism checks.

Linkability: suggested action should include suggested GitHub issue title & body template (automated creation via CI optional).

---

## 6. Quality Gates & CI semantics
Configurable gates (refer to workflow.yaml). Recommended exit codes:

| Gate | Condition | CI Action | Exit Code |
|------|-----------|----------|----------:|
| Low fail | Any cap.score < scoring.thresholds.low | Fail build | 3 |
| Regression fail | Δ < -regression_delta_threshold | Fail build | 4 |
| Missing detector strict | capability_map.overrides references absent detector | Fail build | 5 |
| Template drift warn | template_hash changed (manual review) | Warn & optionally fail | 2 (warn) |
| Low confidence (optional) | score_confidence < threshold | Mark require-review, do not fail | 0 (flagged) |

Implementations:
- audit_runner.py already implements regression detection & exit code 3 on regressions when enabled.
- Add explicit missing detector strict gate in stage_s3 validation (enhancement).

---

## 7. Determinism & Integrity Checks (procedure)
Determinism procedure (automated in CI step):
1. Run full pipeline twice (no source changes).
2. Compare:
   - workspace_root_sha (canonical repo listing SHA)
   - audit_artifacts/capabilities_scored.json content normalized (ordering & timestamps ignored)
3. If mismatch → fail determinism gate (report diff, highlight non-deterministic detectors, file filters, or unsorted traversal).

Canonicalization:
- workspace_root_sha = SHA256( canonical_json(sorted file paths) ) — audit_runner.py uses similar approach; ensure sort and json.dumps(..., separators=(',',':')) or documented canonicalizer.
- Template hash = SHA256(concat(sorted .j2 bytes)) — enforcement in render_template.

Integrity chain:
- manifest.artifacts[] contains name, sha, size, format, generated_at
- manifest.template_hash present
- manifest.metrics_schema_version present

---

## 8. Measurement Methods & Sampling Rules (auditability)
- File reads truncated to MAX_READ_BYTES (200KB) — documented and reported (possible undercount).
- SAFE_TEXT_EXT list defines parsable files; non-text files excluded from pattern search.
- Dynamic detectors loaded only when capability_map.dynamic == true; load errors logged to warnings.
- Weight normalization: when provided weights sum != 1.0, auto-normalize and record "weights_normalized_from:<total>" in manifest warnings.
- Duplicate heuristic: legacy stem-based calculation (audit_runner.py::duplication_ratio). v2 token-sim available as opt-in (metrics_schema_version bump).
- Coverage ingestion: if coverage_map present, use coverage_map.json to compute m.tests.coverage; else fallback to test-file heuristics.

---

## 9. Instrumentation Points & Implementation Hooks (concrete)
Files to change or add for full v2 feature parity:

- scripts/space_traversal/audit_runner.py
  - Add: capability_map.overrides application (merge aliasing) during S3 (apply merges to capabilities list).
  - Add: strict missing-detector validation (option in workflow.yaml).
  - Add: write capability_matrix_<ts>.json companion in S6 render.
  - Add: optional validator to canonicalize capabilities_scored.json ordering.
  - Where present, prefer using capability_scoring.py helpers.

- scripts/space_traversal/capability_scoring.py
  - Expose per-component confidence fields; return structured explanation used by explain command.

- scripts/space_traversal/detectors/
  - Support detect_v2() contract (evidence ranges, confidence). Backwards compatible with detect().

- scripts/space_traversal/coverage_ingest.py (new)
  - Parse coverage.xml (coverage.py/Cobertura) → produce audit_artifacts/coverage_map.json.

- scripts/space_traversal/dedupe_token_sim.py (new)
  - Implement MinHash / n-gram token similarity for evidence grouping and compute m.dup.token_sim.

- templates/audit/capability_matrix.md.j2
  - FIX: Low Maturity header currently sums functionality + consistency in attached template — update to show scoring.thresholds.low instead. Pass thresholds in render context.

- .copilot-space/workflow.yaml
  - Add knobs: scoring.sources.coverage: true/false; options.fail_on_missing_detector: true/false; metrics.version: "2.0.0".

Quick recommended small PRs:
1. Apply capability_map.overrides merging in stage_s3 (3 days).
2. Write JSON companion during S6 (1 day).
3. Update template to reference thresholds rather than weight sum (0.2 day).
4. Add missing-detector strict gate and unit tests (1 day).
(Estimates: small changes; see Implementation Backlog in Enhancement Plan.)

---

## 10. Data Schemas (canonical JSON fields)

capabilities_raw.json (schema excerpt)
{
  "generated": 1700000000,
  "version": "2.0.0",
  "capabilities": [
    {
      "id": "checkpointing",
      "evidence_files": ["src/io/checkpoint.py"],
      "found_patterns": ["save_checkpoint"],
      "required_patterns": ["save_checkpoint","load"],
      "meta": {"detector":"static_rule"}
    }
  ]
}

capabilities_scored.json (schema excerpt)
{
  "generated": 1700000000,
  "version": "2.0.0",
  "capabilities": [
    {
      "id": "checkpointing",
      "components": {
        "functionality": {"value":0.90,"confidence":0.95},
        "consistency": {"value":0.92,"confidence":0.9},
        "tests": {"value":0.6,"coverage":0.42,"confidence":0.8},
        "safeguards": {"value":0.7,"density":0.002,"confidence":0.85},
        "documentation": {"value":0.8,"anchor_score":0.6,"confidence":0.8}
      },
      "score": 0.8285,
      "score_confidence": 0.86,
      "found_patterns": [...],
      "evidence_files": [...],
      "provenance": {"generated_from":"capabilities_raw.json","generator":"audit_runner.py@<sha>"}
    }
  ]
}

audit_run_manifest.json (schema excerpt)
{
  "timestamp": 1700000000,
  "version": "2.0.0",
  "repo_root_sha": "<sha>",
  "artifacts": [{"name":"capabilities_scored.json","sha":"<sha>","size":1234,"format":"json","generated_at":1700}],
  "template_hash": "<sha>",
  "weights": { ... },
  "metrics_schema_version": "2.0.0",
  "warnings": ["weights_normalized_from:1.05"],
  "baseline_manifest_ref": "<optional: path|sha>"
}

---

## 11. Detector API (v1 + v2 compatibility)
- v1 (current repo detectors):
  def detect(file_index: dict) -> dict:
    return {
      "id":"new-cap",
      "evidence_files":[...],
      "found_patterns":[...],
      "required_patterns":[...],
      "meta":{}
    }

- v2 (enhanced; backward compatible):
  def detect_v2(file_index: dict) -> dict:
    return {
      "id":"new-cap",
      "evidence":[
        {"path":"src/x.py","sha":"<sha>","ranges":[{"start_line":10,"end_line":25}],"confidence":0.9,"excerpt":"..."}
      ],
      "found_patterns":["save"],
      "required_patterns":["save","load"],
      "meta":{"layer":"io","detector_version":"v2"}
    }

Loaders:
- audit_runner.py MUST support both detect() and detect_v2() and normalize outputs into capabilities_raw.json. If detect_v2 present, prefer it; otherwise accept detect().

---

## 12. Coverage Ingestion (design notes)
- coverage_ingest.py will:
  - Parse coverage.xml (Cobertura or coverage.py xml)
  - Map covered line numbers by file → produce audit_artifacts/coverage_map.json
  - stage_s4_scoring will use coverage_map to compute m.tests.coverage when available and include per-cap "coverage" numeric.

Fallback: if coverage_map missing, use estimate_test_depth heuristic (current audit_runner.py behavior).

---

## 13. Dashboard & Visualization Recommendations
Widgets:
- Capability Leaderboard (sortable by score, score_confidence)
- Component Contribution Heatmap (capability × components)
- Coverage Gauges (per-cap, per-module)
- Safeguard Radar (families vs density)
- Duplication Cluster graph (token similarity clusters)
- Temporal Trend (avg_score, avg_confidence, low_count)
Data endpoints: reports/*.json companion files and weekly aggregates for time-series.

Retention: keep raw artifacts for 90 days (configurable), weekly aggregates for 1 year.

---

## 14. CI / Automation Snippets & Policies
- Full run:
  python scripts/space_traversal/audit_runner.py run
- Diff (json):
  python scripts/space_traversal/audit_runner.py diff --old baseline/capabilities_scored.json --new audit_artifacts/capabilities_scored.json
- Explain:
  python scripts/space_traversal/audit_runner.py explain checkpointing

CI expectations:
- Failing exit codes mapped to gates (see Quality Gates).
- Baseline update policy: only update baseline after PR with human review and change log.

---

## 15. Pre-Commit / Release Checklist
- [ ] S1–S7 executed successfully and artifacts committed (if required)
- [ ] Manifest integrity validated (repo_root_sha & template_hash)
- [ ] JSON companion (capability_matrix_<ts>.json) present for the latest run
- [ ] No unreviewed regressions (diff summary attached)
- [ ] New detectors documented and tests added
- [ ] metrics_schema_version bumped if metrics changed

---

## 16. Appendix A — Template fixes & repo divergences (actionable)
1. capability_matrix.md.j2: currently shows "Low Maturity (< {{ (weights.functionality + weights.consistency) | round(2) }} heuristic)". This is inconsistent with workflow.yaml scoring.thresholds.low. Proposed fix: change to display "{{ scoring.thresholds.low }}" and ensure stage_s6_render passes scoring thresholds into context. (Small PR recommended.)

2. capability_scoring.py exists but stage_s4_scoring in audit_runner.py bypasses it. Proposed: refactor audit_runner.py to import and use capability_scoring.normalize_weights/explain_score functions to centralize logic (improves testability).

3. capability_map.overrides merging: workflow.yaml lists overrides (e.g., training-engine: ["train_loop","functional_training"]) but audit_runner.py does not apply them. Proposed: implement aliasing/merge in stage_s3_capabilities — when overrides configured, canonicalize IDs and merge evidence/found_patterns/required_patterns accordingly.

4. Missing detector gate: repo lacks strict enforcement of missing capability references from workflow overrides. Proposed: fail on missing detector if options.fail_on_missing_detector true.

5. Companion JSON rendering: audit_runner.py only writes markdown for S6 — add JSON companion write step for deterministic diffs.

---

## 17. Appendix B — Suggested Small PRs (priority)
- PR-1: Apply overrides merging in S3 + unit tests (owner: @maintainer) — 1–2 days.
- PR-2: Fix capability_matrix.j2 Low Maturity label & pass thresholds into template context — 0.5 day.
- PR-3: Write capability_matrix_<ts>.json companion in S6 & update make targets — 0.5 day.
- PR-4: Hook capability_scoring.py functions into audit_runner.py stage_s4_scoring — 1 day.
- PR-5: Add workflow.yaml option options.fail_on_missing_detector and enforce it in S3 — 0.5–1 day.
- PR-6: Implement coverage_ingest.py and wire scoring.sources.coverage flag — 3–5 days (feature P1).

---

## 18. Change Log
- v2.0.0: Consolidated canonical template; added detector v2 contract, coverage & token-sim hooks, companion JSON, metrics_schema_version, CI exit mapping; verified alignment with attached repo artifacts.
- v1.2.0: Base metrics catalog, dashboards, companion JSON recommendation (from earlier assistant output).
- v1.1.0: Repo-implemented features: dynamic detectors, explain & diff commands, template hash, determinism guards (as seen in audit_runner.py).

---

End of Canonical Status Update Template (v2.0.0)

Notes:
- This file intentionally synthesizes the attached repository code and the previously proposed enhancement plan. It is a superset of the current repo behavior (audit_runner.py, templates) and the desired enhancements for improved measurement fidelity.
- If you would like, I can now:
  - Produce the specific PR diffs (file patches) for PR-1..PR-5 above.
  - Generate unit tests for the new behaviors (overrides merge, missing-detector gate, JSON companion).
  - Produce the new detector v2 loader and a detector example.

