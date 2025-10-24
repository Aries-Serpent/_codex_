# [Template]: Python File Relocation with Backward Compatibility

- **Version:** v1.0.0
- **Last Updated:** 2025-10-24
- **Owner Role:** Documentation Architect → Maintainer (executor)
- **Intended Audience:** Developers authoring migrations, maintainers validating rollouts

---

## Executive Summary

Use this template when relocating Python modules or packages while preserving backwards compatibility. The flow protects import stability, retains git history, and documents mitigation tasks for downstream consumers.

## Prerequisites

- Baseline branch is synced with `main` and CI is green.
- [`sitecustomize.py`](../sitecustomize.py) is available for compatibility hooks.
- Legacy entry points tracked in [`legacy_root/`](../..) (create if missing).
- Tests covering the old import path exist or have placeholders to be written.
- Confirm that release notes require an entry in `docs/CHANGELOG.md`.

## Execution Phases

### Phase 1 — Validate Baseline
- Capture baseline test results (`pytest -k "[PLACEHOLDER:scope]"`).
- Document existing import graph using `python -m modulefinder [PLACEHOLDER:module_path]`.
- Identify callers via `rg "[PLACEHOLDER:callable_name]" src/ tests/`.

### Phase 2 — Scaffold Target Layout
- Create destination package at `[PLACEHOLDER:target_package]`.
- Move files with `git mv` to retain history.
- Update `__init__.py` exports to expose required symbols.

### Phase 3 — Implement Compatibility Layer
- Add shim in [`sitecustomize.py`](../sitecustomize.py) mapping old module name to new module object:
  ```python
  import importlib
  import sys

  def _install_alias():
      module = importlib.import_module("[PLACEHOLDER:new_module]")
      sys.modules["[PLACEHOLDER:legacy_module]"] = module
  _install_alias()
  ```
- For CLI modules, update [`src/cli/__init__.py`](../../src/cli/__init__.py) imports.
- Document alias removal plan in `docs/CHANGELOG.md` under "Deprecated".

### Phase 4 — Update Call Sites
- Replace imports using `sed -i '' 's/[PLACEHOLDER:legacy_module]/[PLACEHOLDER:new_module]/g'` (macOS) or GNU variant.
- Update pytest fixtures in [`tests/conftest.py`](../../tests/conftest.py) referencing legacy modules.
- Adjust notebooks or scripts under `notebooks/` and `scripts/` if required.

### Phase 5 — Expand Test Coverage
- Add new tests validating the relocated API in `tests/[PLACEHOLDER:target_package]/`.
- Ensure legacy import path remains functional using compatibility tests in `tests/templates/`.
- Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -k "[PLACEHOLDER:module_name]"`.

### Phase 6 — Document & Communicate
- Update `docs/templates/README.md` index if template evolves.
- Add changelog entry summarising migration impact.
- Post release note in contributor channel including deprecation date `[PLACEHOLDER:removal_date]`.

## Success Criteria

- New module layout committed with preserved history (`git log --follow`).
- Compatibility shim registered and covered by unit tests.
- Test coverage at or above 85% for touched modules (verify with `coverage html`).
- Changelog and README updates merged.
- Maintainer sign-off recorded in PR checklist.

## Rollback Procedure

1. Revert the commit range: `git revert [PLACEHOLDER:commit_range]`.
2. Remove compatibility shim from `sitecustomize.py`.
3. Restore legacy module layout with `git checkout HEAD^ -- [PLACEHOLDER:legacy_path]`.
4. Re-run baseline tests to confirm legacy behaviour remains intact.
5. Update changelog with rollback note and notify maintainers.

## Customization Guide

| Placeholder | Description | Example |
| --- | --- | --- |
| `[PLACEHOLDER:scope]` | Targeted pytest keyword expression | `relocation or alias` |
| `[PLACEHOLDER:module_path]` | Path to entry module used for dependency graph | `src/codex/services/api.py` |
| `[PLACEHOLDER:callable_name]` | Function or class name used to trace call sites | `RuntimeConfigLoader` |
| `[PLACEHOLDER:target_package]` | Destination package/module | `src/codex/services/runtime` |
| `[PLACEHOLDER:new_module]` | Fully qualified import for new module | `codex.services.runtime.config` |
| `[PLACEHOLDER:legacy_module]` | Fully qualified name for legacy module | `codex.runtime.config` |
| `[PLACEHOLDER:module_name]` | Friendly module identifier for pytest filters | `runtime_config` |
| `[PLACEHOLDER:removal_date]` | Planned removal date for compatibility shim | `2026-03-01` |
| `[PLACEHOLDER:commit_range]` | SHA range for migration changes | `abc123..def456` |
| `[PLACEHOLDER:legacy_path]` | Filesystem path to prior module location | `src/codex/legacy/runtime_config.py` |

## Reference Material

- [`docs/validation/`](../validation/) for writing validation plans.
- [`tests/templates/`](../../tests/templates/) for discovery checks.
- [`conftest.py`](../../conftest.py) to register fixtures supporting migration tests.
- [`pyproject.toml`](../../pyproject.toml) for coverage configuration updates.

---
**Review Gate:** Maintainer confirms compatibility shim, test coverage, and documentation updates before merge.
