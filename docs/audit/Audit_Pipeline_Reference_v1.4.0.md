# Audit Pipeline Reference - v1.4.0

**Roles**: [Audit Orchestrator], [Capability Cartographer]  
**Energy**: 5  
**Version**: 1.4.0  
**Last Updated**: 2025-12-09

> **NOTE**: Full explanations in:  
> - `Traversal_Workflow.md` (flow & formulas)  
> - `Usage_Guide.md` (commands & ops)  
> - `docs/audit/` (v1.4.0 feature guides)

---

## 1. Purpose

Deterministic audit pipeline: harvest → facet → extract → score → gap → render → manifest (integrity chain).

**NEW in v1.4.0**:
- Coverage augmentation for accurate test scoring
- Token-similarity for content-based duplication detection
- Enhanced reporting with daily status updates

---

## 2. Stages (S1–S7)

| ID | Output | Action | Notes |
|----|--------|--------|-------|
| S1 | context_index.json | Enumerate + hash file list (sorted) | |
| S2 | facets.json | Regex domain clustering | |
| S3 | capabilities_raw.json | Static + dynamic detectors merge | |
| S4 | capabilities_scored.json | Component weighting (auto-normalize) | **v1.4.0: Coverage & token-similarity** |
| S5 | gaps.json | Threshold filter (low < 0.70) | |
| S6 | capability_matrix_<ts>.md | Jinja render (template_hash embedded) | **v1.4.0: Enhanced reports** |
| S7 | audit_run_manifest.json | Hash chain (repo_root_sha + artifacts) | |

---

## 3. Core Principles

- **Determinism**: Sorted + truncated reads, reproducible hashes
- **Transparency**: Explain & diff commands
- **Extensibility**: Custom detectors in `detectors/`
- **Offline Safety**: No network calls
- **Minimal Writes**: Only to `audit_artifacts/` and `reports/`
- **Backward Compatibility**: v1.4.0 fully compatible with v1.3.x

---

## 4. Scoring (Defaults)

### Component Weights
```yaml
functionality: 0.25
consistency: 0.20
tests: 0.25
safeguards: 0.15
documentation: 0.15
```

### Score Formula
```
Score = Σ(weight × component ∈ [0,1])
```

### Component Calculations

| Component | Formula | v1.4.0 Enhancement |
|-----------|---------|-------------------|
| **Functionality** | pattern_ratio = found_patterns / required_patterns | - |
| **Consistency** | 1 - dup_ratio | **Token-similarity available** |
| **Tests** | test_evidence_ratio | **Coverage augmentation available** |
| **Safeguards** | safeguard_keyword_breadth | - |
| **Documentation** | doc_token_density | - |

---

## 5. Duplicate Heuristics (v1.4.0)

### Simple (Default, Backward Compatible)
```
dup_ratio = Σ(file_stem_duplicates) / evidence_count
```
- Fast: O(n)
- Filename-based
- Deterministic

### Token-Similarity (v1.4.0 NEW)
```yaml
# Enable in workflow.yaml
scoring:
  dup:
    heuristic: "token_similarity"
    threshold: 0.7                # Jaccard similarity threshold
    max_pairwise: 1000           # Scalability cap
    max_tokens_per_file: 1000    # Memory control
```

**Algorithm**:
1. Tokenize file content
2. Compute Jaccard similarity: J(A,B) = |A ∩ B| / |A ∪ B|
3. Mark pairs with J ≥ threshold as duplicates
4. Return duplicate_pairs / total_pairs

**Benefits**:
- Content-aware
- Detects copy-paste code
- Configurable sensitivity

**See**: `docs/audit/Configuration_v1.4.0.md`

---

## 6. Coverage Augmentation (v1.4.0 NEW)

### Enable Coverage
```yaml
# workflow.yaml
scoring:
  coverage:
    enabled: true
    xml_patterns:
      - "coverage.xml"
      - "**/coverage.xml"
    augment_tests_score: true
```

### How It Works
1. Discover coverage XML files (Cobertura/coverage.py format)
2. Parse to generate `coverage_map.json`
3. Scoring: `test_score = max(baseline_heuristic, coverage_percent)`

### Benefits
- Accurate test scores based on actual coverage
- Visibility into coverage gaps
- Incentivizes writing tests

**See**: `docs/audit/Configuration_v1.4.0.md`

---

## 7. Safeguard Keywords

**Current List**:
- sha256, checksum, verify, validate
- rng, seed, random_state, deterministic
- offline, WANDB_MODE=offline, no_network
- backup, checkpoint, snapshot, integrity

**Customize**: Edit in `scripts/space_traversal/audit_runner.py`

---

## 8. Key Commands

