# Space Traversal Capability Audit Guide (v1.4.0)

> Generated: 2025-11-09 | Author: Codex Audit System  
> Roles: [Audit Orchestrator], [Capability Cartographer]  
> Energy: 5/5

---

## 1. Purpose

**Deterministic audit pipeline** for the **_codex_** ML platform that:
- **Harvests** → repo structure (depth-gated traversal)
- **Facets** → domain clustering (ML-specific patterns)
- **Extracts** → capability detection (static + dynamic detectors)
- **Scores** → maturity assessment (5-component weighting + external metrics)
- **Gaps** → threshold analysis (low < 0.70 flagging)
- **Renders** → markdown matrix (Jinja2 templates)
- **Manifests** → integrity chain (SHA256 provenance + warnings aggregation)

---

## 2. Codex-Specific Enhancements (v1.4.0)

### New Capabilities Detected

Based on actual repo structure, the audit now recognizes:

| Domain | Facet Keys | Required Patterns | Added In |
|--------|-----------|-------------------|----------|
| **ML Training** | `train` | `train`, `epoch`, `loss` | v1.4.0 |
| **Model Serving** | `serve`, `inference` | `serve`, `predict`, `api` | v1.4.0 |
| **Experiment Tracking** | `logging`, `tracking` | `mlflow`, `wandb`, `tensorboard` | v1.0 |
| **Data Pipelines** | `data`, `dataset` | `split`, `loader`, `transform` | v1.0 |
| **Security/Secrets** | `security`, `secret` | `sanitize`, `redact`, `baseline` | v1.4.0 |
| **Status Reporting** | `status`, `audit` | `codex_status`, `report` | v1.4.0 |
| **Archival/Bundling** | `archive`, `bundle` | `prefix`, `manifest`, `pointer` | v1.4.0 |

### External Metrics Integration (P5)

```bash
# New environment variables (required for P5 features)
export TOKEN_SIMILARITY_ENABLE=1      # Enables token_similarity.json ingestion
export COVERAGE_ENABLE=1              # Enables coverage_stats.json ingestion
export SECURITY_SEVERITY_ENABLE=1     # Enables security_severity.json classification
export SEVERITY_MULTIPLIER_MODE=additive  # Mode: additive|penalty|none
export BUNDLE_PREFIX_MODE=1           # Auto-prefix validation
export PREFIX_VALIDATE_AUTO=1         # Run validate_prefixes.py in manifest stage
export SUMMARY_ENABLE=1               # Emit knobs_effective.json sidecar
```

### Component Scoring Updates

```python
# v1.4.0 formulas (applied in stage_s4_scoring)
consistency = base_consistency * similarity_index  # P5: token similarity multiplier
tests = max(base_tests, coverage_percent)          # P5: coverage XML override
safeguards = base_safeguards * sev_factor          # P5: severity-influenced (additive/penalty)
```

---

## 3. Stages (S1–S7) — Updated

| ID | Output | Action | Codex-Specific Logic |
|----|--------|--------|----------------------|
| **S1** | `context_index.json` | Enumerate + hash (sorted) | Depth gating via `AUDIT_DEPTH` env; skips `.venv/`, `node_modules/`, `audit_artifacts/` |
| **S2** | `facets.json` | Regex domain clustering | Extended patterns: `serve`, `inference`, `secret`, `status`, `archive` |
| **S3** | `capabilities_raw.json` | Static + dynamic detectors | Loads `scripts/space_traversal/detectors/*.py`; truncates evidence at 50 files if depth < 4 |
| **S4** | `capabilities_scored.json` | Component weighting (5D) | Consumes `token_similarity.json`, `coverage_stats.json`, `security_severity.json` |
| **S5** | `gaps.json` + `component_gaps.json` | Threshold filter (low < 0.70) | Computes `missing_patterns`, `zero_components`, `missing_detectors` |
| **S6** | `capability_matrix_<ts>.md` | Jinja render | Includes `thresholds`, `gap_summary`, `missing_detectors` in context |
| **S7** | `audit_run_manifest.json` | Hash chain + warnings | Auto-runs `validate_prefixes.py` (warn-only); aggregates knobs snapshot |

---

## 4. Core Principles

| Principle | Enforcement |
|-----------|-------------|
| **Determinism** | Sorted traversal, truncated reads (200KB), stable merges |
| **Transparency** | `explain` command, JSON component breakdown, `partials` field |
| **Extensibility** | Drop-in detectors in `scripts/space_traversal/detectors/` |
| **Offline Safety** | No network calls; all external data via local JSON |
| **Minimal Writes** | Outputs restricted to `audit_artifacts/`, `reports/`, root manifest |

---

## 5. Directory Layout (Codex-Aligned)

