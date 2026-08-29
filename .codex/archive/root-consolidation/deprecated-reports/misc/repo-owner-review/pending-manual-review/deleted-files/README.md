# Deleted Files for Manual Review

This folder contains files that were removed from the repository root during cleanup. These files are preserved here for repository owner review before permanent deletion.

## Files Restored

| File | Original Location | Description | Recommendation |
|------|------------------|-------------|----------------|
| `_codex_repo_map.json` | Root | Repository file mapping | Can be regenerated - safe to delete |
| `audit_run_manifest.json` | Root | Audit run manifest | Can be regenerated - safe to delete |
| `codex_dependency_report.json` | Root | Dependency analysis report | Can be regenerated - safe to delete |
| `codex_reproducibility_manifest.json` | Root | Reproducibility manifest | Can be regenerated - safe to delete |
| `installation_summary.json` | Root | Installation summary | Can be regenerated - safe to delete |

## Files Not Restored (Ephemeral/Generated)

The following files were removed and NOT restored as they are purely ephemeral:

| File | Reason |
|------|--------|
| `=` | Empty file (likely created by accident) |
| `Traversal_Workflow.md` | Duplicate of `docs/Traversal_Workflow.md` |
| `Usage_Guide.md` | Duplicate of `docs/Usage_Guide.md` |
| `artifacts_sha256.txt` | Moved to `reports/artifacts_sha256.txt` |
| `batchsetpatchset_segments.zip` | Moved to `archive/` |
| `capabilities_excerpt.txt` | Moved to `reports/` |
| `codex_env_snapshot.json` | Moved to `reports/codex/` |
| `codex_mltest_infra_summary.json` | Moved to `reports/codex/` |
| `codex_secret_scan_report.json` | Moved to `reports/codex/` |
| `compare_report.json` | Moved to `reports/` |
| `diagnostic_results.txt` | Moved to `reports/diagnostics/` |
| `test_results_stage1.txt` | Moved to `reports/diagnostics/` |

## How to Handle

1. **Review each file** in this folder
2. **If needed**: Move to appropriate location or regenerate
3. **If not needed**: Delete this folder and its contents
4. **Update**: Remove this folder once review is complete

## Regeneration Commands

```bash
# Regenerate repo map
python tools/generate_repo_map.py

# Regenerate audit manifest
python -m scripts.space_traversal.audit_runner --generate-manifest

# Regenerate dependency report
python tools/analyze_dependencies.py --output codex_dependency_report.json
```

---

*Generated: 2025-12-21*
*By: Copilot Workflow Fixes PR*
