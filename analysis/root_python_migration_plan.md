# Root Python File Migration Plan (Dry Run)

## Parameters

- **target_subfolder:** `src/legacy_root`
- **include_patterns:** `['*.py']`
- **exclude_patterns:** _none_
- **dry_run:** `true`
- **update_references:** `true`
- **languages:** `['python']`
- **repo_path:** `./`
- **report_format:** `markdown`

## Candidate Summary

| File | Proposed Destination | Classification | Rationale |
| --- | --- | --- | --- |
| `codex_task_sequence.py` | `src/legacy_root/codex_task_sequence.py` | requires-refactor | Module is a top-level compatibility shim for `cli.task_sequence`; relocating it breaks consumers that import `codex_task_sequence` unless a new alias is installed early in interpreter startup. |
| `conftest.py` | `src/legacy_root/conftest.py` | blocked | Pytest only discovers project-wide fixtures from root-level `conftest.py`; moving it would stop `src` path injection and environment bootstrapping required for every test session. |
| `sitecustomize.py` | `src/legacy_root/sitecustomize.py` | blocked | Python auto-imports `sitecustomize` from the startup search path; relocating it would disable MLflow fallback wiring and sys.path adjustments verified by dedicated tests. |

_No safe-to-move files were identified under the current patterns._

## Per-File Analysis & Required Actions

### codex_task_sequence.py — Requires Refactor

This shim re-exports `cli.task_sequence` so legacy entry points can continue importing the historical module name. While there are no direct code imports inside the repository, documentation and status templates cite the file explicitly, and downstream tooling may still execute `import codex_task_sequence`.

| Reference | Line(s) | Snippet | Suggested Action |
| --- | --- | --- | --- |
| `docs/CHANGELOG/changelog_codex.md` | 388-393 | “Added codex_ready_task_sequence.yaml … Replaced codex_task_sequence.py …” | Update narrative to mention the shim now lives under `src/legacy_root/` after relocation. |
| `docs/status_update_prompt.md` | 184-189 | "## Codex-ready Task Sequence" block with `{{codex_task_sequence}}` placeholder | Confirm template instructions reference the new module path or clarify the placeholder still points to the legacy import name. |

**Proposed Refactor Steps**

1. Move the shim with history: `git mv codex_task_sequence.py src/legacy_root/codex_task_sequence.py`.
2. Preserve the legacy import alias during interpreter bootstrap by extending `sitecustomize.py` to register the relocated module under its original name:

   ```diff
   diff --git a/sitecustomize.py b/sitecustomize.py
   --- a/sitecustomize.py
   +++ b/sitecustomize.py
   @@
   -import sys
   +import importlib
   +import sys
   @@
   if src_str not in sys.path:
       sys.path.insert(0, src_str)
   +
   +# Keep ``import codex_task_sequence`` working after relocating the shim.
   +sys.modules.setdefault(
   +    "codex_task_sequence",
   +    importlib.import_module("legacy_root.codex_task_sequence"),
   +)
   ```
3. Review Markdown references and update any file-path mentions to match the new location.
4. No packaging metadata changes are required because the project already uses `src` layout; ensure `src/legacy_root/__init__.py` exists (create if necessary) so the module import works.

**Verification (post-move)**

- `python -c "import codex_task_sequence; print(codex_task_sequence.implementation_module)"`
- `python -m cli.task_sequence --help`
- `pytest tests/tracking/test_mlflow_entrypoints.py tests/tracking/test_default_file_backend.py`

### conftest.py — Blocked

`conftest.py` seeds `sys.path`, `PYTHONPATH`, and environment guards before pytest collection. Removing it from the repository root prevents auto-discovery of fixtures and breaks deterministic test setup referenced by documentation and tooling.

| Reference | Line(s) | Snippet | Suggested Action |
| --- | --- | --- | --- |
| `docs/dev/testing.md` | 36-42 | “Tests are deterministic: `tests/conftest.py` seeds …” (implicitly relies on root stub) | If relocation is unavoidable, leave a root stub that re-imports the moved module so docs stay accurate. |
| `docs/guides/offline_transformers.md` | 1-14 | “`codex_local_gates.sh`/`tests/conftest.py`” guidance | Update guidance only after a stub is in place. |
| `scripts/space_traversal/detectors/testing_infrastructure.py` | 20-58 | Detector flags `conftest.py` as a pytest configuration artifact | Update detector logic only after new location is confirmed and stub exists. |

**Blocking Issues & Recommendations**

- Pytest loads root-level `conftest.py` automatically; moving it requires adding a lightweight root file that imports the relocated module and re-applies `sys.path`/environment mutations before collection.
- Coordination with QA/Testing stakeholders is necessary before attempting any move because CI and developer workflows depend on the current path.

### sitecustomize.py — Blocked

`sitecustomize.py` is imported implicitly whenever Python starts inside this repository, ensuring `src` is on `sys.path` and that MLflow defaults are installed. Multiple tests reload it to assert side effects, and internal tooling expects it at the repository root.

| Reference | Line(s) | Snippet | Suggested Action |
| --- | --- | --- | --- |
| `tests/tracking/test_mlflow_entrypoints.py` | 19-26 | Reloads `sitecustomize` to validate MLflow URI enforcement | Keep a root module or stub so the import path remains valid before modifying tests. |
| `tests/tracking/test_default_file_backend.py` | 10-19 | Imports and reloads `sitecustomize`, expecting environment variables | Provide a root shim if the implementation moves. |
| `tools/apply_branchA_all.py` | 66-97 | Automation script patches `sitecustomize.py` at the root path | Update automation only after a stub or new path is finalized. |

**Blocking Issues & Recommendations**

- Python only auto-imports `sitecustomize` when it is importable via the default module search path; relocating it without updating installation metadata or leaving a root proxy would break interpreter initialization and downstream tests.
- Any relocation plan must include either a `.pth` file or a root `sitecustomize.py` that delegates to the new implementation.

## Migration Commands & Patches (Dry Run)

Because this is a dry run, no commands were executed. When ready to proceed:

```bash
git mv codex_task_sequence.py src/legacy_root/codex_task_sequence.py
# Apply the sitecustomize alias diff shown above
```text

Update documentation references via targeted edits (examples):

- Replace `codex_task_sequence.py` path mentions with `src/legacy_root/codex_task_sequence.py` in affected Markdown files.
- Clarify templates that the import alias remains `codex_task_sequence` even after the move.

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Alias not installed, breaking `import codex_task_sequence` for legacy tooling | High | Medium | Add `sys.modules` aliasing in `sitecustomize.py` and run import smoke tests. |
| Documentation becomes outdated after relocation | Medium | Medium | Update changelog and status template during migration; include doc review in checklist. |
| Moving `conftest.py`/`sitecustomize.py` without stubs breaks CI immediately | High | High | Treat both files as blocked until stub strategy and stakeholder approval are obtained. |

## Rollback Instructions

1. `git mv src/legacy_root/codex_task_sequence.py codex_task_sequence.py`
2. `git checkout -- sitecustomize.py` (to drop alias changes)
3. Revert any documentation edits touching the file path references.
4. Re-run targeted pytest suites to ensure the environment behaves as before.

## Post-Migration Checklist

- [ ] `python -c "import codex_task_sequence"`
- [ ] `python -m cli.task_sequence --help`
- [ ] `pytest tests/tracking/test_mlflow_entrypoints.py tests/tracking/test_default_file_backend.py`
- [ ] Review and update changelog/status templates mentioning `codex_task_sequence.py`

## Notes

- This is a dry-run analysis. No repository state was modified.
- Proceed only after stakeholder sign-off for blocked files.
