# Entry Points Removed or Commented Out

This document explains why 22 entry points are commented out in `pyproject.toml` and which profiles will enable them.

## Overview

The codex-ml package provides 27+ CLI entry points, but only 5 are available in the **core** profile. The remaining 22 require additional dependencies from the **runtime** or **full** profiles.

This document maintains clarity about:
- Which entry points are disabled and why
- What profile each entry point requires
- Expected activation timeline for each profile

## Commented Entry Points (22 total)

### Training & Evaluation (Requires [runtime] profile)

| Command | Module Reference | Reason | Status |
|---------|------------------|--------|--------|
| `codex-train` | `codex_ml.cli.entrypoints:train_main` | Requires torch, transformers | ⏳ Runtime |
| `codex-eval` | `codex_ml.cli.entrypoints:eval_main` | Requires torch, transformers | ⏳ Runtime |
| `codex-infer` | `codex_ml.cli.infer:main` | Requires torch, transformers | ⏳ Runtime |
| `codex-validate-config` | `codex_ml.cli.validate:main` | Requires runtime infrastructure | ⏳ Runtime |
| `codex-perf` | `codex_ml.cli.perf.bench:main` | Requires performance testing deps | ⏳ Runtime |

### Code Analysis (Requires [full] profile or specific subsystems)

| Command | Module Reference | Reason | Status |
|---------|------------------|--------|--------|
| `codex-analyze` | `codex.analysis.cli:analyze_main` | Module not found in current codebase | ❌ Not Implemented |
| `codex-audit` | `codex.audit.cli:audit_main` | Module not found in current codebase | ❌ Not Implemented |
| `codex-smell` | `codex.quality.cli:smell_main` | Module not found in current codebase | ❌ Not Implemented |
| `codex-metrics` | `codex.ast.cli:metrics_main` | Module not found in current codebase | ❌ Not Implemented |
| `codex-ast` | `codex.cli.ast_cli:main` | Module not found in current codebase | ❌ Not Implemented |
| `codex-report` | `codex.reporting.cli:report_main` | Module not found in current codebase | ❌ Not Implemented |
| `codex-dashboard` | `codex.reporting.cli:dashboard_main` | Module not found in current codebase | ❌ Not Implemented |

### Utility Commands (Requires [full] profile)

| Command | Module Reference | Reason | Status |
|---------|------------------|--------|--------|
| `codex-list-plugins` | `codex_ml.cli.list_plugins:main` | Plugin system requires full profile | ⏳ Full |
| `codex-ndjson` | `codex_utils.cli.ndjson_summary:main` | Utility requiring extended functionality | ⏳ Full |
| `codex-offline-bootstrap` | `codex_ml.cli.offline_bootstrap:main` | Bootstrap requires full environment | ⏳ Full |
| `codex-tokenizer` | `tokenization.cli:app` | Requires tokenization infrastructure | ⏳ Full |
| `codex-setup` | `cli.setup:main` | Setup requires full infrastructure | ⏳ Full |
| `codex-patch-runner` | `cli.patch_runner:main` | Requires full CLI infrastructure | ⏳ Full |
| `codex-update-runner` | `cli.update_runner:main` | Requires full CLI infrastructure | ⏳ Full |
| `codex-script` | `cli.script_polish:main` | Script processing requires full profile | ⏳ Full |
| `codex-workflow` | `cli.workflow:main` | Workflow requires full infrastructure | ⏳ Full |
| `codex-task-sequence` | `cli.task_sequence:main` | Task system requires full profile | ⏳ Full |
| `codex-ast-upgrade` | `cli.ast_upgrade:main` | AST tools require full profile | ⏳ Full |
| `codex-audit-runner` | `cli.audit_runner_root:main` | Auditing requires full infrastructure | ⏳ Full |

## Legend

| Status | Meaning |
|--------|---------|
| ✅ Core | Available in [core] profile |
| ⏳ Runtime | Enabled in [runtime] profile |
| ⏳ Full | Enabled in [full] profile |
| ❌ Not Implemented | Module does not exist in codebase |

## Activation Plan

### Phase 2 (Runtime Profile)
- Uncomment 5 training/evaluation entry points
- Add runtime dependencies: `torch>=2.0`, `transformers>=4.30`, `ray[serve]>=2.5`
- Verify all 5 entry points are functional
- Update .codex/archive/misc/INSTALL.md with runtime entry points documentation

### Phase 3 (Full Profile)
- Uncomment remaining 17 utility/analysis entry points
- Add full profile dependencies: all development tools, testing frameworks, ML ecosystem
- Verify all 17 entry points are functional
- Update .codex/archive/misc/INSTALL.md with full entry points documentation
- Note: The 7 "Not Implemented" entries may require codebase refactoring or architectural changes

## Migration Path

**For users upgrading from core → runtime:**
```bash
# Install runtime profile (replaces core)
pip install codex-ml[runtime]

# New available commands:
# codex-train, codex-eval, codex-infer, codex-validate-config, codex-perf
```

**For users upgrading from runtime → full:**
```bash
# Install full profile (replaces runtime)
pip install codex-ml[full]

# New available commands:
# codex-list-plugins, codex-ndjson, codex-offline-bootstrap, + 9 more utilities
```

## Notes

- Entry point definitions are in `pyproject.toml` under `[project.scripts]`
- This file documents the rationale but the actual entry point status is controlled by the `pyproject.toml` comments
- Keep this file in sync with `pyproject.toml` changes to maintain clarity