| Path | Description | Notes |
|------|-------------|-------|
| `scripts/space_traversal/` | Orchestration, scoring, validators | Core audit engine |
| `scripts/space_traversal/detectors/` | Drop-in capability detectors | Auto-loaded if `capability_map.dynamic: true` |
| `scripts/config/` | Knob parsing (depth gating) | Provides `get_depth()`, `normalize_from_env()` |
| `scripts/archive/` | Prefix validation | `validate_prefixes.py` auto-invoked in S7 |
| `scripts/status/` | Status reporting utilities | Potential detectors for status capability |
| `scripts/security/` | Security/secret utilities | Feeds into safeguards scoring |
| `templates/audit/` | Jinja2 templates | `capability_matrix.md.j2` + custom templates |
| `audit_artifacts/` | Intermediate JSON outputs | S1–S5 outputs + external metrics |
| `reports/` | Published markdown matrices | Timestamped capability matrices |
| `.copilot-space/workflow.yaml` | Declarative pipeline config | Defines weights, thresholds, stages |

---

## 6. Scoring Components (Default Weights)

| Component | Weight | Definition | Signals | Codex Metric Source |
|-----------|-------:|------------|---------|---------------------|
| **functionality** | 0.25 | Presence & pattern coverage | Required pattern hits | Static detectors |
| **consistency** | 0.20 | Non-duplication & similarity | `1 - dup_ratio * similarity_index` | `token_similarity.json` (P5) |
| **tests** | 0.25 | Coverage breadth | `max(test_ratio, coverage_percent)` | `coverage_stats.json` (P5) |
| **safeguards** | 0.15 | Integrity & reproducibility | Keyword presence * severity factor | `security_severity.json` (P5) |
| **documentation** | 0.15 | Doc token density | Synonym-expanded doc hits | Synonym map in `audit_runner.py` |

**Auto-normalization**: If weights ≠ 1.0, system normalizes and logs warning in manifest.

---

## 7. Execution Entrypoints (Codex-Specific)

| Command | Function | Example |
|---------|----------|---------|
| **Full run** | S1→S7 pipeline | `python scripts/space_traversal/audit_runner.py run` |
| **Single stage** | Run one stage | `python scripts/space_traversal/audit_runner.py stage S4` |
| **Explain score** | Component breakdown | `python scripts/space_traversal/audit_runner.py explain logging-tracking` |
| **Diff reports** | Compare two runs | `python scripts/space_traversal/audit_runner.py diff --old A.md --new B.md` |
| **Validate gates** | Policy check | `python scripts/space_traversal/audit_runner.py validate` |

---

## 8. Configuration (.copilot-space/workflow.yaml)

### Key Fields

| Path | Type | Example | Description |
|------|------|---------|-------------|
| `version` | semver | `1.4.0` | Workflow spec version |
| `stages` | list | `[S1, S2, ..., S7]` | Execution ordering |
| `weights` | map | `{functionality: 0.25, ...}` | Component weights (auto-normalized) |
| `scoring.thresholds.low` | float | `0.70` | Low maturity cutoff |
| `scoring.thresholds.medium` | float | `0.85` | Medium maturity label |
| `scoring.component_caps` | map | `{functionality: 1.0}` | Per-component ceiling (optional) |
| `capability_map.dynamic` | bool | `true` | Enable detector auto-loading |
| `capability_map.overrides` | map | `{training-engine: ["train_loop"]}` | ID merging/aliasing |
| `output.reports_dir` | str | `reports` | Matrix output location |
| `output.artifacts_dir` | str | `audit_artifacts` | JSON artifacts location |
| `output.matrix_template` | str | `templates/audit/capability_matrix.md.j2` | Jinja2 template path |
| `options.fail_on_score_regression` | bool | `true` | Exit non-zero if Δ < threshold |
| `options.regression_delta_threshold` | float | `0.02` | Regression sensitivity |
| `options.fail_on_low_maturity` | bool | `false` | Exit non-zero if any cap < low |
| `options.fail_on_missing_detector` | bool | `false` | Exit non-zero if detector absent |

---

## 9. Safeguard Keywords (Codex-Extended)

### Default Keywords
```python
SAFEGUARD_KEYWORDS = [
    "sha256", "checksum", "rng", "seed",
    "offline", "WANDB_MODE"
]
```

### Codex-Recommended Additions (v1.4.0)
```python
# Already added to scripts/space_traversal/audit_runner.py
SAFEGUARD_KEYWORDS += [
    "deterministic", "reproduce", "manifest",
    "baseline", "secret", "sanitize"
]
```

**Scoring Logic**: `safeguards = (keywords_with_hits / total_keywords) * severity_factor`

---

## 10. Adding a Capability Detector (Codex Example)

### Step-by-Step

