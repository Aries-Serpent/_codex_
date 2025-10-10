# [Guide]: Copilot Space Audit Usage (v1.1.0)
> Generated: 2025-10-10 04:31:26 UTC | Author: mbaetiong
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
```bash
python scripts/space_traversal/audit_runner.py explain checkpointing
```

## 4. Update Weights
Edit `.copilot-space/workflow.yaml` → rerun S4–S7:
```bash
python scripts/space_traversal/audit_runner.py stage S4
python scripts/space_traversal/audit_runner.py stage S5
python scripts/space_traversal/audit_runner.py stage S6
python scripts/space_traversal/audit_runner.py stage S7
```

## 5. Add a New Capability
| Step | Action |
|------|--------|
| 1 | Create detector in `scripts/space_traversal/detectors/` |
| 2 | Implement `detect()` contract |
| 3 | Run `stage S3` or full `run` |
| 4 | Inspect `capabilities_raw.json` |
| 5 | Confirm matrix entry |

## 6. Determinism Validation
Two sequential runs (no source changes) must produce identical:
- `repo_root_sha`
- `capabilities_scored.json` (excluding timestamp)

## 9. Red Flags
| Symptom | Cause | Action |
|---------|-------|--------|
| Sudden score drop | Deleted/renamed evidence file | Restore or revise patterns |
| Zero safeguards | Keyword set stale | Expand `SAFEGUARD_KEYWORDS` |
| High duplication penalty | Over-capture by facet regex | Narrow facet patterns |
| Low docs despite coverage | Tokens too narrow | Extend `DOCS_SYNONYMS_MAP` or per-capability `docs_keywords` |

## 15. Frequently Asked
| Question | Answer |
|----------|--------|
| Can I disable a stage? | Remove from `stages` array (ensure dependencies satisfied) |
| How to isolate a regression? | Re-run stages sequentially; compare JSON artifacts |
| Where to add synonyms? | Edit `DOCS_SYNONYMS_MAP` in scripts/space_traversal/audit_runner.py or add `docs_keywords` in BASE_CAPABILITY_RULES |

*End of Guide*
