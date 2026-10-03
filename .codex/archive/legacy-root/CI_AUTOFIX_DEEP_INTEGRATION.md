# CI Auto-Fix Deep Integration

**Status:** Implemented wrapper layer for campaign workflows

## New wrappers

- `/home/runner/work/_codex_/_codex_/scripts/ci/enhanced_diagnostics.py`
  - Runs detection-only diagnostics
  - Enriches the base auto-fix report with blocking-pattern summary
- `/home/runner/work/_codex_/_codex_/scripts/ci/bulk_remediation_orchestrator.py`
  - Runs remediation mode and returns a structured orchestration summary

## CLI entry point

```bash
python -m codex.cli chronicle auto-fix --check-only --json
python -m codex.cli chronicle auto-fix --pattern 25 --json
python -m codex.cli chronicle auto-fix --dry-run
```

## Design intent

The wrappers keep `auto_fix_common_issues.py` as the source of truth while providing a stable, structured interface for:

- personalized CLI usage
- campaign dashboards
- future agent orchestration
