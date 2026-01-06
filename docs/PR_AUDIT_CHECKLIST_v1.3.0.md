# [Checklist]: PR Audit Template (v1.3.0) — Deterministic Capability Audit & Compliance
> Generated: Previous Cycle-12-05 | Author: mbaetiong

🧠 Roles: [Audit Orchestrator], [Capability Cartographer]  
⚡ Energy: 5  
⚛️ Physics:
- Path🛤️
- Fields🔄
- Patterns👁️
- Redundancy🔀
- Balance⚖️

## Overview

Use this template to validate PRs via the deterministic audit pipeline (S1–S7).  
Attach commands, outputs, artifacts, and SHAs. Confirm determinism, gates, and offline policy.

---

## 1) Required Safety Confirmations

- [ ] **NETWORK_SAFETY_ACK** — No network operations performed by this PR
- [ ] **OFFLINE_MODE_CONFIRM** — All audit/test operations run in strict offline mode

---

## 2) Recommended Configuration (Opt-In)

- [ ] **AUDIT_DEPTH=4** — Full depth audit (default 3); acknowledge depth selection
- [ ] **CONTENT_FILTER_MODE** — PII filtering enabled (pii or combined), if applicable
- [ ] **PII_PATTERN_SET=extended** — Extended patterns (emails, phones, IPs)
- [ ] **ALLOWLIST_PROFILE=A|B|C** — Optional file type filtering
- [ ] **MAX_BUNDLE_MB, ARCHIVE_FORMAT, ARCHIVE_POINTER_STYLE** — Artifact bundling (if used)

---

## 3) Archival Operations (if deletes/moves)

- [ ] **ADR drafted & linked** (`docs/arch/ADR-YYYYMMDD-brief-title.md`)
- [ ] **Tombstone stubs added** (`docs/arch/tombstone_template.md` per file)
- [ ] **Evidence appended** (`.codex/evidence/archive_ops.jsonl`)
- [ ] **Pointer bundle generated** (`scripts/archival/select_and_compress.py`)
- [ ] **CHANGELOG updated** (Deprecations section)

---

## 4) Scope

| Field | Value |
|-------|-------|
| **S‑IDs** | S1–S7 |
| **Areas** | docs, tests, CI, detectors |

### Description

Clear description of change scope and intent.

---

## 5) Verification Commands

Attach outputs, timestamps, exit codes for each command executed.

| Task | Command |
|------|---------|
| **Full run** | `python scripts/space_traversal/audit_runner.py run` |
| **Single stage** | `python scripts/space_traversal/audit_runner.py stage S4` |
| **Explain score** | `python scripts/space_traversal/audit_runner.py explain checkpointing` |
| **Diff** | `python scripts/space_traversal/audit_runner.py diff --old A --new B` |
| **Fast path** | `make space-audit-fast` |
| **Determinism** | `python scripts/space_traversal/verify_determinism.py --runs 2` |

---

## 6) Artifacts & Evidence

Attach files, SHAs, sizes for all generated artifacts.

| File | SHA256 (first 8 chars) | Size |
|------|------------------------|------|
| `audit_artifacts/context_index.json` | ________ | ___ KB |
| `audit_artifacts/facets.json` | ________ | ___ KB |
| `audit_artifacts/capabilities_raw.json` | ________ | ___ KB |
| `audit_artifacts/capabilities_scored.json` | ________ | ___ KB |
| `audit_artifacts/gaps.json` | ________ | ___ KB |
| `reports/capability_matrix_<ts>.md` | ________ | ___ KB |
| `audit_run_manifest.json` | ________ | ___ KB |

---

## 7) Determinism Proof

- [ ] **repo_root_sha[run1] == repo_root_sha[run2]** (attach values)
  - Run 1 SHA: ________
  - Run 2 SHA: ________
  - Equality: [ ] PASS [ ] FAIL
  
- [ ] **capabilities_scored.json equal across two runs** (normalized; exclude timestamp)
  - Normalized comparison: [ ] PASS [ ] FAIL
  
- [ ] **Template hash present and unchanged** across runs unless explicitly updated
  - Template hash: ________
  - Status: [ ] Unchanged [ ] Updated (justified)

---

## 8) Security & Vulnerability Checks (if configured)

- [ ] **CodeQL analysis** — 0 alerts (attach summary)
  - Status: [ ] PASS [ ] FAIL [ ] N/A
  - Alerts: ___
  
- [ ] **Secret detection** — 0 findings
  - Tool: ___
  - Status: [ ] PASS [ ] FAIL [ ] N/A
  
- [ ] **Injection/path traversal checks** — reviewed
  - Status: [ ] SAFE [ ] ISSUES [ ] N/A
  
- [ ] **Supply chain security** — reviewed
  - Dependencies checked: [ ] YES [ ] NO [ ] N/A

---

## 9) Code Evolution Tracking

| Aspect | Before | After | Delta |
|--------|--------|-------|------:|
| Type hint coverage | ___% | ___% | ___% |
| Import hygiene | ___% | ___% | ___% |
| Module organization health | ___ | ___ | ___ |
| Technical debt items | ___ | ___ | -___ |

---

## 10) Enhanced Impact Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|------------:|
| Legacy Imports | ___ | ___ | -___% |
| False Positives | ___ | ___ | -___% |
| Exception Comments | ___ | ___ | +___ |
| Shadowing Risk | ___ | ___ | -___% |
| Namespace Pollution | ___ | ___ | -___% |

---

## 11) Post-Merge Action Plan

| Window | Action |
|--------|--------|
| **0–24h** | Rotate baseline artifacts; tag release if applicable |
| **1–7d** | Monitor nightly audit trends; refine detectors |
| **1–4w** | Adjust weights/thresholds; expand safeguards |
| **1–3m** | Integrate coverage XML (1.3.x); add trend aggregation (1.4.x) |

