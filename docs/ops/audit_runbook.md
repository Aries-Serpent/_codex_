# Space Traversal Audit Runbook (v1.4.0)
> Updated: Previous Cycle-12-10 | Author: Audit System  
🧠 Roles: [Primary: Audit Lead], [Secondary: CI Maintainer] ⚡ Energy: 5

## Purpose

End-to-end operational guide for running, validating, and interpreting the capability audit pipeline per Space Traversal Workflow v1.4.0.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make space-audit` | Full audit pipeline (S1→S7) |
| `make space-audit-fast` | Quick audit (S1,S3,S4,S6) |
| `make space-validate` | Validate quality gates |
| `make space-explain cap=<id>` | Explain capability score |
| `make space-diff old=<a> new=<b>` | Compare two audit runs |
| `nox -s space_audit` | Full audit via nox |
| `nox -s space_audit_fast` | Fast audit via nox |

---

## Audit Pipeline Stages

| Stage | Command | Output | Description |
|-------|---------|--------|-------------|
| S1 | `audit_runner.py stage S1` | `context_index.json` | Enumerate repo files with SHA256 |
| S2 | `audit_runner.py stage S2` | `facets.json` | Domain pattern clustering |
| S3 | `audit_runner.py stage S3` | `capabilities_raw.json` | Capability detection (static + dynamic) |
| S4 | `audit_runner.py stage S4` | `capabilities_scored.json` | 5-component weighted scoring |
| S5 | `audit_runner.py stage S5` | `gaps.json`, `component_gaps.json` | Low maturity identification |
| S6 | `audit_runner.py stage S6` | `capability_matrix_*.md` | Jinja2 report rendering |
| S7 | `audit_runner.py stage S7` | `audit_run_manifest.json` | Integrity chain manifest |

---

## Running a Full Audit

### Prerequisites
```bash
# Install dependencies
pip install pyyaml jinja2

# Verify audit_runner is accessible
python scripts/space_traversal/audit_runner.py --help
```

### Execution
```bash
# Full pipeline
python scripts/space_traversal/audit_runner.py run

# Or via make
make space-audit
```

### Expected Outputs
- `audit_artifacts/context_index.json` — File listing with hashes
- `audit_artifacts/facets.json` — Domain-grouped files
- `audit_artifacts/capabilities_raw.json` — Raw capability detection
- `audit_artifacts/capabilities_scored.json` — Scored capabilities
- `audit_artifacts/gaps.json` — Low maturity list
- `audit_artifacts/component_gaps.json` — Component-level gap analysis
- `reports/capability_matrix_<timestamp>.md` — Human-readable report
- `reports/codex_status_update_<date>.md` — Daily status issue body
- `audit_run_manifest.json` — Integrity manifest

---

## Validating Quality Gates

```bash
# Run validation
python scripts/space_traversal/audit_runner.py validate

# Or via make
make space-validate
```

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | All gates pass |
| 2 | Missing artifacts (run audit first) |
| 4 | Low maturity detected (`fail_on_low_maturity: true`) |
| 5 | Missing detector detected (`fail_on_missing_detector: true`) |

### Configuration
Edit `.copilot-space/workflow.yaml`:
```yaml
options:
  fail_on_low_maturity: true       # Exit 4 if any cap < 0.70
  fail_on_missing_detector: false  # Exit 5 if override detector missing
  fail_on_score_regression: true   # Exit 3 on diff regression
  regression_delta_threshold: 0.02 # Δ sensitivity
```

---

## Interpreting gaps.json

```bash
# View low maturity capabilities
jq '.low_maturity[].id' audit_artifacts/gaps.json

# View scores
jq '.low_maturity[] | {id, score}' audit_artifacts/gaps.json
```

### Fields
- `low_maturity[]` — Capabilities with score < `thresholds.low` (0.70)
- `low_threshold` — Active threshold value

---

## Interpreting component_gaps.json

```bash
# View capabilities with zero components
jq '.component_gaps[] | select(.zero_components | length > 0) | {id, zero_components}' audit_artifacts/component_gaps.json

# View missing patterns
jq '.component_gaps[] | select(.missing_patterns | length > 0) | {id, missing_patterns}' audit_artifacts/component_gaps.json
```

### Fields
- `id` — Capability ID
- `score` — Current score
- `zero_components` — Components with 0.0 value
- `low_components` — Components with value < 0.5
- `missing_patterns` — Patterns not found
- `missing_detectors` — Detector aliases not found

---

## Interpreting audit_run_manifest.json

```bash
# View artifact hashes
jq '.artifacts[] | {name, sha}' audit_run_manifest.json

# Check for warnings
jq '.warnings' audit_run_manifest.json

# View effective weights
jq '.normalized_weights' audit_run_manifest.json
```

### Key Fields
- `repo_root_sha` — Hash of sorted file list (detect additions/deletions)
- `artifacts[]` — Per-artifact SHA256 hashes
- `template_hash` — Jinja2 template hash
- `weights` — Configured weights
- `normalized_weights` — Auto-normalized weights
- `warnings` — Configuration warnings
- `coverage_stats` — Coverage metrics (if available)
- `metrics_schema_version` — Schema version (2.0.0)

---

## Explaining a Capability Score

```bash
# Explain a specific capability
python scripts/space_traversal/audit_runner.py explain checkpointing

# Or via make
make space-explain cap=checkpointing
```

### Example Output
```
Explain: checkpointing
  functionality  value=0.8000 weight=0.250 contribution=0.2000
  consistency    value=0.9500 weight=0.200 contribution=0.1900
  tests          value=0.6000 weight=0.250 contribution=0.1500
  safeguards     value=0.5000 weight=0.150 contribution=0.0750
  documentation  value=0.8000 weight=0.150 contribution=0.1200
  Total score: 0.7350
```

---

## Comparing Two Audit Runs

```bash
# Compare baseline to current
python scripts/space_traversal/audit_runner.py diff \
  --old baseline/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json

# Or via make
make space-diff old=baseline/capabilities_scored.json new=audit_artifacts/capabilities_scored.json
```

### Output Format
```
ID,OLD,NEW,DELTA
checkpointing,0.72,0.73,+0.0100
tokenization,0.85,0.82,-0.0300
```

---

## Determinism Verification

```bash
# Run audit twice
make space-audit
cp audit_run_manifest.json manifest_run1.json

make space-audit  
cp audit_run_manifest.json manifest_run2.json

# Compare (should be identical except timestamp)
diff <(jq -S 'del(.timestamp)' manifest_run1.json) \
     <(jq -S 'del(.timestamp)' manifest_run2.json)
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `validate: exit 4` | Capability below threshold | Review gaps.json, improve coverage |
| Missing capability | Detector syntax error | Check stderr during S3 |
| All safeguards = 0 | Keywords not in files | Expand keyword list in workflow.yaml |
| Template hash mismatch | Templates edited | Re-run full pipeline |
| Non-deterministic | Unsorted lists | Add `sorted()` to detector returns |

---

## Maintenance Cadence

| Interval | Task |
|----------|------|
| Daily | Review auto-generated status issue |
| Weekly | Run full audit, commit manifest |
| Monthly | Rebalance weights, update synonyms |
| Quarterly | Review detector coverage |
| Pre-Release | Full audit + validate + freeze manifest |

---

## Environment Variables

```bash
# Depth control
export AUDIT_DEPTH=4

# Coverage integration
export COVERAGE_ENABLE=1

# Token similarity (experimental)
export TOKEN_SIMILARITY_ENABLE=1

# Offline mode
export WANDB_MODE=offline
```

---

*End of Audit Runbook v1.4.0*