1. **Create Detector File**
   ```python
   # scripts/space_traversal/detectors/ml_serving.py
   def detect(file_index: dict) -> dict:
       """Detect ML serving capability."""
       files = file_index.get("files", [])
       evidence = []
       found_patterns = set()
       required_patterns = ["serve", "predict", "api"]
       
       for meta in files:
           path = meta["path"]
           if any(k in path.lower() for k in ["serve", "api", "inference"]):
               evidence.append(path)
               if "serve" in path.lower():
                   found_patterns.add("serve")
               if "api" in path.lower():
                   found_patterns.add("api")
       
       return {
           "id": "ml-serving",
           "evidence_files": sorted(set(evidence)),
           "found_patterns": sorted(found_patterns),
           "required_patterns": required_patterns,
           "meta": {"layer": "inference", "priority": "high"}
       }
   ```

2. **Enable Dynamic Loading** (in `workflow.yaml`)
   ```yaml
   capability_map:
     dynamic: true
     overrides:
       ml-serving: ["serve", "predict", "api"]
   ```

3. **Run Pipeline**
   ```bash
   python scripts/space_traversal/audit_runner.py run
   ```

4. **Verify** in `audit_artifacts/capabilities_raw.json` and final matrix.

---

## 11. Manifest Fields (v1.4.0)

| Field | Description | Example |
|-------|-------------|---------|
| `repo_root_sha` | SHA256 of sorted file listing | `7f3a2e...` |
| `artifacts[]` | Per-artifact SHA array | `[{name: "gaps.json", sha: "abc123"}]` |
| `template_hash` | Concatenated Jinja template hash | `e4b5c...` |
| `weights` | Effective normalized weights | `{functionality: 0.25, ...}` |
| `warnings` | Aggregated warnings | `["weights_normalized_from:1.05", "prefix_violations:2"]` |
| `knobs_effective` | Snapshot of effective env vars | `{TOKEN_SIMILARITY_ENABLE: "1", ...}` (if `SUMMARY_ENABLE=1`) |

---

## 12. Quality Gates (Codex-Tuned)

| Gate | Condition | Action | Config Key |
|------|-----------|--------|------------|
| **Low Fail** | Any cap score < `low` | Exit code 4 | `options.fail_on_low_maturity: true` |
| **Regression Fail** | Δ < `-regression_delta_threshold` | Exit code 3 | `options.fail_on_score_regression: true` |
| **Missing Detector** | Detector in overrides but absent | Exit code 4 | `options.fail_on_missing_detector: true` |
| **Prefix Violations** | Bundling prefix mismatch | Warning in manifest | `BUNDLE_PREFIX_MODE=1` |
| **High Severity Secrets** | `security_severity.counts.high > 0` | Warning in manifest | `SECURITY_SEVERITY_ENABLE=1` |

---

## 13. Failure Radar (Codex-Contextualized)

| Symptom | Stage | Root Cause | Remediation |
|---------|-------|------------|-------------|
| **Missing capability** | S3 | Detector not loaded / syntax error | Enable `dynamic: true`; check Python traceback |
| **Zero safeguards** | S4 | Keywords not found in evidence | Expand `SAFEGUARD_KEYWORDS` list |
| **High duplication** | S4 | Over-broad facet regex | Narrow patterns (e.g., `r"serve"` → `r"serve\.py$"`) |
| **Template hash mismatch** | S7 | Template edited post-run | Re-run full pipeline |
| **Low consistency** | S4 | Duplicate file stems | Refactor code or accept penalty |
| **Zero tests** | S4 | No test files linked | Add tests or enable `COVERAGE_ENABLE=1` |

---

## 14. Environment Variables (Complete List)

```bash
# Depth control
export AUDIT_DEPTH=4  # Max directory depth (default: 3)

# External metrics (P5)
export TOKEN_SIMILARITY_ENABLE=1      # Enable similarity index
export COVERAGE_ENABLE=1              # Enable coverage stats
export SECURITY_SEVERITY_ENABLE=1     # Enable severity classification
export SEVERITY_MULTIPLIER_MODE=additive  # additive|penalty|none

# Prefix validation (P5)
export BUNDLE_PREFIX_MODE=1           # Enable prefix checking
export PREFIX_VALIDATE_AUTO=1         # Auto-run validator in S7

# Knobs summary
export SUMMARY_ENABLE=1               # Emit knobs_effective.json

# Override output paths (optional)
export AUDIT_ARTIFACTS_DIR=audit_artifacts
export REPORTS_DIR=reports
```

---

## 15. Key Commands Reference

