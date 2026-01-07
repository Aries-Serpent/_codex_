# [Runbook]: Space Audit Operations (v1.1.0)
> Generated: 2025-12-06 04:45:00Z | Author: Comprehensive Audit System  
> 🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Commands
| Task | Command |
|------|---------|
| Full run | `python scripts/space_traversal/audit_runner.py run` |
| Single stage | `python scripts/space_traversal/audit_runner.py stage S4` |
| Explain score | `python scripts/space_traversal/audit_runner.py explain checkpointing` |
| Diff reports | `python scripts/space_traversal/audit_runner.py diff --old A --new B` |
| Fast path | `make space-audit-fast` |

## Artifacts
| Path | Description |
|------|-------------|
| `audit_artifacts/context_index.json` | File index & hashes |
| `audit_artifacts/facets.json` | Domain clustering |
| `audit_artifacts/capabilities_raw.json` | Capabilities (raw) |
| `audit_artifacts/capabilities_scored.json` | Capabilities (scored) |
| `audit_artifacts/gaps.json` | Low maturity segmentation |
| `reports/capability_matrix_<ts>.md` | Rendered matrix report |
| `audit_run_manifest.json` | Integrity chain |

## Troubleshooting
| Symptom | Fix |
|---------|-----|
| Missing capability | Enable dynamic detectors; fix detector exceptions |
| All safeguards 0 | Update keyword list in `audit_runner.py` |
| High duplication | Narrow facet regex; refine grouping |
| Template hash mismatch | Re-run full pipeline |

*End of Runbook*