| Task | Command |
|------|---------|
| **Full run** | `python scripts/space_traversal/audit_runner.py run` |
| **Fast path** | `make space-audit-fast` (skips S2, S5, S7) |
| **Single stage** | `python scripts/space_traversal/audit_runner.py stage S4` |
| **Explain score** | `python scripts/space_traversal/audit_runner.py explain <capability-id>` |
| **Diff results** | `python scripts/space_traversal/audit_runner.py diff --old A --new B` |
| **Coverage gen** | `pytest --cov=src --cov-report=xml` |
| **Manual coverage** | `python scripts/space_traversal/coverage_ingest.py coverage.xml` |

---

## 9. Config (workflow.yaml)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| version | string | "1.4.0" | Spec semver |
| stages | list[str] | ["S1"..."S7"] | Ordered stage IDs |
| weights | dict | See §4 | Component weights (auto-normalize) |
| scoring.thresholds.low | float | 0.70 | Low maturity cutoff |
| scoring.coverage.enabled | bool | false | **v1.4.0**: Enable coverage augmentation |
| scoring.coverage.xml_patterns | list[str] | ["coverage.xml"] | **v1.4.0**: Coverage file patterns |
| scoring.dup.heuristic | string | "simple" | **v1.4.0**: "simple" or "token_similarity" |
| scoring.dup.threshold | float | 0.7 | **v1.4.0**: Jaccard similarity threshold |
| capability_map.dynamic | bool | false | Enable detector discovery |
| capability_map.overrides | dict | {} | Merge/alias capability IDs |
| options.fail_on_score_regression | bool | false | Exit non-zero if score drops |

**See**: `docs/audit/Configuration_v1.4.0.md` for full v1.4.0 options

---

## 10. Add Custom Detector

**Create**: `scripts/space_traversal/detectors/detector_<id>.py`

```python
def detect(file_index: dict) -> dict:
    """
    file_index: {"files": [{"path": "...", "hash": "..."}], ...}
    """
    evidence_files = []
    found_patterns = []
    required_patterns = ["pattern1", "pattern2"]
    
    # Your detection logic here
    for file in file_index["files"]:
        if matches_criteria(file):
            evidence_files.append(file["path"])
            found_patterns.append("pattern1")
    
    return {
        "id": "new-capability",
        "evidence_files": evidence_files,
        "found_patterns": found_patterns,
        "required_patterns": required_patterns,
        "meta": {"custom_key": "value"}
    }
```

**Run**: `python scripts/space_traversal/audit_runner.py stage S3`  
**Verify**: Check `capabilities_raw.json` and `capabilities_scored.json`

---

## 11. Manifest Fields

| Field | Description | v1.4.0 |
|-------|-------------|--------|
| repo_root_sha | SHA256(sorted file names) | ✓ |
| artifacts[].sha | Per-JSON hash | ✓ |
| template_hash | Concatenated Jinja hash | ✓ |
| weights | Effective normalized weights | ✓ |
| coverage_enabled | Coverage augmentation status | **NEW** |
| dup_heuristic | Duplication method used | **NEW** |
| warnings | Weight or stage notes | ✓ |

---

## 12. Quality Gates (Optional)

| Gate | Condition | Result |
|------|-----------|--------|
| Low fail | score < low_threshold | Exit non-zero |
| Regression fail | Δscore < -regression_delta | Exit non-zero |
| Hash drift warn | template_hash changed | Manual review |
| Missing detector | Referenced but absent | Exit non-zero |
| **Coverage drop** | **coverage_percent < previous** | **Exit non-zero (v1.4.0)** |

---

## 13. Determinism Check

**Expectation**: Run twice unchanged → identical:
- `repo_root_sha`
- `capabilities_scored.json` (ignoring timestamp)
- `coverage_map.json` (if coverage enabled)

**Mismatch** ⇒ Inspect:
- Detector ordering
- File filters
- Token-similarity randomness (should be deterministic)

---

## 14. Failure Radar

| Symptom | Fix |
|---------|-----|
| Missing capability | Enable dynamic discovery or fix detector |
| All safeguards = 0 | Update keyword list |
| High duplication | Narrow facet regex or tune token-similarity threshold |
| Template hash mismatch | Re-run pipeline |
| **coverage_map.json missing** | **Check xml_patterns, verify coverage.xml exists** |
| **Token-similarity slow** | **Reduce max_pairwise or use simple heuristic** |
| **Scores decreased in v1.4.0** | **Token-similarity more accurate; review findings** |

**See**: `docs/audit/Troubleshooting_v1.4.0.md`

---

## 15. Pre-Commit Checklist

