# [Reference]: P5 Scoring Integration & Severity Influence
> Generated: 2024-11-06 19:34:45 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

## 1. Added Metrics
| Metric | Source Artifact | Influence |
|--------|-----------------|-----------

|
| similarity_index | token_similarity.json | Multiplies legacy (1 - duplication_ratio) to form consistency |
| coverage_percent | coverage_stats.json | Elevates tests component via max(test_ratio, coverage_percent) |
| severity_factor | security_severity.json | Adjusts safeguards component (additive / penalty / none) |

## 2. Consistency (New)
`consistency = (1 - duplication_ratio) * similarity_index`  
If similarity unavailable: fallback `consistency = 1 - duplication_ratio`.

## 3. Tests (New)
`tests = max(test_file_ratio, coverage_percent)`  
If coverage absent: fallback `tests = test_file_ratio`.

## 4. Safeguards (Severity Influence)
| Mode | Formula | Clamp |
|------|---------|-------|
| additive (default) | safeguards_raw × (1 + Σ weighted severity counts) | ≤ 1.25 |
| penalty | safeguards_raw × (1 - weighted severity penalty) | ≥ 0.75 |
| none | safeguards_raw | — |

Weights default: high=0.05, medium=0.02, low=0.01.

## 5. Prefix Auto-Validation
When `BUNDLE_PREFIX_MODE=1` and `PREFIX_VALIDATE_AUTO=1`:
- Runs validate_prefixes
- Adds `prefix_violations:<count>` to manifest warnings if any violations.

## 6. Knobs Summary Sidecar
If `SUMMARY_ENABLE=1`: emits `audit_artifacts/knobs_effective.json` capturing active integration knobs for provenance.

## 7. Backward Compatibility
If any auxiliary artifact or knob is missing:
- Score components revert to legacy computation paths.
- No new warnings introduced.

## 8. Fallback Table
| Component | Missing Artifact | Behavior |
|-----------|------------------|----------|
| consistency | token_similarity.json absent | Use duplication-only |
| tests | coverage_stats.json absent | Use test_ratio only |
| safeguards | security_severity.json absent or knob off | No severity multiplier |
| prefix validation | validator disabled | No prefix warning |

## 9. Warning Codes (Additions)
| Code | Trigger |
|------|--------|
| prefix_violations:<n> | Prefix validation found n violations |
| weights_normalized_from:<sum> | Weights auto-normalized |
| (Existing) invalid_regex:<count> | PII pattern compile failures |

## 10. Manifest Impact
Added:
- Potential `knobs_effective.json` sidecar.
- Additional warnings aggregated from severity and prefix validation.

## 11. Rollback
Unset knobs or remove artifacts:
```bash
unset TOKEN_SIMILARITY_ENABLE COVERAGE_ENABLE SECURITY_SEVERITY_ENABLE PREFIX_VALIDATE_AUTO
git checkout scripts/space_traversal/audit_runner.py
```text

*End of P5 Integration Reference*
