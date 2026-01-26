# External Storage Offload Index

**Created**: 2026-01-26T06:48:00Z  
**Purpose**: Track files offloaded from main repository to external storage for size optimization  
**QA Integration**: Maintains organization for effective Codebase QA Walkthrough Analysis

## Directory Structure

```
misc/repo-owner-review/
├── OFFLOAD_INDEX.md                 # This file - inventory of offloaded files
├── README.md                         # General repo-owner-review documentation
├── historical-coverage/              # Old coverage reports (keep latest in main repo)
├── historical-logs/                  # Historical log extracts (keep critical logs only)
├── historical-artifacts/             # Runtime CI/CD artifacts (gates, validation)
├── archive-files/                    # Archive packages (.zip, .tar.gz)
├── temp-outputs/                     # Temporary build/analysis outputs
├── deprecated-reports/               # Deprecated report files
├── archived-artifacts/               # Existing archived artifacts
└── archived-backups/                 # Existing archived backups
```

## Offload Principles

1. **Preserve History**: All offloaded files maintain original paths in metadata
2. **QA Accessibility**: Structure supports QA walkthrough analysis needs
3. **Retrieval Ready**: Clear documentation for accessing offloaded files
4. **Size Optimization**: Target ~5-10MB reduction in repository size
5. **CI/CD Safe**: Keep active/recent artifacts that CI/CD depends on

## Categories

### Historical Coverage Reports
**Location**: `historical-coverage/`  
**Rationale**: Keep only current_coverage.json in main repo for active development  
**Retention**: All historical coverage data preserved for trend analysis

### Historical Logs
**Location**: `historical-logs/`  
**Rationale**: Keep only error_captures.log in main repo for active debugging  
**Retention**: All extracted logs preserved for historical troubleshooting

### Historical Artifacts
**Location**: `historical-artifacts/`  
**Rationale**: Move old CI/CD gate logs and validation reports  
**Retention**: Keep for compliance and audit purposes

### Archive Files
**Location**: `archive-files/`  
**Rationale**: Consolidate all .zip/.tar.gz files not actively referenced  
**Retention**: Permanent archive for reference

### Temporary Outputs
**Location**: `temp-outputs/`  
**Rationale**: Move temp/ and output/ directory contents  
**Retention**: Short-term (90 days) unless documented as needed

### Deprecated Reports
**Location**: `deprecated-reports/`  
**Rationale**: Move _codex_reports/ contents (superseded by .codex structure)  
**Retention**: 180 days for reference, then eligible for deletion

## Offloaded Files Inventory

### Coverage Reports (Offloaded: 2026-01-26)
| Original Path | Offload Location | Size | Reason |
|--------------|------------------|------|--------|
| `coverage_reports/phase1_iteration1.json` | `historical-coverage/phase1_iteration1.json` | ~400KB | Historical - Phase 1 complete |
| `coverage_reports/phase1_iteration2.json` | `historical-coverage/phase1_iteration2.json` | ~400KB | Historical - Phase 1 complete |
| `coverage_reports/phase2_iter.json` | `historical-coverage/phase2_iter.json` | ~400KB | Historical - Phase 2 complete |
| `coverage_reports/coverage_iteration2.json` | `historical-coverage/coverage_iteration2.json` | ~400KB | Historical - Superseded |
| `coverage_reports/coverage_agents.json` | `historical-coverage/coverage_agents.json` | ~400KB | Historical snapshot |
| `coverage_reports/coverage_agents_full.json` | `historical-coverage/coverage_agents_full.json` | ~400KB | Historical snapshot |
| `coverage_reports/coverage_working_tests.json` | `historical-coverage/coverage_working_tests.json` | ~400KB | Historical snapshot |
| `coverage_reports/coverage_analysis_static.md` | `historical-coverage/coverage_analysis_static.md` | ~50KB | Historical analysis |

**Kept in Main Repo**: 
- `coverage_reports/current_coverage.json` (active reference)
- `coverage_reports/coverage.json` (active reference)

### Log Files (Offloaded: 2026-01-26)
| Original Path | Offload Location | Size | Reason |
|--------------|------------------|------|--------|
| `logs/extracted_log_59387658652.md` | `historical-logs/extracted_log_59387658652.md` | ~200KB | Historical extract |
| `logs/extracted_log_60269597152.md` | `historical-logs/extracted_log_60269597152.md` | ~200KB | Historical extract |
| `logs/extracted_log_60562804384.md` | `historical-logs/extracted_log_60562804384.md` | ~200KB | Historical extract |
| `logs/extracted_log_60557908501.md` | `historical-logs/extracted_log_60557908501.md` | ~200KB | Historical extract |
| `logs/extracted_log_59387344823.md` | `historical-logs/extracted_log_59387344823.md` | ~200KB | Historical extract |
| `logs/extracted_chatgptcodex-v2.md` | `historical-logs/extracted_chatgptcodex-v2.md` | ~200KB | Historical extract |
| `logs/extracted_patch_chatgpt-codex.md` | `historical-logs/extracted_patch_chatgpt-codex.md` | ~200KB | Historical extract |

**Kept in Main Repo**: 
- `logs/error_captures.log` (active error tracking)

