# [Guide]: Copilot Space Audit Usage (v1.1.0)
> Generated: 2025-10-18 08:55:23 UTC | Author: mbaetiong

 Roles: [Primary: Workflow Steward], [Secondary: Reliability Analyst]  Energy: 5

## 1. Quick Run
```bash
python scripts/space_traversal/audit_runner.py run
```

## 2. Single Stage Invocation
```bash
python scripts/space_traversal/audit_runner.py stage S4
```

## 3. Explain a Capability Score
```python
from scripts/space_traversal.capability_scoring import explain_score
import json
data = json.load(open("audit_artifacts/capabilities_scored.json"))
weights = {"functionality":0.25,"consistency":0.2,"tests":0.25,"safeguards":0.15,"documentation":0.15}
print(explain_score(data["capabilities"][0], weights))
```
CLI alternative:
```bash
python scripts/space_traversal/audit_runner.py explain checkpointing
```

## 4. Update Weights & Caps
Edit `.copilot-space/workflow.yaml` → rerun S4–S7:
```bash
python scripts/space_traversal/audit_runner.py stage S4
python scripts/space_traversal/audit_runner.py stage S5
python scripts/space_traversal/audit_runner.py stage S6
python scripts/space_traversal/audit_runner.py stage S7
```

Example caps/dup config:
```yaml
scoring:
  component_caps:
    functionality: 1.0
    consistency: 1.0
    tests: 0.9
    safeguards: 1.0
    documentation: 1.0
  dup:
    heuristic: token_similarity   # requires dup_similarity.py; falls back to simple if unavailable
```

## 5. Add a New Capability
| Step | Action |
|------|--------|
| 1 | Create detector in `scripts/space_traversal/detectors/` |
| 2 | Implement `detect()` contract (include optional `meta`) |
| 3 | Run `stage S3` or full `run` |
| 4 | Inspect `capabilities_raw.json` |
| 5 | Confirm matrix entry; meta renders under capability detail |

## 6. Component Interpretation
| Component | Meaning | Optimization Path |
|-----------|---------|-------------------|
| Functionality | Core code presence | Implement missing modules |
| Consistency | Single authoritative path | Deduplicate or facade |
| Tests | Coverage proxy | Add targeted tests |
| Safeguards | Integrity & reproducibility | Add hashes, seeds, offline guards |
| Documentation | Knowledge clarity | Expand docs & link concepts |

## 7. Determinism Validation
Two sequential runs (no source changes) must produce identical:
- `repo_root_sha`
- `capabilities_scored.json` (excluding timestamp)
If mismatch: review detector randomness or unsorted enumeration.

## 8. CI Integration (Optional)
```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py diff --old baseline/capabilities_scored.json --new audit_artifacts/capabilities_scored.json
```

## 9. Red Flags
| Symptom | Cause | Action |
|---------|-------|--------|
| Sudden score drop | Deleted/renamed evidence file | Restore or revise patterns |
| Zero safeguards | Keyword set stale | Expand `SAFEGUARD_KEYWORDS` |
| High duplication penalty | Over-capture by facet regex | Narrow regex or enable token_similarity |

## 10. Diff Reports
```bash
python scripts/space_traversal/audit_runner.py diff --old reports/capability_matrix_prev.md --new reports/capability_matrix_latest.md
```

## 11. Practical Snippets
List scored IDs:
```bash
jq -r '.capabilities[].id' audit_artifacts/capabilities_scored.json
```

## 12. Manifest Inspection
```bash
jq '.' audit_run_manifest.json
```

## 13. Cleanup
```bash
make space-clean
```

## 14. Upgrade Checklist (Before Raising Version)
- [ ] New detectors stable
- [ ] No nondeterministic ordering introduced
- [ ] Template hash updated & manifest regenerated
- [ ] All weights sum to 1.0 (or normalized with warning acknowledgment)

## 15. Frequently Asked
| Question | Answer |
|----------|--------|
| Can I disable a stage? | Remove from `stages` array (ensure dependencies satisfied) |
| How to isolate a regression? | Re-run stages sequentially; compare JSON artifacts |
| Where to add synonyms? | Extend detection logic inside dynamic detectors |

*End of Guide*