---

## 12) Compliance Matrix

| Policy | Status | Notes |
|--------|--------|-------|
| **S1–S7 complete** | [ ] PASS [ ] FAIL | ___ |
| **Determinism** | [ ] PASS [ ] FAIL | ___ |
| **Offline policy** | [ ] PASS [ ] FAIL | ___ |
| **Security checks** | [ ] PASS [ ] N/A | ___ |
| **Gates thresholds** | [ ] PASS [ ] FAIL | ___ |
| **Weight normalization warning** | [ ] None [ ] Justified | ___ |
| **Manifest chain verified** | [ ] PASS [ ] FAIL | ___ |

---

## 13) Final Checklist

- [ ] All stages succeeded (S1–S7)
- [ ] No unexpected warnings
- [ ] Manifest & report added
- [ ] No unapproved regressions (diff reviewed)
- [ ] New detectors documented (Appendix if added)
- [ ] Safety confirmations complete
- [ ] All artifacts attached with SHAs
- [ ] Determinism verified (if applicable)
- [ ] Post-merge plan defined

---

## Appendix — Commands Quick Reference

### Full Audit Pipeline

```bash
# Run complete S1-S7 pipeline
python scripts/space_traversal/audit_runner.py run

# Expected output:
# - audit_artifacts/*.json (context, capabilities, gaps, facets)
# - reports/capability_matrix_*.md
# - audit_run_manifest.json
```

### Individual Stages

```bash
# S1: Discovery - Scan capabilities and patterns
python scripts/space_traversal/audit_runner.py stage S1

# S2: Contextualize - Build dependency graph
python scripts/space_traversal/audit_runner.py stage S2

# S3: Score - Calculate maturity scores
python scripts/space_traversal/audit_runner.py stage S3

# S4: Detect Gaps - Identify missing capabilities
python scripts/space_traversal/audit_runner.py stage S4

# S5: Identify Facets - Categorize capabilities
python scripts/space_traversal/audit_runner.py stage S5

# S6: Render Template - Generate capability matrix
python scripts/space_traversal/audit_runner.py stage S6

# S7: Manifest - Create audit manifest
python scripts/space_traversal/audit_runner.py stage S7
```

### Analysis Commands

```bash
# Explain a capability's score breakdown
python scripts/space_traversal/audit_runner.py explain checkpointing

# Diff two audit runs
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/capabilities_scored_run1.json \
  --new audit_artifacts/capabilities_scored_run2.json
```

### Determinism Validation

```bash
# Run audit twice and compare for determinism
python scripts/space_traversal/verify_determinism.py --runs 2

# Expected: Identical normalized outputs (excluding volatile fields)
```

### Fast Path (Partial Run)

```bash
# Quick validation (S1-S4 only)
make space-audit-fast

# Or manually:
python scripts/space_traversal/audit_runner.py stage S1
python scripts/space_traversal/audit_runner.py stage S2
python scripts/space_traversal/audit_runner.py stage S3
python scripts/space_traversal/audit_runner.py stage S4
```

---

## Dependencies

### Required
- Python 3.12.3+
- pyyaml
- jinja2

### Optional (for full functionality)
- torch (for training capability detection)
- transformers (for model capability detection)
- mlflow (for experiment tracking detection)

### Installation

```bash
# Minimal (core audit only)
pip install pyyaml jinja2

# Full (all detectors)
pip install pyyaml jinja2 torch transformers mlflow
```

---

## CI Integration Guide

### GitHub Actions Example

```yaml
name: Audit Pipeline

on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install pyyaml jinja2
      
      - name: Run audit pipeline
        run: |
          python scripts/space_traversal/audit_runner.py run
      
      - name: Verify determinism
        run: |
          python scripts/space_traversal/verify_determinism.py --runs 2
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: audit-artifacts
          path: |
            audit_artifacts/
            reports/
            audit_run_manifest.json
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'yaml'`  
**Solution**: Install pyyaml: `pip install pyyaml`

**Issue**: Determinism check fails  
**Solution**: Check for timestamp fields or non-deterministic operations. Review `verify_determinism.py` normalization logic.

**Issue**: S6 template rendering fails  
**Solution**: Ensure `.copilot-space/workflow.yaml` exists and has correct `matrix_template` path.

**Issue**: Import detection misses capabilities  
**Solution**: Check detector patterns in `scripts/space_traversal/detectors/*.py`

---

## Version History

- **v1.3.0** (Previous Cycle-12-05): Enhanced with S1-S7 pipeline integration, determinism verification, security checks, code evolution tracking
- **v1.2.0** (Previous Cycle-11-06): Baseline version with safety confirmations and standard verification
- **v1.1.0** (Previous Cycle-10-01): Initial structured checklist
- **v1.0.0** (Previous Cycle-09-01): Original basic checklist

---

## References

- **Workflow Guide**: `docs/Traversal_Workflow.md`
- **Usage Guide**: `docs/Usage_Guide.md`
- **Audit Runner**: `scripts/space_traversal/audit_runner.py`
- **Determinism Verifier**: `scripts/space_traversal/verify_determinism.py`
- **Workflow Config**: `.copilot-space/workflow.yaml`
- **Template Index**: `docs/PR_AUDIT_CHECKLISTS.md`

---

**Template Status**: ✅ ACTIVE  
**Recommended For**: All PRs with code changes, especially those affecting capabilities, detectors, or audit pipeline  
**Maintained By**: @copilot, @mbaetiong  
**Last Updated**: Previous Cycle-12-05
