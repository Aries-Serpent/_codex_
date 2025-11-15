# IMDS File Consolidation Matrix
> Generated: 2025-11-14 23:00:10 UTC | Author: mbaetiong

## Purpose
Provide an authoritative consolidation table mapping all overlapping IMDS-related PR artifacts to the single canonical implementation merged toward `0D_base_`.

## Source Mapping
| PR # | Branch | Artifact(s) | Unique Value | Canonical Action |
|------|--------|-------------|--------------|------------------|
| 2233 | imds/diagnostic-2226-20251114T213200 | Script | Strong base authored by maintainer | Merge (script source) |
| 2228 | copilot/add-imds-diagnostic-runbook | Script + Runbook | Detailed runbook baseline | Integrate runbook content |
| 2230 | copilot/imdsdiagnostic-2226-20251114t213200-again | Script + Runbook + Summary | Implementation summary doc | Cherry-pick summary only |
| 2231 | copilot/add-runbook-and-make-script-executable | Script + Runbook | Duplicate improvements | Close after consolidation |
| 2232 | copilot/add-imds-diagnostic-runbook-again | Script + Typo fix claim | Redundant iteration | Close |
| 2229 | copilot/imdsdiagnostic-2226-20251114t213200 | Script + Runbook (dirty) | Conflicted state | Close |
| 2225 | copilot/sub-pr-2207 | Audit docs (deployment) | Independent domain | Separate merge path |
| 2227 | copilot/autonomous-deployment-orchestration | Orchestration logic | Independent domain | Separate merge path |

## Consolidated Artifact Decisions
| Artifact | Chosen Source | Notes |
|----------|---------------|-------|
| `.github/scripts/imds_diagnostic.sh` | 2233 + enhancements | Extended checks + JSON |
| `.github/docs/imds_diagnostic_RUNBOOK.md` | 2228 baseline + v1.3 revision | Unified formatting & safety model |
| `IMDS_IMPLEMENTATION_SUMMARY.md` | 2230 | Optional maintainers’ context |
| Redundant runbooks/scripts | 2231, 2232, 2229 | Decommission post-merge |

## Avoiding Conflicts
| Risk | Resolution |
|------|------------|
| Divergent permission bits | Set final mode 755 |
| Multiple runbook versions | Single canonical file with version table |
| Unapplied typo fixes | Verified & integrated in final script |
| Dirty merge state (2229) | Close after canonical merge |

## Validation Before Merge
| Check | Command | Expected |
|-------|---------|----------|
| Syntax | `bash -n .github/scripts/imds_diagnostic.sh` | No output |
| Executable bit | `ls -l .github/scripts/imds_diagnostic.sh` | `-rwxr-xr-x` |
| Dry-run preview | `bash .github/scripts/imds_diagnostic.sh --dry-run` | Recommendation section |
| JSON output | `bash .github/scripts/imds_diagnostic.sh --json` | `diagnostic_results.json` |
| Apply safety | `sudo bash .github/scripts/imds_diagnostic.sh --apply` | Backups and rule insertion only |

## Decommission Log (Populate After Merge)
| PR Closed | Final SHA | Reason | Replacement |
|-----------|-----------|--------|------------|
| 2228 | TBD | Runbook integrated | Canonical runbook |
| 2230 | TBD | Summary cherry-picked | Consolidated docs |
| 2231 | TBD | Duplicate | Canonical script/runbook |
| 2232 | TBD | Redundant iteration | Canonical script |
| 2229 | TBD | Conflicted | Canonical script |
| 2225 | N/A | Independent | Kept separate |
| 2227 | N/A | Independent | Kept separate |

## Next Enhancements
| Enhancement | Description | Priority |
|-------------|-------------|----------|
| ShellCheck Workflow | Lint future script changes | Medium |
| Pre-flight IMDS Action | Gating step before deployment | High |
| Prometheus Export | Optional metrics for fleet | Low |
| Automated Approval Gate | Signed token for remediation | Medium |

Relates to issue: #2226