```bash
# Full audit
python scripts/space_traversal/audit_runner.py run

# Single-stage re-run
python scripts/space_traversal/audit_runner.py stage S4

# Explain specific capability
python scripts/space_traversal/audit_runner.py explain ml-serving

# Compare two runs
python scripts/space_traversal/audit_runner.py diff \
  --old reports/capability_matrix_20251109_095000.md \
  --new reports/capability_matrix_20251109_095233.md

# Validate policy gates
python scripts/space_traversal/audit_runner.py validate
```

---

## 16. Physics-Inspired Design Notes

### Path: Deterministic Traversal
- Sorted iteration ensures reproducible order
- Depth gating prevents runaway recursion
- Skip prefixes filter vendor/cache directories

### Fields: Dynamic Detector Loading
- Extensibility without core modification
- Auto-discovery via Python introspection
- Isolated failure domains (per-detector try/catch)

### Patterns: Facet-Based Clustering
- Domain regex patterns group evidence
- Synonym expansion (docs scoring)
- Multi-pattern OR logic (flexibility)

### Redundancy: Multi-Signal Scoring
- 5 independent components (functionality, consistency, tests, safeguards, docs)
- External metrics override (P5: coverage, similarity)
- Aggregated warnings (manifest consolidation)

### Balance: Weight Normalization
- Auto-correct if sum ≠ 1.0
- Transparent logging (manifest warnings)
- Override-safe (component caps)

---

## 17. Determinism Validation

### Procedure
1. Run pipeline twice without code changes:
   ```bash
   python scripts/space_traversal/audit_runner.py run
   mv audit_run_manifest.json audit_run_manifest_A.json
   python scripts/space_traversal/audit_runner.py run
   mv audit_run_manifest.json audit_run_manifest_B.json
   ```

2. Compare (ignoring timestamp):
   ```bash
   jq 'del(.timestamp)' audit_run_manifest_A.json > A_norm.json
   jq 'del(.timestamp)' audit_run_manifest_B.json > B_norm.json
   diff A_norm.json B_norm.json
   ```

3. **Expected**: No diff except `generated` timestamps in artifacts.

---

## 18. Maintenance Cadence (Codex-Tuned)

| Interval | Tasks |
|----------|-------|
| **Weekly** | Run audit; review deltas; commit if material changes |
| **Monthly** | Rebalance weights; refine detectors; update synonyms |
| **Quarterly** | Validate duplication heuristic vs manual review; rotate safeguard keywords |
| **Before Release** | Full audit + policy gates (`validate` command); freeze manifest |

---

## 19. FAQ (Codex-Contextualized)

### Q: How do I add ML-specific patterns?
**A**: Update `DOMAIN_PATTERNS` in `audit_runner.py`:
```python
# Example: Add GPU training pattern
DOMAIN_PATTERNS["gpu"] = re.compile(r"cuda|gpu|torch\.cuda", re.I)
```

### Q: Why is my capability score 0.00?
**A**: Check these in order:
1. Evidence files found? (Check `capabilities_raw.json`)
2. Required patterns present? (Scan evidence file content)
3. Weights properly normalized? (Check manifest warnings)
4. Component caps too restrictive? (Review `scoring.component_caps` in YAML)

### Q: How to disable external metrics?
**A**: Unset environment variables:
```bash
unset TOKEN_SIMILARITY_ENABLE
unset COVERAGE_ENABLE
unset SECURITY_SEVERITY_ENABLE
```

### Q: Where are the actual detector files?
**A**: In the repo at `scripts/space_traversal/detectors/` (now includes ml_serving.py, status_reporting.py, archival_bundling.py).

---

## 20. Domain Patterns (Extended v1.4.0)

```python
DOMAIN_PATTERNS = {
    # Original
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
```

---

## 21. Synonym Map (Documentation Scoring)

```python
DOCS_SYNONYMS_MAP = {
    "checkpointing": ["ckpt", "checkpointing", "checkpoints"],
    "tokenization": ["tokenizer", "tokenize", "bpe", "sentencepiece"],
    "training-engine": ["trainer", "training", "train"],
    "evaluation-metrics": ["metrics", "eval", "perplexity", "accuracy", "loss"],
    "data-pipeline": ["dataset", "dataloader", "loader", "ingest", "preprocess"],
    "safety-security": ["sanitize", "redact", "secret", "security", "baseline"],
    "logging-tracking": ["tracking", "mlflow", "wandb", "tensorboard", "log"],
    "configuration": ["config", "hydra", "omegaconf", "yaml"],
    
    # Codex-specific (v1.4.0)
    "ml-serving": ["serve", "api", "inference", "predict", "fastapi"],
    "inference-serving": ["serve", "api", "inference", "predict", "fastapi"],
    "status-reporting": ["status", "audit", "report", "codex_status"],
    "archival-bundling": ["archive", "bundle", "manifest", "pointer"],
}
```

---

*End of Space Traversal Guide v1.4.0*