- [ ] S1–S7 success (or fast path S1,S3,S4,S6)
- [ ] No unexpected warnings
- [ ] Manifest & report generated
- [ ] Diffs reviewed (no unapproved regressions)
- [ ] New detectors documented
- [ ] **Coverage generated (if enabled)**
- [ ] **Token-similarity performance acceptable (if enabled)**

---

## 16. v1.4.0 Migration

**From v1.3.x**:
- ✅ Fully backward compatible
- ✅ New features are opt-in
- ✅ No breaking changes

**Enable v1.4.0 features**:
1. Add coverage config to workflow.yaml
2. Run tests with coverage: `pytest --cov=src --cov-report=xml`
3. Enable token-similarity: Set `scoring.dup.heuristic: "token_similarity"`
4. Run audit: `make space-audit`

**See**: `docs/audit/Migration_v1.3_to_v1.4.md`

---

## 17. Upgrade Path

| Version | Features |
|---------|----------|
| 1.3.x | Baseline audit pipeline |
| **1.4.0** (current) | **Coverage augmentation, Token-similarity, Enhanced reporting** |
| 1.5.x (planned) | Trend aggregation, historical tracking |
| 2.0.0 (planned) | Multi-repo federation, API server |

---

## 18. Documentation

### Core Docs
- `Traversal_Workflow.md` - Technical workflow details
- `Usage_Guide.md` - Operational commands and examples
- `AGENTS.md` - Repository conventions

### v1.4.0 Feature Guides
- `docs/audit/Configuration_v1.4.0.md` - Configuration options and examples
- `docs/audit/Migration_v1.3_to_v1.4.md` - Migration guide from v1.3.x
- `docs/audit/Troubleshooting_v1.4.0.md` - Common issues and solutions
- `docs/audit/API_Reference_v1.4.0.md` - Module API documentation
- `docs/audit/Integration_Examples.md` - CI/CD and tool integrations
- `docs/audit/Performance_Tuning.md` - Optimization strategies

---

## 19. Quick Start v1.4.0

### Basic Audit (v1.3.x compatible)
```bash
python scripts/space_traversal/audit_runner.py run
```

### With Coverage Augmentation
```bash
# 1. Generate coverage
pytest --cov=src --cov-report=xml

# 2. Enable in workflow.yaml
# scoring:
#   coverage:
#     enabled: true

# 3. Run audit
make space-audit
```

### With Token-Similarity
```bash
# 1. Enable in workflow.yaml
# scoring:
#   dup:
#     heuristic: "token_similarity"
#     threshold: 0.7

# 2. Run audit
make space-audit
```

### Full v1.4.0 Experience
```bash
# Enable both features in workflow.yaml, then:
pytest --cov=src --cov-report=xml
make space-audit
```

---

## 20. Performance Tips (v1.4.0)

| Scenario | Configuration | Command |
|----------|--------------|---------|
| **Quick check** | Simple dup, no coverage | `make space-audit-fast` |
| **CI/CD** | Token-sim (max_pairwise=500) | `make space-audit-fast` |
| **Development** | Full features, default params | `make space-audit` |
| **Production** | Full features, high accuracy | `python ... run` |
| **Pre-commit** | Simple dup, no coverage | `make space-audit-fast` |

**See**: `docs/audit/Performance_Tuning.md`

---

## 21. Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| coverage_map.json missing | Check `scoring.coverage.enabled: true` and `coverage.xml` exists |
| Slow performance | Reduce `max_pairwise` or use `heuristic: "simple"` |
| Scores decreased | Token-similarity more accurate; review if findings are valid |
| Import errors | Run from repo root: `cd /path/to/_codex_` |
| Type errors | Already fixed in v1.4.0; if custom code, add type ignores |

**See**: `docs/audit/Troubleshooting_v1.4.0.md`

---

## 22. Integration Examples

- **GitHub Actions**: See `docs/audit/Integration_Examples.md`
- **GitLab CI**: See `docs/audit/Integration_Examples.md`
- **Pre-commit Hooks**: See `docs/audit/Integration_Examples.md`
- **MLflow Logging**: See `docs/audit/Integration_Examples.md`
- **Slack Notifications**: See `docs/audit/Integration_Examples.md`

---

## Summary

v1.4.0 enhances the audit pipeline with:
- ✅ **Coverage augmentation** for accurate test scores
- ✅ **Token-similarity** for content-based duplicate detection
- ✅ **Enhanced reporting** with daily status updates
- ✅ **Backward compatibility** with v1.3.x
- ✅ **Comprehensive documentation** (6 new guides)

**All features are opt-in and fully configurable.**

---

**Version**: 1.4.0  
**Maintained By**: Audit Pipeline Team  
**Last Updated**: 2025-12-09  
**Questions**: See documentation in `docs/audit/` or create an issue