### Artifacts (Offloaded: 2026-01-26)
| Original Path | Offload Location | Size | Reason |
|--------------|------------------|------|--------|
| `artifacts/validate_report_20251119.json.gz.b64` | `historical-artifacts/validate_report_20251119.json.gz.b64` | ~100KB | Historical validation |
| `artifacts/gates/nox-typecheck.log` | `historical-artifacts/gates/nox-typecheck.log` | ~50KB | Historical gate log |
| `artifacts/gates/nox-lint.log` | `historical-artifacts/gates/nox-lint.log` | ~50KB | Historical gate log |
| `artifacts/gates/pytest-analysis-cov.log` | `historical-artifacts/gates/pytest-analysis-cov.log` | ~100KB | Historical gate log |
| `artifacts/gates/pytest-analysis.log` | `historical-artifacts/gates/pytest-analysis.log` | ~100KB | Historical gate log |
| `artifacts/gates/nox-tests_min-rerun.log` | `historical-artifacts/gates/nox-tests_min-rerun.log` | ~50KB | Historical gate log |
| `artifacts/gates/nox-tests_min-rerun2.log` | `historical-artifacts/gates/nox-tests_min-rerun2.log` | ~50KB | Historical gate log |

**Kept in Main Repo**: 
- `artifacts/metrics/*` (active metrics)
- `artifacts/models/*` (active models)
- `artifacts/model_regression_log.ndjson` (active tracking)
- `artifacts/.gitkeep` (structure preservation)

### Archive Files (Offloaded: 2026-01-26)
| Original Path | Offload Location | Size | Reason |
|--------------|------------------|------|--------|
| `misc/audio_cleaner_beta_v1.zip` | `archive-files/audio_cleaner_beta_v1.zip` | ~132KB | Legacy tool archive |
| `misc/cognitivecodex-main.zip` | `archive-files/cognitivecodex-main.zip` | ~600KB | Legacy app archive |
| `docs/plans/implement_dependency.zip` | `archive-files/implement_dependency.zip` | ~50KB | Old implementation archive |

**Kept in Main Repo**: 
- `archive/cognitive_codex_app.zip` (documented in archive/INDEX.md)
- `misc/repo-owner-review-archive.tar.gz` (self-referential archive)

### Temporary Outputs (Offloaded: 2026-01-26)
| Original Path | Offload Location | Size | Reason |
|--------------|------------------|------|--------|
| `temp/bridge_codex_copilot_bridge/` | `temp-outputs/bridge_codex_copilot_bridge/` | ~280KB | Temporary bridge files |
| `output/IntegratedDocEvolution.md` | `temp-outputs/IntegratedDocEvolution.md` | ~7KB | Temporary output |

### Deprecated Reports (Offloaded: 2026-01-26)
| Original Path | Offload Location | Size | Reason |
|--------------|------------------|------|--------|
| `_codex_reports/audit_requirement_mapping.md` | `deprecated-reports/audit_requirement_mapping.md` | ~20KB | Superseded by .codex/qa_walkthrough/ |
| `_codex_reports/errors_2025-10-19.md` | `deprecated-reports/errors_2025-10-19.md` | ~20KB | Historical error report |
| `_codex_reports/errors_2025-11-05.md` | `deprecated-reports/errors_2025-11-05.md` | ~20KB | Historical error report |
| `_codex_reports/errors_2025-11-12.md` | `deprecated-reports/errors_2025-11-12.md` | ~20KB | Historical error report |
| `_codex_reports/metric_plugin_duplicates_resolution.md` | `deprecated-reports/metric_plugin_duplicates_resolution.md` | ~20KB | Historical resolution |
| `_codex_reports/status_update_2025-10-19.md` | `deprecated-reports/status_update_2025-10-19.md` | ~20KB | Historical status |

## Retrieval Process

### For Developers
1. Clone repository normally
2. Check `OFFLOAD_INDEX.md` for historical file locations
3. Access files in `misc/repo-owner-review/[category]/`
4. Reference original paths in commit history if needed

### For CI/CD
- No changes required - CI/CD uses current/active files only
- Historical artifacts not required for builds/tests

### For QA Walkthrough
1. Current state: Active files in main repository
2. Historical trend analysis: Access `historical-coverage/`, `historical-logs/`
3. Audit trail: Reference `OFFLOAD_INDEX.md` metadata
4. Full context: Combine current + historical data

## QA Walkthrough Integration

### Current Coverage Analysis
- **Active File**: `coverage_reports/current_coverage.json`
- **Historical Trend**: `misc/repo-owner-review/historical-coverage/*.json`
- **Analysis Tool**: `.codex/qa_walkthrough/coverage_analysis.json`

### Log Analysis
- **Active Log**: `logs/error_captures.log`
- **Historical Logs**: `misc/repo-owner-review/historical-logs/*.md`
- **Error Tracking**: Maintained in active log

### Artifact Analysis
- **Active Metrics**: `artifacts/metrics/*.json`
- **Historical Gates**: `misc/repo-owner-review/historical-artifacts/gates/*.log`
- **Model Files**: `artifacts/models/` (active, not offloaded)

## Size Impact

**Estimated Reduction**: ~6-8MB from main repository  
**Categories**:
- Coverage Reports: ~2.8MB
- Logs: ~1.4MB
- Artifacts: ~500KB
- Archives: ~800KB
- Temp/Output: ~280KB
- Deprecated Reports: ~120KB

**Total Offloaded**: ~5.9MB

## Maintenance Schedule

- **Weekly**: Review temp-outputs/ for files older than 90 days
- **Monthly**: Update OFFLOAD_INDEX.md with new offloads
- **Quarterly**: Review deprecated-reports/ for deletion candidates
- **Annually**: Archive historical coverage/logs to compressed format

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-26 | Initial offload structure and inventory | QA Walkthrough Agent |

---

**Maintained by**: QA Walkthrough Agent  
**Category**: Repository Organization  
**Status**: Active  
**Last Updated**: 2026-01-26T06:48:00Z
